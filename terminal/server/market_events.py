"""Proof-authorized latest-state SSE;bounded clients/payload/no per-client event queue."""
import asyncio,json,time
from starlette.responses import StreamingResponse
from starlette.requests import ClientDisconnect

class SendDeadline(Exception):pass

class MarketEvents:
    def __init__(self,source,*,clients=8,interval=.25,heartbeat=1.):
        self.source=source;self.limit=clients;self.interval=interval;self.heartbeat=heartbeat
        self.clients=0;self.sent=0;self.coalesced=0;self.timeouts=0;self.closed=False
        self.in_flight_sends=0;self.in_flight_bytes=0;self.peak_in_flight_bytes=0
    def status(self):return {'clients':self.clients,'maximum_clients':self.limit,'snapshots_sent':self.sent,'coalesced_checks':self.coalesced,'send_timeouts':self.timeouts,'application_queue_depth':0,'in_flight_sends':self.in_flight_sends,'in_flight_body_bytes':self.in_flight_bytes,'peak_in_flight_body_bytes':self.peak_in_flight_bytes,'upstream_queue_depth':'UNAVAILABLE_NO_PUBLIC_TRANSPORT_METRIC','policy':'Latest snapshots coalesce;no per-client event backlog;source ingestion independent;stable checks are not a count of dropped source events'}
    def reserve(self):
        if self.closed or self.clients>=self.limit:return False
        self.clients+=1;return True
    async def frames(self,profile=None):
        from .market_delta import MarketProjection
        projection=MarketProjection() if profile=='delta-v1' else None
        previous=None;emitted=0.
        while not self.closed:
            s=self.source;key=(s.receipts,s.generation,s.state,s.phase,s.duplicates,s.out_of_order,str(s.pending))
            now=time.monotonic()
            if key!=previous or now-emitted>=self.heartbeat:
                snapshot=s.view();snapshot['browser_push']=self.status()
                if projection:snapshot=projection.project(snapshot)
                data=json.dumps(snapshot,separators=(',',':'),allow_nan=False)
                frame='event: state\ndata: '+data+'\n\n'
                if len(frame.encode())>1024*1024:
                    yield 'event: error\ndata: {"code":"MARKET_SNAPSHOT_BUDGET"}\n\n';return
                self.sent+=1;previous=key;emitted=now
                yield frame
            else:self.coalesced+=1
            await asyncio.sleep(self.interval)
    def response(self,profile=None):return BoundedEvents(self,profile)

class BoundedEvents(StreamingResponse):
    def __init__(self,hub,profile=None):
        self.hub=hub
        super().__init__(hub.frames(profile),media_type='text/event-stream',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no','Cross-Origin-Resource-Policy':'same-origin'})
    async def stream_response(self,send):
        async def bounded(message):
            size=len(message.get('body',b''))
            self.hub.in_flight_sends+=1;self.hub.in_flight_bytes+=size
            self.hub.peak_in_flight_bytes=max(self.hub.peak_in_flight_bytes,self.hub.in_flight_bytes)
            try:await asyncio.wait_for(send(message),2.)
            except TimeoutError:
                self.hub.timeouts+=1;raise SendDeadline from None
            finally:
                self.hub.in_flight_sends-=1;self.hub.in_flight_bytes-=size
        try:await super().stream_response(bounded)
        except SendDeadline:pass
    async def __call__(self,scope,receive,send):
        try:await super().__call__(scope,receive,send)
        except ClientDisconnect:pass
        finally:
            try:await self.body_iterator.aclose()
            finally:self.hub.clients-=1
