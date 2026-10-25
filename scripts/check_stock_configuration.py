#!/usr/bin/env python3
"""Safe owner diagnostics:configuration names/presence only,zero provider requests."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace

def report(environment=None):
    return {'schema':'gig.stock.configuration.v1','configuration':StockWorkspace(environment=environment).configuration(),'network_requests':0,'secret_values_printed':False,'market_data_host':'data.alpaca.markets','account_order_endpoints_used':False,'action':'Configure existing account keys as private Codespaces repository secrets,review applicable free entitlements/policies,then restart server and select a stock. Never paste keys into chat.'}

if __name__=='__main__':print(json.dumps(report(),indent=2))
