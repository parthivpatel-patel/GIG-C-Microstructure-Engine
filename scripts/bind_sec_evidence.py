#!/usr/bin/env python3
"""Privacy-safe offline binding of existing SEC reports;never fetches orloads secrets."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.verification.artifacts import EvidenceError,write_private
from terminal.verification.sec_binding import bind


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--expected-report-sha256',required=True)
    p.add_argument('--declaration',type=Path);p.add_argument('--expected-source-sha');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:
        result=bind(a.report,a.expected_report_sha256,declaration_path=a.declaration,expected_source_sha=a.expected_source_sha)
        write_private(a.output,result)
        print(json.dumps(result,sort_keys=True))
        return 2 if result['status']=='INCOMPLETE_METADATA'else 1 if result['reported_result']!='AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE'else 0
    except EvidenceError as error:code=error.code
    except Exception:code='sanitized_binding_failure'
    print(json.dumps({'schema':'gig.sec.evidence.binding.failure.v1','status':'REJECTED','code':code,'provider_requests':0,'private_contact_disclosed':False}));return 1


if __name__=='__main__':raise SystemExit(main())
