# Dependency, artifact and security qualification

Candidate: `b91de9e0189a6a4ebbcb1c1cbcc583945495e297`. These are local offline checks; target OS patch/advisory clearance remains pending.

| Check | Actual result | Boundary |
|---|---|---|
| Runtime direct pins | All match; 19 installed distributions inventoried | Requires-Dist metadata is inventoried without printing direct URLs or private configuration |
| `python -m pip check` | No broken requirements | Existing cache-ownership warning retained; dependency consistency is not CVE clearance |
| Source-distribution patterns | 3 tests passed | No unanchored force-includes introduced |
| Candidate sdist build/inventory | 1,142 safe intended byte-identical file members | Required native/build/schema trees present; no extraction, links, traversal, duplicate members, caches/private outputs admitted |
| Installed native-wheel consumer | 8 interface + 6 export tests passed; research example completed | Existing installed Release package, not a newly built wheel; native/package/build inputs unchanged |
| Native Release CTest | 11 passed, including eight frozen references and three binding contracts | Existing unchanged-source binaries; not a new C++ compilation or ARM64 result |
| TypeScript/Vite production build | Passed | Existing deferred 516.95 kB OrbitControls chunk warning retained, not suppressed |
| Frontend unit tests | 118 passed, 0 failed/skipped | Production entry 249.05 kB / 77.55 kB gzip; all 22 asset hashes unchanged |
| Browser/native/security | 40 final checks plus a clean-candidate handshake capture | Local headless Chromium software renderer, not owner-edge/physical-device evidence |
| Verified TLS proxy | 6 + 6 + 8 = 20 checks passed | Dedicated ephemeral test CA, CERT_REQUIRED and hostname validation; no TLS verification disabled |

Archive: `gig_microstructure-0.1.1.tar.gz`; compressed bytes: 7,631,813; SHA256: `bd2e51a19e82d4c49b3ca1f6f319ed110d035629d225d84426867cdad9320fc5`. The manifest and archive bind the clean candidate before this documentation closure; the final documentation-only commit does not change the tested runtime. No claim is made that this archive includes its own future evidence report.

Runtime inventory includes package versions/dependency names and Python/OpenSSL/SQLite/Expat versions. No new dependency, provider endpoint, port visibility, trading permission, secret or deployment configuration is introduced. The new owner-gated ARM64 cohort remains manual-only with the existing free-usage/branch gates. No workflow was dispatched.

The fixture network guard, provider-disabled cohorts and HTTP/WS security tests remain active. The local TLS checks cover ordinary forwarding, rewritten WS Origin/Host, rewritten HTTP issuer, foreign-origin denial and cross-origin preflight denial. Proxy fixtures are not proof of the real owner Codespaces trust boundary.

No current offline vulnerability/advisory database or owner-target OS evidence was supplied. Pins, a successful build and `pip check` cannot clear runtime, transitive JS/native dependencies, OpenSSL, SQLite, Expat or OS advisories. Fresh target advisory review, installed artifact provenance and patch status are **PENDING**. No package upgrades or warnings were hidden to manufacture clearance. Source archive inventory is an accidental/private-output check, not proof against a malicious maintainer.

Reproduce with existing free local tools (no provider calls):

```bash
.venv/bin/python -m pip check
.venv/bin/python tests/test_python.py
.venv/bin/python tests/test_export_contracts.py
.venv/bin/python examples/python_research.py
.venv/bin/python tests/test_sdist_patterns.py
.venv/bin/python -m build --sdist --no-isolation --outdir build/sprint2-sdist
.venv/bin/python scripts/check_sdist_inventory.py build/sprint2-sdist/gig_microstructure-0.1.1.tar.gz --manifest build/sprint2-sdist-manifest.json
npm --prefix terminal/web test
npm --prefix terminal/web run build
```

The build toolchain must already contain the pinned build requirements. Artifact/public-source privacy review found no raw market data, credentials, owner contact values, private databases or binaries among committed changes. Ignored raw logs, screenshots, archives and temporary fixture state were not committed; EVIDENCE.json contains safe summaries/hashes only.
