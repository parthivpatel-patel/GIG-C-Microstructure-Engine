"""Exact, deliberately narrow paper-order contracts. Limit/day/integer shares only."""
from dataclasses import dataclass, asdict
import hashlib
import json
import re
from urllib.parse import urlencode

PAPER_HOST = 'https://paper-api.alpaca.markets'
ACTIVE = frozenset(('SUBMITTED', 'ACCEPTED', 'PARTIALLY_FILLED', 'CANCEL_REQUESTED',
                    'CANCEL_REJECTED', 'UNKNOWN'))
TERMINAL = frozenset(('FILLED', 'REJECTED', 'CANCELED', 'EXPIRED'))
STATES = ACTIVE | TERMINAL
MAX_ORDERS = 128
MAX_AUDIT = 2048


class PaperError(ValueError):
    """Finite public codes only;never broker text,headers or credential values."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def integer(value, low=0, high=10**12):
    if type(value) is not int or not low <= value <= high:
        raise PaperError('paper_integer_boundary')
    return value


def cents(value):
    if type(value) is not str or not re.fullmatch(r'(?:0|[1-9][0-9]{0,5})(?:\.[0-9]{1,2})?', value):
        raise PaperError('paper_exact_cent_price_required')
    a, _, b = value.partition('.')
    return integer(int(a) * 100 + int(b.ljust(2, '0') or '0'), 1, 100000000)


def intent(value):
    required = {'symbol', 'side', 'quantity', 'limit_price', 'type', 'time_in_force'}
    if type(value) is not dict or set(value) != required:
        raise PaperError('paper_intent_fields')
    if type(value['symbol']) is not str or not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?', value['symbol']):
        raise PaperError('paper_symbol')
    if value['side'] not in ('buy', 'sell') or value['type'] != 'limit' or value['time_in_force'] != 'day':
        raise PaperError('paper_limit_day_only')
    q = value['quantity']
    if type(q) is not str or not re.fullmatch(r'[1-9][0-9]{0,4}', q) or int(q) > 10000:
        raise PaperError('paper_integer_shares_required')
    p = cents(value['limit_price'])
    return {**value, 'limit_price': f'{p // 100}.{p % 100:02d}'}


def nonce(value):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', value):
        raise PaperError('paper_request_identity')
    return value


def client_id(profile, request_id, definition):
    return 'gatlas-paper-' + hashlib.sha256(canonical([profile, nonce(request_id), definition])).hexdigest()[:32]


def endpoint(method, path, base=PAPER_HOST):
    """Pure request construction;does not authenticate or open a connection."""
    if base != PAPER_HOST:
        raise PaperError('paper_live_or_dynamic_host_rejected')
    allowed = (method == 'GET' and path in ('/v2/account', '/v2/positions', '/v2/orders')) or (method == 'POST' and path == '/v2/orders')
    if not allowed:
        raise PaperError('paper_endpoint_rejected')
    return PAPER_HOST + path


def lookup_endpoint(identity):
    if type(identity) is not str or not re.fullmatch(r'gatlas-paper-[0-9a-f]{32}', identity):
        raise PaperError('paper_client_identity')
    return PAPER_HOST + '/v2/orders:by_client_order_id?' + urlencode({'client_order_id': identity})


@dataclass(frozen=True)
class RiskLimits:
    """Conservative EXAMPLE profile,never an owner-approved real-account limit."""
    max_order_cents: int = 10000
    max_position_cents: int = 50000
    max_gross_cents: int = 100000
    max_daily_loss_cents: int = 5000
    max_open_orders: int = 8
    max_snapshot_age_ms: int = 5000
    max_price_distance_bps: int = 500

    def __post_init__(self):
        for v in (self.max_order_cents, self.max_position_cents, self.max_gross_cents, self.max_daily_loss_cents):
            integer(v, 1, 10**9)
        integer(self.max_open_orders, 1, 8)
        integer(self.max_snapshot_age_ms, 1, 10000)
        integer(self.max_price_distance_bps, 1, 1000)

    def view(self):
        return {'profile': 'EXAMPLE_NOT_OWNER_APPROVED_FOR_BROKER', **asdict(self)}


@dataclass(frozen=True)
class ExecutionGate:
    enabled: bool = False
    owner_reviewed: bool = False
    limits_reviewed: bool = False
    reference: str = ''

    @classmethod
    def configured(cls, environment):
        # Non-secret independent execution policy only;never reads API credentials.
        return cls(*(environment.get('GIG_PAPER_' + key) == '1' for key in
                     ('EXECUTION_ENABLED', 'OWNER_REVIEWED', 'RISK_LIMITS_REVIEWED')),
                   environment.get('GIG_PAPER_PERMISSION_REFERENCE', ''))

    def require(self):
        if not (self.enabled is True and self.owner_reviewed is True and self.limits_reviewed is True
                and type(self.reference) is str and 1 <= len(self.reference) <= 160
                and all(32 <= ord(c) < 127 for c in self.reference)):
            raise PaperError('paper_execution_independently_disabled')
