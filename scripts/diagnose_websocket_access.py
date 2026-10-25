#!/usr/bin/env python3
"""Owner-run handshake only: no subscription/send,terminal activation,recording or raw payload output."""
import argparse,asyncio,datetime,json,socket,ssl
from urllib.request import getproxies
from urllib.parse import urlsplit
import websockets.asyncio.client
from websockets.exceptions import InvalidStatus,ProxyError,InvalidProxyStatus,ConnectionClosed

ENDPOINTS={'kraken':'wss://ws.kraken.com/v2','coinbase':'wss://ws-feed.exchange.coinbase.com/'}

class FixedEndpoint(websockets.asyncio.client.connect):
    def process_redirect(self,error):return error

async def diagnose(provider,*,connector=FixedEndpoint,resolver=None,proxy_configured=None):
    if provider not in ENDPOINTS:raise ValueError('provider_not_allowlisted')
    endpoint=ENDPOINTS[provider];host=urlsplit(endpoint).hostname
    proxy=any(getproxies().get(k) for k in ('http','https','all','ws','wss')) if proxy_configured is None else proxy_configured
    report={'schema':'gig.websocket.handshake_diagnostic.v1','provider':provider,'endpoint':endpoint,
        'dns':{'status':'NOT_OBSERVED_PROXY_RESOLUTION' if proxy else 'NOT_ATTEMPTED'},
        'tls':{'status':'NOT_OBSERVED'},'websocket':{'status':'NOT_ATTEMPTED'},
        'protocol':{'status':'NOT_OBSERVED','control_frames':0,'unexpected_application_frame':False},
        'proxy_configuration_present':proxy,'subscriptions_sent':0,'application_messages_sent':0,
        'market_fields_retained':False,'recording':False,'terminal_live_mode_started':False,
        'limits':{'overall_async_seconds':12,'open_seconds':5,'passive_seconds':2,'close_seconds':2,
                  'maximum_frames':2,'maximum_frame_bytes':4096,'maximum_consumed_bytes':8192,'retries':0,'redirects':0}}
    phase='dns';context=ssl.create_default_context()
    assert context.check_hostname and context.verify_mode==ssl.CERT_REQUIRED
    try:
        async with asyncio.timeout(12):
            if not proxy:
                lookup=resolver or asyncio.get_running_loop().getaddrinfo
                try:
                    records=await asyncio.wait_for(lookup(host,443,type=socket.SOCK_STREAM),2)
                    report['dns']={'status':'RESOLVED','address_records':len(records),'scope':'local resolver;not proof of provider reachability'}
                except socket.gaierror:report['dns']={'status':'FAILED'};return report
            phase='connect'
            async with connector(endpoint,ssl=context,open_timeout=5,close_timeout=2,max_size=4096,
                                 max_queue=1,ping_interval=None) as ws:
                transport=ws.transport;tls=transport.get_extra_info('ssl_object')
                if tls is None or not tls.getpeercert():
                    report['tls']={'status':'UNVERIFIED_TRANSPORT'};return report
                if ws.response.status_code!=101:
                    report['websocket']={'status':'INVALID_UPGRADE_STATUS','http_status':ws.response.status_code};return report
                report['tls']={'status':'VERIFIED','hostname_check':True,'certificate_verification':True}
                report['websocket']={'status':'UPGRADED','http_status':ws.response.status_code}
                report['protocol']['status']='NO_CONTROL_FRAME_WITHIN_BUDGET';phase='passive'
                for _ in range(2):
                    try:raw=await asyncio.wait_for(ws.recv(),2)
                    except asyncio.TimeoutError:break
                    if type(raw) is not str or len(raw.encode())>4096:
                        report['protocol']['status']='UNSUPPORTED_OR_OVERSIZED_FRAME';break
                    try:data=json.loads(raw)
                    except (ValueError,RecursionError):report['protocol']['status']='INVALID_CONTROL_JSON';break
                    kind=(data.get('channel') if provider=='kraken' else data.get('type')) if type(data) is dict else None
                    allowed=('status','heartbeat') if provider=='kraken' else ('subscriptions','heartbeat','status','error')
                    if type(kind) is not str or kind not in allowed:
                        report['protocol'].update(status='UNEXPECTED_APPLICATION_FRAME_STOPPED',unexpected_application_frame=True);break
                    report['protocol']['control_frames']+=1
                    report['protocol']['status']='PASSIVE_CONTROL_ONLY_NOT_PROTOCOL_QUALIFICATION'
                    # Do not copy any payload fields. Control type is sufficient for reachability.
    except ConnectionClosed as error:report['protocol'].update(status='CLOSED_WITHOUT_SUBSCRIPTION',close_code=error.rcvd.code if error.rcvd else None)
    except ssl.SSLCertVerificationError:report['tls']={'status':'CERTIFICATE_REJECTED'}
    except ssl.SSLError:report['tls']={'status':'TLS_FAILED'}
    except (ProxyError,InvalidProxyStatus):report['websocket']={'status':'PROXY_FAILURE'}
    except InvalidStatus as error:
        report['tls']={'status':'VERIFIED_TO_HTTP_RESPONSE','hostname_check':True}
        report['websocket']={'status':'UPGRADE_REJECTED','http_status':error.response.status_code}
    except (asyncio.TimeoutError,TimeoutError):report['timeout_phase']=phase
    except Exception:report['transport_error']='SANITIZED_CONNECT_OR_PROTOCOL_FAILURE'
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--provider',choices=tuple(ENDPOINTS),default='kraken');a=p.parse_args()
    result=asyncio.run(diagnose(a.provider));result['checked_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print(json.dumps(result,indent=2))
