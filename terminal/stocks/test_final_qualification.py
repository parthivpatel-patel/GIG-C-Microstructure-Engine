"""Independent offline final-candidate regressions; no provider connections."""
import asyncio
import unittest
from unittest.mock import patch

from .service import StockWorkspace
from .live import LiveIEX
from .test_repair import ENV


class IEXAdmission(unittest.TestCase):
    def test_distinct_read_only_stream_gate_does_not_need_legacy_live_flag(self):
        environment = {**ENV, 'GIG_ALPACA_LIVE_ENABLED': '0',
                       'GIG_PAPER_EXECUTION_ENABLED': '0',
                       'GIG_ALPACA_IEX_STREAM_ENABLED': '1'}
        stream = LiveIEX(StockWorkspace(environment=environment))
        self.assertEqual(set(stream.require()), {'APCA-API-KEY-ID', 'APCA-API-SECRET-KEY'})
        self.assertEqual(environment['GIG_ALPACA_LIVE_ENABLED'], '0')
        self.assertEqual(environment['GIG_PAPER_EXECUTION_ENABLED'], '0')

    def test_explicit_new_gate_off_overrides_legacy_on(self):
        stream = LiveIEX(StockWorkspace(environment={**ENV,
            'GIG_ALPACA_LIVE_ENABLED': '1', 'GIG_ALPACA_IEX_STREAM_ENABLED': '0'}))
        with self.assertRaisesRegex(ValueError, 'live_explicit_enable_required'):
            stream.require()

    def test_invalid_new_boolean_never_falls_back(self):
        for value in ('true', '', 'yes', '2', None):
            with self.subTest(value=value):
                stream = LiveIEX(StockWorkspace(environment={**ENV,
                    'GIG_ALPACA_LIVE_ENABLED': '1', 'GIG_ALPACA_IEX_STREAM_ENABLED': value}))
                with self.assertRaises(ValueError):
                    stream.require()

    def test_new_gate_cannot_grant_base_permissions(self):
        stream = LiveIEX(StockWorkspace(environment={'GIG_ALPACA_IEX_STREAM_ENABLED': '1'}))
        with self.assertRaises(ValueError):
            stream.require()

    def test_legacy_configuration_remains_compatible_if_new_gate_absent(self):
        stream = LiveIEX(StockWorkspace(environment={**ENV, 'GIG_ALPACA_LIVE_ENABLED': '1'}))
        self.assertEqual(len(stream.require()), 2)


class RetryArithmetic(unittest.TestCase):
    def test_independent_exponential_endpoints(self):
        from .retry import retry_delay
        for attempt, expected in enumerate((2, 4, 8, 16, 30), 1):
            self.assertEqual(retry_delay(attempt, random_source=lambda: 0), expected / 2)
            self.assertEqual(retry_delay(attempt, random_source=lambda: 1), expected)
            self.assertEqual(retry_delay(attempt, random_source=lambda: .25), expected * .625)

    def test_retry_after_floor_never_exceeds_budget(self):
        from .retry import retry_delay
        for sample in (0, .5, 1):
            self.assertEqual(retry_delay(1, minimum=5, ceiling=5, random_source=lambda: sample), 5)
            self.assertGreaterEqual(retry_delay(2, minimum=3, ceiling=5, random_source=lambda: sample), 3)

    def test_invalid_attempts_reject(self):
        from .retry import retry_delay
        for attempt in (True, 0, -1, 6, 1.5):
            with self.assertRaises(ValueError):
                retry_delay(attempt)

    def test_invalid_bounds_reject_before_randomness(self):
        from .retry import retry_delay
        for low, high in ((6, 5), (-1, 5), (0, 31), (0, 0), (float('nan'), 5), (0, float('inf'))):
            with self.assertRaises(ValueError):
                retry_delay(1, minimum=low, ceiling=high,
                            random_source=lambda: self.fail('invalid budget sampled'))

    def test_invalid_samples_reject(self):
        from .retry import retry_delay
        for value in (-.01, 1.01, True, None, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                retry_delay(1, random_source=lambda: value)


PRIVATE = {'CODESPACES': 'true', 'CODESPACE_NAME': 'authored-private-candidate'}


class PrivateProfile(unittest.TestCase):
    def profile(self, **changes):
        from .private_iex import private_environment
        return private_environment({**ENV, **PRIVATE, **changes}, confirm_private=True)

    def test_confirmation_required_without_reading_credentials(self):
        from .private_iex import private_environment
        with self.assertRaisesRegex(ValueError, 'confirmation_required'):
            private_environment({})

    def test_codespace_metadata_required(self):
        from .private_iex import private_environment
        with self.assertRaisesRegex(ValueError, 'codespace_required'):
            private_environment(ENV, confirm_private=True)
        with self.assertRaises(ValueError):
            self.profile(CODESPACE_NAME='bad/name')

    def test_only_exact_origin_allowed(self):
        for origin in ('https://attacker.invalid', '*',
                       'https://authored-private-candidate-8787.app.github.dev,https://attacker.invalid'):
            with self.assertRaises(ValueError):
                self.profile(GIG_TERMINAL_ALLOWED_ORIGINS=origin)

    def test_broker_and_retention_overrides_are_fail_closed(self):
        profile = self.profile(GIG_ALPACA_LIVE_ENABLED='1', GIG_PAPER_EXECUTION_ENABLED='1',
                               GIG_ALPACA_STORE_ENABLED='1', GIG_HISTORY_STORE_ENABLED='1',
                               GIG_ALPACA_OPTIONS_ENABLED='1')
        for key in ('GIG_ALPACA_LIVE_ENABLED', 'GIG_PAPER_EXECUTION_ENABLED',
                    'GIG_ALPACA_STORE_ENABLED', 'GIG_HISTORY_STORE_ENABLED',
                    'GIG_ALPACA_HISTORY_EXPORT_APPROVED', 'GIG_ALPACA_OPTIONS_ENABLED',
                    'GIG_ALPACA_HISTORY_SIP_APPROVED'):
            self.assertEqual(profile[key], '0')
        self.assertEqual(profile['GIG_ALPACA_IEX_STREAM_ENABLED'], '1')
        self.assertEqual(LiveIEX(StockWorkspace(environment=profile)).require(),
                         StockWorkspace(environment=profile).permission('alpaca'))

    def test_input_not_mutated_and_sec_settings_preserved(self):
        from .private_iex import private_environment
        original = {**ENV, **PRIVATE, 'GIG_SEC_ENABLED': '1',
                    'GIG_SEC_USER_AGENT': 'AUTHORED_CONTACT_NOT_AN_OWNER_VALUE'}
        before = original.copy()
        profile = private_environment(original, confirm_private=True)
        self.assertEqual(original, before)
        self.assertEqual(profile['GIG_SEC_USER_AGENT'], original['GIG_SEC_USER_AGENT'])
        self.assertEqual(profile['GIG_SEC_ENABLED'], '1')

    def test_no_credential_configuration_is_invented(self):
        from .private_iex import private_environment
        with self.assertRaisesRegex(ValueError, 'server_credentials_required'):
            private_environment(PRIVATE, confirm_private=True)

    def test_ready_does_not_claim_provider_or_private_authentication(self):
        from .private_iex import readiness
        value = readiness({**ENV, **PRIVATE})
        self.assertTrue(value['ready'])
        self.assertFalse(value['provider_verified'])
        self.assertFalse(value['private_port_verified'])
        self.assertFalse(value['execution_enabled'])
        self.assertEqual(value['network_requests'], 0)
        import json
        public = json.dumps(value)
        for key in ('ALPACA_API_KEY_ID', 'ALPACA_API_SECRET_KEY'):
            if ENV.get(key):
                self.assertNotIn(ENV[key], public)

    def test_invalid_configuration_errors_do_not_echo_values(self):
        from .private_iex import readiness
        value = readiness({**ENV, **PRIVATE, 'CODESPACE_NAME': 'SECRET_INVALID/name'})
        self.assertFalse(value['ready'])
        self.assertNotIn('SECRET_INVALID', str(value))

    def test_history_permission_is_iex_only(self):
        from .historical_v2 import HistoricalPermission
        permission = HistoricalPermission.configured(self.profile())
        permission.require('iex')
        with self.assertRaises(ValueError):
            permission.require('sip')


class AsyncReliability(unittest.IsolatedAsyncioTestCase):
    async def test_stream_uses_injected_jitter_and_finite_retry_budget(self):
        stream = LiveIEX(StockWorkspace(environment={**ENV, 'GIG_ALPACA_IEX_STREAM_ENABLED': '1'}),
                         connector=lambda *_a, **_k: (_ for _ in ()).throw(OSError()),
                         random_source=lambda: .25, retry_budget=3)
        delays = []
        async def timed_out(waiter, timeout):
            delays.append(timeout)
            waiter.close()
            raise TimeoutError()
        with patch('terminal.stocks.live.asyncio.wait_for', side_effect=timed_out):
            await stream.run()
        self.assertEqual(delays, [1.25, 2.5])
        self.assertEqual(stream.failures, 3)
        self.assertEqual(stream.reason, 'retry_budget_exhausted')
        self.assertIsNone(stream.socket)
        self.assertEqual(stream.phase, 'DISCONNECTED')

    async def test_history_429_jitter_and_retry_after_floor(self):
        from .historical_v2 import HistoricalClient
        from .test_sprint4_history import Clock, PERMISSION, QUERY, response, bar
        from terminal.alpaca_wire import FixtureWire
        clock = Clock()
        queue = [response({}, 429, {'retry-after': '2'}), response({}, 429),
                 response({'bars': {'AAPL': [bar()]}})]
        wire = FixtureWire(lambda *_: queue.pop(0))
        client = HistoricalClient(wire, permission=PERMISSION, clock=clock.time,
                                  monotonic=clock.monotonic, sleep=clock.sleep,
                                  random_source=lambda: .25)
        value = await client.acquire(QUERY)
        self.assertEqual(value['record_count'], 1)
        self.assertEqual(len(wire.calls), 3)
        self.assertIn(2, clock.waits)
        self.assertIn(2.5, clock.waits)
        self.assertEqual(value['origin'], 'HISTORICAL_SYNTHETIC')

    async def test_permission_revocation_after_backoff_prevents_next_http(self):
        from .historical_v2 import HistoricalClient, HistoricalPermission
        from .test_sprint4_history import Clock, PERMISSION, QUERY, response
        from terminal.alpaca_wire import FixtureWire
        clock = Clock()
        wire = FixtureWire(lambda *_: response({}, 429))
        client = HistoricalClient(wire, permission=PERMISSION, clock=clock.time,
                                  monotonic=clock.monotonic, random_source=lambda: 0)
        async def revoke(seconds):
            await clock.sleep(seconds)
            client.permission = HistoricalPermission()
        client.sleep = revoke
        with self.assertRaises(ValueError):
            await client.acquire(QUERY)
        self.assertEqual(len(wire.calls), 1)
        self.assertFalse(client.cache)
        self.assertFalse(client.lock.locked())

    async def test_cancel_backoff_does_not_open_another_stream(self):
        reached = asyncio.Event()
        async def wait():
            reached.set()
            await asyncio.Event().wait()
        stream = LiveIEX(StockWorkspace(environment={**ENV, 'GIG_ALPACA_IEX_STREAM_ENABLED': '1'}),
                         connector=lambda *_a, **_k: (_ for _ in ()).throw(OSError()))
        with patch.object(stream.stop_event, 'wait', side_effect=wait):
            stream.task = asyncio.create_task(stream.run())
            await reached.wait()
            await stream.close()
        self.assertEqual(stream.failures, 1)
        self.assertEqual(stream.state, 'STOPPED')
        self.assertIsNone(stream.task)


class OwnerTool(unittest.TestCase):
    def test_default_history_interval_is_bounded_without_calendar_claim(self):
        import datetime as dt
        from scripts.private_iex import default_interval
        self.assertEqual(default_interval(dt.datetime(2026, 11, 2, tzinfo=dt.timezone.utc)),
                         ('2026-10-30T14:30:00Z', '2026-10-30T14:35:00Z'))

    def test_default_command_is_offline_and_redacted(self):
        import contextlib, io, json
        from scripts import private_iex as cli
        with patch('sys.argv', ['private_iex']), patch.dict('os.environ', {}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(), 2)
        value = json.loads(output.getvalue())
        self.assertEqual(value['network_requests'], 0)
        self.assertFalse(value['ready'])

    def test_launcher_only_executes_existing_startup_with_safe_environment(self):
        from scripts import private_iex as cli
        with patch('sys.argv', ['private_iex', '--start', '--confirm-private-single-user']), \
                patch.dict('os.environ', {**ENV, **PRIVATE}, clear=True), \
                patch.object(cli.os, 'execve', side_effect=SystemExit('TEST_EXEC_INTERCEPT')) as execute:
            with self.assertRaisesRegex(SystemExit, 'TEST_EXEC_INTERCEPT'):
                cli.main()
        path, args, environment = execute.call_args.args
        self.assertEqual(path, '/bin/bash')
        self.assertTrue(args[1].endswith('/scripts/start_terminal.sh'))
        self.assertEqual(environment['GIG_ALPACA_LIVE_ENABLED'], '0')
        self.assertEqual(environment['GIG_PAPER_EXECUTION_ENABLED'], '0')

    def test_qualification_requires_exclusive_window_before_any_socket(self):
        from scripts import private_iex as cli
        import contextlib, io
        with patch('sys.argv', ['private_iex', '--qualify', '--confirm-private-single-user']), \
                patch.dict('os.environ', {**ENV, **PRIVATE}, clear=True), \
                patch.object(cli.socket, 'create_connection', side_effect=AssertionError('must not connect')), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(), 2)

    def test_existing_gateway_prevents_standalone_provider_qualification(self):
        from scripts.private_iex import refuse_existing_gateway
        with patch('socket.create_connection'):
            with self.assertRaisesRegex(ValueError, 'stop_existing_gateway'):
                refuse_existing_gateway()

    def test_uncertain_gateway_state_fails_closed(self):
        from scripts.private_iex import refuse_existing_gateway
        with patch('socket.create_connection', side_effect=TimeoutError()):
            with self.assertRaisesRegex(ValueError, 'presence_unknown'):
                refuse_existing_gateway()

    def test_invalid_qualification_plan_opens_no_transport(self):
        from scripts.private_iex import qualify
        from .private_iex import private_environment
        environment = private_environment({**ENV, **PRIVATE}, confirm_private=True)
        with patch('terminal.alpaca_wire.HTTPWire.send', side_effect=AssertionError('no provider')):
            with self.assertRaises(ValueError):
                asyncio.run(qualify(environment, start='bad', end='bad', seconds=5))

    def test_native_arm_workflow_remains_manual_and_owner_gated(self):
        from pathlib import Path
        workflow = (Path(__file__).resolve().parents[2] / '.github/workflows/native-arm64.yml').read_text()
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('inputs.free_usage_verified', workflow)
        self.assertIn('refs/heads/development/gig-ui-redesign', workflow)
        self.assertNotIn('pull_request:', workflow)
        self.assertNotIn('\n  push:', workflow)
        self.assertIn('ubuntu-24.04-arm', workflow)


class QualificationIntegrity(unittest.IsolatedAsyncioTestCase):
    async def test_fixture_results_never_qualify_live_provider(self):
        from scripts.private_iex import qualify
        from .private_iex import private_environment
        from unittest.mock import AsyncMock
        fixture = dict(origin='HISTORICAL_SYNTHETIC', record_count=1, has_more=False,
                       source_records=[{'sha256': 'a' * 64}], canonical_sha256='b' * 64)
        environment = private_environment({**ENV, **PRIVATE}, confirm_private=True)
        with patch('terminal.stocks.historical_v2.HistoricalClient.acquire',
                   new=AsyncMock(return_value=fixture)), \
             patch('terminal.stocks.qualification.collect_stream',
                   new=AsyncMock(return_value={'status': 'INCONCLUSIVE_OR_FAILED_STREAM_WINDOW'})), \
             patch('terminal.alpaca_wire.HTTPWire.send', side_effect=AssertionError('no provider')):
            report = await qualify(environment, start='2024-01-02T14:30:00Z',
                                   end='2024-01-02T14:35:00Z', seconds=5)
        self.assertEqual(report['status'], 'INCOMPLETE_OR_BLOCKED')
        self.assertEqual(len(report['stages']), 4)
        self.assertFalse(report['raw_records_emitted'])
        self.assertFalse(report['private_edge_verified'])

    async def test_unexpected_probe_failure_closes_both_resources(self):
        from scripts.private_iex import qualify
        from .private_iex import private_environment
        from unittest.mock import AsyncMock
        environment = private_environment({**ENV, **PRIVATE}, confirm_private=True)
        with patch('terminal.stocks.historical_v2.HistoricalClient.acquire',
                   new=AsyncMock(side_effect=RuntimeError('AUTHORED_FAIL'))), \
             patch('terminal.stocks.live.LiveIEX.close', new_callable=AsyncMock) as close, \
             patch('terminal.stocks.service.StockWorkspace.close', new_callable=AsyncMock) as workspace_close:
            with self.assertRaisesRegex(RuntimeError, 'AUTHORED_FAIL'):
                await qualify(environment, start='2024-01-02T14:30:00Z',
                              end='2024-01-02T14:35:00Z', seconds=5)
        close.assert_awaited_once()
        workspace_close.assert_awaited_once()


class SanitizedBoundary(unittest.TestCase):
    def test_unexpected_qualification_exception_cannot_echo_provider_context(self):
        import contextlib, io
        from scripts import private_iex as cli
        async def failure(*_a, **_k):
            raise RuntimeError('AUTHORED_CREDENTIAL_MUST_NOT_APPEAR')
        with patch('sys.argv', ['private_iex', '--qualify', '--confirm-private-single-user',
                                '--exclusive-stream-window']), \
                patch.dict('os.environ', {**ENV, **PRIVATE}, clear=True), \
                patch.object(cli, 'refuse_existing_gateway'), \
                patch.object(cli, 'qualify', side_effect=failure), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main(), 2)
        self.assertNotIn('AUTHORED_CREDENTIAL_MUST_NOT_APPEAR', output.getvalue())
        self.assertIn('BLOCKED_OR_REJECTED', output.getvalue())


class SourceCategories(unittest.IsolatedAsyncioTestCase):
    async def test_source_rejection_is_distinct_redacted_and_prevents_more_authentication(self):
        from scripts.private_iex import qualify, safe_source_failure
        from .private_iex import private_environment
        from terminal.alpaca_wire import WireError
        from unittest.mock import AsyncMock
        for status, category in ((401, 'AUTHENTICATION'), (403, 'ENTITLEMENT'),
                                 (404, 'RANGE_OR_RESOURCE_UNAVAILABLE'), (429, 'RATE_LIMIT')):
            error = WireError('AUTHORED_SECRET_CONTEXT', status=status)
            value = safe_source_failure(error)
            self.assertEqual(value['category'], category)
            self.assertNotIn('AUTHORED_SECRET_CONTEXT', str(value))
        environment = private_environment({**ENV, **PRIVATE}, confirm_private=True)
        with patch('terminal.stocks.historical_v2.HistoricalClient.acquire',
                   new=AsyncMock(side_effect=WireError('private', status=401))) as acquire, \
                patch('terminal.stocks.qualification.collect_stream',
                      side_effect=AssertionError('no further authentication')):
            report = await qualify(environment, start='2024-01-02T14:30:00Z',
                                   end='2024-01-02T14:35:00Z', seconds=5)
        self.assertEqual(acquire.await_count, 1)
        self.assertEqual(report['status'], 'INCOMPLETE_OR_BLOCKED')
        self.assertEqual(report['stages']['bars']['category'], 'AUTHENTICATION')
