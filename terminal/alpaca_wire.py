"""Bounded Alpaca wire transport. No connection/credential access on construction.

Only explicit, validated fixed-host plans can reach HTTPWire. Tests inject
FixtureWire;fixture origin cannot be selected through an HTTP response or browser.
"""
import asyncio
from dataclasses import dataclass, field
from decimal import Decimal
import hashlib
import inspect
import json
from urllib.parse import urlsplit


class WireError(ValueError):
    def __init__(self, code, *, status=None, retry_after=None):
        self.code, self.status, self.retry_after = code, status, retry_after
        super().__init__(code)


@dataclass(frozen=True)
class WireResponse:
    status: int
    body: bytes
    headers: dict = field(default_factory=dict)


def decode(response, *, cap=512*1024):
    if type(response) is not WireResponse or type(response.status) is not int or type(response.body) is not bytes or len(response.body)>cap or type(response.headers) is not dict:
        raise WireError('wire_response_boundary')
    if response.status not in (200,201,204):
        status=response.status if response.status in (401,403,404,409,422,429) or 500<=response.status<=599 else None
        retry=response.headers.get('retry-after')
        retry=int(retry) if type(retry) is str and retry.isascii() and retry.isdecimal() and len(retry)<=3 else None
        raise WireError('provider_http_'+str(status) if status else 'provider_http_unexpected',status=status,retry_after=retry)
    if response.status==204:
        if response.body:raise WireError('wire_unexpected_body')
        return None,hashlib.sha256(response.body).hexdigest()
    def pairs(items):
        value={}
        for k,v in items:
            if k in value:raise ValueError('duplicate')
            value[k]=v
        return value
    try:value=json.loads(response.body,parse_float=Decimal,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('constant')))
    except (ValueError,UnicodeError,RecursionError):raise WireError('wire_json_schema') from None
    return value,hashlib.sha256(response.body).hexdigest()


class FixtureWire:
    """Explicit authored transport;never imports or invokes an HTTP client."""
    fixture=True
    def __init__(self, handler):self.handler=handler;self.calls=[]
    async def send(self,method,url,body=None):
        # Calls stay test-local;public errors never expose query cursors/body.
        self.calls.append((method,url,body))
        value=self.handler(method,url,body)
        return await value if inspect.isawaitable(value) else value


class HTTPWire:
    fixture=False
    def __init__(self, authorize, credential_headers, validate):
        self.authorize,self.credential_headers,self.validate=authorize,credential_headers,validate
    async def send(self,method,url,body=None):
        self.authorize()  # Recheck expiry/policy before even obtaining credentials.
        self.validate(method,url,body)
        u=urlsplit(url)
        if u.scheme!='https' or u.netloc not in ('data.alpaca.markets','paper-api.alpaca.markets') or u.username or u.password or u.fragment:
            raise WireError('wire_fixed_host_required')
        if u.netloc=='data.alpaca.markets' and (method!='GET' or u.path not in ('/v2/stocks/bars','/v2/stocks/quotes','/v2/stocks/trades')):
            raise WireError('wire_fixed_endpoint_required')
        if u.netloc=='paper-api.alpaca.markets' and (not u.path.startswith('/v2/') or method not in ('GET','POST','DELETE')):
            raise WireError('wire_fixed_endpoint_required')
        headers=self.credential_headers()
        if type(headers) is not dict or set(headers)!={'APCA-API-KEY-ID','APCA-API-SECRET-KEY'}:
            raise WireError('wire_server_credentials_required')
        import httpx
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(5),follow_redirects=False,limits=httpx.Limits(max_connections=1),headers={'Accept-Encoding':'identity'}) as client:
                async with client.stream(method,url,headers=headers,json=body) as response:
                    h=response.headers
                    if h.get('content-encoding','identity').lower() not in ('identity',''):
                        raise WireError('wire_compressed_response_refused')
                    length=h.get('content-length')
                    if length is not None and (not length.isascii() or not length.isdecimal() or len(length)>9 or int(length)>512*1024):
                        raise WireError('wire_body_budget')
                    data=bytearray()
                    async for chunk in response.aiter_raw():
                        if len(data)+len(chunk)>512*1024:raise WireError('wire_body_budget')
                        data.extend(chunk)
                    if length is not None and len(data)!=int(length):raise WireError('wire_body_length')
                    return WireResponse(response.status_code,bytes(data),{'retry-after':h.get('retry-after')})
        except (httpx.HTTPError,TimeoutError,OSError):
            # Order callers must treat this as ambiguous;never echo request/auth.
            raise WireError('wire_transport_unknown') from None
