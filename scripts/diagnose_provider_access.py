#!/usr/bin/env python3
"""Metadata-only owner diagnostic. No WebSocket, subscription, body read or recording."""
import argparse,datetime,json
import httpx
from urllib.parse import urlsplit,urljoin

ENDPOINTS={
 'kraken':('https://docs.kraken.com/api/docs/websocket-v2/book/','https://www.kraken.com/legal','https://ws.kraken.com/v2'),
 'coinbase':('https://docs.cdp.coinbase.com/exchange/websocket-feed/channels','https://www.coinbase.com/legal/market_data','https://ws-feed.exchange.coinbase.com/'),
}

def safe_redirect(url,location):
    if type(location) is not str or len(location)>512:return None
    try:original=urlsplit(url);target=urlsplit(urljoin(url,location))
    except ValueError:return None
    if (target.scheme!='https' or target.hostname!=original.hostname or target.username or target.password
            or target.query or target.fragment or target.path.rstrip('/')!=original.path.rstrip('/')):return None
    try:
        if target.port not in (None,443):return None
    except ValueError:return None
    return target.geturl()

def diagnose(provider,client):
    if provider not in ENDPOINTS:raise ValueError('provider_not_allowlisted')
    result=[]
    for url in ENDPOINTS[provider]:
        try:
            with client.stream('HEAD',url) as response:
                result.append({'url':url,'http_status':response.status_code,'redirect_followed':False,
                    'redirect_target':safe_redirect(url,getattr(response,'headers',{}).get('location')) if response.status_code in (301,302,307,308) else None,
                    'response_body_read':False,'meaning':'metadata reachability only;not protocol,licensing or feed qualification'})
        except httpx.HTTPError as error:
            category='proxy_connect_denied' if isinstance(error,httpx.ProxyError) else 'transport_failure'
            result.append({'url':url,'http_status':None,'failure':category,'response_body_read':False})
    return {'schema':'gig.provider.metadata_diagnostic.v1','provider':provider,'results':result,
        'observed_market_records':0,'websocket_started':False,'permission_verified':False,'recording':False,
        'credentials_or_proxy_configuration_recorded':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--provider',choices=tuple(ENDPOINTS),default='kraken');a=p.parse_args()
    with httpx.Client(timeout=5,follow_redirects=False,trust_env=True,limits=httpx.Limits(max_connections=1,max_keepalive_connections=1)) as client:
        report=diagnose(a.provider,client)
    report['checked_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print(json.dumps(report,indent=2))
