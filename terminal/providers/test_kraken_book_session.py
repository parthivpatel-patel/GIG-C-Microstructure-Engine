"""Authored offline book negotiation; official response fields, local session fences."""
import copy,json,unittest
from .kraken import KrakenBookAdapter,ProviderError,BOOK_SESSION_PROFILE,UINT64_MAX
from .test_kraken import book

class BookSession(unittest.TestCase):
 def adapter(self,**options):
  calls=[];a=KrakenBookAdapter(lambda **kw:calls.append(kw),book_session_profile=BOOK_SESSION_PROFILE,book_request_id=100,**options);a.connect();return a,calls
 def ack(self,a,**changes):
  value={'method':'subscribe','success':True,'req_id':a.book_subscription_request()['req_id'],
   'result':{'channel':'book','symbol':a.symbol,'depth':10,'snapshot':True},
   'time_in':'2026-01-01T00:00:00.000000001Z','time_out':'2026-01-01T00:00:00.000000002Z'}
  value.update(changes);return value
 def accept(self,a,now=1):return a.feed(json.dumps(self.ack(a)),now)
 def test_pure_request_builder_and_matching_ack_preserve_exact_metadata(self):
  a,calls=self.adapter();before=(a.state,a._book_acknowledged,a._book_generation)
  request=a.book_subscription_request();self.assertEqual(request,{'method':'subscribe','params':{'channel':'book','symbol':['BTC/USD'],'depth':10,'snapshot':True},'req_id':101});self.assertEqual((a.state,a._book_acknowledged,a._book_generation),before)
  response=self.ack(a);response['result']['warnings']=['authored deprecation'];r=a.feed(json.dumps(response),1)
  self.assertEqual(r['request_id'],'101');self.assertEqual(r['local_generation'],'1');self.assertEqual(r['depth'],10);self.assertTrue(r['snapshot']);self.assertEqual(r['warnings'],['authored deprecation']);self.assertEqual(r['source_times_ns']['time_in'],'1767225600000000001');self.assertIsNone(r['source_sequence']);self.assertEqual(a.state,'SYNCHRONIZING');self.assertEqual(calls,[])
  a.feed(book(),2);self.assertEqual(len(calls),1);self.assertEqual(a.state,'LIVE');self.assertFalse(a.capabilities['profile_verified'])
 def test_book_snapshot_requires_current_ack_and_ack_does_not_replace_snapshot(self):
  a,calls=self.adapter()
  with self.assertRaisesRegex(ProviderError,'acknowledgment_required'):a.feed(book(),1)
  self.assertEqual(calls,[]);a.connect();self.accept(a,2)
  with self.assertRaisesRegex(ProviderError,'snapshot_required'):a.feed(book(kind='update'),3)
  self.assertEqual(calls,[])
 def test_wrong_depth_snapshot_and_request_types_fail_before_native(self):
  cases=[('depth',25),('depth',True),('depth','10'),('snapshot',False),('snapshot',1)]
  for field,value in cases:
   a,calls=self.adapter();response=self.ack(a);response['result'][field]=value
   with self.subTest(field=field,value=value),self.assertRaises(ProviderError):a.feed(json.dumps(response),1)
   self.assertEqual(calls,[]);self.assertFalse(a._book_acknowledged)
  for value in(None,True,'101',102,-1,2**64):
   a,calls=self.adapter();response=self.ack(a);response['req_id']=value
   with self.subTest(req_id=value),self.assertRaisesRegex(ProviderError,'book_ack_request_id'):a.feed(json.dumps(response),1)
   self.assertEqual(calls,[])
 def test_optional_fields_are_bounded_and_unknown_fields_reject(self):
  for warnings in('text',[1],['x'*257],['x']*17,['unsafe\ntext']):
   a,calls=self.adapter();response=self.ack(a);response['result']['warnings']=warnings
   with self.assertRaisesRegex(ProviderError,'book_ack_warnings'):a.feed(json.dumps(response),1)
   self.assertEqual(calls,[])
  for location in('top','result'):
   a,_=self.adapter();response=self.ack(a)
   if location=='top':response['unknown']=True
   else:response['result']['unknown']=True
   with self.assertRaisesRegex(ProviderError,'book_ack_fields'):a.feed(json.dumps(response),1)
 def test_time_metadata_is_exact_validated_and_cannot_regress_receive_order(self):
  for change in({'time_in':'invalid'},{'time_out':'2025-01-01T00:00:00Z'},{'time_out':True}):
   a,calls=self.adapter()
   with self.assertRaises(ProviderError):a.feed(json.dumps(self.ack(a,**change)),1)
   self.assertEqual(calls,[])
  a,calls=self.adapter();self.accept(a,10)
  with self.assertRaisesRegex(ProviderError,'receive_clock_regression'):a.feed(book(),9)
  self.assertFalse(a._book_acknowledged)
  with self.assertRaisesRegex(ProviderError,'acknowledgment_required'):a.feed(book(),11)
  self.assertEqual(calls,[])
 def test_reconnect_changes_request_identity_and_rejects_old_ack(self):
  a,calls=self.adapter();stale=self.ack(a);self.accept(a);a.feed(book(),2);a.disconnected()
  self.assertFalse(a._book_acknowledged)
  with self.assertRaisesRegex(ProviderError,'session_not_connecting'):a.feed(json.dumps(stale),3)
  a.connect();self.assertEqual(a.book_subscription_request()['req_id'],102)
  with self.assertRaisesRegex(ProviderError,'book_ack_request_id'):a.feed(json.dumps(stale),4)
  self.assertEqual(len(calls),1);self.assertEqual(a.bids,{})
  a.connect();self.accept(a,5);a.feed(book(),6);self.assertEqual(len(calls),2)
 def test_redundant_ack_and_heartbeat_do_not_make_stale_book_live(self):
  a,calls=self.adapter();self.accept(a);a.feed(book(),2);now=10_000_000_003;self.assertEqual(a.status(now)['state'],'STALE')
  self.accept(a,now);self.assertEqual(a.state,'STALE');self.assertEqual(a.last_book_receive_ns,2)
  a.feed('{"channel":"heartbeat"}',now+1);self.assertEqual(a.state,'STALE');self.assertEqual(len(calls),1)
 def test_bad_checksum_or_native_failure_invalidates_negotiation_atomically(self):
  for failure in('checksum','native'):
   a,calls=self.adapter();self.accept(a);a.feed(book(),2);before=(a.bids.copy(),a.asks.copy())
   if failure=='native':a.apply_native=lambda **_:(_ for _ in()).throw(MemoryError())
   raw=book([('99','1')], [('102','1')],checksum=0 if failure=='checksum'else None)
   with self.assertRaises(ProviderError):a.feed(raw,3)
   self.assertEqual((a.bids,a.asks),before);self.assertFalse(a._book_acknowledged);self.assertEqual(len(calls),1)
   with self.assertRaisesRegex(ProviderError,'session_not_connecting'):self.accept(a,4)
 def test_unexpected_book_envelope_fields_do_not_gain_authority(self):
  a,calls=self.adapter();self.accept(a);value=json.loads(book());value['reset']=True
  with self.assertRaisesRegex(ProviderError,'book_envelope_fields'):a.feed(json.dumps(value),2)
  self.assertEqual(calls,[])
 def test_profile_configuration_request_exhaustion_and_legacy_compatibility(self):
  for profile,request in(('unreviewed',1),(None,1),(BOOK_SESSION_PROFILE,None),(BOOK_SESSION_PROFILE,True),(BOOK_SESSION_PROFILE,-1),(BOOK_SESSION_PROFILE,2**64)):
   with self.assertRaises(ProviderError):KrakenBookAdapter(lambda **_:None,book_session_profile=profile,book_request_id=request)
  a,_=self.adapter();a._book_generation=UINT64_MAX-a.book_request_id;before=a.state
  with self.assertRaisesRegex(ProviderError,'request_id_exhausted'):a.connect()
  self.assertEqual(a.state,before)
  calls=[];legacy=KrakenBookAdapter(lambda **kw:calls.append(kw));self.assertNotIn('req_id',legacy.book_subscription_request());legacy.feed(book(),1);self.assertEqual(len(calls),1)
  legacy.connect();r=legacy.feed('{"method":"subscribe","success":true,"result":{"channel":"book","symbol":"BTC/USD"}}',2);self.assertEqual(r,{'kind':'acknowledgment','source_sequence':None})
 def test_optional_ack_times_and_warning_arrays_can_be_absent(self):
  a,calls=self.adapter();response=self.ack(a);response.pop('time_in');response.pop('time_out');r=a.feed(json.dumps(response),1)
  self.assertEqual(r['warnings'],[]);self.assertEqual(r['source_times_ns'],{});self.assertEqual(calls,[])

if __name__=='__main__':unittest.main(verbosity=2)
