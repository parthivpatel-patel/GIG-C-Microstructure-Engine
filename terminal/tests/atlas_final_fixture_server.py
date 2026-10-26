"""Local authored final qualification server;no real credentials or provider transport."""
import os,tempfile
from pathlib import Path
from terminal.tests.atlas5_fixture_server import authored,ENV
from terminal.stocks.service import StockWorkspace
from terminal.stocks.history_store import HistoryStore
from terminal.server.app import create_app
import uvicorn
if __name__=='__main__':
    os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:18794'
    with tempfile.TemporaryDirectory(prefix='gig-final-authored-') as root:
        uvicorn.run(create_app(stock_workspace=StockWorkspace(environment=ENV,fetcher=authored,history_store=HistoryStore(Path(root)/'private'))),host='127.0.0.1',port=18794)
