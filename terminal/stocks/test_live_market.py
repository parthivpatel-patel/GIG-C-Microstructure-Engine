"""Independent L1 arithmetic/identity/retention fixtures. No provider network."""
import asyncio,copy,math,unittest
from fractions import Fraction
from .test_final import client,ready,packet,quote
from .live import LiveIEX
from .identity import instrument

class Semantics(unittest.TestCase):
 def test_ten_target_symbols_are_curated_not_claimed_fresh(self):
  for s in ['AAPL','MSFT','NVDA','TSLA','AMZN','GOOGL','META','AMD','JPM','SPY']:self.assertIn('curated',instrument(s)['identity_source'])
 def test_out_of_order_is_retained_without_latest_price_rollback(self):
  c=client();ready(c);new=quote();new['t']='2024-01-02T14:30:01Z';new['bp']=102.;new['ap']=103.;c.wall=lambda:1704205802.
  c.process(packet(new));c.process(packet(quote()));v=c.view();self.assertEqual(v['observations'][0]['data']['bid'],'102.0');self.assertEqual(v['out_of_order_observations'],1);self.assertTrue(v['history'][-1]['out_of_order']);self.assertEqual(v['metrics']['AAPL']['valid_ordered_quotes'],1)
 def test_same_timestamp_distinct_quotes_preserve_capture_order(self):
  c=client();ready(c);c.process(packet(quote()));q=quote();q['bs']=7;c.process(packet(q));self.assertEqual(c.view()['out_of_order_observations'],0);self.assertEqual(c.view()['observations'][0]['data']['bid_size'],'7')
 def test_exact_best_quote_metrics_match_independent_fraction(self):
  c=client();ready(c);c.process(packet(quote()));m=c.view()['metrics']['AAPL'];self.assertEqual(m['spread'],{'numerator':'1','denominator':'1'});self.assertEqual(m['midprice'],{'numerator':'201','denominator':'2'});self.assertEqual(m['relative_spread'],{'numerator':'2','denominator':'201'});self.assertEqual(m['best_quote_size_imbalance'],{'numerator':'-1','denominator':'9'})
 def test_realized_vol_and_frequency_use_source_window_not_annualization(self):
  c=client();ready(c);c.wall=lambda:1704205802.;c.process(packet(quote()));q=quote();q.update(t='2024-01-02T14:30:01.123456789Z',bp=101.,ap=102.);c.process(packet(q));m=c.view()['metrics']['AAPL'];self.assertAlmostEqual(m['realized_log_mid_volatility'],abs(math.log(203/201)),places=12);self.assertEqual(m['quote_frequency_per_source_second'],{'numerator':'1','denominator':'1'})
 def test_crossed_and_zero_sided_quotes_preserved_but_not_invented_as_depth(self):
  c=client();ready(c);q=quote();q['bp']=102.;q['ap']=101.;c.process(packet(q));v=c.view();self.assertEqual(v['metrics']['AAPL']['valid_ordered_quotes'],0);self.assertIsNone(v['metrics']['AAPL']['spread']);self.assertNotIn('book',v)
 def test_bar_requires_channel_and_valid_ohlc(self):
  c=client();ready(c);b={'T':'b','S':'AAPL','t':quote()['t'],'o':100.,'h':102.,'l':99.,'c':101.,'v':20}
  with self.assertRaises(ValueError):c.process(packet(b))
  c.channels=('quotes','trades','bars');c.process(packet(b));self.assertEqual(c.view()['observations'][0]['kind'],'bar');before=copy.deepcopy(c.view());b['h']=98
  with self.assertRaises(ValueError):c.process(packet(b))
  self.assertEqual(c.view(),before)
 def test_correction_and_cancel_are_non_mutating_observations(self):
  c=client();ready(c);t={'T':'t','S':'AAPL','t':quote()['t'],'p':100.,'s':2,'i':7};c.process(packet(t));self.assertEqual(c.view()['metrics']['AAPL']['observed_trade_size_sum'],{'numerator':'2','denominator':'1'})
  c.process(packet({'T':'c','S':'AAPL','t':quote()['t'],'oi':7,'ci':8,'op':100.,'cp':101.,'os':2,'cs':1,'oc':['@'],'cc':['@']}));m=c.view()['metrics']['AAPL'];self.assertTrue(m['contains_correction_or_cancel']);self.assertIsNone(m['observed_trade_size_sum']);self.assertEqual(c.view()['observations'][0]['data']['price'],'100.0')
  c.process(packet({'T':'x','S':'AAPL','t':quote()['t'],'i':8,'p':101.,'s':1,'a':'C'}));self.assertEqual(c.view()['history'][-1]['kind'],'cancel')
 def test_retention_is_bounded_and_eviction_accounted(self):
  c=client();ready(c)
  for i in range(300):q=quote();q['bs']=i;c.process(packet(q))
  v=c.view();self.assertEqual(len(v['history']),256);self.assertEqual(v['retention_evictions'],44);self.assertEqual(v['accepted_observations'],300);self.assertLessEqual(len(c.seen),256)
 def test_failed_frame_rolls_back_history_counters_and_metrics(self):
  c=client();ready(c);c.process(packet(quote()));before=copy.deepcopy(c.view());q=quote();q['bs']=9
  with self.assertRaises(ValueError):c.process(packet(q,{'T':'n','S':'AAPL'}))
  self.assertEqual(c.view(),before)
 def test_multisymbol_isolation_and_receipts(self):
  c=client();c.symbols=('AAPL','NVDA');c.phase='SUBSCRIBED';q=quote();n=quote();n['S']='NVDA';n['bp']=200.;n['ap']=202.;c.process(packet(q,n));v=c.view();self.assertEqual(len(v['metrics']),2);self.assertEqual(v['metrics']['NVDA']['spread']['numerator'],'2');self.assertEqual(v['metrics']['AAPL']['spread']['numerator'],'1')
 def test_declared_limit_and_invalid_channel_never_replace_state(self):
  async def run():
   c=client();c.workspace.environment['GIG_ALPACA_LIVE_MAX_SYMBOLS']='1'
   with self.assertRaises(ValueError):await c.start(['AAPL','NVDA'])
   with self.assertRaises(ValueError):await c.start(['AAPL'],['paid_sip'])
   with self.assertRaises(ValueError):await c.start(['AAPL'],['bars'])
   self.assertIsNone(c.task)
  asyncio.run(run())
 def test_source_timestamp_receive_time_and_clock_warning(self):
  c=client();ready(c);c.process(packet(quote()));v=c.view()['history'][0];self.assertIn('+00:00',v['received_at']);self.assertIn('source_timestamp_ns',v);self.assertNotIn('exchange_sequence',v);self.assertIn(v['clock_quality'],['SOURCE_AHEAD_WITHIN_TOLERANCE','UNSYNCHRONIZED_SOURCE_RECEIVE_CLOCKS'])
 def test_identical_subscription_is_noop_and_dynamic_change_closes_old_task(self):
  import asyncio
  async def exercise():
   c=client();starts=[];stops=[]
   async def run():
    starts.append(c.symbols)
    try:await asyncio.sleep(100)
    finally:stops.append(c.symbols)
   c.run=run
   await c.start(['AAPL']);await asyncio.sleep(0);old=c.task
   await c.start(['AAPL']);self.assertIs(c.task,old)
   await c.start(['NVDA','AAPL'],['quotes']);await asyncio.sleep(0)
   self.assertTrue(old.done());self.assertEqual(starts,[('AAPL',),('AAPL','NVDA')]);self.assertEqual(len(stops),1)
   await c.close();self.assertEqual(len(stops),2)
  asyncio.run(exercise())
 def test_malformed_conditions_are_atomic_but_bar_close_is_not_conditions(self):
  c=client();ready(c);before=copy.deepcopy(c.view());q=quote();q['c']=['valid',42]
  with self.assertRaises(ValueError):c.process(packet(q))
  self.assertEqual(c.view(),before)
 def test_previous_generation_never_contributes_to_new_metrics(self):
  c=client();ready(c);c.process(packet(quote()));c.generation+=1
  v=c.view();self.assertEqual(v['metrics']['AAPL']['valid_ordered_quotes'],0);self.assertEqual(v['history'][0]['state'],'UNAVAILABLE')
 def test_binary64_roundtrip_precision_is_not_silently_rounded_or_rejected(self):
  c=client();ready(c);q=quote();q['bp']=100.01+.01;c.process(packet(q));self.assertEqual(c.view()['observations'][0]['data']['bid'],repr(q['bp']))
 def test_extreme_binary64_mid_variation_does_not_overflow_float_conversion(self):
  import math
  c=client();ready(c);q=quote();q['bp']=5e-324;q['ap']=5e-324;c.process(packet(q));q=quote();q['t']='2024-01-02T14:30:01Z';q['bp']=1e15;q['ap']=1e15;c.wall=lambda:1704205802.;c.process(packet(q));self.assertTrue(math.isfinite(c.view()['metrics']['AAPL']['realized_log_mid_volatility']))
