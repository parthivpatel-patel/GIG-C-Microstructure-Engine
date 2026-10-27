"""Independent projection reconstruction oracle;authored records,not provider observations."""
import copy,json,unittest
from terminal.server.market_delta import MarketProjection
class Projection(unittest.TestCase):
 def test_thousand_windows_equal_independent_full_reference_including_staleness(self):
  projection=MarketProjection();cache={};seq=0;prior_receipt=0
  for i in range(1000):
   rows=[{'receipt_index':n,'state':'STALE' if i%7==0 else 'SIMULATED','receive_age_seconds':float(i-n),'data':{'bid':str(n)},'generation':1} for n in range(max(1,i-255),i+1)]
   full={'generation':1,'symbols':['AAPL'],'channels':['quotes'],'accepted_observations':i,'history':rows,'phase':'SUBSCRIBED'};before=copy.deepcopy(full);wire=projection.project(full);d=wire.pop('browser_delta');self.assertEqual(full,before);self.assertEqual(d['sequence'],seq+1);self.assertEqual(d['base_sequence'],seq);self.assertEqual(d['base_receipt'],prior_receipt)
   if d['mode']=='full':cache={}
   for row in wire['history']:cache[row['receipt_index']]=row
   restored=[]
   for n,state,age in d['history_status']:restored.append({**cache[n],'state':state,'receive_age_seconds':age})
   self.assertEqual(restored,rows);cache={r['receipt_index']:r for r in restored};seq=d['sequence'];prior_receipt=i
 def test_configuration_changes_and_reconnect_start_full_without_touching_source(self):
  value={'generation':1,'symbols':['AAPL'],'channels':['quotes'],'accepted_observations':0,'history':[]};p=MarketProjection();self.assertEqual(p.project(value)['browser_delta']['mode'],'full');self.assertEqual(p.project(value)['browser_delta']['mode'],'delta');value['symbols']=['NVDA'];self.assertEqual(p.project(value)['browser_delta']['mode'],'full');self.assertEqual(MarketProjection().project(value)['browser_delta']['sequence'],1)
 def test_steady_window_projection_reduces_payload(self):
  rows=[{'receipt_index':i,'state':'SIMULATED','receive_age_seconds':0,'data':{'metadata':'x'*600}} for i in range(1,257)];s={'generation':1,'symbols':['AAPL'],'channels':['quotes'],'accepted_observations':256,'history':rows};p=MarketProjection();p.project(s);wire=p.project(s);self.assertFalse(wire['history']);self.assertLess(len(json.dumps(wire)),len(json.dumps(s))//4)
