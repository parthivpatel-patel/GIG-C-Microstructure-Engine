#!/usr/bin/env python3
"""Bounded real-clock, authored four-symbol IEX/SQLite/ASGI workload. No network.

Exercises the actual stream lifecycle through a bounded fake provider transport,
not an authenticated provider. Actual SSE250ms cadence and2s send deadlines run.
"""
import argparse
import asyncio
from collections import deque
import datetime as dt
import gc
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
import time
import tracemalloc

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
SYMBOLS=('AAPL','AMZN','MSFT','NVDA')


class Socket:
    def __init__(self,owner):
        self.owner=owner;self.queue=asyncio.Queue(4)
    async def __aenter__(self):
        self.owner.opens+=1;self.owner.latest=self
        await self.put([{'T':'success','msg':'connected'}]);return self
    async def __aexit__(self,*_):
        self.owner.closes+=1
        while not self.queue.empty():self.queue.get_nowait()
    async def put(self,rows):
        import msgpack
        raw=msgpack.packb(rows);assert len(raw)<=32768
        await self.queue.put(raw);self.owner.queue_peak=max(self.owner.queue_peak,self.queue.qsize())
    async def recv(self):
        value=await self.queue.get()
        if isinstance(value,Exception):raise value
        return value
    async def send(self,raw):
        import msgpack
        value=msgpack.unpackb(raw,raw=False);action=value['action']
        if action=='auth':await self.put([{'T':'success','msg':'authenticated'}])
        else:
            self.owner.subscription_messages+=1
            await self.put([{'T':'subscription',**{c:[] if action=='unsubscribe' else value.get(c,[])for c in ('quotes','trades','bars')}}])


class Transport:
    opens=0;closes=0;queue_peak=0;subscription_messages=0;latest=None
    def __call__(self,url,**kwargs):
        from terminal.stocks.live import ENDPOINT
        assert url==ENDPOINT and kwargs['max_queue']==4 and kwargs['max_size']==32768
        return Socket(self)


async def until(predicate,seconds=3):
    async with asyncio.timeout(seconds):
        while not predicate():await asyncio.sleep(.001)


def stamp(ns):
    seconds,fraction=divmod(ns,10**9)
    return dt.datetime.fromtimestamp(seconds,dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+f'.{fraction:09d}Z'


def semantic(row):return [row['receipt_index'],row['symbol'],row['kind'],row['data']]

def digest(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()


async def exercise(batches=300,cadence=.1,slow_delay=2.25,trace=True):
    from terminal.server.market_events import MarketEvents
    from terminal.stocks.live import LiveIEX
    from terminal.stocks.service import StockWorkspace
    from terminal.stocks.observation_store import ObservationStore
    from terminal.stocks.test_repair import ENV
    if type(batches)is not int or not 6<=batches<=3000 or not .001<=cadence<=.1:raise ValueError('workload_budget')
    if not 0<=slow_delay<=3:raise ValueError('consumer_delay_budget')
    start=time.monotonic();cpu=time.process_time();source_epoch=time.time_ns()
    oracle=deque(maxlen=10000);semantic_input=[];samples=[];connections=[];responses=[]
    counters={'successful_body_sends':0,'body_bytes':0,'validated_snapshots':0,'rejected_ninth_client':0,'cancelled_consumers':0,'injected_disk_faults':0,'explicit_restarts':0,'automatic_reconnects':0,'late_candidates':0}
    factory=Transport();stream=None;hub=None
    if trace:tracemalloc.start()
    async def consume(response,delay):
        cache={};sequence=0
        async def send(message):
            nonlocal cache,sequence
            body=message.get('body',b'')
            if body and delay:await asyncio.sleep(delay)
            if not body:return
            text=body.decode();assert text.startswith('event: state\ndata: ')
            data=json.loads(text.split('data: ',1)[1]);delta=data['browser_delta']
            assert delta['sequence']==sequence+1;sequence=delta['sequence']
            if delta['mode']=='full':cache={}
            cache.update({r['receipt_index']:r for r in data['history']})
            cache={n:{**cache[n],'state':state,'receive_age_seconds':age}for n,state,age in delta['history_status']}
            expected={r[0]:r for r in oracle}
            for n,row in cache.items():
                assert semantic(row)==expected[n]
                assert row['origin']=='HISTORICAL_SYNTHETIC' and row['state']!='LIVE'
            assert len(cache)<=256
            counters['successful_body_sends']+=1;counters['body_bytes']+=len(body);counters['validated_snapshots']+=1
        async def receive():await asyncio.Event().wait()
        await response({'type':'http','asgi':{'version':'3.0','spec_version':'2.4'},'method':'POST','path':'/authored','headers':[]},receive,send)
    def add_client(delay=0):
        assert hub.reserve();response=hub.response('delta-v1');responses.append(response)
        task=asyncio.create_task(consume(response,delay));connections.append(task)
    with tempfile.TemporaryDirectory(prefix='gig-sustained-authored-')as private:
        store=ObservationStore(private,retention_seconds=3600)
        stream=LiveIEX(StockWorkspace(environment={**ENV,'GIG_ALPACA_IEX_STREAM_ENABLED':'1','GIG_ALPACA_LIVE_ENABLED':'0','GIG_PAPER_EXECUTION_ENABLED':'0'}),connector=factory,store=store,retry_budget=2,random_source=lambda:0)
        stream.capture_id='a'*32
        hub=MarketEvents(stream,interval=.25,heartbeat=1.)
        try:
            async with asyncio.timeout(batches*cadence+20):
                await stream.start(list(SYMBOLS));await until(lambda:stream.phase=='SUBSCRIBED')
                for delay in (0,.02,.4,slow_delay,0,0,0,0):add_client(delay)
                assert not hub.reserve();counters['rejected_ninth_client']+=1
                expected=0;duplicates=0
                for i in range(batches):
                    due=start+i*cadence;await asyncio.sleep(max(0,due-time.monotonic()))
                    channels=('quotes',)if batches//3<=i<batches//2 else ('quotes','trades')
                    if tuple(sorted(stream.channels))!=tuple(sorted(channels)):
                        await stream.start(list(SYMBOLS),list(channels));await until(lambda:stream.pending is None and stream.phase=='SUBSCRIBED')
                    if i and i%max(5,batches//4)==0:
                        if i==batches//4:
                            opened=factory.opens;await factory.latest.queue.put(OSError('AUTHORED_DISCONNECT'))
                            await until(lambda:factory.opens>opened and stream.phase=='SUBSCRIBED')
                            counters['automatic_reconnects']+=1
                        else:
                            await stream.close();await stream.start(list(SYMBOLS),list(channels));await until(lambda:stream.phase=='SUBSCRIBED');counters['explicit_restarts']+=1
                    if i==batches//3:
                        connections[0].cancel()
                        try:await connections[0]
                        except asyncio.CancelledError:counters['cancelled_consumers']+=1
                        add_client()
                    rows=[];planned=[]
                    for j,symbol in enumerate(SYMBOLS):
                        source_ns=source_epoch+int(i*cadence*10**9)
                        if i and i%19==0:source_ns-=int(2*cadence*10**9);counters['late_candidates']+=1
                        q={'T':'q','S':symbol,'t':stamp(source_ns),'bp':100+j,'ap':101+j,'bs':1+i%100,'as':2+j}
                        rows.append(q);planned.append([expected+len(planned)+1,symbol,'quote',{'bid':str(100+j),'ask':str(101+j),'bid_size':str(1+i%100),'ask_size':str(2+j)}])
                        if 'trades'in channels:
                            rows.append({'T':'t','S':symbol,'t':stamp(source_ns),'p':100+j,'s':1,'i':i*4+j})
                            planned.append([expected+len(planned)+1,symbol,'trade',{'price':str(100+j),'size':'1'}])
                    if i==batches//2:
                        before=store.summary()['records'];store.before_commit=lambda:(_ for _ in ()).throw(OSError(28,'AUTHORED_ENOSPC'))
                        await factory.latest.put(rows);await until(lambda:stream.state=='FAILED')
                        assert stream.receipts==expected and store.summary()['records']==before
                        counters['injected_disk_faults']+=1;store.before_commit=None
                        await stream.start(list(SYMBOLS),list(channels));await until(lambda:stream.phase=='SUBSCRIBED')
                    oracle.extend(planned);semantic_input.append([i,channels,len(rows)])
                    await factory.latest.put(rows);expected+=len(rows);await until(lambda:stream.receipts==expected)
                    if i%17==0:
                        await factory.latest.put(rows);duplicates+=len(rows);await until(lambda:stream.duplicates==duplicates)
                    assert stream.receipts==expected and len(stream.history)<=256 and len(stream.seen)<=256
                    if i%max(1,batches//5)==0:
                        gc.collect();current,peak=tracemalloc.get_traced_memory()if trace else(0,0)
                        samples.append({'batch':i,'accepted':expected,'history':len(stream.history),'traced_current_bytes':current,'traced_peak_bytes':peak,'rss_hwm_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'database_bytes':store.path.stat().st_size,'clients':hub.clients,'schedule_lag_seconds':max(0,time.monotonic()-due)})
                assert stream.receipts==expected and stream.duplicates==duplicates
                await stream.close();hub.closed=True
                results=await asyncio.gather(*connections,return_exceptions=True)
                assert all(r is None or isinstance(r,asyncio.CancelledError)for r in results),[type(r).__name__ for r in results]
                recovered=ObservationStore(private).recover()
                actual=[semantic(r['event'])for r in recovered]
                assert 0<len(actual)<=min(expected,10000) and actual==list(oracle)[-len(actual):]
                assert actual[0][0]==expected-len(actual)+1
                assert all(r['classification']=='RETAINED_HISTORICAL_NOT_CURRENT'for r in recovered)
                assert hub.clients==0 and hub.in_flight_sends==0 and hub.in_flight_bytes==0
                report={'schema':'gig.sustained.qualification.v1','origin':'HISTORICAL_SYNTHETIC','batches':batches,'nominal_cadence_seconds':cadence,'projection_interval_seconds':.25,'symbols':list(SYMBOLS),'accepted':expected,'duplicates':duplicates,'out_of_order':stream.out_of_order,'retained':len(stream.history),'storage_retained':len(actual),'storage_evictions':expected-len(actual),'retention_evictions':stream.evicted,'source_opens':factory.opens,'source_closes':factory.closes,'source_queue_peak':factory.queue_peak,'subscription_messages':factory.subscription_messages,'final_generation':stream.generation,'counters':counters,'backpressure':hub.status(),'samples':samples,'semantic_output_sha256':digest(actual),'recipe_sha256':digest(semantic_input),'wall_seconds':time.monotonic()-start,'parent_cpu_seconds':time.process_time()-cpu,'database_bytes':store.path.stat().st_size,'rss_peak_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'scope':'Real asyncio clocks and ASGI sends;fake bounded provider. ENOSPC injected at transaction boundary;SQLite_FULL separately tested. Programmed recovery gaps offer no candidate events;not an exchange completeness test. No network,private-edge,arrival SLA,full-session or source-loss claim. Tracing includes bounded independent oracle/test harness.'}
        finally:
            hub.closed=True
            await stream.close()
            for task in connections:
                if not task.done():task.cancel()
            await asyncio.gather(*connections,return_exceptions=True)
            if trace:tracemalloc.stop()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batches',type=int,default=300,choices=range(300,3001));p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():p.error('Refusing existing evidence path')
    report=asyncio.run(exercise(a.batches))
    from terminal.verification.artifacts import write_private
    import subprocess
    report['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report['tracked_dirty']=bool(subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT))
    write_private(a.output,report)
    print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
