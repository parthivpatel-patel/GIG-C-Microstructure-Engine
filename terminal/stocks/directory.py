"""Fixed official listing sources;rights-gated,atomic two-file replacement,not feed entitlement."""
import asyncio,bisect,datetime,hashlib,httpx,re,time
from pathlib import Path
from .market_catalog import MarketCatalog
from .identity import SYMBOL_PATTERN
URLS={'nasdaq':'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt','other':'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'}
HEADERS={'nasdaq':['Symbol','Security Name','Market Category','Test Issue','Financial Status','Round Lot Size','ETF','NextShares'],'other':['ACT Symbol','Security Name','Exchange','CQS Symbol','ETF','Round Lot Size','Test Issue','NASDAQ Symbol']}
EXCHANGES={'A':'NYSE American','N':'NYSE','P':'NYSE Arca','Z':'Cboe BZX','V':'IEX'}
MAX_BYTES=8*1024*1024;MAX_ROWS=100000
class SearchIndex:
 def __init__(self,rows):
  self.rows=rows;self.symbols=sorted(rows);self.tokens={}
  for s,r in rows.items():
   for token in set(re.findall(r'[a-z0-9]+',r['name'].casefold())):self.tokens.setdefault(token,set()).add(s)
  self.words=sorted(self.tokens)
 def search(self,query,offset=0,limit=20):
  if type(query) is not str or len(query)>80 or any(ord(c)<32 for c in query) or type(offset) is not int or type(limit) is not int or not 0<=offset<=MAX_ROWS or not 1<=limit<=100:raise ValueError('directory_search_bounds')
  q=query.strip().upper();prefix=self.symbols[bisect.bisect_left(self.symbols,q):bisect.bisect_right(self.symbols,q+'\uffff')] if q else self.symbols
  hits=set(prefix);terms=re.findall(r'[a-z0-9]+',query.casefold());names=None
  for term in terms:
   found=set()
   for word in self.words[bisect.bisect_left(self.words,term):bisect.bisect_right(self.words,term+'\uffff')]:found.update(self.tokens[word])
   names=found if names is None else names&found
  hits.update(names or ());ordered=sorted(hits,key=lambda s:(s!=q,not s.startswith(q),s));chosen=ordered[offset:offset+limit]
  return {'results':[dict(self.rows[s]) for s in chosen],'matches':len(ordered),'returned':len(chosen),'offset':offset,'limit':limit,'next_offset':offset+limit if offset+limit<len(ordered) else None,'search_method':'exact ticker, ticker prefix, all company-name word prefixes'}
def parse_files(files,origin='HISTORICAL_SYNTHETIC'):
 rows={};excluded={'test_issue':0,'unsupported_symbol':0};sources=[]
 for kind in ('nasdaq','other'):
  raw=files[kind]
  if type(raw) is not bytes or not 1<=len(raw)<=MAX_BYTES:raise ValueError('directory_bytes')
  text=raw.decode('utf-8-sig');lines=text.splitlines()
  if len(lines)<3 or len(lines)>MAX_ROWS+2 or any(len(l)>2048 for l in lines):raise ValueError('directory_record_bounds')
  if lines[0].split('|')!=HEADERS[kind]:raise ValueError('directory_header')
  footer=lines[-1].split('|');stamp=footer[0]
  if len(footer)!=len(HEADERS[kind]) or any(footer[1:]) or not stamp.startswith('File Creation Time: '):raise ValueError('directory_footer')
  created=datetime.datetime.strptime(stamp[20:],'%m%d%Y%H:%M').isoformat()
  for line in lines[1:-1]:
   values=line.split('|')
   if len(values)!=len(HEADERS[kind]):raise ValueError('directory_columns')
   r=dict(zip(HEADERS[kind],values));symbol=r['Symbol' if kind=='nasdaq' else 'ACT Symbol'];name=r['Security Name']
   if not 1<=len(name)<=256 or any(ord(c)<32 for c in name) or r['Test Issue'] not in ('Y','N') or r['ETF'] not in ('Y','N') or not re.fullmatch(r'[1-9][0-9]{0,8}',r['Round Lot Size']):raise ValueError('directory_fields')
   if kind=='nasdaq' and (r['Market Category'] not in ('Q','G','S') or r['Financial Status'] not in tuple('NDEQGHJK') or r['NextShares'] not in ('Y','N')):raise ValueError('directory_nasdaq_enum')
   if kind=='other' and r['Exchange'] not in EXCHANGES:raise ValueError('directory_exchange')
   if r['Test Issue']=='Y':excluded['test_issue']+=1;continue
   if not re.fullmatch(SYMBOL_PATTERN,symbol):excluded['unsupported_symbol']+=1;continue
   if symbol in rows:raise ValueError('directory_symbol_collision')
   if len(rows)>=MAX_ROWS:raise ValueError('directory_total_budget')
   rows[symbol]={'symbol':symbol,'name':name,'exchange':'NASDAQ' if kind=='nasdaq' else EXCHANGES[r['Exchange']],'asset_id':None,'security_type':'ETF' if r['ETF']=='Y' else 'NEXTSHARES' if r.get('NextShares')=='Y' else 'UNCLASSIFIED_LISTED_SECURITY','listing_status':'PRESENT_IN_SOURCE_NOT_TRADABILITY','round_lot_size':r['Round Lot Size'],'financial_status':r.get('Financial Status'),'aliases':{k:r[k] for k in ('CQS Symbol','NASDAQ Symbol') if k in r},'source_directory':kind}
  sources.append({'url':URLS[kind],'sha256':hashlib.sha256(raw).hexdigest(),'file_creation_local_time':created,'clock_zone':'UNSPECIFIED_BY_FILE','source_records':len(lines)-2})
 if len({s['file_creation_local_time'][:10] for s in sources})!=1:raise ValueError('directory_date_mismatch')
 if not rows:raise ValueError('directory_empty')
 catalog=MarketCatalog();catalog.rows=rows;catalog.source={'reference':'Nasdaq Trader two-file symbol directory','as_of':None,'authority':'OFFICIAL_DIRECTORY_RESPONSE' if origin=='OBSERVED_OFFICIAL_RESPONSE' else 'AUTHORED_DIRECTORY_FIXTURE','sources':sources,'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':origin,'excluded':excluded,'coverage':'Accepted non-test symbols from both complete files;not delisted history,security subtype inference,SEC identity or feed entitlement'};catalog.index=[];catalog.search_index=SearchIndex(rows)
 return catalog
class DirectoryService:
 def __init__(self,workspace,fetcher=None,clock=time.monotonic):
  self.workspace=workspace;self.fetcher=fetcher;self.clock=clock;self.last_attempt=None;self.lock=asyncio.Lock();self.state={'status':'NOT_LOADED','last_error':None,'accepted_count':0,'last_success':None}
 def approved(self):
  e=self.workspace.environment;ref=e.get('GIG_DIRECTORY_PERMISSION_REFERENCE','')
  return e.get('GIG_DIRECTORY_USE_APPROVED')=='1' and type(ref) is str and 1<=len(ref)<=256 and not any(ord(c)<32 for c in ref)
 async def refresh(self):
  if not self.approved():raise ValueError('directory_source_use_not_approved')
  if self.lock.locked():raise ValueError('directory_refresh_busy')
  if self.last_attempt is not None and self.clock()-self.last_attempt<300:raise ValueError('directory_refresh_cooldown')
  async with self.lock:
   self.last_attempt=self.clock();files={}
   try:
    async with asyncio.timeout(25):
     if self.fetcher:
      for kind,url in URLS.items():files[kind]=await self.fetcher(url)
     else:
      async with httpx.AsyncClient(timeout=10,follow_redirects=False,trust_env=True) as client:
       for kind,url in URLS.items():
        async with client.stream('GET',url) as response:
         if response.status_code!=200:raise ValueError('directory_http_status')
         if response.headers.get('content-length') and int(response.headers['content-length'])>MAX_BYTES:raise ValueError('directory_content_length')
         raw=bytearray()
         async for block in response.aiter_bytes(65536):
          if len(raw)+len(block)>MAX_BYTES:raise ValueError('directory_bytes')
          raw.extend(block)
         files[kind]=bytes(raw)
     catalog=await asyncio.to_thread(parse_files,files,'HISTORICAL_SYNTHETIC' if self.fetcher else 'OBSERVED_OFFICIAL_RESPONSE')
     self.workspace.catalog=catalog
     self.state={'status':'ACCEPTED','last_error':None,'accepted_count':len(catalog.rows),'last_success':catalog.source['received_at']}
   except asyncio.CancelledError:raise
   except (ValueError,OSError,UnicodeError,httpx.HTTPError,TimeoutError):
    self.state={**self.state,'status':'STALE_LAST_ACCEPTED' if self.state['accepted_count'] else 'UNAVAILABLE','last_error':'directory_refresh_rejected;previous_identity_snapshot_preserved'}
    raise ValueError('directory_refresh_rejected') from None
  return self.view()
 def view(self):return {**self.state,'approved':self.approved(),'source':self.workspace.catalog.source,'catalog_count':len(self.workspace.catalog.rows),'actual_official_count':self.state['accepted_count'] if self.workspace.catalog.source.get('authority')=='OFFICIAL_DIRECTORY_RESPONSE' else 0,'limits':{'bytes_per_file':MAX_BYTES,'max_rows_resource_budget':MAX_ROWS,'refresh_interval_seconds':21600},'retention':'Process-lifetime catalog only;no directory file persisted','identity_only':True}
 async def run(self):
  while True:
   if self.approved():
    try:await self.refresh()
    except ValueError:pass
   if self.approved() or self.workspace.environment.get('GIG_SEC_DIRECTORY_AUTO_REFRESH')=='1':
    try:
     self.workspace.permission('sec')
     await self.workspace.refresh_identities()
    except (ValueError,httpx.HTTPError,TimeoutError):pass
   await asyncio.sleep(21600)
