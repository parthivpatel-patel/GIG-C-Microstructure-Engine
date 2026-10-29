"""Private loopback authored account-reference/history fixtures;never calls upstream."""
import sys,json,uuid
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.tests.product_fixture_server import app,w
from terminal.stocks.test_alpaca_data import asset,response
from terminal.stocks.test_repair import option_data
import uvicorn
old=w.fetcher
async def fetch(url,headers,cap):
    u=urlsplit(url);q=parse_qs(u.query)
    if u.netloc=='paper-api.alpaca.markets' and u.path=='/v2/assets':
        status=q['status'][0]
        rows=[asset(s,identity=i+1) for i,s in enumerate(sorted(set(w.catalog.rows)|{'AMZN'}))] if status=='active' else [asset('OLDQ','inactive',100000,exchange='NYSE',tradable=False)]
        return json.dumps(rows).encode()
    if u.netloc=='data.alpaca.markets' and u.path in ('/v2/stocks/bars','/v2/stocks/quotes','/v2/stocks/trades'):
        kind=u.path.rsplit('/',1)[1];symbol=q['symbols'][0];page=2 if 'page_token' in q else 1
        source=response(kind,symbol,token='AUTHORED_PRIVATE_PAGE' if page==1 else None)
        a=source[kind][symbol][0];a['t']=f'2026-10-20T{10+page:02}:00:00.123456789Z'
        b={**a,'t':f'2026-10-20T{12+page:02}:00:00.123456789Z'}
        # Pages must not overlap backwards:page1 11/13,then page2 14/16.
        if page==2:a['t']='2026-10-20T14:00:00.123456789Z';b['t']='2026-10-20T16:00:00.123456789Z'
        if kind=='bars':
            base=100 if symbol=='AAPL' else 50
            for i,r in enumerate((a,b)):r.update(o=str(base),h=str(base+10),l=str(base-10),c=str(base+(page-1)*2+i),v=10)
        source[kind][symbol]=[a,b]
        return json.dumps(source).encode()
    if u.netloc=='data.alpaca.markets' and u.path.startswith('/v1beta1/options/snapshots/'):
        return json.dumps(option_data(u.path.rsplit('/',1)[1]),default=str).encode()
    raw=await old(url,headers,cap)
    if u.netloc=='data.alpaca.markets' and u.path.startswith('/v2/stocks/'):
        # The legacy fixture otherwise returns AAPL for every non-NVDA symbol.
        # Author the actually requested identity;do not bypass production validation.
        p=json.loads(raw);p['symbol']=u.path.split('/')[3];return json.dumps(p).encode()
    return raw
w.fetcher=fetch
if __name__=='__main__':uvicorn.run(app,host='127.0.0.1',port=18798)
