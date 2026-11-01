"""Loopback only authored Sprint4 fixture:never credentials or provider sockets."""
import os,sys,time,json,hashlib
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for k in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN'):os.environ.pop(k,None)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):os.environ[k]='0'
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18804'
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace
from terminal.stocks.historical_v2 import HistoricalClient,HistoricalPermission,ns,utc
from terminal.alpaca_wire import FixtureWire,WireResponse
from terminal.paper.test_alpaca import Provider,Clock,ACCOUNT,START,GATE,LIMITS
from terminal.paper.alpaca import PaperAuthorization
from terminal.paper.contracts import canonical
from terminal.paper.provider_workspace import PaperProviderWorkspace
import uvicorn

def history(method,url,body):
 q=parse_qs(urlsplit(url).query);s=q['symbols'][0];kind=urlsplit(url).path.rsplit('/',1)[1];lo=ns(q['start'][0]);hi=ns(q['end'][0]);base={'AAPL':100,'MSFT':200,'NVDA':50}.get(s,70);rows=[]
 for i in range(12):
  t=utc(lo+(hi-lo)*i//12);p=base+[0,1,2,1,3,2,4,3,5,4,6,7][i]
  if kind=='bars':r=dict(t=t,o=p,h=p+1,l=p-1,c=p,v=10+i,vw=p,n=2)
  elif kind=='quotes':r=dict(t=t,bp=p,ap=p+1,bs=2+i,**{'as':3+i},bx='V',ax='V')
  else:r=dict(t=t,p=p,s=2+i,i=i+1,x='V')
  rows.append(r)
 return WireResponse(200,json.dumps({kind:{s:rows},'next_page_token':None}).encode())
clock=Clock();remote=Provider(clock)
auth=PaperAuthorization(GATE,True,True,True,True,True,True,True,True,ACCOUNT,START,clock.ms+900000,hashlib.sha256(canonical(LIMITS.view())).hexdigest())
root=Path(os.environ['GIG_SPRINT4_PRIVATE'])
paper=PaperProviderWorkspace(root/'provider',authorization=auth,limits=LIMITS,transport=FixtureWire(remote.call),clock=clock.now,monotonic=clock.monotonic,sleep=clock.sleep,reference=lambda s:dict(symbol=s,feed='iex',origin='HISTORICAL_SYNTHETIC',at_ms=clock.ms,price_cents=10000))
h=HistoricalClient(FixtureWire(history),permission=HistoricalPermission(True,True,True,True,True,'AUTHORED_NOT_OWNER_PERMISSION',('iex','sip')))
from terminal.paper.workspace import PaperWorkspace
app=create_app(stock_workspace=StockWorkspace(environment={}),historical_client=h,paper_provider=paper,paper_workspace=PaperWorkspace(root/'fake'))
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=18804,proxy_headers=False)
