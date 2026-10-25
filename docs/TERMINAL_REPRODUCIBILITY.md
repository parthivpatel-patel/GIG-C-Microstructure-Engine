# Local native terminal reproduction

Use CPython3.12,C++20 GCC/Clang,CMake>=3.20,Ninja,Node24/npm. Existing pinned native
build tools:requirements-python.lock. Gateway lock:terminal/server/requirements.txt;
frontend/test npm locks are committed. No restricted data or credentials required.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-python.lock
.venv/bin/python -m pip install -r terminal/server/requirements.txt
CXX=g++ .venv/bin/python -m pip install --no-build-isolation .
npm --prefix terminal/web ci --ignore-scripts
npm --prefix terminal/web run build
.venv/bin/python -m terminal.server
```

Open **http://127.0.0.1:8787**. This serves the built frontend and native REST/WS
from one origin. Keep one worker. Optional hot development:npm --prefix terminal/web
run dev (localhost5173 proxies /api to8787). Do not expose Vite directly to untrusted
networks. If your Python build tools are not on PATH, activate the venv before
building. Explicit CXX=g++ avoids inherited invalid compiler strings.

Native authored ITCH/LOBSTER diagnostic buttons additionally require:

```sh
cmake --preset release
cmake --build --preset release
GIG_TERMINAL_NATIVE_BUILD="$PWD/build/release" .venv/bin/python -m terminal.server
```

The environment variable selects a trusted local build directory, never a browser
supplied path. Without binaries those two diagnostics return structured unavailable.
No private sample is opened. Permission-restricted catalog entries remain blocked.

```sh
.venv/bin/python -m unittest terminal.server.test_server terminal.providers.test_kraken terminal.test_historical terminal.test_recording terminal.test_recording_api
npm --prefix terminal/web test
npm --prefix terminal/tests ci --ignore-scripts
cd terminal/tests
TERMINAL_URL=http://127.0.0.1:8787 npm test
```

Browser checks require a real Chromium executable (/usr/bin/chromium default;
CHROMIUM_PATH overrides). No bundled browser is downloaded by these instructions.
Browser outputs/screenshots go to ignored build/terminal/browser. Physical Android,
external forwarded URL and hardware GPU are not implied by viewport/SwiftShader tests.
For command-only native diagnostics set GIG_TERMINAL_NATIVE_BUILD appropriately.

Private phone access:use an authenticated platform forward of8787,then configure
GIG_TERMINAL_ALLOWED_ORIGINS to the exact HTTPS origin (no path/wildcard) before
startup. The app adds that hostname to TrustedHost. This environment has not supplied
a verified external preview URL or forwarding capability; localhost is verified only.
If the platform requires binding0.0.0.0,use its documented private forwarding setup
and uvicorn terminal.server.app:app --host0.0.0.0 --port8787 --workers1 with the
same documented bounds from terminal/server/__main__.py. Do not expose a public
unauthenticated service. GitHub Pages cannot execute this native Linux backend.
Codespaces eligibility/free quota is owner/account dependent;no cloud resources created.

Recording UI explicitly stores only fixed authored source into ignored
terminal/recordings,maximum8datasets,512records/2MiB each,24h replay validity.
Verify replays the exact source into fresh native state;delete removes the fixed
authored identity. Expiry refuses replay;deletion is operator-triggered,not a daemon.
Future observed recording requires separate rights review and implementation gates.
