"""Versioned raw joint-session recording through actual native/product consumers.

Authored deterministic source only: no app factory, listener or provider request.
"""
import ast,asyncio,copy,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .kraken_joint_recording import (PROFILE,SCHEMA,JointL2Writer,JointRecordedSession,
 save_joint_fixture,authored_joint_frames,_session,validate_log,replay_joint,_sha)
from .l2_recording import L2Writer,load_l2,replay_l2
from .l2_playback import open_recorded_session,RecordedSession,save_fixture,discover,delete_session,prune_expired
from .recording import canonical
from .l2_capture import Capture
from .providers.kraken import ProviderError
from .providers.kraken_coordinator import PROFILE as SESSION_PROFILE
from .providers.supervisor import FeedSupervisor
from .providers.test_supervisor import ENV
from .server.engine import NativeSession


class JointRecording(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def saved(self):
  m=save_joint_fixture(self.root);m,rows=load_l2(self.root,m['identity']);return m,rows
 def rewrite(self,m,rows):
  body=b''.join(canonical(row)+b'\n'for row in rows);m['sha256']=hashlib.sha256(body).hexdigest();m['bytes']=len(body);m['records']=len(rows);m['manifest_sha256']=_sha({k:v for k,v in m.items()if k!='manifest_sha256'});target=self.root/m['identity'];(target/'events.jsonl').write_bytes(body);(target/'manifest.json').write_bytes(canonical(m));return body
 def test_versioned_manifest_owns_session_intent_and_original_raw_receipts(self):
  m,rows=self.saved();self.assertEqual(m['schema'],SCHEMA);self.assertEqual(m['profile'],PROFILE);self.assertEqual(m['records'],8);self.assertEqual(m['joint_session']['local_generation'],'1');self.assertEqual([r['req_id']for r in m['joint_session']['subscriptions']],[101,201]);self.assertFalse(m['market_session_complete']);self.assertFalse(m['independent_source_authentication']);self.assertIsNone(m['source_sequence'])
  for i,row in enumerate(rows):self.assertEqual(row['ordinal'],i);self.assertEqual(row['normalized']['source_sha256'],hashlib.sha256(row['raw'].encode()).hexdigest());self.assertEqual(row['normalized']['receive_monotonic_ns'],row['receive_monotonic_ns'])
 def test_actual_version_aware_consumer_and_native_prefix_metrics(self):
  m,rows=self.saved();session=open_recorded_session(self.root,m['identity']);self.assertIsInstance(session,JointRecordedSession);self.assertEqual(session.event_count,8);self.assertEqual(session.view(0,False,1)['book'],{'bids':[],'asks':[]});self.assertFalse(session.view(3,False,1)['eligible']);v=session.view(8,False,1);self.assertEqual(v['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(v['book']['bids'][0]['price_ticks'],'9900000000');self.assertEqual(v['metrics']['spread'],{'numerator':'300000000','denominator':'1'});self.assertFalse(v['feed']['sequence_complete']);self.assertEqual(v['provenance']['profile'],PROFILE)
 def test_native_session_steps_seeks_and_stops_at_real_record_boundary(self):
  m,_=self.saved();native=NativeSession();native.recorded_session=open_recorded_session(self.root,m['identity']);native.restart();native.playing=True
  while native.step():pass
  v=native.state();self.assertEqual(native.position,8);self.assertFalse(native.playing);self.assertEqual(v['book']['bids'][0]['price_ticks'],'9900000000');self.assertEqual(v['dataset'],'recorded-l2');self.assertTrue(v['diagnostics']['native_status']['recorded_native_prefix_cache']);native.restart();self.assertEqual(native.position,0);self.assertEqual(native.state()['book']['bids'],[])
 def test_deterministic_fresh_native_replay_matches_cached_prefixes(self):
  m,rows=self.saved();session=open_recorded_session(self.root,m['identity'])
  for pos in range(9):
   replay=replay_l2(m,rows,pos);cached=session.view(pos,False,1);self.assertEqual(replay['native']['bids']if replay['native']else[],cached['book']['bids']);self.assertEqual(replay['eligible'],cached['eligible']);self.assertEqual(replay['source_sha256'],m['sha256'])
 def test_source_trade_status_and_book_receipts_stay_separate(self):
  m,_=self.saved();view=open_recorded_session(self.root,m['identity']).view(8,False,1);sources=view['provenance']['joint_source_receipts'];self.assertTrue({'status','book','trade','book_subscription','trade_subscription'}<=sources.keys());self.assertNotEqual(sources['trade']['source_sha256'],sources['book']['source_sha256']);self.assertEqual(view['flow']['trades'][0]['trade_id'],'7');self.assertEqual(view['flow']['classification'],'provider_reported_side_not_inferred_cancellations')
 def test_cached_views_are_detached_and_replay_position_is_exact_integer(self):
  m,rows=self.saved();session=open_recorded_session(self.root,m['identity']);v=session.view(8,False,1);v['book']['bids'][0]['quantity']='bad';v['flow']['trades'][0]['side']='bad';v['provenance']['joint_source_receipts']['book']['source_sha256']='bad';self.assertEqual(session.view(8,False,1)['book']['bids'][0]['quantity'],'100000000');self.assertEqual(session.view(8,False,1)['flow']['trades'][0]['side'],'buy')
  for pos in(True,-1,9,1.0):
   with self.subTest(pos=pos),self.assertRaisesRegex(ValueError,'replay_position'):replay_joint(m,rows,pos)
 def test_complete_capture_does_not_claim_complete_market_initialization(self):
  m,_=self.saved();v=open_recorded_session(self.root,m['identity']).view(8,False,1);self.assertFalse(v['provenance']['complete_initialization']);self.assertEqual(v['provenance']['initialization_scope'],'subscribed aggregate L2 only');self.assertFalse(v['feed']['market_session_complete']);self.assertFalse(v['feed']['real_time'])
 def test_resigned_normalized_receipt_changes_are_rederived_from_raw_bytes(self):
  m,rows=self.saved();rows[3]['normalized']['book_eligible']=False;self.rewrite(m,rows)
  with self.assertRaisesRegex(ValueError,'normalization_mismatch'):open_recorded_session(self.root,m['identity'])
 def test_modified_original_hash_or_missing_member_reject(self):
  m,_=self.saved();path=self.root/m['identity']/'events.jsonl';body=path.read_bytes();path.write_bytes(body+b' ')
  with self.assertRaisesRegex(ValueError,'recording_digest'):open_recorded_session(self.root,m['identity'])
  path.unlink()
  with self.assertRaises(ValueError):open_recorded_session(self.root,m['identity'])
 def test_resigned_changed_source_bytes_still_cannot_authorize_stale_receipt(self):
  m,rows=self.saved();rows[3]['raw']=rows[3]['raw'].replace('100.0','99.0');self.assertNotEqual(rows[3]['normalized']['source_sha256'],hashlib.sha256(rows[3]['raw'].encode()).hexdigest());self.rewrite(m,rows)
  with self.assertRaises(ValueError):open_recorded_session(self.root,m['identity'])
 def test_resigned_ordinal_clock_and_count_corruption_fail_closed(self):
  m,rows=self.saved()
  for change in('ordinal','clock','count'):
   mm,rr=copy.deepcopy(m),copy.deepcopy(rows)
   if change=='ordinal':rr[2]['ordinal']=7
   elif change=='clock':rr[2]['receive_monotonic_ns']='0'
   else:rr.pop(0)
   self.rewrite(mm,rr)
   with self.subTest(change=change),self.assertRaises(ValueError):open_recorded_session(self.root,m['identity'])
 def test_resigned_missing_ack_status_and_snapshot_cannot_publish_prefix(self):
  m,rows=self.saved()
  for index in(0,1,2,3):
   mm,rr=copy.deepcopy(m),copy.deepcopy(rows);rr.pop(index)
   for i,r in enumerate(rr):r['ordinal']=i
   self.rewrite(mm,rr)
   with self.subTest(index=index),self.assertRaises(ValueError):open_recorded_session(self.root,m['identity'])
 def test_duplicate_keys_fractional_tokens_and_negative_zero_reject(self):
  m,rows=self.saved();good=b''.join(canonical(r)+b'\n'for r in rows)
  for bad in(good.replace(b'"ordinal":0',b'"ordinal":0,"ordinal":0',1),good.replace(b'"ordinal":0',b'"ordinal":0.00000000000000000001',1),good.replace(b'"ordinal":0',b'"ordinal":-0',1)):
   mm=copy.deepcopy(m);mm['sha256']=hashlib.sha256(bad).hexdigest();mm['bytes']=len(bad);mm['manifest_sha256']=_sha({k:v for k,v in mm.items()if k!='manifest_sha256'})
   with self.subTest(body=bad[:40]),self.assertRaises(ValueError):validate_log(m['identity'],mm,bad)
 def test_fractional_manifest_token_is_validated_before_number_coercion(self):
  m,_=self.saved();path=self.root/m['identity']/'manifest.json';raw=path.read_bytes();self.assertIn(b'"records":8',raw);path.write_bytes(raw.replace(b'"records":8',b'"records":8.00000000000000000001'))
  with self.assertRaises(ValueError):open_recorded_session(self.root,m['identity'])
 def test_truncated_newline_rejects_even_if_digest_rewritten(self):
  m,rows=self.saved();body=b''.join(canonical(r)+b'\n'for r in rows)[:-1];m['bytes']=len(body);m['sha256']=hashlib.sha256(body).hexdigest();m['manifest_sha256']=_sha({k:v for k,v in m.items()if k!='manifest_sha256'})
  with self.assertRaisesRegex(ValueError,'truncated'):validate_log(m['identity'],m,body)
 def test_session_manifest_tampering_and_false_completeness_reject(self):
  m,rows=self.saved();body=b''.join(canonical(r)+b'\n'for r in rows)
  for change in('depth','generation','request','profile','sequence','complete','unknown'):
   mm=copy.deepcopy(m)
   if change=='depth':mm['joint_session']['depth']=25
   elif change=='generation':mm['joint_session']['local_generation']='2'
   elif change=='request':mm['joint_session']['subscriptions'][0]['req_id']=102
   elif change=='profile':mm['profile']='provisional_kraken_v2'
   elif change=='sequence':mm['source_sequence']='1'
   elif change=='complete':mm['market_session_complete']=True
   else:mm['unknown']=True
   mm['manifest_sha256']=_sha({k:v for k,v in mm.items()if k!='manifest_sha256'})
   with self.subTest(change=change),self.assertRaises(ValueError):validate_log(m['identity'],mm,body)
 def test_joint_data_is_never_admitted_by_legacy_recorded_session(self):
  m,_=self.saved()
  with self.assertRaisesRegex(ValueError,'joint_consumer_required'):RecordedSession(self.root,m['identity'])
  save_fixture(self.root);legacy=open_recorded_session(self.root,'authored-l2-v2');self.assertIsInstance(legacy,RecordedSession)
 def test_catalog_profile_delete_and_symlink_refusal(self):
  m,_=self.saved();catalog=discover(self.root);self.assertEqual(catalog['sessions'][0]['recording_profile'],PROFILE);self.assertEqual(catalog['sessions'][0]['origin'],'HISTORICAL_SYNTHETIC');path=self.root/m['identity']/'events.jsonl';real=path.read_bytes();path.unlink();other=self.root/'outside';other.write_bytes(real);path.symlink_to(other)
  with self.assertRaisesRegex(ValueError,'recording_path'):open_recorded_session(self.root,m['identity'])
  path.unlink();path.write_bytes(real);self.assertTrue(delete_session(self.root,m['identity']))
 def test_observed_grant_is_checked_before_any_payload_read(self):
  m,_=self.saved();path=self.root/m['identity']/'manifest.json';m['origin']='LIVE_OBSERVED';path.write_bytes(canonical(m));(path.parent/'events.jsonl').unlink()
  with self.assertRaisesRegex(ValueError,'observed_processing_permission'):open_recorded_session(self.root,m['identity'])
 def test_observed_writer_requires_separate_retention_permission(self):
  for kwargs in({'enabled':False},{'enabled':True,'origin':'LIVE_OBSERVED'}):
   with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):JointL2Writer(self.root,'denied',**kwargs)
  self.assertEqual(list(self.root.iterdir()),[])
 def test_incomplete_or_fenced_generation_aborts_before_atomic_publication(self):
  for stop in(1,3):
   c,token,_=_session('authored','BTC/USD','HISTORICAL_SYNTHETIC');writer=JointL2Writer(self.root,'incomplete',enabled=True)
   for i,raw in enumerate(authored_joint_frames(c.subscription_requests(token))[:stop]):writer.append(raw,i,normalized=c.feed(raw,i,token=token))
   with self.assertRaisesRegex(ValueError,'initialization_or_fence'):writer.finish()
   self.assertEqual(list(self.root.iterdir()),[])
 def test_receipt_rejection_aborts_source_storage(self):
  c,token,_=_session('authored','BTC/USD','HISTORICAL_SYNTHETIC');raw=authored_joint_frames(c.subscription_requests(token))[0];receipt=c.feed(raw,0,token=token)
  for change in('generation','origin','hash','capture'):
   writer=JointL2Writer(self.root,'invalid',enabled=True);r=copy.deepcopy(receipt)
   if change=='generation':r['local_generation']='2'
   elif change=='origin':r['origin']='LIVE_OBSERVED'
   elif change=='hash':r['source_sha256']='0'*64
   else:r['capture']='bad capture'
   with self.subTest(change=change),self.assertRaises(ValueError):writer.append(raw,0,normalized=r)
   self.assertEqual(list(self.root.iterdir()),[])
 def test_joint_recording_does_not_cross_transport_generation(self):
  c,token,_=_session('authored','BTC/USD','HISTORICAL_SYNTHETIC');writer=JointL2Writer(self.root,'generation',enabled=True);raw=authored_joint_frames(c.subscription_requests(token))[0];r=c.feed(raw,0,token=token);writer.append(raw,0,normalized=r);c.disconnected();token=c.connect('second');r=c.feed(raw,1,token=token)
  with self.assertRaisesRegex(ValueError,'joint_receipt'):writer.append(raw,1,normalized=r)
  self.assertEqual(list(self.root.iterdir()),[])
 def test_cache_byte_budget_is_enforced_before_publication(self):
  with patch('terminal.kraken_joint_recording.MAX_CACHE_BYTES',1),self.assertRaisesRegex(ValueError,'cache_budget'):save_joint_fixture(self.root)
  self.assertEqual(list(self.root.iterdir()),[])
 def test_expiry_and_clock_regression_hide_and_clear_native_prefixes(self):
  m,_=self.saved()
  for now in(m['created_unix_seconds']-1,m['created_unix_seconds']+m['retention_seconds']+1):
   session=open_recorded_session(self.root,m['identity'])
   with patch('terminal.kraken_joint_recording.time.time',return_value=now):v=session.view(8,True,1);self.assertEqual(v['origin'],'UNAVAILABLE');self.assertEqual(v['book']['bids'],[]);self.assertEqual(session.frames,[]);self.assertEqual(session.event_count,0)
 def test_book_receive_wall_clock_is_not_refreshed_by_trade(self):
  c,token,_=_session('clocked','BTC/USD','HISTORICAL_SYNTHETIC');writer=JointL2Writer(self.root,'clocked',enabled=True);frames=authored_joint_frames(c.subscription_requests(token))[:6]
  for i,raw in enumerate(frames):writer.append(raw,i,receive_unix_ns=str(100+i),normalized=c.feed(raw,i,token=token))
  m=writer.finish();session=open_recorded_session(self.root,m['identity']);self.assertEqual(session.view(6,False,1)['received_at_ns'],'104');self.assertEqual(session.view(6,False,1)['provenance']['joint_source_receipts']['trade']['receive_monotonic_ns'],'5')
 def test_atomic_publish_failure_keeps_existing_dataset_unchanged(self):
  m,_=self.saved();before=(self.root/m['identity']/'events.jsonl').read_bytes()
  with self.assertRaisesRegex(ValueError,'recording_exists'):JointL2Writer(self.root,m['identity'],enabled=True)
  self.assertEqual((self.root/m['identity']/'events.jsonl').read_bytes(),before)
 def test_flush_or_validation_failure_never_publishes_complete_target(self):
  with patch('terminal.kraken_joint_recording.JointL2Writer._validate_finish',side_effect=ValueError('authored failure')),self.assertRaisesRegex(ValueError,'authored failure'):save_joint_fixture(self.root)
  self.assertEqual(list(self.root.iterdir()),[])
 def test_fresh_process_restores_exact_native_prefix(self):
  m,_=self.saved();script='''import json,sys\nfrom terminal.l2_playback import open_recorded_session\ns=open_recorded_session(sys.argv[1],sys.argv[2]);print(json.dumps(s.view(8,False,1),sort_keys=True))''';result=subprocess.run([sys.executable,'-c',script,str(self.root),m['identity']],capture_output=True,text=True,check=True);out=json.loads(result.stdout);self.assertEqual(out['book']['bids'][0]['price_ticks'],'9900000000');self.assertEqual(out['provenance']['manifest_sha256'],m['manifest_sha256']);self.assertFalse(out['feed']['real_time'])
 def test_application_consumer_dispatch_is_source_verified_without_factory(self):
  tree=ast.parse(Path(__file__).with_name('server').joinpath('app.py').read_text());f=next(n for n in ast.walk(tree)if isinstance(n,ast.AsyncFunctionDef)and n.name=='recording');s=ast.unparse(f);self.assertIn('open_recorded_session',s);self.assertIn('save_joint_l2_fixture',s);self.assertIn('recording_writer_type()',s);self.assertIn('require_recording_profile(capture)',s)


 def test_actual_native_recording_state_reaches_typescript_and_ladder_consumer(self):
  m,_=self.saved();native=NativeSession();native.recorded_session=open_recorded_session(self.root,m['identity']);native.dataset='recorded-l2';native.restart();states=[]
  for position in range(9):native.position=position;states.append(native.state())
  source=self.root/'states.json';source.write_bytes(canonical(states));script=self.root/'check.mjs'
  script.write_text("""import fs from 'node:fs';import assert from 'node:assert/strict';
 const {validateState}=await import(process.argv[2]);const {displayedLadder}=await import(process.argv[3]);const values=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
 assert.equal(values.length,9);for(const state of values){assert.equal(validateState(state),state);assert.equal(state.mode,'HISTORICAL_REPLAY');assert.equal(state.feed.real_time,false);assert.equal(state.feed.sequence_complete,false);assert.equal(state.provenance.complete_initialization,false);assert.equal(state.provenance.independent_source_authentication,false);displayedLadder(state.book.bids,10)}
 const last=values.at(-1);assert.equal(last.book.bids[0].price_ticks,'9900000000');assert.equal(last.flow.trades[0].trade_id,'7');assert.equal(last.provenance.profile,'ORIGINAL_RAW_JOINT_SESSION_RECORDING_V1');console.log('joint_native_typescript_prefixes=9');""")
  root=Path(__file__).resolve().parents[1];result=subprocess.run(['node','--experimental-strip-types',str(script),(root/'terminal/web/src/contracts.ts').as_uri(),(root/'terminal/web/src/bookPresentation.ts').as_uri(),str(source)],capture_output=True,text=True,check=True,timeout=30);self.assertIn('joint_native_typescript_prefixes=9',result.stdout)


 def test_non_online_status_fences_entire_candidate_before_publication(self):
  c,token,_=_session('fenced','BTC/USD','HISTORICAL_SYNTHETIC');writer=JointL2Writer(self.root,'fenced',enabled=True);frames=authored_joint_frames(c.subscription_requests(token))
  for i,raw in enumerate(frames):writer.append(raw,i,normalized=c.feed(raw,i,token=token))
  status=json.loads(frames[0]);status['data'][0]['system']='maintenance';raw=canonical(status).decode();writer.append(raw,8,normalized=c.feed(raw,8,token=token))
  with self.assertRaisesRegex(ValueError,'initialization_or_fence'):writer.finish()
  self.assertEqual(list(self.root.iterdir()),[])
 def test_capture_identity_cannot_change_within_same_numeric_generation(self):
  c,token,_=_session('first','BTC/USD','HISTORICAL_SYNTHETIC');raw=authored_joint_frames(c.subscription_requests(token))[0];writer=JointL2Writer(self.root,'identity',enabled=True);writer.append(raw,0,normalized=c.feed(raw,0,token=token));other,second,_=_session('second','BTC/USD','HISTORICAL_SYNTHETIC')
  with self.assertRaisesRegex(ValueError,'generation_changed'):writer.append(raw,1,normalized=other.feed(raw,1,token=second))
  self.assertEqual(list(self.root.iterdir()),[])


class JointCapture(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.feeds=[]
 async def asyncTearDown(self):
  for feed in self.feeds:await feed.close()
 async def settle(self,condition):
  for _ in range(200):
   if condition():return
   await asyncio.sleep(.001)
  self.fail('authored bounded capture did not settle')
 async def test_actual_capture_writer_dispatch_and_owned_queue_receipts(self):
  c,token,_=_session('captured','BTC/USD','HISTORICAL_SYNTHETIC');capture=await Capture.create(self.root,'captured',enabled=True,version=2,writer_type=JointL2Writer)
  for i,raw in enumerate(authored_joint_frames(c.subscription_requests(token))):
   receipt=c.feed(raw,i,token=token);capture.offer(raw,i,None,receipt);receipt['sha256']='bad';await self.settle(lambda:capture.written==i+1)
  out=await capture.stop();self.assertEqual(out['state'],'COMPLETE');self.assertIsInstance(open_recorded_session(self.root,'captured'),JointRecordedSession)
 async def test_actual_supervisor_attaches_joint_capture_before_first_frame(self):
  released=asyncio.Event();queue=asyncio.Queue()
  async def transport(permission,*,stop,symbol,subscriptions):
   await released.wait()
   for raw in authored_joint_frames(subscriptions):yield raw;await asyncio.sleep(.01)
   while True:yield await queue.get()
  feed=FeedSupervisor(environment={**ENV,'GIG_LIVE_KRAKEN_SESSION_PROFILE':SESSION_PROFILE},transport=transport);self.feeds.append(feed);await feed.start();capture=await Capture.create(self.root,'supervised',enabled=True,writer_type=feed.recording_writer_type());feed.require_recording_profile(capture);feed.capture=capture;released.set();await self.settle(lambda:feed.messages==8 and capture.written==8);self.assertEqual((await capture.stop())['state'],'COMPLETE');self.assertEqual(open_recorded_session(self.root,'supervised').view(8,False,1)['book']['bids'][0]['price_ticks'],'9900000000')
 async def test_source_interrupt_aborts_pending_joint_recording(self):
  released=asyncio.Event()
  async def transport(permission,*,stop,symbol,subscriptions):
   await released.wait()
   for raw in authored_joint_frames(subscriptions)[:4]:yield raw;await asyncio.sleep(.01)
   raise ProviderError('authored_interruption')
  feed=FeedSupervisor(environment={**ENV,'GIG_LIVE_KRAKEN_SESSION_PROFILE':SESSION_PROFILE},transport=transport);self.feeds.append(feed);await feed.start();capture=await Capture.create(self.root,'interrupted',enabled=True,writer_type=JointL2Writer);feed.capture=capture;released.set();await self.settle(lambda:feed.failures>=1 and capture.task.done());self.assertEqual(capture.state,'ERROR');self.assertFalse((self.root/'interrupted').exists())
 async def test_legacy_writer_cannot_receive_joint_receipt_and_profile_is_explicit(self):
  feed=FeedSupervisor(environment={**ENV,'GIG_LIVE_KRAKEN_SESSION_PROFILE':SESSION_PROFILE},transport=lambda *_:None);feed.session_profile=SESSION_PROFILE
  legacy=await Capture.create(self.root,'legacy',enabled=True,version=2)
  try:
   with self.assertRaisesRegex(ProviderError,'profile_unavailable'):feed.require_recording_profile(legacy)
   self.assertIs(feed.recording_writer_type(),JointL2Writer);feed.environment={};self.assertIs(feed.recording_writer_type(),L2Writer)
  finally:await legacy.abort('authored done')


 async def test_capture_reports_publication_uncertainty_without_removing_artifact(self):
  from .recording import sync_directory
  def sync(path):
   if Path(path)==self.root:raise OSError('authored directory-sync failure')
   return sync_directory(path)
  c,token,_=_session('uncertain','BTC/USD','HISTORICAL_SYNTHETIC')
  with patch('terminal.l2_recording.sync_directory',side_effect=sync):
   capture=await Capture.create(self.root,'uncertain',enabled=True,writer_type=JointL2Writer)
   for i,raw in enumerate(authored_joint_frames(c.subscription_requests(token))):
    capture.offer(raw,i,None,c.feed(raw,i,token=token));await self.settle(lambda:capture.written==i+1)
   result=await capture.stop()
  self.assertEqual(result['state'],'ERROR');self.assertEqual(result['reason'],'recording_joint_publication_uncertain');self.assertIsInstance(open_recorded_session(self.root,'uncertain'),JointRecordedSession)


class JointPublicationAndEnvelope(unittest.TestCase):
 setUp=JointRecording.setUp
 saved=JointRecording.saved
 def test_noncanonical_row_envelopes_reject_before_replay_divergence(self):
  m,rows=self.saved()
  for body in(b''.join(json.dumps(row).encode()+b'\n'for row in rows),b''.join(canonical(row)+b'\r\n'for row in rows)):
   mm=copy.deepcopy(m);mm['bytes']=len(body);mm['sha256']=hashlib.sha256(body).hexdigest();mm['manifest_sha256']=_sha({k:v for k,v in mm.items()if k!='manifest_sha256'})
   with self.subTest(body=body[:30]),self.assertRaisesRegex(ValueError,'noncanonical_envelope'):validate_log(m['identity'],mm,body)
 def test_postpublication_directory_sync_failure_preserves_valid_artifact(self):
  from .recording import sync_directory
  from .kraken_joint_recording import JointPublicationUncertain
  def sync(path):
   if Path(path)==self.root:raise OSError('authored directory-sync failure')
   return sync_directory(path)
  with patch('terminal.l2_recording.sync_directory',side_effect=sync),self.assertRaisesRegex(JointPublicationUncertain,'publication_uncertain'):save_joint_fixture(self.root)
  self.assertTrue((self.root/'authored-joint-l2-v1/manifest.json').is_file());self.assertTrue(open_recorded_session(self.root,'authored-joint-l2-v1').view(8,False,1)['eligible'])

