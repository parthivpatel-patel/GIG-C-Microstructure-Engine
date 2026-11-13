"""Deterministic private source revision and publication fault acceptance."""
import asyncio,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from .test_sec_filing_ingest import client,CIK,ACC,AGENT,resources,Wire,Clock
from .sec_filing_ingest import IngestError
from .sec_ingest_store import FilingCheckpointStore
from .service import StockWorkspace
class IngestStore(unittest.IsolatedAsyncioTestCase):
 async def payload(self):
  c,_,_=client();await c.ingest(ACC);return c,c.checkpoint()
 async def test_exclusive_store_and_restore_do_not_overwrite_or_connect(self):
  c,raw=await self.payload()
  with tempfile.TemporaryDirectory()as directory:
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True);sha=store.save(raw);self.assertEqual(sha,store.save(raw));self.assertEqual(store.load(sha),raw);r,_,_=client();r.enabled=False;r.restore(store.load(sha),sha);self.assertEqual(r.collection.page(),c.collection.page());self.assertEqual((Path(directory)/(sha+'.json')).stat().st_mode&0o777,0o600);self.assertNotIn(AGENT.encode(),raw)
 async def test_store_quota_and_corruption_cannot_publish_new_state(self):
  _,raw=await self.payload()
  with tempfile.TemporaryDirectory()as directory:
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True,max_bytes=1)
   with self.assertRaisesRegex(IngestError,'exhausted'):store.save(raw)
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True,max_revisions=1);sha=store.save(raw)
   with self.assertRaises(IngestError):store.save(raw+b' ')
   (Path(directory)/(sha+'.json')).write_bytes(b'corrupt')
   with self.assertRaisesRegex(IngestError,'integrity'):store.load(sha)
 async def test_interrupted_write_before_publication_leaves_no_revision(self):
  c,raw=await self.payload()
  with tempfile.TemporaryDirectory()as directory:
   def fail():raise OSError('authored disk full')
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True,before_publish=fail)
   with self.assertRaises(OSError):store.save(raw)
   self.assertEqual([p for p in Path(directory).iterdir()if p.suffix=='.json'],[])
 async def test_after_publication_uncertainty_requires_explicit_reopen(self):
  _,raw=await self.payload()
  with tempfile.TemporaryDirectory()as directory:
   def fail():raise OSError('authored interruption')
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True,after_publish=fail)
   with self.assertRaisesRegex(ValueError,'uncertain'):store.save(raw)
   sha=hashlib.sha256(raw).hexdigest();self.assertEqual(store.load(sha),raw)
 async def test_private_directory_and_symlink_policy(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);public=root/'public';public.mkdir(mode=0o755);public.chmod(0o755)
   with self.assertRaisesRegex(IngestError,'private'):FilingCheckpointStore(public,enabled=True,retention_approved=True)
   link=root/'link';link.symlink_to(root,target_is_directory=True)
   with self.assertRaisesRegex(IngestError,'symlink'):FilingCheckpointStore(link,enabled=True,retention_approved=True)
 async def test_allocation_failure_preserves_old_memory_state(self):
  from unittest.mock import patch
  c,raw=await self.payload()
  with patch.object(c,'_rebuild',side_effect=MemoryError):
   with self.assertRaises(MemoryError):await c.ingest(ACC,fresh=True)
  self.assertEqual(c.checkpoint(),raw)
 async def test_cross_process_restore_with_network_guard_and_disabled_transport(self):
  _,raw=await self.payload()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'image';path.write_bytes(raw);program="import socket,hashlib,pathlib,json;from terminal.stocks.sec_filing_ingest import FilingIngestor\ndef denied(*a,**k):raise AssertionError('NO_NETWORK')\nsocket.socket.connect=denied;socket.socket.bind=denied\nr=pathlib.Path(__import__('sys').argv[1]).read_bytes();c=FilingIngestor('0000320193');v=c.restore(r,hashlib.sha256(r).hexdigest());assert c.state=='PAUSED_RESTORED';assert not c.enabled;assert c.collection.page()['total']==1;print(json.dumps(v))"
   result=subprocess.run([sys.executable,'-c',program,str(path)],capture_output=True,text=True,timeout=15);self.assertEqual(result.returncode,0,result.stderr[-500:]);self.assertEqual(json.loads(result.stdout)['filings'],1)
 async def test_workspace_factory_preserves_shared_rate_gate_and_company_scope(self):
  clock=Clock();wire=Wire(resources(),clock)
  async def not_used(*_):raise AssertionError('NO_OLD_SOURCE_FETCH')
  env={'GIG_SEC_ENABLED':'1','GIG_SEC_POLICY_REVIEWED':'1','GIG_SEC_USER_AGENT':AGENT};workspace=StockWorkspace(environment=env,fetcher=not_used,clock=clock);workspace.last_request=0;coordinator=workspace.create_sec_filing_ingestor('AAPL',transport=wire,enabled=True,sleep=clock.sleep);self.assertIs(coordinator.lock,workspace.lock);await coordinator.ingest(ACC);workspace.install_sec_filing_result('AAPL')
  from .xbrl_product import company_contract
  from .test_xbrl_statements import ROLE,LATE
  result=company_contract(workspace,'AAPL',LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(result['statement_view']['status'],'AVAILABLE');self.assertEqual(result['source_ingestion']['state'],'ACCEPTED');self.assertGreaterEqual(wire.calls[0][1],1.01);self.assertEqual(result['data_origin'],'HISTORICAL_SYNTHETIC')
  with self.assertRaises(ValueError):workspace.create_sec_filing_ingestor('AAPL')
