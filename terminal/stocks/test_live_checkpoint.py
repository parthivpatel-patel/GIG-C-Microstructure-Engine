"""Private synthetic SQLite and fake coroutines only; no application or network."""
import asyncio,copy,json,sqlite3,tempfile,unittest
from unittest.mock import patch
from .observation_store import ObservationStore
from .test_final import client,ready,packet,quote

class Checkpoint(unittest.TestCase):
 def setup_client(self,directory):
  store=ObservationStore(directory);c=client();c.store=store;c.capture_id=c.source_session_id;ready(c)
  return c,store
 def test_atomic_frame_and_checkpoint_restart_restores_only_intent(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.generation=8;c.process(packet(quote()));saved=s.recover_control();self.assertEqual(saved['control']['accepted_receipt'],1)
   other=client();other.store=ObservationStore(d);other.capture_id=other.source_session_id
   result=other.restore_control();self.assertEqual(other.restore_control(),result);self.assertIsNone(other.task)
   self.assertEqual(other.symbols,('AAPL',));self.assertEqual(other.generation,8);self.assertNotEqual(c.source_session_id,other.source_session_id)
   self.assertEqual(other.history,[]);self.assertEqual(other.latest,{});self.assertEqual(other.receipts,0);self.assertEqual(other.phase,'DISCONNECTED');self.assertEqual(other.state,'RECOVERY_REQUIRED')
   self.assertFalse(result['hot_l3_restored']);self.assertTrue(result['requires_fresh_observation'])
 def test_failed_commit_keeps_source_and_control_at_identical_previous_prefix(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.process(packet(quote()));before=s.recover_control();semantic=copy.deepcopy(c.view())
   s.before_commit=lambda:(_ for _ in ()).throw(OSError('authored disk-full'))
   q=quote();q['bs']=7
   with self.assertRaisesRegex(ValueError,'storage_rejected'):c.process(packet(q))
   self.assertEqual(s.recover_control(),before);self.assertEqual(len(s.recover()),1);self.assertEqual(c.view(),semantic)
 def test_legacy_ledger_without_checkpoint_still_recovers(self):
  with tempfile.TemporaryDirectory()as d:
   c=client();ready(c);events=c.process(packet(quote()));s=ObservationStore(d);s.append(c.source_session_id,events)
   self.assertIsNone(s.recover_control());self.assertEqual(len(s.recover()),1)
 def test_uncoordinated_legacy_append_invalidates_checkpoint_instead_of_stale_restore(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.process(packet(quote()));q=quote();q['bs']=6;c.store=None;events=c.process(packet(q));s.append(c.source_session_id,events)
   self.assertIsNone(s.recover_control());self.assertEqual(len(s.recover()),2)
 def test_digest_corruption_oversize_and_contradictory_tail_reject_recovery(self):
  for mode in ('digest','oversize','tail'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as d:
    c,s=self.setup_client(d);c.process(packet(quote()))
    with sqlite3.connect(s.path)as db:
     if mode=='digest':db.execute("UPDATE live_checkpoint SET digest=?",('0'*64,))
     elif mode=='oversize':db.execute("UPDATE live_checkpoint SET payload=?",(b'x'*4097,))
     else:
      from hashlib import sha256
      raw=db.execute('SELECT payload FROM live_checkpoint').fetchone()[0];v=json.loads(raw);v['observation_tail']='0'*64;raw=json.dumps(v).encode();db.execute('UPDATE live_checkpoint SET payload=?,digest=?',(raw,sha256(raw).hexdigest()))
    with self.assertRaisesRegex(ValueError,'live_checkpoint_'):s.recover_control()
 def test_invalid_scope_counters_and_extra_authority_never_publish(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);before=s.recover_control()
   for values in ({'generation':True},{'generation':2**53},{'symbols':['AAPL','AAPL']},{'channels':['depth']},{'retry_budget':0},{'active':'yes'},{'secret':'forbidden'}):
    with self.subTest(values=values),self.assertRaises(ValueError):s.save_control({**c.control(),**values})
    self.assertEqual(s.recover_control(),before)
 def test_observation_corruption_also_blocks_valid_control(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.process(packet(quote()))
   with sqlite3.connect(s.path)as db:db.execute('UPDATE records SET payload=?',(b'bad',))
   with self.assertRaises(ValueError):s.recover_control()
 def test_revoked_permissions_and_existing_observations_cannot_be_overwritten(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.process(packet(quote()))
   with self.assertRaisesRegex(ValueError,'idle_worker'):c.restore_control()
   other=client();other.store=s;other.workspace.environment={};before=other.generation
   with self.assertRaises(ValueError):other.restore_control()
   self.assertEqual(other.generation,before);self.assertIsNone(other.task)
 def test_retention_pruning_does_not_mark_recovered_observations_live(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=self.setup_client(d);c.process(packet(quote()));s.clock=lambda:10**12;s.prune()
   self.assertEqual(s.recover(),[]);self.assertEqual(s.recover_control()['control']['accepted_receipt'],1)

class Lifecycle(unittest.IsolatedAsyncioTestCase):
 async def test_recovered_generation_advances_before_fake_transport_and_old_ack_is_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=Checkpoint().setup_client(d);c.generation=12;c.persist_control();other=client();other.store=s;other.capture_id=other.source_session_id;other.restore_control();seen=[]
   class Fake:
    async def __aenter__(self):seen.append(other.generation);return self
    async def __aexit__(self,*args):pass
    async def recv(self):return packet({'T':'subscription','quotes':['AAPL'],'trades':['AAPL']})
   other.connector=lambda *args,**kwargs:Fake();await other.run()
   self.assertEqual(seen,[13]);self.assertEqual(other.state,'FAILED');self.assertEqual(other.reason,'subscription_mismatch');self.assertEqual(other.receipts,0)
 async def test_checkpoint_failure_precedes_any_transport_open(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=Checkpoint().setup_client(d);called=[];s.before_commit=lambda:(_ for _ in ()).throw(OSError('authored storage exhaustion'))
   c.connector=lambda *a,**k:called.append(True)
   await c.run();self.assertEqual(called,[]);self.assertEqual(c.state,'FAILED');self.assertEqual(c.reason,'recovery_checkpoint_rejected')
 async def test_pending_desired_subscription_survives_interrupt_without_restoring_pending_ack(self):
  with tempfile.TemporaryDirectory()as d:
   c,s=Checkpoint().setup_client(d);c.pending={'symbols':('NVDA',),'channels':('quotes','trades'),'step':'UNSUBSCRIBE_SENT','started':100};c.persist_control()
   other=client();other.store=s;other.restore_control();self.assertEqual(other.symbols,('NVDA',));self.assertIsNone(other.pending);self.assertEqual(other.phase,'DISCONNECTED')
