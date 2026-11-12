"""Actual stock workspace → read-only company adapter and private CLI exports."""
import copy,json,tempfile,unittest,ast
from pathlib import Path
from unittest.mock import patch
from .test_xbrl_statements import collection,entry,LATE,ROLE
from .service import StockWorkspace
from .xbrl_product import company_contract
from .xbrl_instance import XBRLError
from .xbrl_collection import FilingCollection
class XBRLProduct(unittest.TestCase):
 def test_unavailable_is_honest_and_does_not_fetch_or_change_existing_cache(self):
  w=StockWorkspace(environment={});before=copy.deepcopy(w.cache)
  with patch.object(w,'fetch',side_effect=AssertionError('NO_PROVIDER')):
   r=company_contract(w,'AAPL',LATE,role=ROLE);self.assertEqual(r['statement_view']['reason'],'NO_EXPLICITLY_ADMITTED_XBRL_COLLECTION');self.assertEqual(r['data_origin'],'UNAVAILABLE');self.assertTrue(r['read_only']);self.assertEqual(w.cache,before)
 def test_exact_symbol_and_cik_scope_and_detached_collection(self):
  w=StockWorkspace(environment={});c=collection();receipt=w.admit_xbrl_collection('AAPL',c);self.assertEqual(receipt['issuer_cik'],'0000320193');r=company_contract(w,'AAPL',LATE,role=ROLE);self.assertEqual(r['statement_view']['periods'][0]['rows'][0]['value'],'1000');self.assertEqual(r['data_origin'],'HISTORICAL_SYNTHETIC');c._filings.clear();self.assertEqual(company_contract(w,'AAPL',LATE,role=ROLE),r)
  with self.assertRaisesRegex(XBRLError,'issuer_scope'):w.admit_xbrl_collection('MSFT',collection())
 def test_failed_admission_is_atomic_and_memory_bound(self):
  w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection());before=company_contract(w,'AAPL',LATE,role=ROLE);bad=collection();bad._filings[next(iter(bad._filings))]['facts'][0]['value']='999'
  with self.assertRaises(XBRLError):w.admit_xbrl_collection('AAPL',bad)
  with patch('terminal.stocks.xbrl_product.MAX_BYTES',1),self.assertRaisesRegex(XBRLError,'memory_budget'):w.admit_xbrl_collection('AAPL',collection())
  with patch('terminal.stocks.xbrl_product.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):company_contract(w,'AAPL',LATE,role=ROLE)
  self.assertEqual(company_contract(w,'AAPL',LATE,role=ROLE),before)
 def test_identity_change_cannot_reuse_admitted_state(self):
  w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection())
  with patch.object(w,'resolve',return_value={'cik':'0000000001'}),self.assertRaisesRegex(XBRLError,'identity_changed'):company_contract(w,'AAPL',LATE,role=ROLE)
 def test_new_read_only_route_exists_without_constructing_an_application(self):
  tree=ast.parse(Path('terminal/server/app.py').read_text());f=next(n for n in ast.walk(tree)if isinstance(n,ast.AsyncFunctionDef)and n.name=='xbrl_statements_v2');s=ast.unparse(f);self.assertIn("'/api/v2/companies/{symbol}/xbrl-statements'",s);self.assertIn("methods=['GET']",s);self.assertIn('q.multi_items()',s);self.assertIn('analysis.run(partial(',s)
 def test_private_offline_export_is_the_same_versioned_product_contract(self):
  from scripts.inspect_xbrl_instances import inspect,main
  e=entry()
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);(root/'instance.xml').write_bytes(e['raw']);docs=[]
   for i,d in enumerate(e['documents']):
    path=f'taxonomy{i}.xml';(root/path).write_bytes(d['raw']);docs.append({'path':path,'uri':d['uri'],'sha256':d['sha256']})
   batch={'schema':'gig.sec.xbrl.input_dts_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','numeric_profile':None,'entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':'http://fasb.org/us-gaap/2024','instance_uri':e['instance_uri'],'documents':docs}]};(root/'batch.json').write_text(json.dumps(batch));summary,result=inspect(root/'batch.json',LATE,company_symbol='AAPL',statement_role=ROLE);self.assertEqual(result['schema'],'gig.backend.company_xbrl.v1');self.assertEqual(summary['status'],'AVAILABLE');out=root/'private.json'
   self.assertEqual(main(['--batch',str(root/'batch.json'),'--as-of',LATE,'--company-symbol','AAPL','--statement-role',ROLE,'--output',str(out)]),0);self.assertEqual(out.stat().st_mode&0o777,0o600);self.assertEqual(json.loads(out.read_text()),result)
 def test_legacy_company_contract_and_market_entitlements_stay_independent(self):
  w=StockWorkspace(environment={});before=copy.deepcopy(w.environment);w.admit_xbrl_collection('AAPL',collection());self.assertEqual(w.environment,before)
  from terminal.server.backend_contract import company_contract as legacy
  self.assertEqual(legacy(w,'AAPL')['schema'],'gig.backend.company.v2')

class XBRLRoute(unittest.IsolatedAsyncioTestCase):
 async def test_actual_route_body_is_read_only_bounded_and_forwards_explicit_query(self):
  # Execute only this endpoint's AST,not create_app or any ASGI application.
  from starlette.datastructures import QueryParams
  from types import SimpleNamespace
  from terminal.server.analysis import AnalysisGate
  tree=ast.parse(Path('terminal/server/app.py').read_text());f=next(n for n in ast.walk(tree)if isinstance(n,ast.AsyncFunctionDef)and n.name=='xbrl_statements_v2');f.decorator_list=[];module=ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[]));w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection());gate=AnalysisGate();scope={'stocks':w,'analysis':gate,'error':lambda code,message,status=400:{'code':code,'status':status}};exec(compile(module,'<actual-readonly-xbrl-route>','exec'),scope);endpoint=scope[f.name]
  def request(q):return SimpleNamespace(query_params=QueryParams(q),path_params={'symbol':'AAPL'})
  try:
   from urllib.parse import urlencode
   result=await endpoint(request(urlencode({'at':LATE,'role':ROLE})));self.assertEqual(result['statement_view']['status'],'AVAILABLE')
   for q in('at=x&at=y','role=x','at=x&fetch=1','at=not-a-clock'):
    r=await endpoint(request(q));self.assertEqual(r['status'],422)
   r=await endpoint(request(urlencode({'at':LATE,'role':ROLE,'form':'8-K'})));self.assertEqual(r['status'],422)
  finally:await gate.close()
