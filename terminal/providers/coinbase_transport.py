"""Fixed Exchange-shaped candidate transport. No connection on import/default startup.
Current official profile and use must be operator-reviewed before permission is granted.
"""
import asyncio,json
from .kraken import ProviderError,MAX_PAYLOAD

SYMBOLS={'BTC/USD':'BTC-USD','ETH/USD':'ETH-USD'}
async def live_messages(permission,*,stop,symbol='BTC/USD'):
    permission.require_live()
    if symbol not in SYMBOLS:raise ProviderError('coinbase_configuration')
    import websockets.asyncio.client
    class FixedEndpoint(websockets.asyncio.client.connect):
        def process_redirect(self,error):return error
    async with FixedEndpoint('wss://ws-feed.exchange.coinbase.com/',max_size=MAX_PAYLOAD,max_queue=4,
            open_timeout=10,close_timeout=3,ping_interval=20,ping_timeout=10) as ws:
        await ws.send(json.dumps({'type':'subscribe','product_ids':[SYMBOLS[symbol]],'channels':['level2','matches','heartbeat']}))
        while not stop.is_set():
            try:raw=await asyncio.wait_for(ws.recv(),1)
            except asyncio.TimeoutError:continue
            if type(raw) is not str:raise ProviderError('coinbase_text_frame_required')
            yield raw


def research_receipt(receipt):
    """Explicit bridge: maker-reported side stays labelled; no fabricated aggressor direction."""
    if receipt['kind'] not in ('trade','historical_trade'):return receipt
    t=receipt['trade']
    trade={'trade_id':t['trade_id'],'price_ticks':t['price_ticks'],'quantity':t['quantity'],
        'side':t['reported_side'],'side_role':t['reported_side_role'],'aggressor_side':None,
        'source_timestamp_ns':t['source_timestamp_ns'],'origin':t['origin']}
    return {'kind':'trades','historical_snapshot':receipt['kind']=='historical_trade',
            'trades':[] if receipt['duplicate'] else [trade]}
