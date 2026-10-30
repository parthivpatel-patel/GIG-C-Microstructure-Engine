"""SEC configuration,private startup and bounded source fixtures;never live requests."""
import asyncio,copy,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .sec_config import enabled,readiness,resolve,save,KEYS,user_agent_valid
from .service import StockWorkspace,AccessError
from .test_workspace import SEC_ENV,submissions,facts

class Configuration(unittest.TestCase):
 def test_boolean_forms_and_secure_defaults(self):
  for value in ['1','true','TRUE',' yes ','On',True]:self.assertTrue(enabled(value))
  for value in [None,'','0','false','no','off','maybe',1,False,[],{}]:self.assertFalse(enabled(value))
 def test_reported_true_flags_and_readiness_use_same_policy(self):
  for value in ['true','yes','on','1']:
   w=StockWorkspace(environment={**SEC_ENV,'GIG_SEC_ENABLED':value,'GIG_SEC_POLICY_REVIEWED':value});self.assertEqual(w.permission('sec')['User-Agent'],SEC_ENV[KEYS[2]]);self.assertTrue(w.configuration()['sec']['ready']);self.assertEqual(w.configuration()['sec']['missing_configuration'],[])
 def test_disabled_missing_policy_and_invalid_contact(self):
  for env in [{},{**SEC_ENV,'GIG_SEC_POLICY_REVIEWED':'0'},{**SEC_ENV,'GIG_SEC_USER_AGENT':''},{**SEC_ENV,'GIG_SEC_USER_AGENT':'garbage@@!'},{**SEC_ENV,'GIG_SEC_USER_AGENT':'App bad@example.invalid\r\nInjected: header'}]:
   w=StockWorkspace(environment=env);self.assertFalse(w.configuration()['sec']['ready'])
   with self.assertRaises(AccessError):w.permission('sec')
  self.assertIn(KEYS[2],StockWorkspace(environment={**SEC_ENV,KEYS[2]:'invalid'}).configuration()['sec']['missing_configuration'])
 def test_policy_ack_and_identity_required_by_helper(self):
  with tempfile.TemporaryDirectory() as root:
   for contact,policy in [('test@example.invalid',False),('bad',True),('test@example.invalid\n',True)]:
    with self.assertRaises(ValueError):save(contact,policy_reviewed=policy,root=root)
   self.assertFalse((Path(root)/'.gig-sec').exists())
 def test_private_settings_persist_and_environment_wins(self):
  with tempfile.TemporaryDirectory() as root:
   save('test@example.invalid',policy_reviewed=True,root=root);env,meta=resolve({},root=root);self.assertTrue(readiness(env)['ready']);self.assertEqual(meta['source'],'private_file_with_environment_precedence')
   explicit,_=resolve({KEYS[0]:'false',KEYS[2]:''},root=root);self.assertFalse(readiness(explicit)['ready']);self.assertEqual(explicit[KEYS[2]],'')
   self.assertEqual((Path(root)/'.gig-sec/config.json').stat().st_mode&0o777,0o600)
 def test_duplicate_oversize_unknown_and_world_readable_config_fail_closed(self):
  with tempfile.TemporaryDirectory() as root:
   save('test@example.invalid',policy_reviewed=True,root=root);p=Path(root)/'.gig-sec/config.json';valid=p.read_text()
   for text in ['{"GIG_SEC_ENABLED":"1","GIG_SEC_ENABLED":"0"}','x'*4097,'{"ALPACA_API_KEY_ID":"forbidden"}']:
    p.write_text(text);env,meta=resolve({},root=root);self.assertFalse(readiness(env)['ready']);self.assertIsNotNone(meta['error'])
   p.write_text(valid);p.chmod(0o644);self.assertIsNotNone(resolve({},root=root)[1]['error'])
 def test_symlink_configuration_not_read(self):
  with tempfile.TemporaryDirectory() as root:
   target=Path(root)/'other';target.mkdir();(Path(root)/'.gig-sec').symlink_to(target,target_is_directory=True);env,meta=resolve({},root=root);self.assertIsNotNone(meta['error']);self.assertFalse(readiness(env)['ready'])
 def test_two_fresh_processes_see_same_private_readiness_without_contact_disclosure(self):
  with tempfile.TemporaryDirectory() as root:
   save('test@example.invalid',policy_reviewed=True,root=root)
   code='import sys,json;from terminal.stocks.sec_config import resolve,readiness;e,m=resolve({},root=sys.argv[1]);print(json.dumps(readiness(e)))'
   for _ in range(2):
    r=subprocess.run([sys.executable,'-c',code,root],text=True,capture_output=True,timeout=5);self.assertEqual(r.returncode,0,r.stderr);self.assertTrue(json.loads(r.stdout)['ready']);self.assertNotIn('test@example.invalid',r.stdout)
 def test_backend_default_configuration_uses_private_loader(self):
  with tempfile.TemporaryDirectory() as root:
   save('test@example.invalid',policy_reviewed=True,root=root)
   with patch('terminal.stocks.sec_config.resolve',side_effect=lambda e:resolve({},root=root)):
    w=StockWorkspace();self.assertTrue(w.configuration()['sec']['ready']);self.assertNotIn('test@example.invalid',json.dumps(w.configuration()))
   start=Path('scripts/start_terminal.sh').read_text();self.assertLess(start.index('scripts/configure_sec.py --check'),start.index('exec .venv/bin/python -m terminal.server'))
   self.assertIn('if msgpack.version < (1, 2, 3):',start)
 def test_alpaca_flags_are_not_changed_by_sec_parsing_or_private_file(self):
  w=StockWorkspace(environment={**SEC_ENV,'GIG_ALPACA_ENABLED':'true'});self.assertFalse(w.configuration()['alpaca']['ready'])

class Refresh(unittest.IsolatedAsyncioTestCase):
 async def test_true_config_bounded_aapl_facts_and_recent_cache_avoid_requests(self):
  urls=[];clock=[100.]
  async def fetch(url,headers,cap):
   urls.append(url);self.assertEqual(headers['User-Agent'],SEC_ENV[KEYS[2]]);self.assertTrue(url.startswith('https://data.sec.gov/'));return json.dumps(submissions() if '/submissions/' in url else facts()).encode()
  w=StockWorkspace(environment={**SEC_ENV,KEYS[0]:'true',KEYS[1]:'yes'},fetcher=fetch,clock=lambda:clock[0])
  async def sleep(_):w.last_request=-100
  with patch('terminal.stocks.service.asyncio.sleep',sleep):
   first=await w.refresh('AAPL','sec',allow_cached=True);self.assertEqual(len(urls),2);self.assertEqual(first['instrument']['cik'],'0000320193');before=copy.deepcopy(w.cache)
   second=await w.refresh('AAPL','sec',allow_cached=True);self.assertEqual(second['sec_refresh']['status'],'CACHED_RECENT');self.assertEqual(len(urls),2);self.assertEqual(w.cache,before)
   clock[0]+=61;await w.refresh('AAPL','sec',allow_cached=True);self.assertEqual(len(urls),4)
 async def test_policy_revocation_precedes_cache_hit(self):
  w=StockWorkspace(environment={**SEC_ENV,KEYS[0]:'off'});w.cache['AAPL']={'sec':{}};w.sec_accepted['AAPL']=w.clock()
  with self.assertRaises(AccessError):await w.refresh('AAPL','sec',allow_cached=True)
 async def test_429_cooldown_no_retries_or_raw_error_disclosure(self):
  import httpx
  calls=[]
  def handler(request):calls.append(request);return httpx.Response(429,text='private_upstream_error')
  real=httpx.AsyncClient;w=StockWorkspace(environment=SEC_ENV,clock=lambda:100.)
  with patch('terminal.stocks.service.httpx.AsyncClient',side_effect=lambda **kw:real(transport=httpx.MockTransport(handler),**kw)):
   with self.assertRaises(AccessError):await w.fetch('sec','https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json',w.permission('sec'))
   with self.assertRaisesRegex(AccessError,'cooldown'):await w.fetch('sec','https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json',w.permission('sec'))
  self.assertEqual(len(calls),1);self.assertNotIn('private_upstream_error',json.dumps(w.configuration()))
 async def test_missing_and_malformed_facts_preserve_good_filings(self):
  async def fetch(url,*_):return json.dumps(submissions() if '/submissions/' in url else {'cik':320193,'facts':{'us-gaap':{'Revenues':{'units':{'USD':'bad'}}}}}).encode()
  w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
  async def sleep(_):w.last_request=-100
  with patch('terminal.stocks.service.asyncio.sleep',sleep):out=await w.refresh('AAPL','sec')
  self.assertEqual(out['fundamentals']['status'],'PARTIAL');self.assertTrue(out['fundamentals']['filings']);self.assertNotIn('financials',out['fundamentals'])
 async def test_failure_keeps_accepted_data_and_reports_error(self):
  async def fetch(url,*_):return json.dumps(submissions() if '/submissions/' in url else facts()).encode()
  w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
  async def sleep(_):w.last_request=-100
  with patch('terminal.stocks.service.asyncio.sleep',sleep):await w.refresh('AAPL','sec')
  old=copy.deepcopy(w.cache)
  async def fail(*_):raise RuntimeError('secret_private_exception')
  w.fetcher=fail;w.last_request=-100
  with self.assertRaises(AccessError):await w.refresh('AAPL','sec')
  self.assertEqual(w.cache,old);view=w.view('AAPL');self.assertEqual(view['sec_refresh']['status'],'ERROR');self.assertNotIn('secret_private_exception',json.dumps(view))
  started=asyncio.Event()
  async def pending(*_):started.set();await asyncio.Event().wait()
  other=StockWorkspace(environment=SEC_ENV,fetcher=pending)
  task=asyncio.create_task(other.refresh('AAPL','sec'));await started.wait();task.cancel()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertEqual(other.sec_refresh_state['AAPL']['status'],'CANCELLED');self.assertEqual(other.cache,{})


 async def test_component_failure_does_not_erase_previously_accepted_financials(self):
  async def fetch(url,*_):return json.dumps(submissions() if '/submissions/' in url else facts()).encode()
  w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
  async def sleep(_):w.last_request=-100
  with patch('terminal.stocks.service.asyncio.sleep',sleep):await w.refresh('AAPL','sec')
  before=copy.deepcopy(w.cache)
  async def partial(url,*_):
   if '/companyfacts/' in url:raise AccessError('upstream_http_429')
   return json.dumps(submissions()).encode()
  w.fetcher=partial;w.last_request=-100
  with patch('terminal.stocks.service.asyncio.sleep',sleep):
   with self.assertRaisesRegex(AccessError,'cached_financials_preserved'):await w.refresh('AAPL','sec')
  self.assertEqual(w.cache,before);self.assertEqual(w.view('AAPL')['sec_refresh']['status'],'ERROR')

class FixtureBoundary(unittest.TestCase):
 def test_fixture_boundary_recognizes_true_alias_before_any_collection(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  for value in ['true','yes','on']:
   env={**SEC_ENV,KEYS[0]:value,KEYS[1]:value}
   with patch.dict(os.environ,{**env,'GIG_ALPACA_ENABLED':'0','GIG_LIVE_ENABLED':'0','GIG_COINBASE_ENABLED':'0','GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'}),TestClient(create_app(stock_workspace=StockWorkspace(environment=env)),base_url='http://127.0.0.1:8787') as c:
    health=c.get('/api/v1/health').json();self.assertEqual(health['status'],'ok');self.assertFalse(health['fixture_tests_safe'])
