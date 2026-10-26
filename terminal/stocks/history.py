"""Provider-neutral bounded historical observations. No acquisition or live claims.

Construction is transactional: nothing is published until every page is validated.
Gaps are candidates, not proof of missing exchange activity without a calendar.
"""
from dataclasses import asdict, dataclass
from datetime import timezone
from fractions import Fraction
import hashlib
import json
import re
from .identity import symbol
from .prices import decimal, timestamp
from terminal.providers.kraken import timestamp_ns

MAX_BARS = 256
MAX_PAGES = 4
MAX_BYTES = 2 * 1024 * 1024
STATES = ('LIVE', 'DELAYED', 'HISTORICAL', 'SIMULATED', 'STALE', 'UNAVAILABLE', 'BLOCKED')

@dataclass(frozen=True)
class HistorySource:
    provider: str
    feed: str
    coverage: str
    adjustment: str
    origin: str
    entitlement: str
    received_at: str
    price_unit: str = 'provider_reported_price_units'
    volume_unit: str = 'provider_reported_volume_no_lot_conversion'

    def validate(self):
        for field in (self.provider, self.feed, self.coverage, self.entitlement, self.price_unit, self.volume_unit):
            if type(field) is not str or not 1 <= len(field) <= 256 or any(ord(c) < 32 for c in field):
                raise ValueError('history_source')
        if self.adjustment not in ('raw', 'split', 'dividend', 'all', 'unknown'):
            raise ValueError('history_adjustment')
        if self.origin not in ('HISTORICAL_SYNTHETIC', 'OBSERVED_OFFICIAL_RESPONSE'):
            raise ValueError('history_origin')
        if type(self.received_at) is not str:
            raise ValueError('history_receipt')
        timestamp(self.received_at.removesuffix('+00:00')+'Z' if self.received_at.endswith('+00:00') else self.received_at)


def utc(value):
    # Keep exact original/nanosecond source timestamp separately;ISO microsecond
    # rendering must never masquerade as exact source precision.
    return timestamp(value).astimezone(timezone.utc).isoformat()


def normalize(ticker, timeframe, pages, source, *, has_more=False):
    symbol(ticker)
    if timeframe not in ('1Day', '1Hour', '1Min') or type(has_more) is not bool:
        raise ValueError('history_query')
    if type(source) is not HistorySource:
        raise ValueError('history_source')
    source.validate()
    if type(pages) is not list or not 1 <= len(pages) <= MAX_PAGES:
        raise ValueError('history_page_budget')
    # Bound nested traversal before serialization;adapters supply primitive bars.
    count = 0
    for page in pages:
        if type(page) is not dict or len(page) != 2 or set(page) != {'bars', 'sha256'} or type(page['bars']) is not list:
            raise ValueError('history_page')
        if type(page['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}', page['sha256']):
            raise ValueError('history_digest')
        count += len(page['bars'])
        if count > MAX_BARS:
            raise ValueError('history_record_budget')
        for row in page['bars']:
            if type(row) is not dict or not 6 <= len(row) <= 8 or not {'timestamp','open','high','low','close','volume'} <= set(row) or set(row)-{'timestamp','open','high','low','close','volume','vwap','trade_count'}:
                raise ValueError('history_bar')
            if any(type(v) not in (str, type(None)) or (type(v) is str and len(v) > 64) for v in row.values()):
                raise ValueError('history_bar_field')
    if len(json.dumps(pages, separators=(',', ':')).encode()) > MAX_BYTES:
        raise ValueError('history_byte_budget')
    rows = []
    previous = None
    gaps = []
    expected_ns = {'1Day':86400, '1Hour':3600, '1Min':60}[timeframe]*10**9
    for page in pages:
        for raw in page['bars']:
            stamp = int(timestamp_ns(raw['timestamp']))
            timestamp(raw['timestamp'])
            if previous is not None:
                if stamp == previous:
                    raise ValueError('history_duplicate_timestamp')
                if stamp < previous:
                    raise ValueError('history_out_of_order')
                if stamp-previous > expected_ns:
                    gaps.append({'after_index':len(rows)-1,'elapsed_ns':str(stamp-previous)})
            previous = stamp
            row = {k:decimal(raw[k], k != 'volume') for k in ('open','high','low','close','volume')}
            if not Fraction(row['low']) <= min(Fraction(row['open']), Fraction(row['close'])) <= max(Fraction(row['open']),Fraction(row['close'])) <= Fraction(row['high']):
                raise ValueError('history_ohlc')
            row.update(timestamp=raw['timestamp'], timestamp_ns=str(stamp), utc=utc(raw['timestamp']))
            rows.append(row)
    wire = {'schema':'gig.backend.history.v2','symbol':ticker,'timeframe':timeframe,
            'state':'SIMULATED' if source.origin == 'HISTORICAL_SYNTHETIC' else 'HISTORICAL',
            'source':asdict(source),'bars':rows,'record_count':len(rows),
            'page_count':len(pages),'has_more':has_more,'complete_history':False,
            'source_sha256':[p['sha256'] for p in pages], 'gap_candidates':gaps,
            'session':{'status':'UNVERIFIED','reason':'No authoritative exchange calendar,holidays,halts or session completeness supplied'},
            'limitations':['No complete history or publication eligibility inferred from response boundaries',
                           'Gap candidates may be session/weekend/holiday breaks;not missing-event counts',
                           'UTC display is microsecond precision;timestamp_ns preserves exact wire time',
                           'Raw corporate-action discontinuities may dominate returns;no automatic adjustment']}
    wire['canonical_scope'] = 'normalized_observation_core_excluding_derived_research_and_cache_metadata'
    wire['canonical_sha256'] = hashlib.sha256(json.dumps(wire,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return wire


def from_workspace(workspace, ticker):
    """Read accepted cache only;GET never acquires data or expands entitlement."""
    view = workspace.view(ticker)
    data = view['prices']
    records = [r for r in data.get('source_records',[]) if r.get('component') == 'bars']
    if not data.get('bars') or len(records) != 1:
        return {'schema':'gig.backend.history.v2','symbol':ticker,
                'state':'BLOCKED' if not view['capabilities']['iex_refresh'] else 'UNAVAILABLE',
                'bars':[],'record_count':0,'complete_history':False,
                'reason':'accepted_bar_cache_and_unique_source_receipt_required',
                'research':{'status':'UNAVAILABLE','reason':'validated_history_required'}}
    source = HistorySource('alpaca',data.get('feed','unknown'),data.get('scope','unspecified'),
                           data.get('adjustment','unknown'),data['origin'],
                           'fixture_only' if data['origin']=='HISTORICAL_SYNTHETIC' else 'operator_review_not_independent_entitlement_verification',
                           records[0]['received_at'])
    result = normalize(ticker,data['timeframe'],[{'bars':data['bars'],'sha256':records[0]['sha256']}],source,has_more=data.get('next_page_available',False))
    from .price_research import describe
    result['research'] = describe(result['bars'])
    result['cache'] = {'response_age_seconds':data.get('response_age_seconds'),
                       'freshness':data.get('freshness'),'last_refresh_error':data.get('last_refresh_error'),
                       'policy':'manual refresh;process-local eight-symbol cache;historical never promoted to LIVE'}
    return result
