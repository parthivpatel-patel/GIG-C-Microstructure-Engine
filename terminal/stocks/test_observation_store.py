import copy,tempfile,unittest,sqlite3
from .observation_store import ObservationStore
from .test_final import client,ready,packet,quote
class Store(unittest.TestCase):
 def events(self,n=1):
  c=client();ready(c);out=[]
  for i in range(n):q=quote();q['bs']=i+1;out+=c.process(packet(q))
  return out
 def test_interrupted_bootstrap_is_recoverable_in_a_new_process(self):
  import subprocess,sys
  from pathlib import Path
  with tempfile.TemporaryDirectory() as d:
   code="""
import os,socket,sqlite3,sys
from unittest.mock import patch
from terminal.stocks.observation_store import ObservationStore
def forbidden(*args,**kwargs):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=socket.socket.connect=socket.socket.connect_ex=forbidden
from terminal.server import app
assert app._application is None
app.create_app=forbidden
class Interrupted(sqlite3.Connection):
 def execute(self,sql,*args):
  result=super().execute(sql,*args)
  if sql.startswith('CREATE TABLE records'):os._exit(77)
  return result
connect=sqlite3.connect
with patch('sqlite3.connect',side_effect=lambda *a,**kw:connect(*a,**kw,factory=Interrupted)):
 ObservationStore(sys.argv[1])
"""
   result=subprocess.run([sys.executable,'-c',code,d],timeout=15,capture_output=True)
   self.assertEqual(result.returncode,77,result.stderr)
   self.assertTrue((Path(d)/'observations.sqlite3').is_file())
   store=ObservationStore(d)
   store.append('a'*32,self.events())
   self.assertEqual(len(ObservationStore(d).recover()),1)

 def test_concurrent_bootstrap_uses_the_identity_under_the_database_lock(self):
  from concurrent.futures import ThreadPoolExecutor
  from contextlib import contextmanager
  from threading import Barrier
  with tempfile.TemporaryDirectory() as d:
   barrier=Barrier(2,timeout=5)
   class Simultaneous(ObservationStore):
    @contextmanager
    def _connect(self):
     if not hasattr(self,'cached') and not getattr(self,'opening',False):
      self.opening=True
      barrier.wait()
     with super()._connect() as db:yield db
   with ThreadPoolExecutor(max_workers=2) as pool:
    first,second=[future.result(timeout=10) for future in [pool.submit(Simultaneous,d) for _ in range(2)]]
   first.append('a'*32,self.events())
   self.assertEqual(len(second.recover()),1)

 def test_restart_integrity_and_historical_only(self):
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);s.append('a'*32,self.events(3));r=ObservationStore(d).recover();self.assertEqual([v['event']['receipt_index'] for v in r],[1,2,3]);self.assertTrue(all(v['classification']=='RETAINED_HISTORICAL_NOT_CURRENT' for v in r));self.assertNotIn('received_monotonic',r[0]['event'])
 def test_observed_permission_and_atomic_failure(self):
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);e=self.events();e[0]['origin']='OBSERVED_OFFICIAL_RESPONSE'
   with self.assertRaises(ValueError):s.append('a'*32,e)
   s.before_commit=lambda:(_ for _ in ()).throw(OSError('authored disk fault'))
   with self.assertRaises(OSError):s.append('a'*32,self.events())
   self.assertEqual(ObservationStore(d).summary()['records'],0)
 def test_corruption_duplicates_and_expiry(self):
  with tempfile.TemporaryDirectory() as d:
   now=[100.];s=ObservationStore(d,clock=lambda:now[0],retention_seconds=10);s.append('a'*32,self.events());
   with self.assertRaises(ValueError):s.append('a'*32,self.events())
   now[0]=111.;s.prune();self.assertEqual(s.recover(),[]);e=self.events(2)[1:];s.append('a'*32,e)
   with sqlite3.connect(s.path) as db:db.execute("UPDATE records SET payload=?",(b'corrupt',))
   with self.assertRaises(ValueError):s.recover()
 def test_tail_truncation_and_retention_cannot_be_extended_on_restart(self):
  with tempfile.TemporaryDirectory() as d:
   now=[100.];s=ObservationStore(d,clock=lambda:now[0],retention_seconds=10);s.append('a'*32,self.events(2))
   with sqlite3.connect(s.path) as db:db.execute('DELETE FROM records WHERE receipt=2')
   with self.assertRaises(ValueError):s.recover()
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d,clock=lambda:100.,retention_seconds=10);s.append('a'*32,self.events());self.assertEqual(ObservationStore(d,clock=lambda:110.,retention_seconds=86400).recover(),[])
 def test_expiration_cannot_hide_a_corrupted_retained_record(self):
  with tempfile.TemporaryDirectory() as d:
   now=[100.]
   s=ObservationStore(d,clock=lambda:now[0],retention_seconds=10)
   s.append('a'*32,self.events(2))
   with sqlite3.connect(s.path) as db:db.execute('UPDATE records SET payload=? WHERE receipt=1',(b'corrupt',))
   now[0]=111.
   with self.assertRaisesRegex(ValueError,'observation_corrupt_chain'):s.prune()
   with self.assertRaisesRegex(ValueError,'observation_corrupt_chain'):s.append('a'*32,self.events(3)[2:])
   self.assertEqual(s.summary()['records'],2)
   self.assertEqual(s.cached['records'],2)

 def test_truncated_ledger_cannot_be_extended_or_pruned(self):
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);rows=self.events(3);s.append('a'*32,rows[:2])
   with sqlite3.connect(s.path) as db:db.execute('DELETE FROM records WHERE receipt=2')
   with self.assertRaisesRegex(ValueError,'observation_truncated_tail'):s.append('a'*32,rows[2:])
   with self.assertRaisesRegex(ValueError,'observation_truncated_tail'):s.prune()
   self.assertEqual(s.summary()['records'],1)
   self.assertEqual(s.cached['records'],2)

 def test_source_rejection_cannot_publish_partial_accepted_state(self):
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);c=client();c.store=s;c.capture_id='a'*32;ready(c);before=copy.deepcopy(c.view());s.before_commit=lambda:(_ for _ in ()).throw(OSError('authored disk failure'))
   with self.assertRaises(ValueError):c.process(packet(quote()))
   self.assertEqual(c.view(),before);self.assertEqual(s.recover(),[])
 def test_abrupt_process_exit_rolls_back_uncommitted_frame(self):
  import subprocess,sys
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);s.append('a'*32,self.events())
   code="from terminal.stocks.observation_store import ObservationStore;from terminal.stocks.test_observation_store import Store;import os,sys;s=ObservationStore(sys.argv[1],before_commit=lambda:os._exit(77));s.append('b'*32,Store().events())"
   result=subprocess.run([sys.executable,'-c',code,d],timeout=15,capture_output=True);self.assertEqual(result.returncode,77);self.assertEqual(len(ObservationStore(d).recover()),1)
 def test_record_and_byte_caps_keep_verified_retained_suffix(self):
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);events=self.events(10050)
   for i in range(0,len(events),128):s.append('a'*32,events[i:i+128])
   self.assertLessEqual(s.cached['records'],10000);self.assertLessEqual(s.cached['logical_payload_bytes'],16*1024*1024);rows=s.recover();self.assertEqual(rows[-1]['event']['receipt_index'],10050);self.assertGreater(rows[0]['event']['receipt_index'],1)
 def test_clock_rollback_cannot_hide_expired_later_records_from_physical_pruning(self):
  with tempfile.TemporaryDirectory() as d:
   now=[100.];s=ObservationStore(d,clock=lambda:now[0],retention_seconds=10);events=self.events(2);s.append('a'*32,events[:1]);now[0]=90.;s.append('a'*32,events[1:]);now[0]=101.;s.prune();self.assertEqual(s.cached['records'],0);self.assertEqual(s.recover(),[])
 def test_cached_publication_remains_inside_writer_lock(self):
  import threading
  class TrackingLock:
   def __init__(self):self.raw=threading.RLock();self.depth=threading.local()
   def __enter__(self):self.raw.acquire();self.depth.n=getattr(self.depth,'n',0)+1;return self
   def __exit__(self,*args):self.depth.n-=1;self.raw.release()
   def owned(self):return getattr(self.depth,'n',0)>0
  class Guarded(ObservationStore):
   def __setattr__(self,key,value):
    if key=='cached' and self.__dict__.get('guard',False) and not self.lock.owned():raise AssertionError('summary publication outside writer lock permits stale overwrite')
    super().__setattr__(key,value)
  for operation in ('append','prune'):
   with self.subTest(operation=operation),tempfile.TemporaryDirectory() as d:
    s=Guarded(d);s.lock=TrackingLock();s.guard=True
    if operation=='append':s.append('a'*32,self.events())
    else:s.prune()
 def test_concurrent_prune_and_append_leave_consistent_durable_summary(self):
  from concurrent.futures import ThreadPoolExecutor
  with tempfile.TemporaryDirectory() as d:
   s=ObservationStore(d);events=self.events(200)
   def writer():
    for e in events:s.append('a'*32,[e])
   def pruner():
    for _ in range(100):s.prune()
   with ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(writer),pool.submit(pruner)]
    for f in futures:f.result(timeout=15)
   self.assertEqual(s.cached,s.summary());self.assertEqual(len(s.recover()),200)
