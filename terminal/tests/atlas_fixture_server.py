"""Local browser fixture with independently authored annual facts. No provider network."""
import os,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for k in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN'):os.environ.pop(k,None)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):os.environ[k]='0'
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18788'
from terminal.stocks.test_repair import ENV,authored_fetcher
from terminal.stocks.service import StockWorkspace
from terminal.server.app import create_app
import uvicorn
async def fetch(url,headers,cap):
    raw=await authored_fetcher(url,headers,cap)
    if '/companyfacts/' not in url:return raw
    p=json.loads(raw);gaap={}
    for tag,base,instant,eps in [('Revenues',100_000_000_000,False,False),('NetIncomeLoss',20_000_000_000,False,False),('GrossProfit',60_000_000_000,False,False),('OperatingIncomeLoss',40_000_000_000,False,False),('NetCashProvidedByUsedInOperatingActivities',30_000_000_000,False,False),('PaymentsToAcquirePropertyPlantAndEquipment',10_000_000_000,False,False),('Assets',200_000_000_000,True,False),('Liabilities',100_000_000_000,True,False),('StockholdersEquity',100_000_000_000,True,False),('CashAndCashEquivalentsAtCarryingValue',40_000_000_000,True,False),('AssetsCurrent',60_000_000_000,True,False),('LiabilitiesCurrent',30_000_000_000,True,False),('ShortTermBorrowings',1_000_000_000,True,False),('LongTermDebtCurrent',2_000_000_000,True,False),('LongTermDebtNoncurrent',3_000_000_000,True,False),('EarningsPerShareDiluted',2,False,True)]:
        rows=[]
        for i,year in enumerate((2021,2022,2023,2024)):
            row={'val':base+base*i//10,'end':f'{year}-12-31','filed':f'{year+1}-02-01','accn':f'0000000123-{(year+1)%100:02d}-000001','form':'10-K','fy':year,'fp':'FY'}
            if not instant:row['start']=f'{year}-01-01'
            rows.append(row)
        gaap[tag]={'units':{'USD/shares' if eps else 'USD':rows}}
    p['facts']={'us-gaap':gaap};return json.dumps(p).encode()
if __name__=='__main__':uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=fetch)),host='127.0.0.1',port=18788)
