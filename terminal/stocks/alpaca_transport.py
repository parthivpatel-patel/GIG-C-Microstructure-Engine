"""Fixed read-only Alpaca REST destinations; no account/order client exists here."""
import re
from urllib.parse import urlsplit, parse_qs
from .identity import SYMBOL_PATTERN

ASSETS = 'https://paper-api.alpaca.markets/v2/assets'
DATA = 'https://data.alpaca.markets/v2/stocks/'

def validate_url(url, provider):
    if type(url) is not str or len(url) > 4096:
        raise ValueError('alpaca_read_only_destination')
    u = urlsplit(url)
    if u.scheme != 'https' or u.username or u.password or u.fragment or u.port is not None:
        raise ValueError('alpaca_read_only_destination')
    q = parse_qs(u.query, keep_blank_values=True)
    if any(len(v) != 1 for v in q.values()):
        raise ValueError('alpaca_duplicate_query')
    if u.netloc == 'paper-api.alpaca.markets' and u.path == '/v2/assets':
        if provider != 'alpaca' or q not in ({'asset_class':['us_equity'],'status':['active']}, {'asset_class':['us_equity'],'status':['inactive']}):
            raise ValueError('alpaca_asset_reference_query')
        return 'array'
    symbol = '(?:' + SYMBOL_PATTERN.removeprefix('^').removesuffix('$') + ')'
    stocks = re.fullmatch(r'/v2/stocks/(?:(?:bars|quotes|trades)(?:/latest)?|' + symbol + r'/(?:bars|quotes|trades)(?:/latest)?)', u.path)
    options = re.fullmatch(r'/v1beta1/options/snapshots/' + symbol, u.path)
    if u.netloc != 'data.alpaca.markets' or not (stocks and provider == 'alpaca' or options and provider == 'options'):
        raise ValueError('alpaca_read_only_destination')
    if q.get('feed') != ['indicative' if options else 'iex']:
        raise ValueError('alpaca_feed_not_authorized')
    if 'adjustment' in q and q['adjustment'] != ['raw']:
        raise ValueError('alpaca_adjustment_profile')
    return 'object'
