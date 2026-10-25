"""Local-first versioned API, one native owner, bounded latest-state WebSocket output."""
import asyncio
from contextlib import asynccontextmanager, suppress
import json
import os
import re
import ipaddress
from pathlib import Path
import time
from urllib.parse import urlsplit

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import WebSocketRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .engine import ControlError, NativeSession
from .config import launch_settings
from .connection import observation, origin_value
from .stream_tickets import StreamTickets, authorize_socket, PROTOCOL
from .request_proofs import RequestProofs, bootstrap_context, authorize_mutation
import gig_microstructure as gig

MAX_BODY = 4096
MAX_CLIENTS = 8
SEND_TIMEOUT = 2.0
ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'terminal' / 'web' / 'dist'
DEFAULT_ORIGINS = ('http://127.0.0.1:5173', 'http://localhost:5173',
                   'http://127.0.0.1:8787', 'http://localhost:8787')


def origins_from_environment():
    # Resolve here too: uvicorn terminal.server.app:app does not run __main__.
    _, configured, _ = launch_settings(os.environ)
    origins = tuple(x.strip() for x in (configured if configured is not None else ','.join(DEFAULT_ORIGINS)).split(',') if x.strip())
    if not origins or len(origins) > 8:
        raise RuntimeError('configure one to eight explicit GIG_TERMINAL_ALLOWED_ORIGINS')
    for origin in origins:
        u = urlsplit(origin)
        if any(ord(c) < 33 or ord(c) > 126 for c in origin):
            raise RuntimeError('origin must contain printable ASCII without whitespace')
        try:
            port = u.port
        except ValueError:
            raise RuntimeError('invalid origin port') from None
        if port is not None and not 1 <= port <= 65535:
            raise RuntimeError('invalid origin port')
        if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.path or u.query or u.fragment or '*' in origin:
            raise RuntimeError('origins must be exact http(s) origins, without wildcard/credentials/path')
        host = u.hostname
        if not re.fullmatch(r'[A-Za-z0-9.-]+', host):
            try: ipaddress.ip_address(host)
            except ValueError: raise RuntimeError('invalid origin hostname') from None
    return origins


def content_security_policy(origins):
    # Explicit WS equivalents avoid browser differences in connect-src 'self'.
    connections = ["'self'"]
    for origin in origins:
        u = urlsplit(origin)
        connections.extend((origin, ('wss' if u.scheme == 'https' else 'ws') + '://' + u.netloc))
    return ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src " + ' '.join(dict.fromkeys(connections)) +
            "; frame-ancestors 'none'; base-uri 'none'; object-src 'none'")


def error(code, message, status=400):
    return JSONResponse({'schema_version': '1', 'error': {'code': code, 'message': message}}, status_code=status)


async def bounded_json(request):
    if request.headers.get('content-type', '').split(';')[0] != 'application/json':
        raise ControlError('CONTENT_TYPE', 'application/json required')
    data = bytearray()
    try:
        async with asyncio.timeout(5):
            async for chunk in request.stream():
                if len(data) + len(chunk) > MAX_BODY:
                    raise ControlError('BODY_LIMIT', 'request exceeds 4096 bytes')
                data.extend(chunk)
    except asyncio.TimeoutError:
        raise ControlError('BODY_TIMEOUT', 'request body deadline exceeded') from None
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate key')
            result[key] = value
        return result
    try:
        value = json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))
    except (ValueError, UnicodeError, RecursionError):
        raise ControlError('INVALID_JSON', 'invalid JSON document') from None
    if type(value) is not dict:
        raise ControlError('INVALID_JSON', 'JSON object required')
    return value


def json_endpoint(function):
    # Uniform exact JSON transport; bodies remain hand-validated and bounded.
    async def endpoint(request):
        result = await function(request)
        return result if isinstance(result, Response) else JSONResponse(result)
    return endpoint


def create_app():
    origins = origins_from_environment()
    _, _, expected_codespaces_origin = launch_settings(os.environ)
    connections = {'last_mutation': None, 'last_websocket': None, 'last_browser_bootstrap': None, 'last_authenticated_websocket': None, 'last_request_proof_bootstrap': None}
    stream_tickets = StreamTickets()
    request_proofs = RequestProofs()
    native = NativeSession()
    from terminal.providers.supervisor import FeedSupervisor
    feed = FeedSupervisor()
    native.live_feed = feed
    lock = asyncio.Lock()
    work_lock = asyncio.Lock()
    l2_directory=Path(os.environ.get('GIG_TERMINAL_L2_RECORDINGS',str(ROOT/'terminal'/'recordings'/'l2')))
    def observed_processing_allowed():
        from terminal.providers.supervisor import configured_permission
        from terminal.providers.kraken import ProviderError
        try:configured_permission(os.environ).require_live();return True
        except ProviderError:return False
    # Aggregate operation rate bound, including all connected browser clients.
    last_actions = []

    async def replay_loop():
        while True:
            await asyncio.sleep(0.1)
            async with lock:
                if native.playing and native.mode == 'HISTORICAL_REPLAY':
                    try:
                        for _ in range(native.speed):
                            if not native.step():
                                break
                    except gig.EngineError as exc:
                        native.playing = False
                        native.notifications.append({'code': 'NATIVE_REPLAY_REJECTED', 'message': f'{exc.code_name}: {exc.field}'})

    async def retention_loop():
        from terminal.l2_playback import prune_expired
        while True:
            if not work_lock.locked():
                async with work_lock:
                    try:
                        active=feed.capture.writer.stage if feed.capture and not feed.capture.task.done() else None
                        await asyncio.to_thread(prune_expired,l2_directory,active_stage=active)
                    except (ValueError,OSError):
                        native.notifications.append({'code':'RETENTION_CLEANUP_FAILED','message':'Bounded recording retention cleanup refused; inspect private storage locally.'})
            await asyncio.sleep(60)

    @asynccontextmanager
    async def lifespan(app):
        worker = asyncio.create_task(replay_loop())
        retention = asyncio.create_task(retention_loop())
        try:
            yield
        finally:
            await feed.close()
            retention.cancel()
            with suppress(asyncio.CancelledError):await retention
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker

    app = Starlette(lifespan=lifespan)
    app.state.native = native
    allowed_hosts = sorted({'127.0.0.1', 'localhost', '[::1]'} | {urlsplit(x).hostname for x in origins})
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    app.add_middleware(CORSMiddleware, allow_origins=list(origins), allow_methods=['GET', 'POST'],
                       allow_headers=['Content-Type'], allow_credentials=False)

    async def boundary(request, call_next):
        if request.method == 'POST':
            authorized_origin, decision = authorize_mutation(request.headers,request.url.path,origins,expected_codespaces_origin,request_proofs)
            connections['last_mutation'] = {**observation(request), 'decision':'allowed' if authorized_origin else 'rejected_origin',
                'authorization':decision,'authorized_browser_origin':authorized_origin,
                'failure_condition':None if authorized_origin else decision}
            if authorized_origin is None:
                native.rejected += 1
                return error('ORIGIN_DENIED', 'exact configured Origin or valid endpoint-bound same-origin proof required', 403)
            request.state.authorized_browser_origin = authorized_origin
        if request.method == 'POST':
            try:
                declared = int(request.headers.get('content-length', '0'))
            except ValueError:
                return error('BODY_LIMIT', 'invalid content length', 413)
            if declared < 0 or declared > MAX_BODY:
                return error('BODY_LIMIT', 'request exceeds 4096 bytes', 413)
            now = time.monotonic()
            last_actions[:] = [x for x in last_actions if now - x < 1.0]
            if len(last_actions) >= 30:
                native.rejected += 1
                return error('RATE_LIMIT', 'maximum 30 mutations/second across session', 429)
            last_actions.append(now)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = content_security_policy(origins)
        return response

    async def control_error(request, exc):
        native.rejected += 1
        return error(exc.code, str(exc), 413 if exc.code == 'BODY_LIMIT' else 400)

    async def native_error(request, exc):
        native.rejected += 1
        return error('NATIVE_REJECTION', f'{exc.code_name}: {exc.field}', 422)

    app.add_middleware(BaseHTTPMiddleware, dispatch=boundary)
    app.add_exception_handler(ControlError, control_error)
    app.add_exception_handler(gig.EngineError, native_error)

    def route(path, methods):
        def register(function):
            app.add_route(path, function, methods=methods)
            return function
        return register

    def websocket_route(path):
        def register(function):
            app.router.routes.append(WebSocketRoute(path, endpoint=function))
            return function
        return register

    @route('/api/v1/health', methods=['GET'])
    @json_endpoint
    async def health(request):
        return {'schema_version': '1', 'status': 'ok', 'native': True, 'engine': gig.native_build_info(),
                'live_connected': False, 'recording_enabled': False, 'maximum_clients': MAX_CLIENTS}

    @route('/api/v1/state', methods=['GET'])
    @json_endpoint
    async def state(request):
        async with lock:
            return native.state()

    @route('/api/v1/schema', methods=['GET'])
    @json_endpoint
    async def schema(request):
        return json.loads((Path(__file__).resolve().parents[1] / 'contracts/state.schema.json').read_text())

    @route('/api/v1/connection', methods=['GET'])
    @json_endpoint
    async def connection_status(request):
        return {
            'schema_version': '1',
            'policy_version': 'codespaces-request-proof-v4',
            'expected_codespaces_origin': expected_codespaces_origin,
            'configured_origins': list(origins),
            'request': observation(request),
            'last_mutation': connections['last_mutation'],
            'last_websocket': connections['last_websocket'],
            'last_browser_bootstrap': connections['last_browser_bootstrap'],
            'last_request_proof_bootstrap': connections['last_request_proof_bootstrap'],
            'last_authenticated_websocket': connections['last_authenticated_websocket'],
            'connected_clients': native.clients,
            'maximum_clients': MAX_CLIENTS,
            'authority': 'Exact Origin or endpoint-bound same-origin proof;forwarded headers never grant authority',
            'privacy': 'Bounded connection/browser context and public attempt ID;no cookies,tickets,client IP or arbitrary headers',
        }

    @route('/api/v1/request-proof', methods=['GET'])
    @json_endpoint
    async def request_proof(request):
        context, decision = bootstrap_context(request.headers,origins,expected_codespaces_origin)
        connections['last_request_proof_bootstrap'] = {**observation(request),
            'reported_browser_origin':origin_value(request.headers.get('x-gig-browser-origin')),
            'browser_origin':context['origin'] if context else None,
            'target':context['target'] if context else None,'decision':decision,
            'fetch_site':request.headers.get('sec-fetch-site') if request.headers.get('sec-fetch-site') in ('same-origin','same-site','cross-site','none') else None}
        if context is None:return error('BOOTSTRAP_DENIED','same-origin non-simple read context required',403)
        try: proof = request_proofs.issue(context['origin'],context['target'])
        except ValueError:return error('BOOTSTRAP_BUSY','bounded request proof capacity reached',429)
        return JSONResponse({'schema_version':'1','proof':proof,'expires_in_seconds':30},
            headers={'Cache-Control':'no-store','Cross-Origin-Resource-Policy':'same-origin','X-Content-Type-Options':'nosniff'})

    @route('/api/v1/stream-ticket', methods=['POST'])
    @json_endpoint
    async def stream_ticket(request):
        # Boundary proves exact Origin or a one-use endpoint-scoped read capability.
        data = await bounded_json(request)
        origin = request.state.authorized_browser_origin
        expected_url = ('wss' if origin.startswith('https:') else 'ws') + origin[origin.index(':'):] + '/api/v1/stream'
        connections['last_browser_bootstrap'] = {**observation(request),
            'browser_origin': origin_value(data.get('browser_origin')) if type(data.get('browser_origin')) is str else '<invalid>',
            'websocket_url': expected_url if data.get('websocket_url') == expected_url else '<mismatch>',
            'authorized_browser_origin':origin,
            'attempt_id': data.get('attempt_id') if type(data.get('attempt_id')) is str and re.fullmatch(r'[a-f0-9-]{36}',data['attempt_id']) else '<invalid>',
            'decision':'rejected_context'}
        if (set(data) != {'browser_origin','websocket_url','attempt_id'}
                or data['browser_origin'] != origin or data['websocket_url'] != expected_url
                or type(data['attempt_id']) is not str
                or not re.fullmatch(r'[a-f0-9-]{36}',data['attempt_id'])):
            raise ControlError('INVALID_STREAM_BOOTSTRAP','browser context must match the exact configured HTTP Origin')
        try: ticket = stream_tickets.issue(origin,data['attempt_id'])
        except ValueError: return error('STREAM_BUSY','bounded stream proof capacity reached;retry after expiry',429)
        connections['last_browser_bootstrap'] = {**observation(request),
            'authorized_browser_origin':origin,'browser_origin':data['browser_origin'],'websocket_url':data['websocket_url'],
            'attempt_id':data['attempt_id'],'decision':'issued'}
        # Ticket is never logged/retained in diagnostics,URL,DOM or local storage.
        return {'schema_version':'1','ticket':ticket,'protocol':PROTOCOL,'expires_in_seconds':30}

    @route('/api/v1/catalog', methods=['GET'])
    @json_endpoint
    async def catalog(request):
        result=native.catalog()
        provider=result['providers'][0]
        provider['instruments']=['BTC/USD','ETH/USD'];provider['depth']=10
        provider['runtime_state']=feed.state
        provider['live_connected']=feed.state=='LIVE_VERIFIED'
        if feed.permission is not None:
            provider['status']='OPERATOR_CONFIGURED'
            provider['reason']='Server-side protocol/usage attestation; runtime state reports actual connectivity separately.'
        return result

    @route('/api/v1/control', methods=['POST'])
    @json_endpoint
    async def control(request: Request):
        data = await bounded_json(request)
        if set(data) - {'action', 'value'} or type(data.get('action')) is not str:
            raise ControlError('INVALID_CONTROL', 'expected action and optional value only')
        async with lock:
            action,value=data['action'],data.get('value')
            if action=='connect':
                from terminal.providers.kraken import ProviderError
                if value in (None,'kraken'):value={'provider':'kraken','instrument':'BTC/USD','depth':10}
                if (type(value) is not dict or set(value)!={'provider','instrument','depth'}
                        or value['provider']!='kraken' or value['instrument'] not in ('BTC/USD','ETH/USD')
                        or type(value['depth']) is not int or value['depth']!=10):
                    raise ControlError('INVALID_PROVIDER','expected Kraken BTC/USD or ETH/USD depth10; no URLs')
                native.mode='LIVE';native.playing=False
                try:await feed.start(value['instrument'])
                except ProviderError:
                    native.notifications.append({'code':'LIVE_BLOCKED','message':'Explicit server permission and current protocol review required; no connection started.'})
                return native.state()
            if action=='disconnect':
                await feed.close()
                return native.state()
            # Validate and commit synchronous control first; invalid input must not
            # disconnect an otherwise accepted feed. No task runs between these steps.
            native.control(action,value)
            if action in ('mode','dataset'):
                await feed.close()
            return native.state()

    @route('/api/v1/simulate', methods=['POST'])
    @json_endpoint
    async def simulate(request: Request):
        data = await bounded_json(request)
        if set(data) - {'algorithm', 'quantity', 'slices'}:
            raise ControlError('INVALID_SIMULATION', 'unexpected simulation fields')
        async with lock:
            # Bounded native run; no await while native session is being accessed.
            return native.simulation(data.get('algorithm', 'TWAP'), data.get('quantity', '100'), data.get('slices', 5))

    @route('/api/v1/validate', methods=['POST'])
    @json_endpoint
    async def validate(request: Request):
        data = await bounded_json(request)
        if set(data) != {'profile'} or data['profile'] not in ('itch', 'lobster'):
            raise ControlError('INVALID_VALIDATION', 'expected profile itch or lobster')
        if work_lock.locked():
            return error('BUSY', 'one authored validation may run at a time', 409)
        async with work_lock:
            from terminal.historical import run_authored_validation
            try:
                return await run_authored_validation(data['profile'])
            except (ValueError, OSError, asyncio.TimeoutError):
                return error('VALIDATION_UNAVAILABLE', 'Authored native diagnostic unavailable or failed its bounded contract', 422)

    @route('/api/v1/recordings', methods=['GET'])
    @json_endpoint
    async def sessions(request):
        from terminal.l2_playback import discover
        try:return {'schema_version':'1',**await asyncio.to_thread(discover,l2_directory,allow_observed=observed_processing_allowed())}
        except (ValueError,OSError):return error('RECORDING_REFUSED','Recording catalog unavailable or over budget',409)

    @route('/api/v1/recording', methods=['POST'])
    @json_endpoint
    async def recording(request: Request):
        data = await bounded_json(request)
        if data.get('action') in ('start_l2','stop_l2'):
            if set(data)!={'action'}:raise ControlError('INVALID_RECORDING','Capture takes no paths, permissions or URLs')
            if work_lock.locked():return error('BUSY','One recording operation may run at a time',409)
            async with work_lock:
                if data['action']=='stop_l2':
                    result=await feed.capture.stop() if feed.capture else {'state':'DISABLED'}
                    return {'schema_version':'1','recording':result}
                from terminal.providers.supervisor import configured_permission
                from terminal.l2_capture import Capture
                from terminal.providers.kraken import ProviderError
                import uuid
                try:
                    permission=configured_permission(os.environ);permission.require_live()
                    if os.environ.get('GIG_LIVE_RECORDING_ENABLED')!='1' or not permission.recording_approved:
                        raise ValueError('retention_permission_required')
                    if feed.state!='LIVE_VERIFIED' or native.mode!='LIVE':raise ValueError('verified_production_feed_required')
                    if feed.capture and not feed.capture.task.done():raise ValueError('capture_busy')
                    capture=await Capture.create(l2_directory,'capture-'+uuid.uuid4().hex,enabled=True,
                        origin='LIVE_OBSERVED',permission=permission,symbol=feed.symbol,version=2)
                    try:
                        async with lock:
                            await feed.start(feed.symbol)  # Fresh observed source snapshot, never an invented seed.
                            feed.capture=capture
                    except BaseException:await capture.abort('startup_failed');raise
                    return {'schema_version':'1','recording':capture.status()}
                except (ValueError,OSError,ProviderError):return error('RECORDING_REFUSED','Verified production source and separate retention approval required',409)
        if data.get('action') in ('save_l2_fixture','load_l2','delete_l2'):
            if set(data)-{'action','identity'}:raise ControlError('INVALID_RECORDING','Only recording identity is accepted; no paths')
            identity=data.get('identity','authored-l2-v2')
            if work_lock.locked():return error('BUSY','One recording operation may run at a time',409)
            async with work_lock:
                from terminal.l2_playback import save_fixture,RecordedSession,delete_session
                try:
                    if data['action']=='save_l2_fixture':
                        result=await asyncio.to_thread(save_fixture,l2_directory,identity)
                    elif data['action']=='delete_l2':
                        result={'deleted':await asyncio.to_thread(delete_session,l2_directory,identity)}
                    else:
                        candidate=await asyncio.to_thread(RecordedSession,l2_directory,identity,allow_observed=observed_processing_allowed())
                        async with lock:
                            await feed.close()
                            native.recorded_session=candidate;native.dataset='recorded-l2'
                            native.mode='HISTORICAL_REPLAY';native.position=0;native.playing=False
                        result={'identity':identity,'records':candidate.event_count,'cache_encoded_bytes':candidate.cache_bytes}
                except (ValueError,OSError,gig.EngineError):
                    return error('RECORDING_REFUSED','Recording failed integrity, permission, expiry or resource policy',409)
                return {'schema_version':'1','result':result}
        if set(data) - {'action', 'enabled'} or data.get('action') not in ('save', 'verify', 'load', 'delete'):
            raise ControlError('INVALID_RECORDING', 'expected save, verify or delete; no paths or observed data accepted')
        if work_lock.locked():
            return error('BUSY', 'one authored validation or recording may run at a time', 409)
        async with work_lock:
            from terminal.recording import save_authored, load_authored, delete_authored
            from .fixtures import EVENTS
            directory = ROOT / 'terminal' / 'recordings'
            try:
                if data['action'] == 'save':
                    result = await asyncio.to_thread(save_authored, directory, 'authored-v1', EVENTS,
                        origin='HISTORICAL_SYNTHETIC', enabled=data.get('enabled', False))
                elif data['action'] in ('verify', 'load'):
                    result, events = await asyncio.to_thread(load_authored, directory, 'authored-v1')
                    # Fresh native state proves deterministic event replay rather
                    # than trusting a saved browser snapshot as an L3 seed.
                    from .fixtures import rules, replay_config
                    replay = gig.Replay(rules(), replay_config(), limits={'max_orders':'128', 'max_levels':'32', 'max_snapshot_depth':'20'}, resource_budget_bytes='33554432')
                    accepted = replay.run(events)
                    import hashlib
                    result = {**result, 'native_accepted': str(accepted),
                        'native_canonical_sha256': hashlib.sha256(replay.canonical().encode()).hexdigest()}
                    if data['action'] == 'load':
                        async with lock:
                            native.control('dataset', 'terminal-authored-v2')
                else:
                    result = {'deleted': await asyncio.to_thread(delete_authored, directory, 'authored-v1')}
            except (ValueError, OSError):
                return error('RECORDING_REFUSED', 'Authored recording missing, expired, already present or refused by integrity/enablement policy', 409)
            return {'schema_version':'1', 'origin':'HISTORICAL_SYNTHETIC', 'observed_recording':False, 'result':result}

    @websocket_route('/api/v1/stream')
    async def stream(socket: WebSocket):
        accepted, decision, attempt, protocol = authorize_socket(
            socket.headers, socket.scope.get('subprotocols',[]),origins,expected_codespaces_origin,stream_tickets)
        if accepted and native.clients >= MAX_CLIENTS:
            accepted, decision = False, 'rejected_capacity'
        record = {**observation(socket),'has_application_protocol':PROTOCOL in socket.scope.get('subprotocols',[]),
                  'has_stream_proof':any(p.startswith('gig-ticket.') for p in socket.scope.get('subprotocols',[])),
                  'decision':'accepting' if accepted else decision,
                  'authorization':decision,'attempt_id':attempt,'upgrade_status':None if accepted else 403}
        connections['last_websocket'] = record
        if not accepted:
            await socket.close(code=1008)
            return
        native.clients += 1  # Reserve before first await;concurrent upgrades cannot exceed the cap.
        try:
            await socket.accept(subprotocol=protocol)
            record['decision'], record['upgrade_status'] = 'accepted', 101
            if attempt is not None:connections['last_authenticated_websocket'] = record
            while True:
                async with lock:
                    current = native.state()
                # No retained FIFO: latest state coalesces intermediate render frames, never source events.
                await asyncio.wait_for(socket.send_json(current), timeout=SEND_TIMEOUT)
                await asyncio.sleep(0.1)
        except asyncio.TimeoutError:
            native.stream_timeouts += 1
            with suppress(Exception):
                await socket.close(code=1013)
        except (WebSocketDisconnect, RuntimeError, OSError):
            pass
        finally:
            native.clients -= 1

    @route('/{path:path}', methods=['GET'])
    @json_endpoint
    async def static(request):
        path = request.path_params['path']
        if path.startswith('api/'):
            return error('NOT_FOUND', 'unknown API endpoint', 404)
        candidate = (DIST / path).resolve()
        if not candidate.is_relative_to(DIST.resolve()):
            return error('NOT_FOUND', 'not found', 404)
        if candidate.is_file():
            return FileResponse(candidate)
        index = DIST / 'index.html'
        if index.is_file() and '.' not in path:
            return FileResponse(index)
        return error('FRONTEND_NOT_BUILT', 'build terminal/web before opening the browser', 404)

    return app


app = create_app()
