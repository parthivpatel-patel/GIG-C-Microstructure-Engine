#!/usr/bin/env python3
"""Private Codespaces read-only IEX launcher and bounded owner qualification.

Default --check is offline. No credential values or market records are emitted.
--start and --qualify require an operator assertion of the private edge boundary.
"""
import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from terminal.stocks.private_iex import private_environment, readiness


def default_interval(now=None):
    day = (now or dt.datetime.now(dt.timezone.utc)).date() - dt.timedelta(days=1)
    while day.weekday() >= 5:
        day -= dt.timedelta(days=1)
    # A bounded liquid-time candidate, not an exchange holiday/session assertion.
    return f'{day}T14:30:00Z', f'{day}T14:35:00Z'


def refuse_existing_gateway():
    try:
        with socket.create_connection(('127.0.0.1', 8787), timeout=.5):
            pass
    except ConnectionRefusedError:
        return
    except OSError:
        raise ValueError('gateway_presence_unknown') from None
    raise ValueError('stop_existing_gateway_before_exclusive_qualification')


def safe_source_failure(error):
    from terminal.alpaca_wire import WireError
    status = error.status if isinstance(error, WireError) else None
    category = {401: 'AUTHENTICATION', 403: 'ENTITLEMENT',
                404: 'RANGE_OR_RESOURCE_UNAVAILABLE', 429: 'RATE_LIMIT'}.get(
                    status, 'SOURCE_CONFIGURATION_OR_VALIDATION')
    return {'status': 'BLOCKED_OR_REJECTED', 'category': category,
            'http_status': status if status in (401, 403, 404, 422, 429) else None,
            'raw_exception_disclosed': False}


async def qualify(environment, *, start, end, seconds):
    from terminal.alpaca_wire import HTTPWire
    from terminal.stocks.service import StockWorkspace
    from terminal.stocks.historical_v2 import (
        HistoricalClient, HistoricalPermission, validate_plan, validate_query)
    from terminal.stocks.qualification import collect_stream
    from terminal.stocks.live import LiveIEX
    workspace = StockWorkspace(environment=environment)
    permission = HistoricalPermission.configured(environment)
    wire = HTTPWire(lambda: permission.require('iex'),
                    lambda: workspace.permission('alpaca'), validate_plan)
    history = HistoricalClient(wire, permission=permission, identity=workspace.market_identity)
    stream = LiveIEX(workspace, retry_budget=1)
    query = dict(symbol='AAPL', feed='iex', start=start, end=end,
                 kind='bars', timeframe='1Min', adjustment='raw', max_pages=1)
    # Reject the entire plan before the first remote request, not after one read.
    if type(seconds) is not int or not 5 <= seconds <= 60:
        raise ValueError('qualification_window')
    validate_query(query, history.now_ns())
    workspace.permission('alpaca')
    stream.require()
    report = dict(schema='gig.private.iex.qualification.v1',
                  status='PENDING', symbol='AAPL', feed='iex', stages={},
                  raw_records_emitted=False, disk_capture_enabled=False,
                  execution_enabled=False, private_edge_verified=False)
    try:
        async with asyncio.timeout(120):
            for kind in ('bars', 'quotes', 'trades'):
                try:
                    result = await history.acquire({**query, 'kind': kind})
                    observed = result['origin'] == 'OBSERVED_OFFICIAL_RESPONSE'
                    report['stages'][kind] = {
                        'status': 'PASS_BOUNDED_OBSERVATIONS' if observed and result['record_count'] else 'INCONCLUSIVE_EMPTY_OR_UNOBSERVED',
                        'record_count': result['record_count'], 'origin': result['origin'],
                        'has_more': result['has_more'], 'complete_history': False,
                        'source_records': result['source_records'],
                        'canonical_sha256': result['canonical_sha256'],
                    }
                except (ValueError, TimeoutError) as error:
                    # Source values, query cursors, HTTP bodies and credentials stay private.
                    report['stages'][kind] = safe_source_failure(error)
                    if report['stages'][kind]['category'] in ('AUTHENTICATION', 'ENTITLEMENT'):
                        break  # Do not repeatedly authenticate after a definitive rejection.
            if any(s.get('category') in ('AUTHENTICATION', 'ENTITLEMENT')
                   for s in report['stages'].values()):
                report['stages']['stream'] = {'status': 'NOT_ATTEMPTED_SOURCE_ADMISSION_REJECTION'}
            else:
                report['stages']['stream'] = await collect_stream(stream, ['AAPL'], seconds)
            passed = all(s.get('status', '').startswith('PASS_') for s in report['stages'].values())
            report['status'] = 'PASS_BOUNDED_PROVIDER_READS_ONLY' if passed else 'INCOMPLETE_OR_BLOCKED'
    finally:
        await stream.close()
        await workspace.close()
    report['limits'] = {'wall_seconds': 120, 'history_physical_rows': 192,
                        'history_http_attempts': 9, 'upstream_stream_opens': 1,
                        'websocket_frame_bytes': 32768, 'retained_stream_events': 256}
    report['scope'] = 'IEX only;not NBBO,full market tape,L2/L3,exchange comparison or private-edge certification'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true')
    modes.add_argument('--start', action='store_true')
    modes.add_argument('--qualify', action='store_true')
    parser.add_argument('--confirm-private-single-user', action='store_true')
    parser.add_argument('--exclusive-stream-window', action='store_true')
    parser.add_argument('--start-time')
    parser.add_argument('--end-time')
    parser.add_argument('--seconds', type=int, choices=range(5, 61), default=30)
    args = parser.parse_args()
    if not args.start and not args.qualify:
        status = readiness(os.environ)
        print(json.dumps(status, sort_keys=True))
        return 0 if status['ready'] else 2
    try:
        environment = private_environment(os.environ, confirm_private=args.confirm_private_single_user)
        from terminal.stocks.live import secure_msgpack
        secure_msgpack()
        if args.qualify:
            if not args.exclusive_stream_window:
                raise ValueError('exclusive_shared_account_stream_window_required')
            refuse_existing_gateway()
            start, end = default_interval()
            if (args.start_time is None) != (args.end_time is None):
                raise ValueError('both_interval_boundaries_required')
            report = asyncio.run(qualify(environment, start=args.start_time or start,
                                       end=args.end_time or end, seconds=args.seconds))
            print(json.dumps(report, sort_keys=True, indent=2))
            return 0 if report['status'] == 'PASS_BOUNDED_PROVIDER_READS_ONLY' else 2
        # Fixed existing startup path: dependency/native/assets checks remain in force.
        os.execve('/bin/bash', ['bash', str(ROOT / 'scripts/start_terminal.sh')], environment)
    except Exception:
        # Last integration boundary: never echo third-party exception text,
        # provider URLs/bodies, contact strings or credential-bearing context.
        print(json.dumps({'schema': 'gig.private.iex.failure.v1', 'status': 'BLOCKED_OR_REJECTED',
                          'reason': 'private_scope_configuration_dependencies_or_source_probe',
                          'raw_records_emitted': False, 'credential_values_emitted': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
