# P1J independent dependency, security and distribution review

Reviewed October 23, 2026 UTC against `5584ce34de5b839d2a78fabcd8e6603cec1185f3`.
This review changes documentation and private evidence only. It does not approve
publication, upgrades, observed-data claims or production operation.

## Actual inventory and dated checks

Private raw evidence is `build/p1j/evidence/dependency-review.json` and
`security-inventory.json`; the latter retains dependency edges, interpreter and
system-package identities, artifact inventory/hash and official-query responses.
The runtime skill, current environment status and local network policy were read
before queries. Runtime observations were current but HTTP enforcement state was
`unknown`; no enforcement/readiness claim follows. Only bounded HTTPS GETs to
PyPI and official upstream GitHub pages were made, with inherited proxy/TLS trust.
No market bytes, dependency installs, upgrades or network configuration changes occurred.

Command (exit 0):

```sh
PATH=/workspace/gig-tools/bin:$PATH python scripts/review_dependencies.py \
  --wheels build/phase9-dependency-wheels \
  --output build/p1j/evidence/dependency-review.json
```

All 12 version-specific PyPI JSON responses verified identity/version. Every saved
wheel matched that endpoint's filename/SHA256; all 12 installed versions matched
the exact lock. Zero active advisories were returned, zero integrity mismatches
and zero unavailable metadata endpoints. This is a dated PyPI snapshot, not all-source
CVE clearance, a signature or independent publisher authentication. The script
records timestamp, source, dirty state and lock/script hashes. Its exit status alone
is insufficient: unavailable metadata does not cause nonzero exit, so consumers
must also require `unavailable_metadata == []`.

| Role on tested Linux CPython 3.12 | Exact components |
|---|---|
| Direct runtime | jsonschema 4.23.0 |
| Transitive runtime | attrs 26.1.0; jsonschema-specifications 2025.9.1; referencing 0.37.0; rpds-py 2026.9.1; typing_extensions 4.16.0 |
| Direct build | pybind11 2.13.6; scikit_build_core 0.11.6 |
| Build support/frontend | packaging 26.3; pathspec 1.1.1; build 1.2.2.post1; pyproject_hooks 1.3.3 |
| Separate native/host components | system zlib 1.3.1; GCC meta-package 4:14.2.0-1; libstdc++ 14.2.0-19; glibc 2.41-12+deb13u4; CMake 3.31.6; Ninja 1.11.1.git.kitware.jobserver-1 |

The actual review interpreter is CPython 3.12.14 built with Clang 22.1.3. The host
has no Debian package named `clang`; that dpkg query partially succeeds and exits 1,
which is retained rather than treated as absence of a Clang executable. The Python
fixture compressor and optional system-linked native inflater remain separate
implementations. Earlier inspected native header/runtime/library hashes remain in
`build/p1h/evidence/compression-dependency.json`; they are not current CVE evidence.

On the tested interpreter, jsonschema's dependency graph above closes against the
lock. Build extras, JSON format extras and other interpreter/platform markers are
not activated. `pyproject.toml:9` permits Python 3.9–3.12, but this lock and artifact
are qualified only on 3.12 Linux x86_64; older interpreters have extra conditional
build requirements. Ordinary pip installation may resolve transitive runtime
versions other than this lock unless constraints are supplied.

Three bounded official upstream advisory-page GETs returned HTTP 200, untruncated:
`github.com/madler/zlib/security/advisories` (186327 bytes),
`github.com/python/cpython/security/advisories` (184036 bytes), and
`github.com/llvm/llvm-project/security/advisories` (182946 bytes).
Each page says “There aren't any published security advisories.” Raw HTML, extracted
text, timestamps and hashes are privately retained as `official-*-advisories.*`.
That means those repository feeds supplied no advisories; it does **not** establish
that these components lack vulnerabilities or that other official security feeds
are empty. GCC, distro backports, CPython security release notes, glibc, kernel,
CMake and Ninja have not received a comprehensive version/applicability review.
No forbidden API retries or unauthorized mirror queries were made.

## Material findings and acceptance

| ID / severity / status | Evidence and affected contract | Remedy, measurable acceptance, owner/effort and risk |
|---|---|---|
| SEC01 / P1 release gate / BLOCKED: native/platform advisory applicability incomplete | CMakeLists.txt:103–108 activates system zlib >=1.3.1; the official-page observations above are not a complete current platform review. Python script explicitly excludes compiler/CPython/kernel. | Candidate owner/security reviewer must map actual compiler, interpreter, system library and distro patch identities to dated official advisories, including affected/fixed ranges and reachable use. Retain unavailable sources as BLOCKED. Several hours plus source access; residual unknown advisories remain. No automatic upgrade authorized. |
| SEC02 / P1 hosted qualification / BLOCKED: runner zlib resolution unobserved | .github/workflows/ci.yml:9,17–21 requests Ubuntu 24.04 distribution zlib1g-dev; CMakeLists.txt:105 requires >=1.3.1; CMakePresets.json enables streaming in all three presets. Local Debian 1.3.1 success cannot qualify Ubuntu. | CI owner must retain actual runner package/header/runtime versions and configure/test results at candidate SHA. No reproduced hosted failure is alleged. Small effort once hosted access is available; runner drift remains. Parent audit owns hosted access query. |
| SEC03 / P1 public distribution / BLOCKED by scope and absent grant | THIRD_PARTY_NOTICES.md:3–4 explicitly provides no project redistribution license. Dependency notices do not license project code or market data. | Owner must separately authorize any distribution and resolve applicable project/data/dependency rights for its exact manifest. Current acceptance is private unpublished retention. Legal/owner effort unknown; no public release authorized. |
| SEC04 / P2 reproducibility / OPEN limitation | pyproject.toml:2,9–10 pins direct build/runtime only; workflow:34,58 supplies lock/constraints, but ordinary consumer installs can resolve other transitives. Lock has exact versions but no pip-enforced hashes; current manual hash comparison covers saved wheels only. | Preserve exact reviewed wheels and lock alongside private candidate; qualify any differently resolved environment separately. A future hash-enforced install proposal requires approval only if it changes authorized scope. Small documentation/packaging effort; network resolver/source trust remains. |

No reproduced dependency vulnerability or wheel-integrity defect was found by these
bounded checks. SEC01 remains a gate rather than being converted to clearance.
Operational persistence, authentication, broker resilience and live trading are
excluded requirements (RC27), not defects repaired by this documentation review.

## Artifact and notice inspection

Inspected actual `build/p1i/source-dist/gig_microstructure-0.1.1-cp312-cp312-linux_x86_64.whl`:
its complete member list and SHA256 are retained in `security-inventory.json`.
It contains the Python module, native extension, schemas, metadata and
`gig_microstructure/THIRD_PARTY_NOTICES.md`; that notice matches source byte-for-byte.
Its METADATA declares version 0.1.1, Python >=3.9,<3.13 and jsonschema==4.23.0.
No member filename matched the bounded restricted/credential indicators recorded
in that inventory. This filename check is not an exhaustive secret-content scan,
or proof of origin/attestation. Other reviewers own broader source/artifact scans.

CMakeLists.txt:328–330 installs the extension, schemas and third-party notices.
The ordinary wheel feature defaults leave optional streaming OFF; zlib is a
separate enabled native distribution consideration. THIRD_PARTY_NOTICES.md:17–45
includes the pybind11 BSD conditions; lines 58–81 retain zlib's upstream notice.
Installed metadata records MIT for attrs/jsonschema/specifications/referencing/
rpds-py/pyproject_hooks, Apache-2.0 OR BSD-2-Clause for packaging, PSF-2.0 for
typing_extensions and BSD for pybind11. Some distributions express licenses via
classifiers/files rather than the scalar license field; raw paths/classifiers are
retained in dependency-review.json. This is an inventory, not a complete SBOM or
license opinion. No dependency wheel is incorporated wholesale into this project
wheel; redistribution of a bundled wheelhouse would require its own complete
notice/manifest review.

## Later closure evidence (2026-10-23)

The bounded review above is preserved as the P1J checkpoint. Subsequent closure
work reproduced the Ubuntu distro-zlib minimum-version failure, validated an
official checksum-pinned private1.3.1 prefix, and collected dated CPython/Expat/
zlib/vendor-backport evidence. See [RC_SECURITY_APPLICABILITY.md](RC_SECURITY_APPLICABILITY.md)
and [RC_EVIDENCE_CLOSURE_REPORT.md](RC_EVIDENCE_CLOSURE_REPORT.md). SEC01/RC16 and
hosted SEC02/RC17 remain BLOCKED for explicitly documented evidence gaps. A local
runner dependency repair is no longer merely a hypothesis; hosted success still
has not been observed. No project/raw-data distribution permission is inferred.
