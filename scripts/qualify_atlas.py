#!/usr/bin/env python3
"""One bounded owner-run source campaign. No permission grants,raw output or trading."""
import argparse,asyncio,datetime,json,os,socket,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace
from terminal.stocks.qualification import nonretaining_environment,qualify_sources
ROOT=Path(__file__).resolve().parents[1]

def preflight(workspace):
    config=workspace.configuration()
    try:
        with socket.create_connection(('127.0.0.1',8787),timeout=.5):gateway=True
    except OSError:gateway=False
    return {'schema':'gig.atlas.operational.preflight.v1','configuration':config,
            'gateway_port_8787_in_use':gateway,'environment_is_codespaces':os.environ.get('CODESPACES')=='true',
            'authorization_flags_changed':False,'network_provider_requests':0,
            'observed_retention_disabled_for_this_process':workspace.environment.get('GIG_ALPACA_STORE_ENABLED')=='0' and workspace.environment.get('GIG_HISTORY_STORE_ENABLED')=='0',
            'provider_entitlements':'Unknown until narrow source probes;assets/credentials are not market-data entitlement or vendor-rights proof',
            'milestone_2':'NOT_VERIFIED_TARGET_PRIVATE_AUTHENTICATION_AND_OWNER_ACCEPTANCE_REQUIRED'}

async def frontend_comparison(histories,expected):
    process=await asyncio.create_subprocess_exec('node','--experimental-strip-types',str(ROOT/'scripts/check_actual_comparison.mjs'),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.DEVNULL,env={'PATH':os.environ.get('PATH',os.defpath),'LANG':'C.UTF-8'})
    raw=json.dumps({'histories':histories,'expected':expected},separators=(',',':')).encode()
    if len(raw)>524288:
        process.kill();await process.wait();raise ValueError('comparison_input_budget')
    try:
        async with asyncio.timeout(10):out,_=await process.communicate(raw)
    except BaseException:
        if process.returncode is None:process.kill()
        await process.wait();raise
    if process.returncode or len(out)>8192:raise ValueError('comparison_rejected')
    value=json.loads(out)
    if value.get('status')!='PASS':raise ValueError('comparison_rejected')
    return value

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true');p.add_argument('--exclusive-stream-window',action='store_true',help='Owner confirms other applications sharing this account will not consume the free stream slot during this bounded run;not a licensing grant')
    p.add_argument('--end',default=str(datetime.datetime.now(datetime.timezone.utc).date()-datetime.timedelta(days=1)))
    p.add_argument('--seconds',type=int,choices=range(5,61),default=30)
    a=p.parse_args()
    try:
        workspace=StockWorkspace(environment=nonretaining_environment())
        check=preflight(workspace)
        if not a.execute:print(json.dumps(check,indent=2));return 0
        if check['gateway_port_8787_in_use']:
            print(json.dumps({**check,'status':'BLOCKED_ACTIVE_GATEWAY','action':'Stop this ATLAS server with Ctrl+C first;no existing process was changed and no provider request was made.'},indent=2));return 2
        async def run():
            async with asyncio.timeout(180):return await qualify_sources(workspace,end=a.end,seconds=a.seconds,exclusive_stream_window=a.exclusive_stream_window,compare=frontend_comparison)
        report=asyncio.run(run());report['preflight']=check
        print(json.dumps(report,indent=2));return 0 if report['observed_provider_qualification'] else 2
    except Exception:
        print(json.dumps({'schema':'gig.atlas.operational.sources.v1','status':'BLOCKED_OR_REJECTED','reason':'sanitized_configuration_resource_or_source_failure','raw_observations_emitted':False,'credentials_emitted':False,'milestone_2':'NOT_VERIFIED'}));return 2
if __name__=='__main__':raise SystemExit(main())
