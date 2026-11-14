"""Authored repeated-price updates, reconciled against official book guidance."""
import json,unittest
from .test_kraken import book
from .kraken import KrakenBookAdapter,ProviderError

def update(levels,final):
 checksum=json.loads(book(final))['data'][0]['checksum']
 return book(levels,[],kind='update',checksum=checksum)
class OrderedUpdates(unittest.TestCase):
 def adapter(self,**kwargs):
  calls=[];a=KrakenBookAdapter(lambda **kw:calls.append(kw),**kwargs);a.feed(book(),1);return a,calls
 def test_repeated_prices_are_processed_in_wire_order_and_commit_once(self):
  a,calls=self.adapter(ordered_updates=True);a.feed(update([('100','4'),('100.00','5')],[('100.00','5')]),2)
  self.assertEqual(a.bids['10000'][1],'5');self.assertEqual(len(calls),2);self.assertEqual(calls[-1]['bids'],[{'price_ticks':'10000','quantity':'500000000'}])
 def test_delete_then_reinsert_is_distinct_from_reinsert_then_delete(self):
  a,_=self.adapter(ordered_updates=True);a.feed(update([('100','0'),('100','7')],[('100','7')]),2);self.assertEqual(a.bids['10000'][1],'7')
  b,_=self.adapter(ordered_updates=True);b.feed(update([('100','7'),('100','0')],[]),2);self.assertEqual(b.bids,{})
 def test_legacy_default_and_duplicate_snapshot_still_reject(self):
  a,calls=self.adapter()
  with self.assertRaisesRegex(ProviderError,'duplicate_level'):a.feed(update([('100','4'),('100','5')],[('100','5')]),2)
  b,bcalls=self.adapter(ordered_updates=True)
  with self.assertRaisesRegex(ProviderError,'duplicate_level'):b.feed(book([('100','2'),('100.00','2')]),2)
  self.assertEqual(len(calls),1);self.assertEqual(len(bcalls),1)
 def test_bad_final_checksum_rolls_back_every_intermediate_change(self):
  a,calls=self.adapter(ordered_updates=True);before=a.bids.copy();raw=json.loads(update([('100','0'),('100','7')],[('100','7')]));raw['data'][0]['checksum']^=1
  with self.assertRaisesRegex(ProviderError,'checksum_mismatch'):a.feed(json.dumps(raw),2)
  self.assertEqual(a.bids,before);self.assertEqual(len(calls),1)
 def test_profile_flag_is_strict_boolean(self):
  for value in(1,None,'true'):
   with self.assertRaisesRegex(ProviderError,'configuration'):KrakenBookAdapter(lambda **_:None,ordered_updates=value)
