"""Local-first versioned API, one native owner, bounded latest-state WebSocket output."""
import asyncio
from contextlib import asynccontextmanager, suppress
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .engine import ControlError, NativeSession
import gig_microstructure as gig

MAX_BODY = 4096
MAX_CLIENTS = 8
SEND_TIMEOUT = 2.0
ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / 'terminal' / 'web' / 'dist'
DEFAULT_ORIGINS = ('http://127.0.0.1:5173', 'http://localhost:5173',
                   'http://127.0.0.1:8787', 'http://localhost:8787')


def origins_from_environment():
    origins = tuple(x.strip() for x in os.environ.get('GIG_TERMINAL_ALLOWED_ORIGINS', ','.join(DEFAULT_ORIGINS)).split(',') if x.strip())
    if not origins or len(origins) > 8:
        raise RuntimeError('configure one to eight explicit GIG_TERMINAL_ALLOWED_ORIGINS')
    for origin in origins:
        u = urlsplit(origin)
        if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.path or u.query or u.fragment or '*' in origin:
            raise RuntimeError('origins must be exact http(s) origins, without wildcard/credentials/path')
    return origins


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


def create_app():
    origins = origins_from_environment()
    native = NativeSession()
    lock = asyncio.Lock()
    work_lock = asyncio.Lock()
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

    @asynccontextmanager
    async def lifespan(app):
        worker = asyncio.create_task(replay_loop())
        try:
            yield
        finally:
            worker.cancel()
            with suppress(asyncio.CancelledError):
                await worker

    app = FastAPI(title='GIG native research gateway', version='1', docs_url=None, redoc_url=None,
                  openapi_url='/api/v1/openapi.json', lifespan=lifespan)
    app.state.native = native
    allowed_hosts = sorted({'127.0.0.1', 'localhost', '[::1]'} | {urlsplit(x).hostname for x in origins})
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    app.add_middleware(CORSMiddleware, allow_origins=list(origins), allow_methods=['GET', 'POST'],
                       allow_headers=['Content-Type'], allow_credentials=False)

    @app.middleware('http')
    async def boundary(request, call_next):
        if request.method == 'POST' and request.headers.get('origin') not in origins:
            native.rejected += 1
            return error('ORIGIN_DENIED', 'exact configured Origin required for mutations', 403)
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
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' ws://localhost:8787 ws://127.0.0.1:8787; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
        return response

    @app.exception_handler(ControlError)
    async def control_error(request, exc):
        native.rejected += 1
        return error(exc.code, str(exc), 413 if exc.code == 'BODY_LIMIT' else 400)

    @app.exception_handler(gig.EngineError)
    async def native_error(request, exc):
        native.rejected += 1
        return error('NATIVE_REJECTION', f'{exc.code_name}: {exc.field}', 422)

    @app.get('/api/v1/health')
    async def health():
        return {'schema_version': '1', 'status': 'ok', 'native': True, 'engine': gig.native_build_info(),
                'live_connected': False, 'recording_enabled': False, 'maximum_clients': MAX_CLIENTS}

    @app.get('/api/v1/state')
    async def state():
        async with lock:
            return native.state()

    @app.get('/api/v1/catalog')
    async def catalog():
        return native.catalog()

    @app.post('/api/v1/control')
    async def control(request: Request):
        data = await bounded_json(request)
        if set(data) - {'action', 'value'} or type(data.get('action')) is not str:
            raise ControlError('INVALID_CONTROL', 'expected action and optional value only')
        async with lock:
            native.control(data['action'], data.get('value'))
            return native.state()

    @app.post('/api/v1/simulate')
    async def simulate(request: Request):
        data = await bounded_json(request)
        if set(data) - {'algorithm', 'quantity', 'slices'}:
            raise ControlError('INVALID_SIMULATION', 'unexpected simulation fields')
        async with lock:
            # Bounded native run; no await while native session is being accessed.
            return native.simulation(data.get('algorithm', 'TWAP'), data.get('quantity', '100'), data.get('slices', 5))

    @app.post('/api/v1/validate')
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

    @app.post('/api/v1/recording')
    async def recording(request: Request):
        data = await bounded_json(request)
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
                            native.control('mode', 'HISTORICAL_REPLAY')
                            native.restart()
                else:
                    result = {'deleted': await asyncio.to_thread(delete_authored, directory, 'authored-v1')}
            except (ValueError, OSError):
                return error('RECORDING_REFUSED', 'Authored recording missing, expired, already present or refused by integrity/enablement policy', 409)
            return {'schema_version':'1', 'origin':'HISTORICAL_SYNTHETIC', 'observed_recording':False, 'result':result}

    @app.websocket('/api/v1/stream')
    async def stream(socket: WebSocket):
        if socket.headers.get('origin') not in origins or native.clients >= MAX_CLIENTS:
            await socket.close(code=1008)
            return
        await socket.accept()
        native.clients += 1
        try:
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

    @app.get('/{path:path}')
    async def static(path: str):
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
