"""Local-first single-worker launcher with explicit private Codespaces forwarding."""
import os
import uvicorn

from .config import launch_settings


def main():
    host, origins, expected = launch_settings(os.environ)
    if origins:
        os.environ['GIG_TERMINAL_ALLOWED_ORIGINS'] = origins
    if expected:
        print('Codespaces: keep port 8787 PRIVATE. In the Ports panel choose Open in Browser.', flush=True)
        print(f'Expected authenticated origin (not proof of external access): {expected}', flush=True)
    else:
        print('Local browser: http://127.0.0.1:8787 on THIS machine; remote devices need private forwarding.', flush=True)
    uvicorn.run('terminal.server.app:app', host=host, port=8787, workers=1,
                ws_max_size=4096, ws_max_queue=4, timeout_keep_alive=5, timeout_graceful_shutdown=5,
                limit_concurrency=32, h11_max_incomplete_event_size=8192)


if __name__ == '__main__':
    main()
