#!/usr/bin/env python3
"""Private owner configuration. Contact entered without echo,never a CLI argument/log."""
import argparse,getpass,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.sec_config import resolve,readiness,save

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--check',action='store_true');g.add_argument('--configure',action='store_true');p.add_argument('--policy-reviewed',action='store_true');a=p.parse_args()
    if a.configure:
        if not a.policy_reviewed:p.error('Explicit --policy-reviewed acknowledgment required;no configuration changed')
        if not sys.stdin.isatty():p.error('Use an interactive private terminal for hidden contact entry')
        try:result=save(getpass.getpass('Owner contact email (hidden;stored privately): '),policy_reviewed=True)
        except (ValueError,OSError):print('SEC configuration operation failed. Check contact format/private permissions,then run --check to verify the current state.');return 1
        print(json.dumps(result));return 0
    effective,source=resolve(os.environ);state=readiness(effective)
    if source['error']:state.update(ready=False,reason=source['error'])
    print(json.dumps({'schema':'gig.sec.configuration.v1',**state,'configuration_source':source['source'],'contact_disclosed':False}));return 0
if __name__=='__main__':raise SystemExit(main())
