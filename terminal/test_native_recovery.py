"""Real native C++ state with authored events and private SQLite; no app or socket."""
import copy,hashlib,json,os,sqlite3,subprocess,sys,tempfile,unittest
from unittest.mock import patch
import gig_microstructure as gig
from terminal.native_recovery import NativeSourceRecovery,RecoveryError,authored_record
from terminal.server.fixtures import rules,replay_config,event,EVENTS,scope,known

LIMITS={'max_orders':'128','max_levels':'32','max_snapshot_depth':'20'}
SOURCE={'identity':'authored-native-v1','capture_session':'a'*32,'generation':0,'first_capture':0,'initialization':'AUTHORED_COMPLETE_EMPTY','origin':'HISTORICAL_SYNTHETIC'}
def owner(directory,**kwargs):return NativeSourceRecovery(directory,rules=rules(),config=replay_config(),limits=LIMITS,source=SOURCE,implementation_sha256='b'*64,**kwargs)
def record(i,doc=None,**kw):return authored_record(SOURCE,i,EVENTS[i]if doc is None else doc,**kw)
def snapshot_doc():
 s={**scope(),'epoch':'1'};doc=event(100,6,{'kind':'0','coverage':'0','depth':'0','orders':[{'order':{'order_id':'91','side':'0','price_ticks':'9900','quantity':'13'},'priority_index':'3'},{'order':{'order_id':'92','side':'1','price_ticks':'9902','quantity':'17'},'priority_index':'1'}],'levels':[],'boundaries':[{'scope':s,'sequence':'100','last_subevent':'0','subevent_count':'1'}]});doc['data']['metadata']['scope']=known(s);return doc

class NativeRecovery(unittest.TestCase):
 def test_hot_roundtrip_and_exact_suffix_match_direct_native(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);reference=gig.Replay(rules(),replay_config(),limits=LIMITS,resource_budget_bytes='33554432')
   for i in range(25):self.assertTrue(c.apply(record(i))['committed']);reference.apply(EVENTS[i])
   expected=c.accepted_canonical();self.assertEqual(expected,reference.canonical())
   with patch.object(gig.Replay,'apply',side_effect=AssertionError('historical events must not be reapplied')):restored=owner(d)
   self.assertEqual(restored.accepted_canonical(),expected);self.assertEqual(restored.snapshot(),c.snapshot())
   self.assertTrue(restored.apply(record(25))['committed']);reference.apply(EVENTS[25]);self.assertEqual(restored.accepted_canonical(),reference.canonical())
 def test_exact_duplicate_and_conflicting_duplicate_have_distinct_fail_closed_results(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);r=record(0);c.apply(r);before=c.accepted_canonical();self.assertEqual(c.apply(copy.deepcopy(r))['status'],'DUPLICATE_SUPPRESSED');self.assertEqual(c.accepted_canonical(),before)
   changed=copy.deepcopy(EVENTS[0]);changed['data']['payload']['value']['quantity']='99'
   self.assertEqual(c.apply(record(0,changed))['status'],'RECOVERY_REQUIRED');self.assertEqual(c.accepted_canonical(),before)
   with self.assertRaises(RecoveryError):c.snapshot()
   reopened=owner(d);self.assertTrue(reopened.status()['needs_recovery']);self.assertEqual(reopened.status()['diagnostic'],'duplicate_conflict')
 def test_source_gap_is_durable_and_cannot_be_hidden_by_native_checkpoint(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.apply(record(0));before=c.accepted_canonical();self.assertEqual(c.apply(record(2))['status'],'RECOVERY_REQUIRED');new=owner(d)
   self.assertTrue(new.status()['needs_recovery']);self.assertEqual(new.accepted_canonical(),before)
   with self.assertRaisesRegex(RecoveryError,'resynchronization'):new.apply(record(1))
 def test_native_sequence_gap_is_preserved_as_blocked_diagnostic(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.apply(record(0));self.assertEqual(c.apply(record(1,EVENTS[2]))['status'],'RECOVERY_REQUIRED');restored=owner(d)
   self.assertEqual(restored.status()['diagnostic'],'native:sequence_gap');self.assertTrue(restored.status()['needs_recovery'])
 def test_complete_snapshot_resynchronizes_generation_and_old_events_stay_stale(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.apply(record(0));c.apply(record(2));snap=record(100,snapshot_doc(),generation=1,capture_session='c'*32)
   self.assertEqual(c.resynchronize(snap)['status'],'COMMITTED');self.assertFalse(c.status()['needs_recovery']);self.assertEqual(c.resynchronize(snap)['status'],'DUPLICATE_SUPPRESSED')
   restored=owner(d);self.assertEqual(restored.snapshot(),c.snapshot());self.assertEqual(restored.apply(record(1))['status'],'STALE_GENERATION_REJECTED')
   continuation=event(101,0,{'order_id':'93','side':'0','price_ticks':'9899','quantity':'2'});continuation['data']['metadata']['scope']['value']['epoch']='1'
   self.assertTrue(restored.apply(record(101,continuation,generation=1,capture_session='c'*32))['committed'])
 def test_partial_or_aggregate_snapshot_cannot_clear_gap(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.apply(record(2));doc=snapshot_doc();doc['data']['payload']['value']['coverage']='1'
   before=c.accepted_canonical();result=c.resynchronize(record(100,doc,generation=1))
   self.assertEqual(result['status'],'RECOVERY_REQUIRED');self.assertFalse(result['committed']);self.assertEqual(c.accepted_canonical(),before);self.assertTrue(owner(d).status()['needs_recovery'])
 def test_disk_failure_and_memory_failure_leave_both_accepted_prefixes_unchanged(self):
  for fault in (OSError,MemoryError):
   with self.subTest(fault=fault),tempfile.TemporaryDirectory()as d:
    c=owner(d);c.apply(record(0));before=c.accepted_canonical();digest=c.status()['checkpoint_sha256'];c.before_commit=lambda:(_ for _ in ()).throw(fault('authored fault'))
    with self.assertRaises(fault):c.apply(record(1))
    self.assertEqual(c.accepted_canonical(),before);self.assertEqual(owner(d).status()['checkpoint_sha256'],digest)
 def test_commit_publication_uncertainty_blocks_owner_until_reopen_and_duplicate_suppression(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.after_commit=lambda:(_ for _ in ()).throw(OSError('authored after commit'))
   with self.assertRaises(OSError):c.apply(record(0))
   self.assertEqual(c.status()['state'],'PUBLICATION_UNCERTAIN')
   with self.assertRaises(RecoveryError):c.snapshot()
   restored=owner(d);self.assertEqual(restored.status()['capture_index'],0);self.assertEqual(restored.apply(record(0))['status'],'DUPLICATE_SUPPRESSED')
 def test_abrupt_process_exit_before_and_after_commit_selects_one_coherent_prefix(self):
  for phase in ('before_commit','after_commit'):
   with self.subTest(phase=phase),tempfile.TemporaryDirectory()as d:
    owner(d);code='from terminal.test_native_recovery import owner,record;import os,sys;c=owner(sys.argv[1]);setattr(c,sys.argv[2],lambda:os._exit(77));c.apply(record(0))'
    result=subprocess.run([sys.executable,'-c',code,d,phase],capture_output=True,timeout=20);self.assertEqual(result.returncode,77)
    c=owner(d);self.assertEqual(c.status()['capture_index'],None if phase=='before_commit'else 0)
    self.assertEqual(c.apply(record(0))['status'],'COMMITTED'if phase=='before_commit'else'DUPLICATE_SUPPRESSED')
 def test_stale_writers_cannot_overwrite_a_newer_joint_checkpoint(self):
  with tempfile.TemporaryDirectory()as d:
   first=owner(d);stale=owner(d);first.apply(record(0))
   with self.assertRaisesRegex(RecoveryError,'stale_writer'):stale.apply(record(0))
   self.assertEqual(owner(d).status()['capture_index'],0);self.assertTrue(stale.status()['needs_recovery'])
   with self.assertRaises(RecoveryError):stale.snapshot()
 def test_corruption_payload_budget_and_wrong_expected_contract_are_rejected(self):
  for corruption in ('digest','oversize','contract'):
   with self.subTest(corruption=corruption),tempfile.TemporaryDirectory()as d:
    c=owner(d)
    if corruption=='contract':
     with self.assertRaisesRegex(RecoveryError,'source_contract'):NativeSourceRecovery(d,rules=rules(),config=replay_config(),limits=LIMITS,source=SOURCE,implementation_sha256='f'*64)
    else:
     with sqlite3.connect(c.path)as db:
      if corruption=='digest':db.execute('UPDATE checkpoint SET digest=?',('0'*64,))
      else:db.execute('UPDATE checkpoint SET payload=?',(b'x'*(8*1024*1024+1),))
     with self.assertRaises(RecoveryError):owner(d)
 def test_observed_origin_unknown_initial_state_and_bad_source_hash_cannot_be_admitted(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);r=record(0);r['source_sha256']='0'*64
   with self.assertRaisesRegex(RecoveryError,'integrity'):c.apply(r)
   doc=copy.deepcopy(EVENTS[0]);doc['data']['metadata']['provenance']['origin']['value']='1'
   with self.assertRaises((RecoveryError,gig.EngineError)):c.apply(record(0,doc))
   self.assertIsNone(c.status()['capture_index'])
  with tempfile.TemporaryDirectory()as d:
   source={**SOURCE,'initialization':'UNKNOWN'}
   with self.assertRaisesRegex(RecoveryError,'initialization'):NativeSourceRecovery(d,rules=rules(),config=replay_config(),limits=LIMITS,source=source,implementation_sha256='b'*64)
 def test_dedup_window_is_bounded_and_unknown_old_receipts_do_not_silently_apply(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d)
   for i in range(34):c.apply(record(i))
   self.assertEqual(c.apply(record(0))['status'],'RECOVERY_REQUIRED');self.assertEqual(owner(d).status()['capture_index'],33)
 def test_canonical_corruption_cannot_pass_even_with_a_recomputed_outer_digest(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d);c.apply(record(0))
   with sqlite3.connect(c.path)as db:
    raw=db.execute('SELECT payload FROM checkpoint').fetchone()[0];v=json.loads(raw);v['canonical']+='x';raw=json.dumps(v).encode();db.execute('UPDATE checkpoint SET payload=?,digest=?',(raw,hashlib.sha256(raw).hexdigest()))
   with self.assertRaises(gig.EngineError):owner(d)

 def test_large_bounded_native_prefix_can_be_reopened_without_generic_evidence_budget_failure(self):
  with tempfile.TemporaryDirectory()as d:
   c=owner(d)
   for i in range(len(EVENTS)):c.apply(record(i))
   restored=owner(d);self.assertEqual(restored.status()['capture_index'],len(EVENTS)-1);self.assertEqual(restored.accepted_canonical(),c.accepted_canonical())
