"""Loopback-only authored financial/history fixture and ephemeral private storage."""
import os,sys,json,tempfile,datetime
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.atlas2_fixture_server import authored,ENV
from terminal.stocks.service import StockWorkspace
from terminal.stocks.history_store import HistoryStore
from terminal.server.app import create_app
import uvicorn
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18792'
async def fetch(url,headers,cap):
    raw=await authored(url,headers,cap)
    if '/companyfacts/' in url:
        p=json.loads(raw)
        # Authored negative control:one missing reported gross-profit period.
        units=p['facts']['us-gaap']['GrossProfit']['units']['USD']
        p['facts']['us-gaap']['GrossProfit']['units']['USD']=[r for r in units if r['end']!='2023-12-31']
        return json.dumps(p).encode()
    if '/bars?' not in url:return raw
    p=json.loads(raw);start=datetime.date.fromisoformat(parse_qs(urlsplit(url).query)['start'][0][:10]);p['bars']=[]
    for i in range(25):
        v=100+i;p['bars'].append({'t':str(start+datetime.timedelta(days=i+1))+'T14:30:00Z','o':v,'h':v+1,'l':v-1,'c':v,'v':20,'vw':v,'n':2})
    return json.dumps(p).encode()
if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='gig-atlas4-authored-') as root:
        store=HistoryStore(Path(root)/'private')
        uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=fetch,history_store=store)),host='127.0.0.1',port=18792)
