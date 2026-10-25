"""One-use browser handshake proofs; no URL credentials or forwarded-header authority."""
import hashlib
import re
import secrets
import time

PROTOCOL='gig-stream-v1'
PREFIX='gig-ticket.'

class StreamTickets:
    def __init__(self, *, clock=time.monotonic, capacity=32, ttl=30):
        self.clock,self.capacity,self.ttl=clock,capacity,ttl
        self.pending={}
    def prune(self):
        now=self.clock()
        for key,entry in list(self.pending.items()):
            if entry['expires']<=now:del self.pending[key]
    def issue(self,origin,attempt):
        self.prune()
        if len(self.pending)>=self.capacity:raise ValueError('stream_ticket_capacity')
        token=secrets.token_urlsafe(32)
        digest=hashlib.sha256(token.encode()).digest()
        self.pending[digest]={'origin':origin,'attempt_id':attempt,'expires':self.clock()+self.ttl}
        return token
    def consume(self,token):
        self.prune()
        if type(token) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{43}',token):return None
        return self.pending.pop(hashlib.sha256(token.encode()).digest(),None)


def authorize_socket(headers,protocols,origins,expected,tickets):
    """Normal exact Origin remains supported;proxy rewrite needs independent proof.

    X-Forwarded-* is deliberately never examined. Only the fixed reported local
    pair is compatible,and only in server-configured Codespaces context.
    """
    origin=headers.get('origin')
    supplied=[p[len(PREFIX):] for p in protocols if p.startswith(PREFIX)]
    has_proof=bool(supplied)
    if has_proof:
        if len(supplied)!=1 or len(protocols)!=2 or PROTOCOL not in protocols:
            return False,'rejected_ticket_protocol',None,None
        proof=tickets.consume(supplied[0])
        if proof is None:return False,'rejected_ticket',None,None
        if origin in origins and origin==proof['origin']:
            return True,'accepted_origin_ticket',proof['attempt_id'],PROTOCOL
        # Proof was minted only after strict HTTP Origin validation. This is NOT
        # an allowlist addition for localhost and cannot be enabled by spoofed
        # Host/X-Forwarded headers alone.
        if (expected and expected.startswith('https://') and expected in origins
                and proof['origin']==expected and origin=='http://localhost:8787'
                and headers.get('host')=='localhost:8787'):
            return True,'accepted_codespaces_rewrite_ticket',proof['attempt_id'],PROTOCOL
        return False,'rejected_origin',proof['attempt_id'],None
    if origin in origins:return True,'accepted_origin',None,None
    return False,'rejected_origin',None,None
