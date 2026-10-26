"""Loopback-only authored IEX protocol;no provider network or real credentials."""
import os,sys,asyncio,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.atlas_fixture_server import ENV,fetch
from terminal.stocks.service import StockWorkspace
from terminal.server.app import create_app
from terminal.stocks.test_final import packet
import msgpack,uvicorn
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):os.environ[k]='0'
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18797'
class Socket:
 def __init__(self):
  self.symbols=[];self.channels=[];self.tick=0;self.queue=asyncio.Queue();self.queue.put_nowait({'T':'success','msg':'connected'})
 async def __aenter__(self):return self
 async def __aexit__(self,*args):pass
 async def send(self,b):
  m=msgpack.unpackb(b)
  if m['action']=='auth':self.queue.put_nowait({'T':'success','msg':'authenticated'})
  elif m['action']=='subscribe':
   self.channels=[k for k in m if k!='action'];self.symbols=m[self.channels[0]]
   self.queue.put_nowait({'T':'subscription',**{k:self.symbols for k in self.channels}})
  elif m['action']=='unsubscribe':
   self.queue.put_nowait({'T':'subscription',**{k:[] for k in self.channels}});self.channels=[];self.symbols=[]
 async def recv(self):
  if not self.queue.empty():return packet(await self.queue.get())
  await asyncio.sleep(.2)
  if not self.queue.empty():return packet(await self.queue.get())
  if not self.symbols:return packet(await self.queue.get())
  self.tick+=1;t=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z');out=[]
  for i,s in enumerate(self.symbols):
   p=100+i*40+(self.tick%10)*.01
   if 'quotes' in self.channels:out.append({'T':'q','S':s,'t':t,'bp':p,'ap':round(p+.02,2),'bs':4,'as':5})
   if 'trades' in self.channels:out.append({'T':'t','S':s,'t':t,'p':round(p+.01,2),'s':2,'i':self.tick})
  return packet(*out)
app=create_app(stock_workspace=StockWorkspace(environment={**ENV,'GIG_ALPACA_LIVE_ENABLED':'1'},fetcher=fetch))
app.state.stock_live.connector=lambda *a,**k:Socket()
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=18797)
