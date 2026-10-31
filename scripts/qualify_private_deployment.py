"""Non-destructive exact-source runtime inspection. No remote/provider traffic."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from terminal.verification.artifacts import EvidenceError, write_private
from terminal.verification.deployment import qualify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-sha', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check-local-server', action='store_true',
                        help='One fixed loopback health GET; never tests GitHub authentication')
    args = parser.parse_args()
    try:
        report = qualify(Path(__file__).resolve().parents[1], args.expected_sha,
                         check_local_server=args.check_local_server)
        write_private(args.output, report)
        print(json.dumps(report, sort_keys=True))
        return 0 if report['status'] == 'PASS_OFFLINE_CHECKS_ONLY' else 2
    except EvidenceError as error:
        code = error.code
    except Exception:
        code = 'qualification_failed_sanitized'
    print(json.dumps({'schema': 'gig.private.deployment.failure.v1', 'code': code}))
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
