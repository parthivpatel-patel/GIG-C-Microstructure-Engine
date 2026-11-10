"""Independently authored normalized receipts and integer-map oracle;no provider IO."""
import copy,hashlib,json,random,unittest
from fractions import Fraction
from unittest.mock import patch
from .trade_tape import reconcile

def event(n,kind='trade',symbol='AAPL',generation=1,**data):
 payload={'price':'100','size':'2'}if kind=='trade'else{}
 payload.update({k:str(v)for k,v in data.items()})
 row={'source_session_id':'c'*32,'provider':'alpaca','feed':'iex','symbol':symbol,'generation':generation,'receipt_index':n,'kind':kind,'origin':'HISTORICAL_SYNTHETIC','exchange_codes':{'x':'V'},'tape_code':'C','source_timestamp_ns':str(100+n),'trade_id':str(n)if kind=='trade'else None,'data':payload,'conditions':{}}
 row['identity_sha256']=hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest();row['source_sha256']='a'*64;return row

def correction(n,old,new,op=100,os=2,cp=101,cs=1):return event(n,'correction',original_id=old,corrected_id=new,original_price=op,original_size=os,corrected_price=cp,corrected_size=cs)

def check(result,expected):
 assert result['state']=='CONSISTENT_RETAINED_WINDOW',result
 got={int(r['trade_id']):(Fraction(r['price']),Fraction(r['size']))for r in result['trades']}
 assert got==expected,(got,expected)
 v=result['corrected_size_sum'];assert Fraction(int(v['numerator']),int(v['denominator']))==sum((r[1]for r in expected.values()),Fraction())

class TradeTape(unittest.TestCase):
 def test_chain_and_same_identity_corrections_keep_original_source_order(self):
  rows=[event(1),event(2),correction(3,1,8),correction(4,8,8,101,1,102,3)]
  r=reconcile(rows,'AAPL',1);check(r,{8:(102,3),2:(100,2)})
  self.assertEqual([x['trade_id']for x in r['trades']],['8','2']);self.assertEqual(r['trades'][0]['source_timestamp_ns'],'101');self.assertEqual(r['trades'][0]['lineage_receipts'],[1,3,4]);self.assertFalse(r['complete_tape']);self.assertEqual(r['order_book_mutations'],0)
 def test_explicit_authored_cancel_and_no_automatic_observed_action_interpretation(self):
  rows=[event(1),event(2,'cancel',trade_id=1,price=100,size=2,action='C')]
  r=reconcile(rows,'AAPL',1,cancellation_contract='AUTHORED_CANCEL_C_V1');check(r,{});self.assertEqual(r['applied_cancels'],1)
  for profile in [None,'AUTHORED_CANCEL_C_V1']:
   observed=copy.deepcopy(rows)
   for x in observed:x['origin']='OBSERVED_OFFICIAL_RESPONSE'
   r=reconcile(observed,'AAPL',1,cancellation_contract=profile);self.assertEqual(r['error']['code'],'UNSUPPORTED_CANCEL_PROFILE');self.assertIsNone(r['corrected_size_sum'])
 def test_unknown_original_collisions_mismatches_and_retired_ids_fail_closed(self):
  candidates=[[correction(1,9,10)],[event(1),correction(2,1,8,op=99)],[event(1),event(2),correction(3,1,2)],[event(1),correction(2,1,8),correction(3,1,9)]]
  for rows in candidates:
   before=copy.deepcopy(rows);r=reconcile(rows,'AAPL',1);self.assertEqual(r['state'],'UNRESOLVED');self.assertIsNone(r['corrected_size_sum']);self.assertEqual(rows,before)
 def test_duplicate_source_is_accounted_and_conflicting_identity_is_rejected(self):
  first=event(1);dup=copy.deepcopy(first);dup['receipt_index']=2
  r=reconcile([first,dup],'AAPL',1);check(r,{1:(100,2)});self.assertEqual(r['duplicate_records'],1)
  dup['data']['price']='101';r=reconcile([first,dup],'AAPL',1);self.assertEqual(r['error']['code'],'IDENTITY_CONFLICT')
 def test_capture_order_not_clock_sort_and_generation_symbol_scope_isolation(self):
  a=event(1);b=correction(3,1,8);b['source_timestamp_ns']='1'
  rows=[a,event(2,symbol='MSFT'),b,event(4,generation=2)]
  check(reconcile(rows,'AAPL',1),{8:(101,1)});check(reconcile(rows,'MSFT',1),{2:(100,2)});check(reconcile(rows,'AAPL',2),{4:(100,2)})
  r=reconcile([event(2),event(1)],'AAPL',1);self.assertEqual(r['error']['code'],'CAPTURE_ORDER')
 def test_missing_scope_provenance_mixed_origin_and_invalid_numbers_cannot_publish_totals(self):
  for mutate in [lambda r:r.update(tape_code=None),lambda r:r.update(source_sha256='bad'),lambda r:r['data'].update(price='NaN'),lambda r:r.update(exchange_codes={})]:
   r=event(1);mutate(r);v=reconcile([r],'AAPL',1);self.assertEqual(v['state'],'UNRESOLVED');self.assertIsNone(v['corrected_size_sum'])
  rows=[event(1),event(2)];rows[1]['origin']='OBSERVED_OFFICIAL_RESPONSE';self.assertEqual(reconcile(rows,'AAPL',1)['error']['code'],'ORIGIN')
 def test_resource_limits_empty_and_replay_determinism(self):
  with self.assertRaises(ValueError):reconcile([event(1)]*257,'AAPL',1)
  self.assertEqual(reconcile([],'AAPL',1)['state'],'NO_TRADE_INPUT')
  rows=[event(1),correction(2,1,3)];self.assertEqual(reconcile(rows,'AAPL',1),reconcile(copy.deepcopy(rows),'AAPL',1))
 def test_unsupported_cancel_and_condition_conflict_stay_explicit(self):
  rows=[event(1),event(2,'cancel',trade_id=1,price=100,size=2,action='E')]
  self.assertEqual(reconcile(rows,'AAPL',1,cancellation_contract='AUTHORED_CANCEL_C_V1')['error']['code'],'UNSUPPORTED_CANCEL_PROFILE')
  rows=[event(1),correction(2,1,8)];rows[1]['conditions']={'oc':['X']};self.assertEqual(reconcile(rows,'AAPL',1)['error']['code'],'ORIGINAL_CONDITIONS')
 def test_allocation_failure_does_not_modify_inputs(self):
  rows=[event(1)];before=copy.deepcopy(rows)
  with patch('terminal.stocks.trade_tape._wire',side_effect=MemoryError),self.assertRaises(MemoryError):reconcile(rows,'AAPL',1)
  self.assertEqual(rows,before)
 def test_independent_integer_oracle_1000_candidates_and_corruption_negative_control(self):
  rng=random.Random(88241)
  for _ in range(1000):
   rows=[];expected={}
   for i in range(1,rng.randrange(2,7)):
    p,q=rng.randrange(1,10000),rng.randrange(1,100);rows.append(event(i,price=p,size=q));expected[i]=(p,q)
   old=rng.choice(list(expected));p,q=expected.pop(old);new=100;np,nq=rng.randrange(1,10000),rng.randrange(1,100);rows.append(correction(len(rows)+1,old,new,p,q,np,nq));expected[new]=(np,nq)
   if rng.randrange(2):rows.append(event(len(rows)+1,'cancel',trade_id=new,price=np,size=nq,action='C'));del expected[new]
   r=reconcile(rows,'AAPL',1,cancellation_contract='AUTHORED_CANCEL_C_V1');check(r,expected)
   bad=copy.deepcopy(r);bad['corrected_size_sum']['numerator']=str(int(bad['corrected_size_sum']['numerator'])+1)
   with self.assertRaises(AssertionError):check(bad,expected)
 def test_causal_prefix_results_do_not_include_future_corrections(self):
  rows=[event(1,price=100,size=2),event(2,price=101,size=3),correction(3,1,8,100,2,105,7)]
  check(reconcile(rows[:1],'AAPL',1),{1:(100,2)});check(reconcile(rows[:2],'AAPL',1),{1:(100,2),2:(101,3)});check(reconcile(rows,'AAPL',1),{8:(105,7),2:(101,3)})
  rows[2]['data']['corrected_size']='9';check(reconcile(rows[:2],'AAPL',1),{1:(100,2),2:(101,3)})
 def test_foreign_feed_and_boolean_generation_cannot_enter_reconciliation(self):
  for patch_value in [{'provider':'other'},{'feed':'sip'},{'generation':True},{'symbol':'../bad'}]:
   row=event(1);row.update(patch_value);r=reconcile([row],'AAPL',1);self.assertEqual(r['state'],'UNRESOLVED');self.assertIsNone(r['corrected_size_sum'])

 def test_distinct_captures_with_same_generation_and_monotonic_receipts_cannot_mix(self):
  rows=[event(1),correction(2,1,8)];rows[1]['source_session_id']='d'*32
  r=reconcile(rows,'AAPL',1);self.assertEqual(r['state'],'UNRESOLVED');self.assertEqual(r['error']['code'],'SOURCE_SESSION');self.assertIsNone(r['corrected_size_sum'])
