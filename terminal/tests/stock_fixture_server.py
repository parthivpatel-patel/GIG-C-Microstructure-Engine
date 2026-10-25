"""Local-only authored provider injection for browser tests;never contacts upstream hosts."""
import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
for k in ('CODESPACES','CODESPACE_NAME','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN'):os.environ.pop(k,None)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):os.environ[k]='0'
os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18787'
import uvicorn
from terminal.stocks.service import StockWorkspace
from terminal.stocks.test_repair import ENV,authored_fetcher
from terminal.server.app import create_app
if __name__=='__main__':uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=authored_fetcher)),host='127.0.0.1',port=18787)
