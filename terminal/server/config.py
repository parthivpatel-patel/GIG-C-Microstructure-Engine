"""Server-owned launcher/app policy,shared by module and direct ASGI entry points."""
import re


def launch_settings(environment):
    origins = environment.get('GIG_TERMINAL_ALLOWED_ORIGINS')
    host = '127.0.0.1'
    expected_origin = None
    # Process managers may omit CODESPACES while preserving the server-owned
    # codespace name. Derive exact policy from that metadata,never request headers.
    if environment.get('CODESPACES') == 'true' or environment.get('CODESPACE_NAME'):
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
        host = '0.0.0.0' if environment.get('CODESPACES') == 'true' else '127.0.0.1'
    return host, origins, expected_origin
