"""Independent localhost REST/WS boundary checks against a running native gateway."""
import asyncio
import hashlib
import http.client
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

import websockets

BASE = 'http://127.0.0.1:8787'
ORIGIN = BASE
checks = []


def request(path, method='GET', body=None, headers=None):
    conn = http.client.HTTPConnection('127.0.0.1', 8787, timeout=5)
    encoded = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
    h = {'Origin': ORIGIN, 'Content-Type': 'application/json'} if method == 'POST' else {}
    if headers is not None:
        h.update(headers)
    conn.request(method, path, encoded, h)
    response = conn.getresponse(); value = response.read(2 * 1024 * 1024 + 1)
    assert len(value) <= 2 * 1024 * 1024
    status = response.status; result_headers = dict(response.getheaders()); conn.close()
    try: data = json.loads(value)
    except ValueError: data = None
    return status, data, result_headers


def check(name, fn):
    fn(); checks.append({'name': name, 'status': 'PASS'})


def state():
    status, value, _ = request('/api/v1/state'); assert status == 200
    return value


def command(action, value=None):
    data = {'action': action}
    if value is not None: data['value'] = value
    status, output, _ = request('/api/v1/control', 'POST', data)
    assert status == 200, output
    return output


def refused(name, body, expected=400, headers=None):
    before = state()
    status, value, _ = request('/api/v1/control', 'POST', body, headers)
    assert status == expected, (name, status, value)
    after = state()
    for key in ('position', 'mode', 'book', 'metrics'):
        assert after[key] == before[key], (name, key)


async def websocket_checks():
    async with websockets.connect('ws://127.0.0.1:8787/api/v1/stream', origin=ORIGIN, max_size=2*1024*1024) as ws:
        payload = json.loads(await asyncio.wait_for(ws.recv(), 3))
        assert payload['origin'] == 'HISTORICAL_SYNTHETIC'
        assert payload['engine']['native'] is True
        checks.append({'name': 'real WebSocket native state', 'status': 'PASS'})
    for origin in ('https://attacker.invalid', None):
        try:
            async with websockets.connect('ws://127.0.0.1:8787/api/v1/stream', origin=origin, open_timeout=3):
                raise AssertionError('unauthorized WebSocket admitted')
        except websockets.exceptions.InvalidStatus as exc:
            assert exc.response.status_code == 403
        checks.append({'name': f'WebSocket origin refused: {origin}', 'status': 'PASS'})


def run():
    command('mode', 'HISTORICAL_REPLAY'); command('restart')
    check('health real native', lambda: assert_health())
    check('HTTP Host rebinding rejected', lambda: assert_status(request('/api/v1/state', headers={'Host':'attacker.invalid'})[0], 400))
    check('POST foreign Origin refused atomically', lambda: refused('origin', {'action':'step'}, 403, {'Origin':'https://attacker.invalid'}))
    check('POST empty Origin refused atomically', lambda: refused('origin-empty', {'action':'step'}, 403, {'Origin':''}))
    check('unknown fields refused atomically', lambda: refused('field', {'action':'step','extra':True}))
    check('unknown action refused atomically', lambda: refused('action', {'action':'reset_everything'}))
    check('fractional speed refused atomically', lambda: refused('speed', {'action':'speed','value':0.5}))
    check('boolean speed refused atomically', lambda: refused('speed-bool', {'action':'speed','value':True}))
    check('duplicate JSON key refused atomically', lambda: refused('duplicate', b'{"action":"pause","action":"step"}'))
    check('invalid JSON constant refused atomically', lambda: refused('nan', b'{"action":"speed","value":NaN}'))
    check('oversized body refused before mutation', lambda: refused('body', b' ' * 4097, 413))
    check('non-JSON content refused', lambda: refused('content', b'action=step', 400, {'Content-Type':'text/plain'}))
    check('unknown API fails without static fallback', lambda: assert_status(request('/api/v1/not-real')[0],404))
    check('security headers present', lambda: assert_headers())
    asyncio.run(websocket_checks())
    command('restart')
    return {'schema':'gig.terminal.api_boundaries.v1','target':BASE,'origin':'HISTORICAL_SYNTHETIC','checks':checks,'summary':{'passed':len(checks),'failed':0,'skipped':0},'limitations':['Local single process only; no public deployment or live provider connection tested']}


def assert_status(actual, expected): assert actual == expected, (actual, expected)

def assert_health():
    status, value, _ = request('/api/v1/health'); assert status == 200
    assert value['native'] and not value['live_connected'] and not value['recording_enabled']

def assert_headers():
    _,_,h=request('/api/v1/state');lower={k.lower():v for k,v in h.items()}
    assert lower['x-content-type-options']=='nosniff'
    assert lower['cache-control']=='no-store'
    assert "frame-ancestors 'none'" in lower['content-security-policy']


if __name__=='__main__':
    result=run()
    if len(sys.argv)>1:
        output=Path(sys.argv[1]);output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
