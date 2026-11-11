"""Offline source precision and single-owner transport regressions."""
import asyncio,json,unittest
from decimal import Decimal
from unittest.mock import patch
from .kraken import KrakenBookAdapter,decimal_wire,ProviderError
from .supervisor import FeedSupervisor
from .test_kraken import crc_reference
from .test_supervisor import ENV
class Precision(unittest.TestCase):
 def test_json_scientific_numeric_quantity_preserves_exact_lots_and_crc(self):
  calls=[];adapter=KrakenBookAdapter(lambda **event:calls.append(event))
  crc=crc_reference('101'+'3'+'100'+'1')
  raw='{"channel":"book","type":"snapshot","data":[{"symbol":"BTC/USD","bids":[{"price":100,"qty":1e-8}],"asks":[{"price":101,"qty":3}],"checksum":'+str(crc)+'}]}'
  receipt=adapter.feed(raw,1);self.assertEqual(receipt['kind'],'snapshot');self.assertEqual(calls[0]['bids'][0],{'price_ticks':'10000','quantity':'1'})
 def test_decimal_context_does_not_round_or_expand_unbounded_exponents(self):
  from decimal import localcontext
  with localcontext()as context:
   context.prec=2;self.assertEqual(decimal_wire(Decimal('1.23456789e-2'),maximum=2**64-1,scale=10**10),('123456789','0.0123456789'))
  for value in [Decimal('1e999999'),Decimal('1e-999999'),Decimal('NaN'),Decimal('Infinity')]:
   with self.assertRaises(ProviderError):decimal_wire(value,maximum=2**64-1,scale=10**8)

class WorkerRecovery(unittest.IsolatedAsyncioTestCase):
 async def test_concurrent_commands_preserve_one_physical_worker(self):
  feed=FeedSupervisor(environment=ENV,transport=lambda *_:None);active=set();tasks=[];peak=[0]
  async def worker(epoch):
   task=asyncio.current_task();tasks.append(task);active.add(task);peak[0]=max(peak[0],len(active))
   try:await asyncio.Event().wait()
   finally:active.discard(task)
  with patch.object(feed,'_run',new=worker):
   try:
    await feed.start();await asyncio.sleep(0);await asyncio.gather(feed.start('ETH/USD'),feed.start('BTC/USD'));await asyncio.sleep(0);self.assertEqual(peak[0],1);self.assertEqual(len(active),1)
   finally:
    await feed.close()
    for task in tasks:task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
 async def test_bad_snapshot_does_not_reset_retry_exhaustion(self):
  from .test_kraken import book
  opened=[];delays=[]
  async def source(*args,**kwargs):opened.append(1);yield book();yield book(checksum=1)
  async def sleep(delay):delays.append(delay);await asyncio.sleep(0)
  feed=FeedSupervisor(environment=ENV,transport=source,sleep=sleep,jitter=lambda a,b:1)
  await feed.start()
  try:
   for _ in range(1000):
    if feed.task.done():break
    await asyncio.sleep(0)
   self.assertTrue(feed.task.done(),'retry budget must terminate repeated snapshot/corruption cycles');self.assertEqual(len(opened),8);self.assertEqual(feed.reason,'retry_budget_exhausted');self.assertEqual(len(delays),7);self.assertEqual(feed.view()['book']['bids'],[])
  finally:await feed.close()
 async def test_uncooperative_retired_worker_blocks_new_admission_with_bounded_wait(self):
  feed=FeedSupervisor(environment=ENV,transport=lambda *_:None,shutdown_seconds=.001);entered=asyncio.Event();release=asyncio.Event();starts=[]
  async def worker(epoch):
   starts.append(epoch);entered.set()
   while not release.is_set():
    try:await release.wait()
    except asyncio.CancelledError:continue
  with patch.object(feed,'_run',new=worker):
   await feed.start();await entered.wait();feed.cancel()
   try:
    with self.assertRaisesRegex(ProviderError,'worker_shutdown_pending'):await feed.start('ETH/USD')
    self.assertEqual(len(starts),1);self.assertTrue(feed.view()['feed']['retired_worker_pending']);self.assertEqual(feed.view()['book']['bids'],[])
   finally:release.set();await asyncio.sleep(0);await feed.close()
 async def test_invalid_jitter_cannot_create_unbounded_or_nonfinite_wait(self):
  async def source(*a,**k):raise OSError('AUTHORED_PRIVATE_ERROR');yield ''
  for value in(float('nan'),1.3,True):
   waits=[]
   async def sleep(seconds):waits.append(seconds)
   feed=FeedSupervisor(environment=ENV,transport=source,sleep=sleep,jitter=lambda a,b:value);await feed.start();await feed.task
   self.assertEqual(feed.reason,'invalid_retry_jitter');self.assertEqual(waits,[]);self.assertNotIn('AUTHORED_PRIVATE_ERROR',str(feed.view()));await feed.close()
