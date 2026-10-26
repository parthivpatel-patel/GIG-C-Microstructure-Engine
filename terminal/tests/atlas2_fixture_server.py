"""Authored multiyear balances and66 filing records;strictly loopback,no upstream."""
import sys,os,json,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.atlas_fixture_server import fetch,ENV
from terminal.stocks.service import StockWorkspace
from terminal.server.app import create_app
import uvicorn
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18789'
async def authored(url,headers,cap):
 raw=await fetch(url,headers,cap)
 if '/submissions/' not in url:return raw
 p=json.loads(raw);rows={k:[] for k in ('accessionNumber','form','filingDate','primaryDocument','acceptanceDateTime','reportDate')}
 for i in range(66):
  day=str(datetime.date(2024,2,1)+datetime.timedelta(days=i));values=(f'0000000123-24-{i+1:06d}','10-K/A' if i%4==0 else '10-Q',day,f'authored-{i+1}.htm',day+'T12:00:00Z','2023-12-31')
  for k,v in zip(rows,values):rows[k].append(v)
 p['filings']['recent']=rows;return json.dumps(p).encode()
if __name__=='__main__':uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=authored)),host='127.0.0.1',port=18789)
