"""Authored offline WSv2 fixtures; these are never observations or provider access."""
import copy,hashlib,json,unittest
from decimal import Decimal
from .kraken import ProviderError,UINT64_MAX
from .kraken_public_session import KrakenPublicSession,PROFILE,instant

STAMP='2024-02-01T12:00:00.000000001Z'
def status(system='online',connection_id=42,**extras):return {'channel':'status','type':'update','data':[{'system':system,'api_version':'v2','connection_id':connection_id,'version':'2.0.8',**extras}]}
def ack(s,method='subscribe',**changes):
 result={'channel':'trade','symbol':s.symbol}
 if method=='subscribe':result['snapshot']=s.snapshot
 return {'method':method,'success':True,'req_id':s.current_request_id(method),'result':result,**changes}
def trade(id=1,**changes):return {'symbol':'BTC/USD','side':'buy','price':10,'qty':1,'trade_id':id,'timestamp':STAMP,'ord_type':'limit',**changes}
def trades(*values,kind='update'):return {'channel':'trade','type':kind,'data':list(values)}
def raw(p):return json.dumps(p,separators=(',',':'))
def active(**kw):
 s=KrakenPublicSession(**kw);s.connect();s.feed(raw(status()),1);s.feed(raw(ack(s)),2);return s

def window(**changes):return {'event_id':1,'title':'Scheduled service event','expected_start_utc':STAMP,'expected_end_utc':None,'time_to_start_s':0,'phase':'announced','affected_services':['spot_ws'],'order_submission':'discouraged','recommended_action':'reduce_activity','cancel_before_utc':None,'source_url':'https://status.kraken.com/incidents/authored-example',**changes}
def incident(**changes):return {'event_id':2,'title':'Authored incident','incident_status':'investigating','impact':'minor','affected_services':['spot_ws'],'started_at_utc':STAMP,'next_steps':[{'applies_to':['spot_ws'],'type':'expected_online','expected_at_utc':STAMP}],'source_url':'',**changes}

class PublicSession(unittest.TestCase):
 def test_explicit_configuration_and_generation_request_ids(self):
  s=KrakenPublicSession(request_id=200,snapshot=True);s.connect();self.assertEqual(s.subscription_request(),{'method':'subscribe','params':{'channel':'trade','symbol':['BTC/USD'],'snapshot':True},'req_id':201});s.disconnected();s.connect();self.assertEqual(s.subscription_request()['req_id'],203)
  for change in({'request_id':True},{'request_id':-1},{'price_scale':0},{'quantity_scale':True},{'symbol':'XBT/USD'},{'snapshot':1},{'origin':'OBSERVED_OFFICIAL_RESPONSE'}):
   with self.subTest(change=change),self.assertRaises(ProviderError):KrakenPublicSession(**change)
 def test_request_ids_do_not_wrap_or_reuse_on_failed_connect(self):
  s=KrakenPublicSession(request_id=UINT64_MAX-2);s.connect();before=s.generation
  with self.assertRaisesRegex(ProviderError,'exhausted'):s.connect()
  self.assertEqual(s.generation,before)
 def test_no_requests_or_trade_before_connection_status_and_ack(self):
  s=KrakenPublicSession()
  with self.assertRaises(ProviderError):s.subscription_request()
  for setup in(0,1,2):
   s=KrakenPublicSession()
   if setup:s.connect()
   if setup==2:s.feed(raw(status()),1)
   with self.subTest(setup=setup),self.assertRaises(ProviderError):s.feed(raw(trades(trade())),3)
   self.assertTrue(s.reconnect_required)
 def test_initial_status_and_ack_provenance_is_exact_and_observation_claim_absent(self):
  s=KrakenPublicSession();s.connect();body=raw(status());r=s.feed(body,1)
  self.assertEqual(r['source_sha256'],hashlib.sha256(body.encode()).hexdigest());self.assertEqual(r['connection_id'],'42');self.assertEqual(r['local_generation'],'1');self.assertIsNone(r['source_sequence']);self.assertFalse(r['independent_source_authentication']);self.assertFalse(r['full_protocol_qualified']);self.assertEqual(r['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(r['public_session_profile'],PROFILE)
  a=ack(s,time_in='2024-02-01T12:00:00Z',time_out=STAMP);a['result']['warnings']=['Authored advisory'];r=s.feed(raw(a),2);self.assertEqual(r['warnings'],['Authored advisory']);self.assertEqual(s.phase,'ACTIVE')
 def test_ack_identity_snapshot_and_phase_fail_closed(self):
  for change in('id','channel','symbol','snapshot','extra','success','time','warnings','missing_result'):
   s=KrakenPublicSession();s.connect();s.feed(raw(status()),1);p=ack(s)
   if change=='id':p['req_id']+=1
   elif change=='channel':p['result']['channel']='book'
   elif change=='symbol':p['result']['symbol']='ETH/USD'
   elif change=='snapshot':p['result']['snapshot']=True
   elif change=='extra':p['unknown']=True
   elif change=='success':p['success']=1
   elif change=='time':p.update(time_in=STAMP,time_out='2024-01-01T00:00:00Z')
   elif change=='warnings':p['result']['warnings']=[False]
   else:p.pop('result')
   with self.subTest(change=change),self.assertRaises(ProviderError):s.feed(raw(p),2)
   self.assertEqual(s.phase,'RECONNECT_REQUIRED')
  s=active()
  with self.assertRaises(ProviderError):s.feed(raw(ack(s)),3)
 def test_negative_ack_is_explicit_rejection_and_requires_reconnect(self):
  s=KrakenPublicSession();s.connect();s.feed(raw(status()),1);r=s.feed(raw({'method':'subscribe','success':False,'req_id':s.current_request_id(),'error':'Authored rejected request'}),2)
  self.assertEqual(r['kind'],'request_rejected');self.assertTrue(r['reconnect_required']);self.assertEqual(s.phase,'RECONNECT_REQUIRED')
  with self.assertRaises(ProviderError):s.feed(raw(trades(trade())),3)
 def test_unsubscribe_ack_controls_lifecycle_without_sending_anything(self):
  s=active();p=s.unsubscription_request();self.assertEqual(p['method'],'unsubscribe');self.assertEqual(p['params'],{'channel':'trade','symbol':['BTC/USD']});self.assertEqual(p['req_id'],202);s.feed(raw(ack(s,'unsubscribe')),3);self.assertEqual(s.phase,'UNSUBSCRIBED')
  with self.assertRaises(ProviderError):s.feed(raw(trades(trade())),4)
 def test_unsubscribe_requires_active_online_session(self):
  s=KrakenPublicSession();s.connect()
  with self.assertRaises(ProviderError):s.unsubscription_request()
  s=active();s.unsubscription_request()
  with self.assertRaises(ProviderError):s.unsubscription_request()
 def test_exact_number_tokens_before_binary_float_and_wire_order(self):
  s=active();body=raw(trades(trade(3),trade(1),trade(9007199254740993))).replace('"price":10','"price":1.001e1').replace('"qty":1','"qty":0.00000001')
  r=s.feed(body,3);self.assertEqual([t['trade_id']for t in r['trades']],['3','1','9007199254740993']);self.assertEqual(r['trades'][0]['price_ticks'],'1001');self.assertEqual(r['trades'][0]['quantity'],'1');self.assertEqual(r['side_semantics'],'taker_order_side');self.assertFalse(r['gap_detection']);self.assertFalse(r['complete_history']);self.assertIsNone(r['source_sequence'])
 def test_price_quantity_lexical_scale_range_and_floats_are_not_coerced(self):
  for key,value in(('price','10'),('qty','1'),('price',True),('price',-1),('qty',0),('price',0.001),('qty',0.000000001),('price',10**25),('trade_id',-1),('trade_id',1.5),('trade_id',True)):
   s=active()
   with self.subTest(key=key,value=value),self.assertRaises(ProviderError):s.feed(raw(trades(trade(**{key:value}))),3)
   self.assertFalse(s.trades)
  s=active()
  with self.assertRaisesRegex(ProviderError,'public_payload_scalar'):s.accept_payload(trades(trade(price=10.0)),3,'a'*64)
 def test_fractional_trade_id_cannot_round_into_an_integer(self):
  s=active();p=raw(trades(trade())).replace('"trade_id":1','"trade_id":1.00000000000000001')
  with self.assertRaisesRegex(ProviderError,'public_trade_id'):s.feed(p,3)
 def test_rfc3339_offsets_preserve_lexical_and_exact_nanoseconds(self):
  s=active();stamp='2024-02-01T13:00:00.000000001+01:00';r=s.feed(raw(trades(trade(timestamp=stamp))),3)
  self.assertEqual(r['trades'][0]['source_timestamp'],stamp);self.assertEqual(r['trades'][0]['source_timestamp_ns'],instant(STAMP))
  for stamp in('2024-02-31T00:00:00Z','2024-01-01T24:00:00Z','2024-01-01T00:00:60Z','2024-01-01T00:00:00-00:00','2024-01-01T00:00:00.1234567890Z','1969-01-01T00:00:00Z'):
   with self.subTest(stamp=stamp),self.assertRaises(ProviderError):instant(stamp)
 def test_snapshot_limit_is_fifty_and_snapshot_is_explicit_once(self):
  s=active(snapshot=True)
  with self.assertRaisesRegex(ProviderError,'snapshot_required'):s.feed(raw(trades(trade())),3)
  s=active(snapshot=True);r=s.feed(raw(trades(*(trade(i)for i in range(50)),kind='snapshot')),3);self.assertEqual(len(r['trades']),50);self.assertEqual(r['snapshot_trade_limit'],50)
  with self.assertRaisesRegex(ProviderError,'snapshot_unrequested'):s.feed(raw(trades(kind='snapshot')),4)
  s=active(snapshot=True)
  with self.assertRaisesRegex(ProviderError,'budget'):s.feed(raw(trades(*(trade(i)for i in range(51)),kind='snapshot')),3)
  s=active()
  with self.assertRaisesRegex(ProviderError,'snapshot_unrequested'):s.feed(raw(trades(trade(),kind='snapshot')),3)
 def test_update_local_budget_and_retained_identity_window(self):
  s=active()
  for batch in range(3):s.feed(raw(trades(*(trade(batch*100+i)for i in range(100)))),3+batch)
  self.assertEqual(len(s.trades),256);self.assertEqual(len(s.identities),256);self.assertNotIn('0',s.identities);self.assertIn('299',s.identities)
  r=s.feed(raw(trades(trade(0))),6);self.assertEqual(r['trades'][0]['trade_id'],'0');self.assertEqual(r['deduplication_window'],'256')
  s=active()
  with self.assertRaisesRegex(ProviderError,'budget'):s.feed(raw(trades(*(trade(i)for i in range(101)))),3)
 def test_duplicates_are_idempotent_and_conflicts_never_replace_retained_source(self):
  s=active();first=s.feed(raw(trades(trade())),3);r=s.feed(raw(trades(trade())),4);self.assertEqual(r['trades'],[]);self.assertEqual(r['duplicate_trade_ids'],['1']);self.assertEqual(list(s.trades),first['trades']);before=copy.deepcopy(list(s.trades))
  with self.assertRaisesRegex(ProviderError,'conflicting'):s.feed(raw(trades(trade(side='sell'))),5)
  self.assertEqual(list(s.trades),before)
 def test_duplicate_or_malformed_late_member_is_failure_atomic(self):
  for values in((trade(),trade()),(trade(),trade(2,symbol='ETH/USD')),(trade(),trade(2,ord_type='stop')),(trade(),{'trade_id':2})):
   s=active();s.feed(raw(trades(trade(99))),3);before=copy.deepcopy((list(s.trades),s.identities,s.last_receive_ns))
   with self.subTest(values=values),self.assertRaises(ProviderError):s.feed(raw(trades(*values)),4)
   self.assertEqual((list(s.trades),s.identities,s.last_receive_ns),before);self.assertTrue(s.reconnect_required)
 def test_clock_regression_types_and_out_of_range_fail_before_mutation(self):
  for clock in(1,-1,True,UINT64_MAX+1):
   s=active()
   with self.subTest(clock=clock),self.assertRaises(ProviderError):s.feed(raw(trades(trade())),clock)
   self.assertEqual(s.last_receive_ns,2);self.assertFalse(s.trades)
 def test_status_all_documented_states_and_reconnect_fence(self):
  for system in('online','cancel_only','maintenance','post_only'):
   s=active();s.feed(raw(trades(trade())),3);r=s.feed(raw(status(system)),4);self.assertEqual(r['system'],system);self.assertEqual(r['book_reset_required'],system!='online');self.assertEqual(s.reconnect_required,system!='online')
   if system!='online':
    s.feed(raw(status()),5)
    with self.assertRaises(ProviderError):s.feed(raw(trades(trade(2))),6)
 def test_connection_change_cannot_carry_trade_identity_or_restart_without_generation(self):
  s=active();s.feed(raw(trades(trade())),3)
  with self.assertRaisesRegex(ProviderError,'connection_changed'):s.feed(raw(status(connection_id=43)),4)
  self.assertEqual(s.connection_id,'42');s.disconnected();self.assertFalse(s.trades);self.assertFalse(s.identities);s.connect();s.feed(raw(status(connection_id=43)),1);s.feed(raw(ack(s)),2);r=s.feed(raw(trades(trade())),3);self.assertEqual(r['local_generation'],'2');self.assertEqual(len(r['trades']),1)
 def test_maintenance_and_emergency_complete_metadata_remains_in_receipt(self):
  s=active();p=status(upcoming_maintenance=[window()],emergency=[incident()]);r=s.feed(raw(p),3)
  self.assertEqual(r['upcoming_maintenance'][0]['event_id'],'1');self.assertEqual(r['upcoming_maintenance'][0]['expected_start_ns'],instant(STAMP));self.assertIsNone(r['upcoming_maintenance'][0]['expected_end_ns']);self.assertEqual(r['emergency'][0]['next_steps'][0]['expected_at_ns'],instant(STAMP));self.assertEqual(r['emergency'][0]['impact'],'minor');self.assertFalse(s.reconnect_required)
 def test_additive_status_arrays_are_paired_and_strict(self):
  for changes in({'upcoming_maintenance':[]},{'emergency':[]},{'upcoming_maintenance':None,'emergency':[]},{'upcoming_maintenance':[],'emergency':{}},{'unexpected':1}):
   s=active()
   with self.subTest(changes=changes),self.assertRaises(ProviderError):s.feed(raw(status(**changes)),3)
  s=active();r=s.feed(raw(status(upcoming_maintenance=[],emergency=[])),3);self.assertEqual(r['upcoming_maintenance'],[]);self.assertEqual(r['emergency'],[])
 def test_maintenance_fields_enums_bounds_times_and_urls_reject_atomically(self):
  bad=[window(phase='done'),window(event_id=True),window(time_to_start_s=-1),window(recommended_action='trade'),window(affected_services=['orders']),window(affected_services=['spot_ws','spot_ws']),window(expected_end_utc='2024-01-01T00:00:00Z'),window(source_url='https://user:secret@example.invalid'),window(source_url='https://['),window(source_url='https://example.invalid:invalid'),window(source_url='https://example.invalid:0'),window(expected_start_utc='2024-02-01T13:00:00+01:00'),window(title='x'*257)]
  for v in bad:
   s=active();before=(s.connection_id,s.system,s.last_receive_ns)
   with self.subTest(v=v),self.assertRaises(ProviderError):s.feed(raw(status(upcoming_maintenance=[v],emergency=[])),3)
   self.assertEqual((s.connection_id,s.system,s.last_receive_ns),before)
  s=active()
  with self.assertRaisesRegex(ProviderError,'duplicate_event'):s.feed(raw(status(upcoming_maintenance=[window(),window()],emergency=[])),3)
 def test_emergency_next_steps_fields_enums_and_resource_limits(self):
  for changes in({'incident_status':'resolved'},{'impact':'high'},{'next_steps':[{'applies_to':['spot_ws'],'type':'guess','expected_at_utc':STAMP}]},{'next_steps':[{}]},{'next_steps':[incident()['next_steps'][0]]*17}):
   s=active()
   with self.subTest(changes=changes),self.assertRaises(ProviderError):s.feed(raw(status(upcoming_maintenance=[],emergency=[incident(**changes)])),3)
  s=active()
  with self.assertRaisesRegex(ProviderError,'budget'):s.feed(raw(status(upcoming_maintenance=[window(event_id=i)for i in range(17)],emergency=[])),3)
 def test_duplicate_json_nonfinite_invalid_utf8_and_unsupported_messages_fail_closed(self):
  for p in('{"channel":"status","channel":"trade"}','{"x":NaN}','[]','null','{"channel":"heartbeat"}','{"channel":"book"}','{}','\ud800','x'*65537):
   s=active()
   with self.subTest(p=p[:40]),self.assertRaises(ProviderError):s.feed(p,3)
   self.assertTrue(s.reconnect_required)
 def test_direct_payload_boundary_rejects_unbound_receipt_identity(self):
  for p,digest in(([], 'a'*64),({}, 'invalid'),({},None)):
   s=active()
   with self.subTest(p=p,digest=digest),self.assertRaises(ProviderError):s.accept_payload(p,3,digest)
   self.assertTrue(s.reconnect_required)
 def test_direct_payload_depth_nodes_bytes_and_scalars_are_bounded(self):
  deep={};current=deep
  for _ in range(14):current['nested']={};current=current['nested']
  for payload in(deep,{'huge':'x'*65537},{'huge':[None]*101},{'value':Decimal('NaN')},{'value':1<<129},{'value':object()}):
   s=active()
   with self.subTest(payload=str(payload)[:80]),self.assertRaises(ProviderError):s.accept_payload(payload,3,'a'*64)
   self.assertEqual(s.last_receive_ns,2);self.assertTrue(s.reconnect_required)
 def test_raw_and_decoded_digest_authorities_are_not_conflated(self):
  s=active();r=s.feed(raw(trades(trade())),3);self.assertEqual(r['source_hash_basis'],'HASHED_RAW_FRAME')
  s=active();r=s.accept_payload(trades(trade()),3,'a'*64);self.assertEqual(r['source_hash_basis'],'CALLER_SUPPLIED_DIGEST');self.assertFalse(r['independent_source_authentication'])
 def test_returned_receipt_cannot_mutate_retained_identity_window(self):
  s=active();r=s.feed(raw(trades(trade())),3);r['trades'][0]['trade_id']='tampered';r['trades'][0]['price_ticks']='0'
  self.assertEqual(s.trades[0]['trade_id'],'1');self.assertEqual(s.trades[0]['price_ticks'],'1000');r=s.feed(raw(trades(trade())),4);self.assertEqual(r['duplicate_trade_ids'],['1'])
 def test_unknown_status_and_version_do_not_silently_relabel_source(self):
  for change in({'system':'offline'},{'api_version':'v3'},{'connection_id':1.5},{'connection_id':True},{'version':[]},{'version':'x'*129}):
   s=active();p=status();p['data'][0].update(change)
   with self.subTest(change=change),self.assertRaises(ProviderError):s.feed(raw(p),3)
   self.assertEqual(s.connection_id,'42')

if __name__=='__main__':unittest.main()
