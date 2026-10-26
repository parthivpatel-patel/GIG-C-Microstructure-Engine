"""Same-origin read CSRF bootstrap for a proxy that rewrites POST Origin too.

The read requires non-simple headers (unavailable to cross-site simple requests),
SOP/CORS/private-port auth and same-origin Fetch Metadata when supplied. Forwarded
headers never establish authority. Read proofs are one-use and endpoint-scoped.
"""
from .stream_tickets import StreamTickets

TARGETS=frozenset(('/api/v1/control','/api/v1/simulate','/api/v1/validate','/api/v1/recording','/api/v1/stream-ticket','/api/v1/stocks/load','/api/v1/stocks/refresh','/api/v1/stocks/options','/api/v1/stocks/research','/api/v1/stocks/models','/api/v1/stocks/scenarios','/api/v1/stocks/history-store'))

class RequestProofs:
    def __init__(self,**kwargs):self.store=StreamTickets(**kwargs)
    def issue(self,origin,target):return self.store.issue(origin,target)
    def consume(self,value):
        result=self.store.consume(value)
        return None if result is None else {'origin':result['origin'],'target':result['attempt_id']}


def rewritten_local(headers):
    return headers.get('origin')=='http://localhost:8787' and headers.get('host')=='localhost:8787'


def bootstrap_context(headers,origins,expected):
    """Return approved read context,not inferred from forwarded/proxy headers."""
    if headers.get('x-gig-bootstrap')!='same-origin-v1':return None,'missing_non_simple_marker'
    browser=headers.get('x-gig-browser-origin')
    target=headers.get('x-gig-target')
    if browser not in origins:return None,'unconfigured_browser_origin'
    if target not in TARGETS:return None,'invalid_target'
    site=headers.get('sec-fetch-site')
    if site is not None and site!='same-origin':return None,'cross_origin_fetch_metadata'
    raw=headers.get('origin')
    if raw is not None and raw!=browser:
        if not (expected and expected.startswith('https://') and browser==expected and rewritten_local(headers)):
            return None,'unexpected_read_origin'
    # Non-simple headers require a preflight for cross-origin browser callers.
    # CORS allows no such headers,so only same-origin JS can read this response.
    # A raw authenticated HTTP client can forge Origin already;not browser CSRF.
    return {'origin':browser,'target':target},'same_origin_read'


def authorize_mutation(headers,target,origins,expected,proofs):
    raw=headers.get('origin');provided=headers.get('x-gig-request-proof')
    if provided is None:
        return (raw,'exact_origin') if raw in origins else (None,'missing_origin' if raw is None else 'origin_mismatch')
    proof=proofs.consume(provided)
    if proof is None:return None,'invalid_or_expired_request_proof'
    if proof['target']!=target:return None,'request_proof_target_mismatch'
    if raw in origins and raw==proof['origin']:return raw,'exact_origin_request_proof'
    if (expected and expected.startswith('https://') and expected in origins
            and proof['origin']==expected and rewritten_local(headers)):
        return expected,'codespaces_rewrite_request_proof'
    return None,'unexpected_proved_origin'
