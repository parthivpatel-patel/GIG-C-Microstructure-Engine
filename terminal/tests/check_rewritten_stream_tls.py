"""Verified local TLS-terminating proxy -> real native gateway; never contacts Codespaces."""
import asyncio
import json
import os
from pathlib import Path
import socket
import ssl
import subprocess
import sys
import tempfile
from contextlib import suppress
import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route,WebSocketRoute
import websockets
from websockets.asyncio.client import ClientConnection

class RewriteHost(ClientConnection):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        original=self.protocol.connect
        def request():
            value=original()
            del value.headers["Host"]
            value.headers["Host"]="localhost:8787"
            return value
        self.protocol.connect=request

ROOT=Path(__file__).resolve().parents[2]
ORIGIN='https://authored-tls-check-8787.app.github.dev'


def free_port():
    with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]


async def main():
    backend_port,edge_port=free_port(),free_port()
    while edge_port==backend_port:edge_port=free_port()
    environment={**os.environ,'CODESPACES':'true','CODESPACE_NAME':'authored-tls-check','GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN':'app.github.dev'}
    environment.pop('GIG_TERMINAL_ALLOWED_ORIGINS',None)
    checks=[]
    with tempfile.TemporaryDirectory(prefix='gig-forwarded-tls-') as directory:
        cert,key=Path(directory)/'cert.pem',Path(directory)/'key.pem'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=IP:127.0.0.1,DNS:localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        os.chmod(key,0o600)
        trust=ssl.create_default_context(cafile=str(cert))
        assert trust.check_hostname and trust.verify_mode==ssl.CERT_REQUIRED
        backend=subprocess.Popen([sys.executable,'-m','uvicorn','terminal.server.app:app','--host','127.0.0.1','--port',str(backend_port),'--no-access-log'],cwd=ROOT,env=environment,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        forward_headers={'x-forwarded-host':ORIGIN.removeprefix('https://'),'x-forwarded-proto':'https','x-forwarded-port':'443'}
        async def http(request:Request):
            body=await request.body()
            assert len(body)<=4096
            headers={**forward_headers}
            for name in ('origin','content-type'):
                if name in request.headers:headers[name]=request.headers[name]
            async with httpx.AsyncClient(trust_env=False,timeout=5) as client:
                r=await client.request(request.method,f'http://127.0.0.1:{backend_port}'+request.url.path,content=body,headers=headers)
            return Response(r.content,status_code=r.status_code,headers={k:v for k,v in r.headers.items() if k.lower() not in ('content-length','transfer-encoding','connection')})
        async def ws(socket):
            try:
                async with websockets.connect(f'ws://127.0.0.1:{backend_port}/api/v1/stream',origin='http://localhost:8787',additional_headers=forward_headers,proxy=None,max_size=262144,subprotocols=socket.scope.get('subprotocols',[]),create_connection=RewriteHost) as upstream:
                    await socket.accept(subprotocol=upstream.subprotocol)
                    # One real native message is enough to qualify handshake and prefix continuity.
                    await socket.send_text(await asyncio.wait_for(upstream.recv(),5))
                    await socket.close(code=1000)
            except websockets.exceptions.InvalidStatus:
                await socket.close(code=1008)
        edge=uvicorn.Server(uvicorn.Config(Starlette(routes=[WebSocketRoute('/api/v1/stream',ws),Route('/{path:path}',http,methods=['GET','POST'])]),host='127.0.0.1',port=edge_port,ssl_certfile=str(cert),ssl_keyfile=str(key),log_level='error',access_log=False))
        edge_task=None
        try:
            async with httpx.AsyncClient(trust_env=False,timeout=2) as client:
                for attempt in range(100):
                    try:
                        r=await client.get(f'http://127.0.0.1:{backend_port}/api/v1/health')
                        if r.status_code==200:break
                    except (httpx.ConnectError,httpx.ReadError):pass
                    await asyncio.sleep(.05)
                else:raise RuntimeError('native gateway startup failed')
            edge_task=asyncio.create_task(edge.serve())
            for _ in range(100):
                if edge.started:break
                await asyncio.sleep(.02)
            assert edge.started
            base=f'https://127.0.0.1:{edge_port}'
            async with httpx.AsyncClient(verify=trust,trust_env=False,timeout=5,headers={'Origin':ORIGIN}) as client:
                r=await client.get(base+'/');assert r.status_code==200 and '<script' in r.text;checks.append('TLS verified actual frontend HTML')
                r=await client.get(base+'/api/v1/state');assert r.json()['engine']['native'] and r.json()['position']==20;checks.append('TLS proxy actual C++ state')
                r=await client.post(base+'/api/v1/control',json={'action':'step'});assert r.status_code==200 and r.json()['position']==21;checks.append('forwarded HTTPS Origin mutates native prefix')
                r=await client.post(base+'/api/v1/control',json={'action':'pause'},headers={'Origin':'https://attacker.invalid'});assert r.status_code==403;checks.append('foreign Origin denied behind TLS proxy')
                for index in range(2):
                    proof=(await client.post(base+'/api/v1/stream-ticket',json={'browser_origin':ORIGIN,'websocket_url':ORIGIN.replace('https:','wss:')+'/api/v1/stream','attempt_id':f'01234567-89ab-cdef-0123-{index:012d}'})).json()
                    async with websockets.connect(f'wss://127.0.0.1:{edge_port}/api/v1/stream',ssl=trust,origin=ORIGIN,proxy=None,max_size=262144,subprotocols=[proof['protocol'],'gig-ticket.'+proof['ticket']]) as socket:
                        assert socket.response.status_code==101
                        state=json.loads(await asyncio.wait_for(socket.recv(),5));assert state['position']==21
                checks.append('two verified WSS upgrades101 preserve native prefix')
                diag=(await client.get(base+'/api/v1/connection')).json()
                assert diag['last_websocket']['decision']=='accepted'
                assert diag['last_websocket']['origin']=='http://localhost:8787'
                assert diag['last_websocket']['host']=='localhost:8787'
                assert diag['last_websocket']['authorization']=='accepted_codespaces_rewrite_ticket'
                assert diag['last_browser_bootstrap']['origin']==ORIGIN
                assert diag['request']['x_forwarded_proto']=='https' and diag['request']['x_forwarded_host']==ORIGIN.removeprefix('https://')
                assert diag['request']['host']==f'127.0.0.1:{backend_port}'
                checks.append('actual proxy Origin/Host/HTTPS header capture')
            return {'schema':'gig.codespaces.rewritten_origin_tls.v1','tls_verification':'CERT_REQUIRED/check_hostname with dedicated ephemeral test CA;no verification disabled','checks':checks,'passed':len(checks),'failed':0,'captured_proxy_headers':diag,'scope':'Test proxy deliberately rewrites Origin+Host exactly as reported;HTTPS proof minted with unchanged approved Origin. Not identification of the owner rewriting component.'}
        finally:
            edge.should_exit=True
            if edge_task:
                with suppress(asyncio.TimeoutError):await asyncio.wait_for(edge_task,5)
            backend.terminate()
            try:backend.wait(timeout=5)
            except subprocess.TimeoutExpired:backend.kill();backend.wait()

if __name__=='__main__':print(json.dumps(asyncio.run(main()),indent=2))
