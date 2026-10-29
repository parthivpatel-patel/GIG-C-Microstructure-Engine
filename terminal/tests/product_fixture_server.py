"""Authored exchange directory+SEC/IEX fixtures on loopback;no upstream requests."""
import sys,os,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.live_market_fixture_server import Socket
from terminal.tests.atlas_fixture_server import ENV,fetch
from terminal.stocks.service import StockWorkspace
from terminal.stocks.directory import parse_files,HEADERS
from terminal.stocks.test_directory import files
from terminal.server.app import create_app
import uvicorn
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18798'
async def reference_fetch(url,headers,cap):
 if url=='https://www.sec.gov/files/company_tickers.json':return json.dumps({'0':{'ticker':'NEWQ','title':'Authored new registrant','cik_str':42},'1':{'ticker':'AAPL','title':'Authored Apple registrant','cik_str':320193}}).encode()
 return await fetch(url,headers,cap)
w=StockWorkspace(environment={**ENV,'GIG_ALPACA_LIVE_ENABLED':'1'},fetcher=reference_fetch)
f=files();lines=f['nasdaq'].decode().splitlines();f['nasdaq']=('\n'.join(lines[:-1])+ '\n'+'\n'.join(f'{s}|{n}|Q|N|N|100|N|N' for s,n in ([('MSFT','Authored Microsoft'),('NVDA','Authored NVIDIA')]+[(f'EX{i:03}',f'Authored research security {i}') for i in range(50)]))+'\n'+lines[-1]+'\n').encode();w.catalog=parse_files(f);w.directory.state={'status':'ACCEPTED','last_error':None,'accepted_count':len(w.catalog.rows),'last_success':w.catalog.source['received_at']}
app=create_app(stock_workspace=w);app.state.stock_live.connector=lambda *a,**k:Socket()
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=18798)
