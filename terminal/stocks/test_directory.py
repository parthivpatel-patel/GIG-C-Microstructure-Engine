"""Authored listing contracts,not exchange observations or listing coverage evidence."""
import asyncio,copy,unittest
from .directory import parse_files,HEADERS,DirectoryService,SearchIndex

def files():
 def make(kind,rows):return ('|'.join(HEADERS[kind])+'\n'+'\n'.join('|'.join(r) for r in rows)+'\nFile Creation Time: 1028202616:00'+'|'*(len(HEADERS[kind])-1)+'\n').encode()
 return {'nasdaq':make('nasdaq',[[s,n,'Q','N','N','100','N','N'] for s,n in [('AAPL','Authored Apple'),('APLD','Authored Applied Digital'),('CRWV','Authored CoreWeave'),('GOOGL','Authored Alphabet Class A')]]),'other':make('other',[['EXMP.A','Authored Share Class A','N','EXMP.A','N','100','N','EXMP/A'],['ETFQ','Authored Index ETF','P','ETFQ','Y','100','N','ETFQ'],['TEST','Authored Test','A','TEST','N','100','Y','TEST']])}
class Directory(unittest.TestCase):
 def test_identity_and_explicit_classification(self):
  c=parse_files(files());self.assertEqual(len(c.rows),6);self.assertEqual(c.rows['ETFQ']['security_type'],'ETF');self.assertEqual(c.rows['GOOGL']['security_type'],'UNCLASSIFIED_LISTED_SECURITY');self.assertEqual(c.rows['EXMP.A']['aliases']['NASDAQ Symbol'],'EXMP/A');self.assertEqual(c.source['excluded']['test_issue'],1);self.assertEqual(c.source['sources'][0]['clock_zone'],'UNSPECIFIED_BY_FILE')
 def test_required_symbols_search_without_entitlement(self):
  from .service import StockWorkspace
  w=StockWorkspace(environment={});w.catalog=parse_files(files())
  for s in ['AAPL','APLD','CRWV','GOOGL']:
   self.assertEqual(w.search(s)['results'][0]['symbol'],s);self.assertFalse(w.view(s)['capabilities']['iex_refresh'])
  self.assertIsNone(w.resolve('CRWV')['cik'])
 def test_index_name_prefix_pagination_and_bounds(self):
  c=parse_files(files());self.assertEqual(c.search('applied')['results'][0]['symbol'],'APLD');self.assertEqual(c.search('',2,2)['next_offset'],4);self.assertEqual(len(c.search('',4,2)['results']),2)
  for args in [('x',-1,2),('x',0,0),('x',0,101),('x\n',0,2)]:
   with self.assertRaises(ValueError):c.search(*args)
  # Independent scan/rank oracle for indexed pages,including broad name matches.
  rows={f'X{i:03}':{'symbol':f'X{i:03}','name':f'Authored group {i%7} corporation'} for i in range(200)};index=SearchIndex(rows)
  for query in ['','X001','X0','auth','group 3','corpor','unmatched']:
   words=query.lower().split();expected=[]
   for symbol,row in rows.items():
    name_words=row['name'].lower().split()
    if symbol.startswith(query.upper()) or words and all(any(w.startswith(term) for w in name_words) for term in words):expected.append(symbol)
   expected.sort(key=lambda s:(s!=query.upper(),not s.startswith(query.upper()),s))
   self.assertEqual([r['symbol'] for r in index.search(query,3,20)['results']],expected[3:23]);self.assertEqual(index.search(query)['matches'],len(expected))
 def test_invalid_footer_columns_enums_and_collision(self):
  f=files()
  for change in [lambda v:v.replace(b'File Creation Time:',b'No creation marker'),lambda v:v.replace(b'|Q|N|N|100|',b'|Z|N|N|100|'),lambda v:v.replace(b'AAPL|',b'CRWV|'),lambda v:v.replace(b'|100|',b'|0|')]:
   with self.assertRaises(ValueError):parse_files({**f,'nasdaq':change(f['nasdaq'])})
 def test_atomic_two_file_refresh_cooldown_and_failure_retains_previous(self):
  from .service import StockWorkspace
  async def run():
   w=StockWorkspace(environment={'GIG_DIRECTORY_USE_APPROVED':'1','GIG_DIRECTORY_PERMISSION_REFERENCE':'AUTHORED_PERMISSION_NOT_ACTUAL_RIGHTS'});ticks=[0];data=files()
   async def fetch(url):return data['nasdaq' if url.endswith('nasdaqlisted.txt') else 'other']
   d=DirectoryService(w,fetch,lambda:ticks[0]);await d.refresh();old=w.catalog
   with self.assertRaises(ValueError):await d.refresh()
   ticks[0]=301;data['other']=b'truncated'
   with self.assertRaises(ValueError):await d.refresh()
   self.assertIs(w.catalog,old);self.assertEqual(d.view()['status'],'STALE_LAST_ACCEPTED');self.assertEqual(d.view()['actual_official_count'],0)
  asyncio.run(run())
 def test_no_request_without_source_approval(self):
  from .service import StockWorkspace
  called=[]
  async def fetch(url):called.append(url);return b''
  async def run():
   with self.assertRaises(ValueError):await DirectoryService(StockWorkspace(environment={}),fetch).refresh()
  asyncio.run(run());self.assertEqual(called,[])
 def test_v2_pagination_and_proof_mutation_boundary(self):
  from .service import StockWorkspace
  from terminal.server.app import create_app
  from starlette.testclient import TestClient
  w=StockWorkspace(environment={});w.catalog=parse_files(files())
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
   self.assertEqual(len(c.get('/api/v2/securities?limit=2&offset=2').json()['results']),2);self.assertEqual(c.get('/api/v2/securities?limit=0').status_code,422);self.assertFalse(c.get('/api/v2/securities/status').json()['approved']);self.assertEqual(c.post('/api/v1/stocks/directory-refresh',json={}).status_code,403);self.assertEqual(c.post('/api/v1/stocks/directory-refresh',json={},headers={'Origin':'http://127.0.0.1:8787'}).status_code,422)
 def test_source_byte_and_clock_bounds_and_cross_directory_collision(self):
  from .directory import MAX_BYTES
  f=files()
  for other in [b'x'*(MAX_BYTES+1),f['other'].replace(b'10282026',b'10272026'),f['other'].replace(b'EXMP.A|',b'AAPL|',1)]:
   with self.assertRaises(ValueError):parse_files({**f,'other':other})
 def test_cancelled_refresh_never_publishes_partial_directory(self):
  from .service import StockWorkspace
  async def run():
   w=StockWorkspace(environment={'GIG_DIRECTORY_USE_APPROVED':'1','GIG_DIRECTORY_PERMISSION_REFERENCE':'AUTHORED'});before=w.catalog;entered=asyncio.Event()
   async def fetch(url):entered.set();await asyncio.sleep(100)
   d=DirectoryService(w,fetch);task=asyncio.create_task(d.refresh());await entered.wait();task.cancel()
   with self.assertRaises(asyncio.CancelledError):await task
   self.assertIs(w.catalog,before);self.assertFalse(d.lock.locked())
  asyncio.run(run())
