"""Small credential-free diagnostics; forwarded headers are observations,not trust inputs."""
import re
from urllib.parse import urlsplit


def origin_value(value):
    if value is None:return None
    if len(value)>256:return '<invalid>'
    try:
        u=urlsplit(value)
        if u.scheme not in ('http','https') or not u.hostname or u.username or u.password or u.path or u.query or u.fragment:return '<invalid>'
        if any(ord(c)<33 or ord(c)>126 for c in value):return '<invalid>'
        if u.port is not None and not 1<=u.port<=65535:return '<invalid>'
        return value
    except ValueError:return '<invalid>'


def token(value,pattern,limit):
    if value is None:return None
    return value if len(value)<=limit and re.fullmatch(pattern,value) else '<invalid>'


def observation(connection):
    h=connection.headers
    return {
        'origin':origin_value(h.get('origin')),
        'host':token(h.get('host'),r'[A-Za-z0-9.\[\]:-]+',256),
        'x_forwarded_host':token(h.get('x-forwarded-host'),r'[A-Za-z0-9.\[\]:, -]+',256),
        'x_forwarded_proto':token(h.get('x-forwarded-proto'),r'(?:https?|wss?)(?:, ?(?:https?|wss?))*',32),
        'x_forwarded_port':token(h.get('x-forwarded-port'),r'[0-9]{1,5}',5),
        'asgi_scheme':token(connection.scope.get('scheme'),r'https?|wss?',8),
    }
