"""Authored raw frames through actual native L2, never real provider observations."""
import copy,hashlib,json,unittest
from unittest.mock import patch
import gig_microstructure as gig
from .kraken import BOOK_SESSION_PROFILE,BOOK_DEPTH_SESSION_PROFILE,ProviderError,UINT64_MAX
from .kraken_coordinator import KrakenSessionCoordinator,KrakenSessionToken,PROFILE,_digest
from .kraken_public_session import KrakenPublicSession
from .test_kraken_public_session import status,trade,trades,raw,window,incident
from .test_kraken_depth_session import wire,levels

class JointSession(unittest.TestCase):
 def new(self,**kwargs):
  c=KrakenSessionCoordinator(profile=PROFILE,**kwargs);t=c.connect('authored-session-1');return c,t
 def ack(self,c,channel='book',method='subscribe',**changes):
  requests=c.subscription_requests(c._token)
  request=requests[0 if channel=='book'else 1]
  result={'channel':channel,'symbol':c.symbol}
  if channel=='book':result.update(depth=c._book.depth,snapshot=True)
  else:result['snapshot']=c._public.snapshot
  p={'method':method,'success':True,'req_id':request['req_id'],'result':result};p.update(changes);return raw(p)
 def initialized(self,*,snapshot=False,depth=10,**kwargs):
  profile=BOOK_SESSION_PROFILE if depth==10 else BOOK_DEPTH_SESSION_PROFILE
  c,t=self.new(depth=depth,book_profile=profile,trade_snapshot=snapshot,**kwargs)
  c.feed(raw(status()),1,token=t);c.feed(self.ack(c),2,token=t);c.feed(self.ack(c,'trade'),3,token=t)
  c.feed(wire([('100','2')],[('101','1')]),4,token=t)
  if snapshot:c.feed(raw(trades(trade(),kind='snapshot')),5,token=t)
  return c,t
 def checkpoint(self,c):return None if c._native is None else gig._checked(c._native.checkpoint())
 def test_explicit_opt_in_configuration_and_legacy_defaults_stay_separate(self):
  for options in({'profile':'future'},{'profile':PROFILE,'book_profile':None},{'profile':PROFILE,'depth':25},{'profile':PROFILE,'native_capacity':True},{'profile':PROFILE,'native_budget':0},{'profile':PROFILE,'book_request_id':200,'trade_request_id':100}):
   with self.subTest(options=options),self.assertRaises(ProviderError):KrakenSessionCoordinator(**options)
  from .kraken import KrakenBookAdapter
  legacy=KrakenBookAdapter(lambda **_:None);self.assertEqual(legacy.depth,10);self.assertIsNone(legacy.book_session_profile)
 def test_connect_returns_current_process_local_token_and_distinct_pure_requests(self):
  c,t=self.new();p=c.subscription_requests(t);self.assertEqual([r['req_id']for r in p],[101,201]);self.assertEqual([r['params']['channel']for r in p],['book','trade']);self.assertEqual(t,KrakenSessionToken('authored-session-1',1,'BTC/USD'));self.assertIsNone(c._native)
  p[0]['params']['depth']=100;self.assertEqual(c.subscription_requests(t)[0]['params']['depth'],10)
 def test_connection_generation_and_request_ids_never_wrap(self):
  c,t=self.new();c._public.generation=(UINT64_MAX-c._public.request_id)//2;c._book._book_generation=c._public.generation;c._generation=c._public.generation
  with self.assertRaises(ProviderError):c.connect('authored-second')
  self.assertTrue(c._reconnect_required);self.assertFalse(c._eligible)
 def test_bad_capture_labels_and_missing_connection_do_not_admit_source(self):
  c=KrakenSessionCoordinator(profile=PROFILE)
  for capture in('',True,'secret\nvalue','x'*129):
   with self.assertRaises(ProviderError):c.connect(capture)
  with self.assertRaises(ProviderError):c.feed(raw(status()),1,token=None)
 def test_online_status_is_required_before_both_acknowledgments(self):
  for channel in('book','trade'):
   c,t=self.new()
   with self.subTest(channel=channel),self.assertRaisesRegex(ProviderError,'online_status'):c.feed(self.ack(c,channel),1,token=t)
   self.assertIsNone(c._native);self.assertFalse(c.view(2)['book_eligible'])
 def test_both_channels_and_real_book_snapshot_are_required(self):
  c,t=self.new();c.feed(raw(status()),1,token=t);c.feed(self.ack(c),2,token=t);c.feed(wire([('100','2')],[('101','1')]),3,token=t)
  self.assertIsNotNone(c._native);self.assertIsNone(c.view(3)['book']);r=c.feed(self.ack(c,'trade'),4,token=t);self.assertTrue(r['book_eligible']);self.assertEqual(c.view(4)['book']['bids'][0]['quantity'],'200000000')
 def test_requested_trade_snapshot_is_independent_of_native_l2_snapshot(self):
  c,t=self.initialized(snapshot=False);self.assertTrue(c.view(4)['book_eligible'])
  c,t=self.new(trade_snapshot=True);c.feed(raw(status()),1,token=t);c.feed(self.ack(c),2,token=t);c.feed(self.ack(c,'trade'),3,token=t);c.feed(wire([('100','2')],[('101','1')]),4,token=t)
  self.assertIsNone(c.view(4)['book']);before=self.checkpoint(c);r=c.feed(raw(trades(trade(),kind='snapshot')),5,token=t);self.assertTrue(r['book_eligible']);self.assertEqual(self.checkpoint(c),before);self.assertIsNone(r['native_event']);self.assertEqual(r['trade_observation_level'],'EXECUTED_TRADES_NOT_L3_ORDERS')
 def test_native_snapshot_update_revision_and_exact_state_are_preserved(self):
  c,t=self.initialized();a=c.view(4)['book'];self.assertEqual(a['revision'],'1');self.assertEqual(a['metrics']['bid_depth'],{'numerator':'200000000','denominator':'1'})
  r=c.feed(wire([('100','4')],[],kind='update',final=([('100','4')],[('101','1')])),5,token=t);self.assertEqual(r['native_book_revision'],'2');self.assertEqual(c.view(5)['book']['bids'][0]['quantity'],'400000000')
  c.feed(wire([('100','7')],[],kind='update',final=([('100','7')],[('101','1')])),6,token=t);self.assertEqual(c.view(6)['book']['revision'],'3');self.assertEqual(c.view(6)['book']['bids'][0]['quantity'],'700000000')
 def test_raw_hashes_and_exact_native_event_receipt_coverage(self):
  c,t=self.initialized();message=wire([('100','4')],[],kind='update',final=([('100','4')],[('101','1')]));r=c.feed(message,5,token=t)
  self.assertEqual(r['source_sha256'],hashlib.sha256(message.encode()).hexdigest());self.assertEqual(r['source_hash_basis'],'HASHED_RAW_FRAME');self.assertEqual(r['native_event'],r['source_receipt']['native_event']);self.assertEqual(r['native_book_sha256'],_digest(self.checkpoint(c)));self.assertEqual(r['native_book_source_sha256'],r['source_sha256']);self.assertEqual(r['connection_id'],'42');self.assertIsNone(r['source_sequence']);self.assertFalse(r['independent_source_authentication']);self.assertFalse(r['full_protocol_qualified']);self.assertFalse(r['provider_requested']);body={k:v for k,v in r.items()if k!='sha256'};self.assertEqual(r['sha256'],_digest(body))
 def test_trade_status_and_heartbeat_do_not_mutate_native_or_relabel_book_source(self):
  c,t=self.initialized();before=self.checkpoint(c);source=c.view(4)['native_book_source_sha256']
  for now,message in((5,raw(trades(trade()))),(6,raw(status(upcoming_maintenance=[window()],emergency=[incident()]))),(7,'{"channel":"heartbeat"}')):
   r=c.feed(message,now,token=t);self.assertIsNone(r['native_event']);self.assertEqual(self.checkpoint(c),before);self.assertEqual(r['native_book_source_sha256'],source);self.assertTrue(r['book_eligible'])
 def test_unknown_or_malformed_frames_cannot_keep_an_eligible_native_book(self):
  for message in('[]','{"x":NaN}','{"channel":"book","channel":"trade"}','{"channel":"unknown"}','\ud800','x'*65537,{}):
   c,t=self.initialized();before=self.checkpoint(c)
   with self.subTest(message=str(message)[:40]),self.assertRaises(ProviderError):c.feed(message,5,token=t)
   self.assertEqual(self.checkpoint(c),before);v=c.view(6);self.assertFalse(v['book_eligible']);self.assertIsNone(v['book']);self.assertTrue(v['reconnect_required'])
 def test_rejected_subscription_and_wrong_request_or_symbol_fence_all_channels(self):
  for changes in({'success':False,'error':'authored rejection'},{'req_id':999},{'result':{'channel':'book','symbol':'ETH/USD','depth':10,'snapshot':True}}):
   c,t=self.initialized();before=self.checkpoint(c)
   with self.subTest(changes=changes),self.assertRaises(ProviderError):c.feed(self.ack(c,**changes),5,token=t)
   self.assertEqual(self.checkpoint(c),before);self.assertIsNone(c.view(6)['book'])
 def test_trade_rejection_receipt_fences_even_when_book_is_synchronized(self):
  c,t=self.new();c.feed(raw(status()),1,token=t);c.feed(self.ack(c),2,token=t);c.feed(wire([('100','2')],[('101','1')]),3,token=t)
  r=c.feed(raw({'method':'subscribe','success':False,'req_id':201,'error':'authored unavailable'}),4,token=t);self.assertEqual(r['kind'],'request_rejected');self.assertTrue(r['reconnect_required']);self.assertIsNone(c.view(4)['book'])
 def test_all_nononline_states_fence_and_later_online_status_cannot_restore(self):
  for system in('cancel_only','maintenance','post_only'):
   c,t=self.initialized();before=self.checkpoint(c);r=c.feed(raw(status(system)),5,token=t);self.assertTrue(r['reconnect_required']);self.assertFalse(r['book_eligible']);self.assertIsNone(c.view(5)['book']);c.feed(raw(status()),6,token=t)
   with self.assertRaisesRegex(ProviderError,'reconnect_required'):c.feed(wire([('100','3')],[('101','1')]),7,token=t)
   self.assertEqual(self.checkpoint(c),before)
 def test_changed_connection_cannot_reuse_eligible_native_state(self):
  c,t=self.initialized();before=self.checkpoint(c)
  with self.assertRaisesRegex(ProviderError,'connection_changed'):c.feed(raw(status(connection_id=43)),5,token=t)
  self.assertEqual(self.checkpoint(c),before);self.assertIsNone(c.view(6)['book']);self.assertEqual(c.view(6)['connection_id'],'42')
 def test_reconnect_resets_native_and_requires_fresh_status_both_acks_and_snapshot(self):
  c,old=self.initialized();new=c.connect('authored-session-2');self.assertEqual(new.generation,2);self.assertIsNone(c._native);self.assertIsNone(c.view(1)['book']);self.assertEqual([r['req_id']for r in c.subscription_requests(new)],[102,203]);c.feed(raw(status(connection_id=43)),2,token=new);c.feed(self.ack(c),3,token=new);c.feed(self.ack(c,'trade'),4,token=new);self.assertIsNone(c.view(4)['book']);c.feed(wire([('99','7')],[('102','1')]),5,token=new);self.assertEqual(c.view(5)['book']['bids'][0]['quantity'],'700000000');self.assertEqual(c.view(5)['connection_id'],'43')
 def test_old_copied_or_foreign_tokens_are_not_current_connection_authority(self):
  for kind in('old','copied','foreign','mapping'):
   c,t=self.initialized()
   if kind=='old':bad=t;t=c.connect('authored-session-2')
   elif kind=='copied':bad=copy.copy(t)
   elif kind=='foreign':_,bad=self.new()
   else:bad={'capture':t.capture,'generation':t.generation,'symbol':t.symbol}
   with self.subTest(kind=kind),self.assertRaisesRegex(ProviderError,'capture_token'):c.feed(raw(status()),6,token=bad)
   self.assertIsNone(c.view(7)['book']);self.assertTrue(c._reconnect_required)
 def test_bad_clock_does_not_advance_receipt_or_publish_native(self):
  for now in(3,-1,True,UINT64_MAX+1):
   c,t=self.initialized();before=self.checkpoint(c);last=c._last_receipt_sha256
   with self.subTest(now=now),self.assertRaises(ProviderError):c.feed(raw(trades(trade())),now,token=t)
   self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._last_receipt_sha256,last);self.assertIsNone(c.view(5)['book'])
 def test_book_staleness_is_not_refreshed_by_trade_or_heartbeat(self):
  c,t=self.initialized(stale_ns=10);c.feed(raw(trades(trade())),13,token=t);self.assertTrue(c.view(14)['book_eligible'])
  with self.assertRaisesRegex(ProviderError,'book_stale'):c.feed('{"channel":"heartbeat"}',15,token=t)
  self.assertFalse(c._eligible);self.assertTrue(c._reconnect_required)
  c,t=self.initialized(stale_ns=10)
  v=c.view(15);self.assertFalse(v['book_eligible']);self.assertIsNone(v['book']);self.assertEqual(v['reason'],'coordinator_book_stale')
  self.assertFalse(c._eligible)
 def test_bad_crc_and_late_trade_conflict_never_commit_native_or_python_candidates(self):
  for message in(wire([('100','3')],[('101','1')],checksum=0),raw(trades(trade(),trade(2,symbol='ETH/USD')))):
   c,t=self.initialized();before=self.checkpoint(c);bids=copy.deepcopy(c._book.bids);last=c._last_receipt_sha256
   with self.assertRaises(ProviderError):c.feed(message,5,token=t)
   self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._book.bids,bids);self.assertEqual(c._last_receipt_sha256,last);self.assertFalse(c._eligible)
 def test_native_capacity_failure_is_actual_cpp_rollback_and_source_fence(self):
  c,t=self.initialized(depth=100,native_capacity=100);bids,asks=levels(100);c.feed(wire(bids,asks),5,token=t);before=self.checkpoint(c);old_bids=copy.deepcopy(c._book.bids);better=[(str(1200-i),'3')for i in range(100)];better_asks=[(str(1800+i),'4')for i in range(100)]
  with self.assertRaisesRegex(ProviderError,'native_rejected'):c.feed(wire(better,better_asks,kind='update',final=(better,better_asks)),6,token=t)
  self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._book.bids,old_bids);self.assertIsNone(c.view(7)['book'])
 def test_depth_hundred_two_hundred_changes_per_side_commit_atomically(self):
  c,t=self.initialized(depth=100);bids,asks=levels(100);c.feed(wire(bids,asks),5,token=t);better=[(str(1200-i),'3')for i in range(100)];better_asks=[(str(1800+i),'4')for i in range(100)];r=c.feed(wire(better,better_asks,kind='update',final=(better,better_asks)),6,token=t)
  self.assertEqual(len(r['native_event']['bids']),200);self.assertEqual(len(r['native_event']['asks']),200);self.assertEqual(len(c.view(6)['book']['bids']),100);self.assertEqual(r['native_book_revision'],'3')
 def test_receipt_allocation_failure_leaves_prior_native_financial_state_unchanged(self):
  c,t=self.initialized();before=self.checkpoint(c);last=c._last_receipt_sha256
  with patch.object(c,'_make_receipt',side_effect=MemoryError),self.assertRaises(MemoryError):c.feed(wire([('100','3')],[('101','1')]),5,token=t)
  self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._last_receipt_sha256,last);self.assertIsNone(c.view(6)['book'])
 def test_unverified_public_receipt_authority_or_changed_native_event_cannot_bridge(self):
  c,t=self.initialized();before=self.checkpoint(c);original=KrakenPublicSession.feed
  def forged(owner,*a,**kw):r=original(owner,*a,**kw);r['source_hash_basis']='CALLER_SUPPLIED_DIGEST';return r
  with patch.object(KrakenPublicSession,'feed',forged),self.assertRaisesRegex(ProviderError,'public_receipt_binding'):c.feed(raw(trades(trade())),5,token=t)
  self.assertEqual(self.checkpoint(c),before);self.assertFalse(c._eligible)
  c,t=self.initialized();from .kraken import KrakenBookAdapter
  original=KrakenBookAdapter.feed
  def altered(owner,*a,**kw):r=original(owner,*a,**kw);r['native_event']['bids'][0]['quantity']='99';return r
  with patch.object(KrakenBookAdapter,'feed',altered),self.assertRaisesRegex(ProviderError,'native_receipt_binding'):c.feed(wire([('100','3')],[('101','1')]),5,token=t)
  self.assertFalse(c._eligible)
 def test_returned_views_requests_and_receipts_cannot_mutate_owned_source_or_native(self):
  c,t=self.initialized();before=self.checkpoint(c);r=c.feed(raw(trades(trade())),5,token=t);r['source_receipt']['trades'][0]['trade_id']='changed';r['native_book_sha256']='0'*64;v=c.view(6);v['book']['bids'][0]['quantity']='0';self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._public.trades[0]['trade_id'],'1');self.assertEqual(c.view(6)['book']['bids'][0]['quantity'],'200000000')
 def test_trade_unsubscription_intent_and_ack_end_joint_eligibility(self):
  c,t=self.initialized();before=self.checkpoint(c);request=c.trade_unsubscription_request(t);self.assertEqual(request['req_id'],202);self.assertIsNone(c.view(5)['book']);p={'method':'unsubscribe','success':True,'req_id':202,'result':{'channel':'trade','symbol':c.symbol}};r=c.feed(raw(p),6,token=t);self.assertTrue(r['reconnect_required']);self.assertEqual(self.checkpoint(c),before)
  with self.assertRaises(ProviderError):c.feed(wire([('100','3')],[('101','1')]),7,token=t)
 def test_ordered_repeated_updates_reach_native_after_final_depth_and_crc_validation(self):
  c,t=self.initialized(depth=25);bids,asks=levels(25);c.feed(wire(bids,asks),5,token=t)
  final=([('1001','7')]+bids[:-1],asks);r=c.feed(wire([('1001','1'),('1001.00','0'),('1001','7')],[],kind='update',final=final),6,token=t)
  self.assertEqual(c.view(6)['book']['bids'][0],{'price_ticks':'100100','quantity':'700000000'});self.assertEqual(r['subscribed_depth'],25);self.assertEqual(r['checksum_depth'],10);self.assertEqual(r['checksum_scope'],'top_10_per_side_only');self.assertEqual(r['source_frame_bytes'],len(wire([('1001','1'),('1001.00','0'),('1001','7')],[],kind='update',final=final).encode()))
 def test_duplicate_raw_book_frame_does_not_create_a_native_revision_or_refresh_book_clock(self):
  c,t=self.initialized(stale_ns=10);before=self.checkpoint(c);source=c._native_source
  r=c.feed(wire([('100','2')],[('101','1')]),13,token=t);self.assertEqual(r['kind'],'duplicate');self.assertIsNone(r['native_event']);self.assertEqual(self.checkpoint(c),before);self.assertEqual(c._native_source,source);self.assertEqual(c._book.last_book_receive_ns,4)
  self.assertIsNone(c.view(15)['book'])
 def test_exact_large_trade_identity_and_nonintegral_token_do_not_change_native(self):
  c,t=self.initialized();before=self.checkpoint(c);p=raw(trades(trade(9007199254740993))).replace('"price":10','"price":1.001e1').replace('"qty":1','"qty":0.00000001');r=c.feed(p,5,token=t);tr=r['source_receipt']['trades'][0];self.assertEqual(tr['trade_id'],'9007199254740993');self.assertEqual(tr['price_ticks'],'1001');self.assertEqual(tr['quantity'],'1');self.assertEqual(self.checkpoint(c),before)
  p=raw(trades(trade(2))).replace('"trade_id":2','"trade_id":2.00000000000000001')
  with self.assertRaisesRegex(ProviderError,'public_trade_id'):c.feed(p,6,token=t)
  self.assertEqual(self.checkpoint(c),before);self.assertIsNone(c.view(6)['book'])
 def test_native_memory_failure_cannot_publish_initial_financial_state(self):
  c,t=self.new(native_budget=1);c.feed(raw(status()),1,token=t);c.feed(self.ack(c),2,token=t);c.feed(self.ack(c,'trade'),3,token=t)
  with self.assertRaisesRegex(ProviderError,'native_rejected'):c.feed(wire([('100','2')],[('101','1')]),4,token=t)
  self.assertIsNone(c._native);self.assertIsNone(c.view(5)['book']);self.assertTrue(c._reconnect_required)
 def test_native_view_allocation_failure_fences_eligibility_without_changing_image(self):
  c,t=self.initialized();before=self.checkpoint(c)
  with patch('terminal.providers.kraken_coordinator.gig._checked',side_effect=MemoryError),self.assertRaisesRegex(ProviderError,'native_view_unavailable'):c.view(5)
  self.assertEqual(self.checkpoint(c),before);self.assertIsNone(c.view(6)['book'])
 def test_disconnection_removes_native_owner_and_cannot_receive_old_frames(self):
  c,t=self.initialized();c.disconnected();self.assertIsNone(c._native);self.assertIsNone(c.view(5)['book'])
  with self.assertRaisesRegex(ProviderError,'capture_token'):c.feed(raw(status()),6,token=t)

if __name__=='__main__':unittest.main()
