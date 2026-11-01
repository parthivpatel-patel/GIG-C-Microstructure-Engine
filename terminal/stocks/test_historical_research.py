import copy,hashlib,json,math,unittest
from fractions import Fraction
from decimal import Decimal
from terminal.alpaca_wire import WireError
from .historical_research import analyze,compare
from .historical_v2 import ns

def core(prices=(100,110,99,108,120,100),symbol='AAPL'):
 rows=[]
 for i,p in enumerate(prices):
  t=f'2024-01-02T14:{30+i:02d}:00Z';rows.append(dict(timestamp=t,source_timestamp_ns=str(ns(t)),close=str(p),volume='10',vwap=str(p)))
 return dict(schema='gig.alpaca.history.v2',kind='bars',records=rows,canonical_sha256='a'*64,symbol=symbol,origin='HISTORICAL_SYNTHETIC',feed='iex',query=dict(start='2024-01-02T14:30:00Z',end='2024-01-02T15:30:00Z',timeframe='1Min'),adjustment='raw',session={'state':'UNKNOWN'},source_records=[],received_at='2024-01-03T00:00:00Z')
def f(v):return Fraction(int(v['numerator']),int(v['denominator']))
class Research(unittest.TestCase):
 def test_exact_returns_sma_drawdown(self):
  v=analyze(core(),window=2);self.assertEqual(f(v['series'][1]['simple_return']),Fraction(1,10));self.assertEqual(f(v['series'][2]['simple_return']),Fraction(-1,10));self.assertEqual(f(v['series'][1]['trailing_sma']),105)
  self.assertEqual(f(v['summary']['maximum_close_drawdown']),Fraction(1,6));self.assertEqual(f(v['summary']['interval_close_return']),0)
 def test_independent_log_variation(self):
  prices=[100,110,99];v=analyze(core(prices),window=2);expected=math.sqrt(float(Decimal('1.1').ln())**2+float(Decimal('0.9').ln())**2)
  self.assertAlmostEqual(v['summary']['realized_log_variation'],expected,places=14);self.assertAlmostEqual(v['series'][-1]['rolling_log_variation'],expected,places=14)
 def test_volume_turnover_uses_supplied_vwap(self):
  c=core([100,110]);v=analyze(c,window=2);self.assertEqual(f(v['summary']['volume']),20);self.assertEqual(f(v['summary']['notional_turnover']),2100);self.assertEqual(f(v['summary']['supplied_bar_vwap']),105)
  c['records'][0]['vwap']=None;self.assertIsNone(analyze(c,window=2)['summary']['notional_turnover'])
 def test_prefix_no_lookahead(self):
  c=core();a=analyze(c,window=2);c['records'][-1]['close']='500';b=analyze(c,window=2);self.assertEqual(a['series'][:-1],b['series'][:-1])
 def test_insufficient_no_zero_imputation(self):
  for values in ([],[100]):
   v=analyze(core(values),window=2);self.assertEqual(v['state'],'INSUFFICIENT_OBSERVATIONS');self.assertIsNone(v['summary']['realized_log_variation'])
  self.assertIsNone(analyze(core(),window=64)['series'][-1]['trailing_sma'])
 def test_gaps_explicit_break(self):
  c=core([100,110,120]);c['records'][-1]['timestamp']='2024-01-02T16:00:00Z';c['records'][-1]['source_timestamp_ns']=str(ns(c['records'][-1]['timestamp']))
  v=analyze(c,window=2,gap_policy='break',max_gap_seconds=120);self.assertEqual(len(v['gap_candidates']),1);self.assertIsNone(v['series'][-1]['simple_return']);self.assertIsNone(v['series'][-1]['rolling_log_variation'])
 def test_comparison_uses_identical_endpoints(self):
  a=core([100,110,120]);b=core([200,220,240],symbol='MSFT');del b['records'][1];v=compare([analyze(a,window=2),analyze(b,window=2)])
  self.assertEqual(len(v['timestamps_ns']),2);self.assertEqual(f(v['series'][0]['percentage_change'][-1]),20);self.assertEqual(v['series'][0]['percentage_change'],v['series'][1]['percentage_change'])
 def test_comparison_scope_not_mixed(self):
  a=analyze(core(),window=2);b=analyze(core(symbol='MSFT'),window=2)
  for key,value in [('origin','OBSERVED_OFFICIAL_RESPONSE'),('feed','sip'),('adjustment','split')]:
   with self.assertRaises(WireError):compare([a,{**b,key:value}])
  with self.assertRaises(WireError):compare([a,a])
 def test_parameter_and_source_errors(self):
  for params in ({'window':1},{'window':True},{'window':65},{'gap_policy':'guess'},{'gap_policy':'break'},{'max_gap_seconds':0}):
   with self.assertRaises(WireError):analyze(core(),**params)
  with self.assertRaises(WireError):analyze({**core(),'kind':'quotes'})
 def test_zero_invalid_price_and_time(self):
  for key,value in [('close','0'),('source_timestamp_ns','0'),('volume','-1')]:
   c=core();c['records'][0][key]=value
   with self.assertRaises(WireError):analyze(c)
 def test_deterministic_hash(self):
  a=analyze(core(),window=2);b=analyze(core(),window=2);self.assertEqual(a,b);h=a.pop('canonical_sha256');self.assertEqual(hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest(),h)
if __name__=='__main__':unittest.main()
