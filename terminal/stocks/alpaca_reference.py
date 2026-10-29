"""Bounded paper-account asset reference. Identity is not a market-data entitlement."""
import asyncio
import datetime
import re
import uuid
from .alpaca_transport import ASSETS
from .directory import SearchIndex
from .identity import SYMBOL_PATTERN
from .market_catalog import MarketCatalog

MAX_ASSETS = 50000

def parse(batches, origin):
    rows, identities = {}, set()
    excluded = {'unsupported_symbol':0, 'non_us_equity':0}
    for status, assets in batches:
        if type(assets) is not list or len(assets) > MAX_ASSETS:
            raise ValueError('alpaca_assets_budget')
        for asset in assets:
            if type(asset) is not dict or asset.get('status') != status:
                raise ValueError('alpaca_asset_status')
            MarketCatalog.text(asset.get('class'),32)
            if asset.get('class') != 'us_equity':
                excluded['non_us_equity'] += 1
                continue
            symbol, name, exchange, identity = (asset.get(k) for k in ('symbol','name','exchange','id'))
            for value, limit in ((symbol,32),(name,256),(exchange,32),(identity,36)):
                MarketCatalog.text(value, limit)
            if str(uuid.UUID(identity)) != identity:
                raise ValueError('alpaca_asset_id')
            if not re.fullmatch(SYMBOL_PATTERN, symbol):
                excluded['unsupported_symbol'] += 1
                continue
            if symbol in rows or identity in identities:
                raise ValueError('alpaca_asset_collision')
            if len(rows) >= MAX_ASSETS:
                raise ValueError('alpaca_assets_total_budget')
            flags = {}
            for key in ('tradable','marginable','shortable','easy_to_borrow','fractionable'):
                value = asset.get(key)
                if value is not None and type(value) is not bool:
                    raise ValueError('alpaca_asset_flag')
                flags[key] = value
            rows[symbol] = {'symbol':symbol,'name':name,'exchange':exchange,'asset_id':identity,
                'security_type':'US_EQUITY_SUBTYPE_UNVERIFIED','listing_status':status.upper(),
                'provider_flags':flags, 'source_directory':'alpaca_paper_assets',
                'aliases':{'alpaca_symbol':symbol}}
            identities.add(identity)
    if not rows:
        raise ValueError('alpaca_assets_empty')
    catalog = MarketCatalog()
    catalog.rows = rows
    catalog.index = []
    catalog.search_index = SearchIndex(rows)
    catalog.source = {'reference':'Alpaca paper account /v2/assets active+inactive us_equity',
        'as_of':None,'authority':'ALPACA_ACCOUNT_ASSET_REFERENCE','classification':origin,
        'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'excluded':excluded,'coverage':'Provider account asset universe,including inactive/OTC if supplied;not complete current exchange listings,SEC identity,feed entitlement or trading permission'}
    return catalog

class AssetReference:
    def __init__(self, workspace):
        self.workspace = workspace
        self.status = 'NOT_REQUESTED'
        self.last_attempt = None
        self.last_error = None

    def enabled(self):
        mode = self.workspace.environment.get('GIG_ALPACA_ASSET_REFERENCE_ENABLED')
        return mode == '1' or mode is None and self.workspace.production_configuration and not self.workspace.directory.approved()

    def view(self):
        w = self.workspace
        try:
            w.permission('alpaca')
            ready = True
        except ValueError:
            ready = False
        active = w.catalog.source.get('authority') == 'ALPACA_ACCOUNT_ASSET_REFERENCE'
        return {'schema':'gig.alpaca.asset-reference.v1','status':self.status,'ready':ready,
            'automatic_enabled':self.enabled(),'last_error':self.last_error,
            'accepted_count':len(w.catalog.rows) if active else 0,
            'observed_provider_count':len(w.catalog.rows) if active and w.catalog.source.get('classification') == 'OBSERVED_OFFICIAL_RESPONSE' else 0,
            'source':w.catalog.source if active else None,
            'retention':'Process-lifetime reference only;no source files persisted',
            'boundary':'GET paper /v2/assets only;no account/order/position or trading operations'}

    async def refresh(self):
        w = self.workspace
        headers = w.permission('alpaca')
        if self.last_attempt is not None and w.clock() - self.last_attempt < 300:
            raise ValueError('alpaca_asset_refresh_cooldown')
        if w.lock.locked():
            raise ValueError('upstream_refresh_busy')
        async with w.lock:
            self.last_attempt = w.clock()
            try:
                async with asyncio.timeout(25):
                    batches, receipts = [], []
                    for status in ('active','inactive'):
                        await asyncio.sleep(max(0, 1.01-(w.clock()-w.last_request)))
                        url = ASSETS + '?asset_class=us_equity&status=' + status
                        data, digest = await w.fetch('alpaca',url,headers)
                        batches.append((status,data))
                        receipts.append({'url':url,'sha256':digest})
                    catalog = await asyncio.to_thread(parse,batches,w.origin)
                    catalog.source['sources'] = receipts
                    # Do not relabel retained observations after provider symbol reuse.
                    protected = set(w.cache) | {key[0] for key in w.market_history_cache}
                    for symbol in protected:
                        previous = w.catalog.rows.get(symbol,{})
                        if previous.get('asset_id') is not None and (symbol not in catalog.rows or catalog.rows[symbol]['asset_id'] != previous['asset_id']):
                            raise ValueError('alpaca_cached_asset_identity_changed')
                    w.catalog = catalog
                    self.status, self.last_error = 'ACCEPTED', None
            except asyncio.CancelledError:
                raise
            except Exception:
                self.status, self.last_error = 'REJECTED_LAST_ACCEPTED_PRESERVED', 'asset_reference_transport_or_validation_failure'
                raise ValueError(self.last_error) from None
        return self.view()

    async def run(self):
        while True:
            if self.enabled():
                try:
                    # SEC initialization can own the shared upstream lock at startup.
                    # Wait for that local work instead of delaying assets for six hours.
                    # This does not retry a rejected remote request.
                    self.workspace.permission('alpaca')
                    async with asyncio.timeout(55):
                        async with self.workspace.lock:
                            pass
                        await self.refresh()
                except ValueError:
                    pass
                except TimeoutError:
                    self.status, self.last_error = 'INITIALIZATION_BUSY', 'shared_upstream_startup_budget'
            await asyncio.sleep(21600)
