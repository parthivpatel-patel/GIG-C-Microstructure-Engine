"""Private,owner-permitted directory import;listing identity never grants feed entitlement."""
import json,hashlib,re,os,stat,datetime
from .identity import SEEDS,SYMBOL_PATTERN
PATTERN=SYMBOL_PATTERN
class MarketCatalog:
 def __init__(self,raw=None):
  self.reason=None;self.source={'reference':'curated_routing_seeds','as_of':None,'sha256':None,'authority':'CURATED_NOT_CURRENT_EXCHANGE_DIRECTORY'}
  rows=[{'symbol':s,'name':n,'exchange':e,'asset_id':None} for s,n,e,_ in SEEDS]+[{'symbol':s,'name':n,'exchange':'NASDAQ','asset_id':None} for s,n in [('APLD','Applied Digital Corporation'),('CRWV','CoreWeave, Inc.')]]
  if raw is not None:
   if type(raw) is not bytes or len(raw)>8*1024*1024:raise ValueError('catalog_byte_budget')
   def pairs(items):
    out={}
    for k,v in items:
     if k in out:raise ValueError('catalog_duplicate_field')
     out[k]=v
    return out
   try:p=json.loads(raw,object_pairs_hook=pairs)
   except (ValueError,RecursionError):raise ValueError('catalog_json') from None
   if type(p) is not dict or set(p)!={'schema','source','assets'} or p['schema']!='gig.market.catalog.v1':raise ValueError('catalog_schema')
   source=p['source']
   if type(source) is not dict or set(source)!={'reference','as_of'}:raise ValueError('catalog_source')
   self.text(source['reference'],256)
   if source['as_of'] is not None:datetime.date.fromisoformat(source['as_of'])
   if type(p['assets']) is not list or not 1<=len(p['assets'])<=50000:raise ValueError('catalog_row_budget')
   rows=p['assets'];self.source={**source,'sha256':hashlib.sha256(raw).hexdigest(),'authority':'OWNER_SUPPLIED_NOT_INDEPENDENTLY_QUALIFIED'}
  self.rows={}
  for r in rows:
   if type(r) is not dict or set(r)!={'symbol','name','exchange','asset_id'}:raise ValueError('catalog_asset')
   if type(r['symbol']) is not str or not re.fullmatch(PATTERN,r['symbol']):raise ValueError('catalog_symbol')
   self.text(r['name'],128);self.text(r['exchange'],32)
   if r['asset_id'] is not None:self.text(r['asset_id'],128)
   if r['symbol'] in self.rows:raise ValueError('catalog_duplicate_symbol')
   self.rows[r['symbol']]=dict(r)
  self.index=[(r['symbol'].casefold(),r['name'].casefold(),r) for r in sorted(self.rows.values(),key=lambda r:r['symbol'])]
 @staticmethod
 def text(v,limit):
  if type(v) is not str or not 1<=len(v)<=limit or any(ord(c)<32 for c in v):raise ValueError('catalog_text')
 @classmethod
 def configured(cls,environment):
  path=environment.get('GIG_MARKET_CATALOG_FILE')
  if not path:return cls()
  try:
   if environment.get('GIG_MARKET_CATALOG_USE_APPROVED')!='1':raise ValueError('catalog_permission')
   with os.fdopen(os.open(path,os.O_RDONLY|os.O_NONBLOCK|getattr(os,'O_NOFOLLOW',0)),'rb') as f:
    s=os.fstat(f.fileno())
    if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)&0o077:raise ValueError('catalog_private_file')
    return cls(f.read(8*1024*1024+1))
  except (OSError,ValueError,TypeError,KeyError):
   value=cls();value.reason='configured_catalog_unavailable_or_unapproved';return value
 def instrument(self,symbol):
  if type(symbol) is not str or symbol not in self.rows:raise ValueError('unsupported_market_symbol')
  return {**self.rows[symbol],'identity_source':self.source}
 def search(self,query,offset=0,limit=20):
  if not hasattr(self,'search_index'):
   from .directory import SearchIndex
   self.search_index=SearchIndex(self.rows)
  return {**self.search_index.search(query,offset,limit),'schema':'gig.market.search.v1','catalog_count':len(self.rows),'source':self.source,'reason':self.reason,'scope':self.source.get('coverage','Market identity only;not SEC CIK coverage,tradability or streaming entitlement')}
