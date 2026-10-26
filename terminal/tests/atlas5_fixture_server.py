"""Authored gated two-page IEX profile. No network or real-provider permissions."""
import sys,os,json,datetime,tempfile
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.atlas4_fixture_server import fetch,ENV
from terminal.stocks.service import StockWorkspace
from terminal.stocks.history_store import HistoryStore
from terminal.server.app import create_app
import uvicorn
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18793'
async def authored(url,headers,cap):
    query=parse_qs(urlsplit(url).query)
    if '/bars?' not in url or query.get('limit')!=['64']:return await fetch(url,headers,cap)
    start=datetime.date.fromisoformat(query['start'][0][:10]);offset=15 if 'page_token' in query else 0
    rows=[{'t':str(start+datetime.timedelta(days=i+1))+'T14:30:00Z','o':100+i,'h':102+i,'l':99+i,'c':100+i,'v':20,'vw':100+i,'n':2} for i in range(offset,offset+15)]
    return json.dumps({'symbol':'AAPL','bars':rows,'next_page_token':None if offset else 'authored+next=='}).encode()
if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='gig-atlas5-authored-') as root:
        uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=authored,history_store=HistoryStore(Path(root)/'private'))),host='127.0.0.1',port=18793)
