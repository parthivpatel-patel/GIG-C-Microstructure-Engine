"""SEC browser fixtures only. Never makes an HTTP request or changes provider gates."""
import os,sys,json,datetime,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.atlas_fixture_server import fetch,ENV
from terminal.stocks.service import StockWorkspace,AccessError
from terminal.server.app import create_app
import uvicorn
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18796'
COUNTS={}
async def authored(url,headers,cap):
    import re
    cik=re.search(r'CIK(\d{10})',url).group(1)
    key=(cik,'facts' if '/companyfacts/' in url else 'filings');COUNTS[key]=COUNTS.get(key,0)+1
    if key==('0000320193','facts') and COUNTS[key]>1:raise AccessError('upstream_http_429')
    base=url.replace('CIK'+cik,'CIK0000320193');value=json.loads(await fetch(base,headers,cap));value['cik']=int(cik)
    if key==('0001045810','facts'):value={'cik':int(cik),'facts':{}}
    if key==('0001318605','facts'):value={'cik':int(cik),'facts':{'us-gaap':{'Revenues':{'units':{'USD':'malformed'}}}}}
    return json.dumps(value).encode()
class Authored(StockWorkspace):
    def __init__(self,**kw):
        self.offset=0
        super().__init__(clock=lambda:time.monotonic()+self.offset,**kw)
    async def start_load(self,ticker,**kw):
        self.offset+=61 # Independent scenario starts after prior domain cooldown,without disabling it.
        return await super().start_load(ticker,**kw)
    async def refresh(self,ticker,provider,**kwargs):
        result=await super().refresh(ticker,provider,**kwargs)
        if provider=='sec' and ticker=='AAPL':self.offset+=61 # Advance cache expiry AND rate clock coherently.
        return result
    def view(self,ticker):
        result=super().view(ticker)
        if ticker=='MSFT' and result['fundamentals'].get('received_at'):
            old=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=2)).isoformat()
            result['fundamentals']={**result['fundamentals'],'received_at':old,'response_age_seconds':172800,'freshness':'STALE_CACHE'}
        result['_fixture_sec_requests']=sum(v for (c,_),v in COUNTS.items() if c==result['instrument']['cik'])
        return result
if __name__=='__main__':
    # SEC true aliases intentionally reproduce owner configuration;all other providers off.
    env={k:v for k,v in ENV.items() if not k.startswith(('GIG_ALPACA','ALPACA','APCA'))};env.update(GIG_SEC_ENABLED='true',GIG_SEC_POLICY_REVIEWED='yes')
    uvicorn.run(create_app(stock_workspace=Authored(environment=env,fetcher=authored)),host='127.0.0.1',port=18796)
