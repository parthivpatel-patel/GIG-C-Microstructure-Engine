# Release-candidate security applicability — 2026-10-23

Decision: **RC16 BLOCKED**. This is a dated, bounded review for private Linux
x86_64 synthetic research, not vulnerability-free certification. No production
code or dependency version was upgraded. Earlier P1J advisory-page and twelve
PyPI checks remain evidence of those particular responses, not general clearance.
See `RC_CLOSURE_EVIDENCE.json` for versions, official-source hashes and outcomes;
private raw captures are under `build/rc-closure/evidence/`.

## Actual environments and applicability

| Component | Observed identity | Classification / relevant use | Required disposition |
|---|---|---|---|
| Native zlib | Original Debian library/header 1.3.1; Ubuntu distro 1:1.3.dfsg-3.1ubuntu2.3 reports upstream1.3; private qualified Ubuntu prefix1.3.1 | Distro1.3 fails project minimum. Official1.3.1 source is checksum-pinned, built without examples; header/runtime checked. CVE-2026-22184 concerns `contrib/untgz`, explicitly not core library: **not applicable** to the built/packaged inflater. | Retain pinned source identity; review later core-library advisories separately. Do not silently replace the approved minimum or install obsolete distro headers into the candidate. |
| zlib post1.3.1 fixes | Official1.3.2 ChangeLog, 2026-02-17 | `inflateCopy`, `deflateCopy`, negative-length `crc32_combine` fixes are outside production call paths (`inflateInit2`, `inflateGetHeader`, `inflate`, `inflateEnd`). **Not applicable to those specific fixes**; not blanket clearance. | No unnecessary upgrade; broader unknown advisories still belong to RC16. Python fixture compressor uses its interpreter's zlib, separately inventoried. |
| CPython outer | 3.12.14, built Aug25 with Clang22.1.3 | **Affected upstream version / use restricted** for fixes documented in3.12.15, Oct1. Tar extraction filter fixes include CVE-2026-82049; archive decompression limits include CVE-2026-15310. Qualification uses only Git-generated/source-hash-verified archives and pinned dependency wheels; no arbitrary user archives. | Do not process untrusted archives with this interpreter. A provider patch/upgrade and regression qualification is required for broader intake; current input restriction is a scoped deferral, not a fixed-version claim. |
| CPython network/format paths | Same interpreter;3.12.15 notes | Missing-hostname asyncio/`wrap_bio`, SNI callback lifetime (CVE-2026-19445), near-INT_MAX float precision and `HTTPPasswordMgr` scheme scoping (CVE-2026-15806) have upstream fixes newer than runtime. Candidate does not run TLS servers, SNI callbacks, asyncio TLS, custom password managers or externally selected float precision. **Not applicable to these inspected candidate paths**; managed proxy/auth implementation not audited. | Use normal verified HTTPS and bounded inputs; do not extrapolate this review to platform credential services. |
| CPython fresh Ubuntu | 3.12.3-1ubuntu0.17, Aug31 vendor build | **Backported in part / unknown for others**. Installed vendor changelog explicitly lists CVE-2026-4360,15308; earlier updates include1502,4224,6100,7774. Numeric upstream version alone is insufficient. October upstream changes have not been mapped to vendor fixes. | Retain package+changelog identities. Provider/vendor advisory mapping for remaining fixes is required; do not label plain3.12.3 either fully patched or wholly unpatched. |
| Expat outer/fresh | Python outer2.8.3; fresh2.6.1 (`libexpat1`2.6.1-2ubuntu0.6) | **Unknown/partly mitigated**, not cleared. Official2.8.5 fixes CVE-2026-93990 malformed UTF16 surrogates; evidence verifier requires strict UTF8, rejects NUL/DTD/entity declarations before XML parse (`scripts/check_validation_evidence.py`, `junit`). No custom encoding callbacks. This excludes those particular input paths.2.8.4 attribute CPU/salt issues and open nonpublic issues lack complete applicability/backport mapping. Fresh vendor changelog lists56410/56406 and other backports, not a universal fix. | Only locally generated or authenticated qualification JUnit is accepted in this review; no hostile third-party XML clearance. Complete provider/backport analysis or qualify patched runtime. `pyexpat.features` zero-valued entries are **not** interpreted as disabled-feature proof. |
| OpenSSL | Outer Python3.5.8; outer distro libssl3t64 3.5.7-1~deb13u2; fresh Python3.0.13 and distro3.0.13-0ubuntu3.16 | **Unknown** authoritative version/backport applicability. Distinct Python and distro linkage cannot be conflated. | Environment owner supplies dated provider/vendor security mapping; normal TLS verification remains enabled. |
| GCC / libstdc++ | Outer GCC14.2.0-19/libstdc++14.2.0-19; fresh GCC13.3.0-6ubuntu2~24.04.1, runtime libstdc++14.2.0-4ubuntu2~24.04.1 | Trusted project inputs; compiler and runtime are distinct versions. **Unknown** comprehensive advisory applicability. No arbitrary supplied source compilation endpoint. | Qualify actual package identities and vendor advisories; successful sanitizer tests do not clear toolchain CVEs. |
| Clang | Outer19.1.7 private signed Debian packages; fresh18.1.3 (1ubuntu1) | Build-only trusted source, system GCC standard library. Empty LLVM GitHub advisory page from prior review is not global clearance. **Unknown** full mapping. | Preserve versions, package provenance and future vendor review. |
| glibc | Outer2.41-12+deb13u4; fresh2.39-0ubuntu8.9 | **Backported in part / unknown remainder**. Fresh changelog includes CVE-2026-19499 (`strfmon`) and19542 (`tdelete`). No comprehensive outer provider mapping. | Owner/vendor patch review required; don't infer status from major/minor version or feed absence. |
| Kernel / container host | Managed Linux6.18.55 shared by both environments | **Unknown** provider advisory/patch mapping. Fresh rootfs is not a new kernel or VM. No privileged container, daemon restart or network reconfiguration. | Provider-owned security evidence; cannot close through CTest or a rootfs rebuild. |
| CMake/Ninja/Git/curl/apt/Docker | Outer CMake3.31.6; fresh CMake3.28.3-1build7,Ninja1.11.1-2; daemon28.4.0; exact package inventory retained | Build/provision-only, trusted inputs. Official CMake3.31 notes inspected; **unknown** complete security mapping for build/provision toolchain. Docker uses explicit local Unix socket, no host compile outputs mounted. | Use trusted scripts/hash-verified archives; keep daemon/provider CVEs in external applicability review. No new remote service introduced. |
| Python build/runtime dependencies | Exact12-version lock and cached wheel hashes in evidence | Prior same-day official PyPI identity/hash responses:12 matched, zero active advisories returned, zero unavailable. **No advisory returned by this feed**, not universal clearance. Fresh install restores reviewed wheels offline. | Preserve hashes; qualify any alternate dependency resolution separately. Existing lock pins versions, not pip-enforced hashes. |
| Third-party notices | Existing pybind11/zlib/package notices, source and installed wheel | **Inspected**, no new incorporated code/license grant. CI helper obtains official zlib source, preserves upstream source/license in private prefix work. | Project distribution grant and raw-data redistribution remain separate; no release authorization inferred. |

## Authoritative evidence and limits

Official resources captured through the configured proxy with normal TLS trust:

- [zlib ChangeLog](https://raw.githubusercontent.com/madler/zlib/develop/ChangeLog),
  SHA256 `483b3b6ca4c8d8b5f3bd4a8f49b94354e0957123d82b33a4ea4903de4915d56c`.
- [CNA CVE-2026-22184 record](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/22xxx/CVE-2026-22184.json),
  SHA256 `bb2494de3a5bc6ef534aa69abf8b1c2efd4919abe177df6452c76251992e3bfb`.
- [CPython3.12.15 security notes](https://raw.githubusercontent.com/python/cpython/3.12/Misc/NEWS.d/3.12.15.rst),
  SHA256 `1e4bc900b9a566a231ac43da64bb839f269456f7c70aa5f18ea05c8ca7a5e230`.
- [Expat2.8.5 changes](https://raw.githubusercontent.com/libexpat/libexpat/R_2_8_5/expat/Changes),
  SHA256 `d524be92cf55121cb6cb7bc13625f0498f1d31b4990fb52c93a574edbb372939`.
- [Expat open security issue1160](https://github.com/libexpat/libexpat/issues/1160),
  SHA256 `7e470d2d8ae8eff4c08d8940cf24fd85f4a9da20f31b10f182846d3f3e82284c`.
  This is a mutable live page listing unresolved nonpublic reports, including
  unvalidated ones. Its current text also contains a future-dated entry relative
  to this review; that entry is not treated as a verified October23 advisory.
  Nonpublic details cannot be independently assessed here.
- Installed signed Ubuntu package changelogs, `ubuntu-security-changelogs.txt`;
  exact source/installed versions in `final-environment.txt`.

The official Debian security Packages index was reachable, but its target-component
subset had zero matching entries. That is **not** proof of no advisories: packages
may move into point releases. An attempted official repository README returned404;
no substitute mirror was used. Full vendor trackers/provider patch mapping are
unavailable in current evidence. No broad scanner or all-CVE query was executed.

Reproduce inventory with `python -VV`, `ssl.OPENSSL_VERSION`,
`zlib.ZLIB_VERSION/ZLIB_RUNTIME_VERSION`, `pyexpat.EXPAT_VERSION`,
`dpkg-query -W`, compiler version commands, and installed
`/usr/share/doc/*/changelog.Debian.gz`. Preserve fetched bytes, URL, response,
size, SHA256 and review date; review source content as well as HTTP success.

Closure requires a security owner to map unresolved components to dated official
provider/vendor advisories and either record fixed/backported identities, prove
path-specific nonapplicability, or explicitly accept a scoped deferral. No confirmed
new exploitable critical/high engine defect was reproduced. The unresolved platform
and XML applicability questions still prevent formal security gate closure.
