"""Local-first single-worker launcher with explicit private Codespaces forwarding."""
import os
import re
import uvicorn


def launch_settings(environment):
    origins = environment.get('GIG_TERMINAL_ALLOWED_ORIGINS')
    host = '127.0.0.1'
    expected_origin = None
    if environment.get('CODESPACES') == 'true':
        name = environment.get('CODESPACE_NAME', '')
        domain = environment.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,127}', name):
            raise ValueError('CODESPACE_NAME missing or invalid; refusing external bind')
        if not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', domain):
            raise ValueError('Codespaces forwarding domain missing or invalid')
        expected_origin = f'https://{name}-8787.{domain}'
        if origins and expected_origin not in [x.strip() for x in origins.split(',')]:
            raise ValueError('explicit origin configuration excludes the Codespaces browser origin')
        origins = origins or expected_origin
        host = '0.0.0.0'
    return host, origins, expected_origin


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
                ws_max_size=4096, ws_max_queue=4, timeout_keep_alive=5,
                limit_concurrency=32, h11_max_incomplete_event_size=8192)


if __name__ == '__main__':
    main()
