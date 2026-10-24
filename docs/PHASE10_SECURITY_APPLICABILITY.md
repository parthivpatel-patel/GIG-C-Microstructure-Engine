# Phase 10 dependency applicability — October24,2026

**RC16 remains BLOCKED.** This is a dated source/path/vendor review, not a claim
that missing feeds or passing sanitizers prove security. No candidate dependency
was upgraded. Cross compiler/QEMU tools were added only in the existing qualification
container, with27 new packages/0 upgrades; their security boundary is separate.
Raw inventory,21 bounded fetch outcomes/body hashes and selected signed-package
changelogs are in build/extended/evidence/security-* and vendor-changelogs.txt.

## Actual component findings

| Component/version | Authoritative evidence and classification | Mitigation / remaining requirement |
|---|---|---|
| Native zlib1.3.1 | CNA CVE-2026-22184 explicitly limits overflow to contrib/untgz, not core library: **confirmed not applicable** to deployed inflater. Official1.3.2 ChangeLog fixes inflateCopy/deflateCopy/crc32_combine paths not called by engine. |No untgz or minizip intake; engine uses inflateInit2/GetHeader/inflate/End with bounded buffers. Other advisory/backport coverage unresolved, not blanket clearance. |
| Python fixture zlib1.3.2 |Actual header/runtime inventory; contains documented1.3.2 upstream changes: **fixed for those changes**, not all vulnerability-free. |Separate from native1.3.1; maintain artifact identity. |
| Managed CPython3.12.14 |Official3.12.15 security notes datedOct1 document later tar extraction/link/filter, zip decompression, TLS/SNI, huge precision and password-manager fixes. **Affected upstream version; provider patch applicability unresolved.** |Only authenticated Git/source/dependency archives; no hostile archive extraction or arbitrary decompressor. No TLS server/SNI callbacks, custom password manager or near-INT_MAX formatting in engine. Provider must qualify patch/upgrade before broader intake. |
| Ubuntu Python3.12.3-1ubuntu0.17 |Installed vendor changelog explicitly backports CVE-2026-4360 and15308, among others: **backported for named fixes**. |Do not infer all fixes absent/present from upstream version; remaining October upstream/vendor mapping unresolved. |
| Managed Expat2.8.3 |Official2.8.5 fixes CVE-2026-93990 UTF16 surrogate validation. Evidence verifier enforces strict UTF8, rejects NUL/DTD/entities before parsing: **specific UTF16 input path excluded**. Upstream also flags unresolved nonpublic issues. |Restrict to local/authenticated qualification JUnit. Attribute/CPU/salt/provider patch questions remain unresolved; no hostile XML clearance. |
| Ubuntu Expat2.6.1-2ubuntu0.6 |Vendor changelog lists56410/56406 backports: **backported in part**. |Not a complete mapping to managed Expat or all later upstream issues. |
| Managed Python OpenSSL3.5.8 |Official OpenSSL3.5 branch NEWS:3.5.9 Sep29 security release, highest severity High. Includes DTLS/QUIC/CRLDP/EC/SM2/context-switch/CMP fixes. **Unresolved affected-version/provider mapping**; no exploitable engine defect reproduced. |Engine exposes none of DTLS/QUIC/CMP/SM2/custom-context switching. Normal HTTPS client/provider paths still need feature/backport analysis; cannot declare all3.5.9 fixes inapplicable. Owner/provider patch evidence or qualified patched runtime required. |
| Distro OpenSSL3.5.7-1~deb13u2 /Ubuntu3.0.13-0ubuntu3.16 |Actual versions differ from Python linkage. **Unresolved** vendor security mapping; nominal version is not backport evidence. |Preserve TLS verification/proxy trust. Do not conflate curl, interpreter and native linkage; core engine does not link OpenSSL. |
| GCC14.2.0-19/libstdc++14.2.0-19; Ubuntu GCC13.3/runtime14.2 |Actual package inventory; official GCC security page unavailable via proxy. **Source unavailable /unresolved**, not clear. |Trusted project source only; no arbitrary compile service. Require vendor/provider advisory applicability and exact package hashes. |
| Clang19.1.7, Ubuntu18.1.3 |Official LLVM SECURITY.md reachable, but a reporting policy is not a complete advisory list. **Unresolved**. |No broad scanner/advisory absence claim; trusted build-only use. |
| glibc2.41-12+deb13u4; Ubuntu2.39-0ubuntu8.9 |Ubuntu changelog lists CVE-2026-19499/19542 fixes: **backported in part**. Full outer/provider mapping unresolved. |Do not derive global status from distro version; obtain provider evidence. |
| Kernel6.18.55 |Managed/shared kernel, no provider patch manifest available: **unresolved**. |Container/cross/emulated tests do not close host security or independent-machine gate. |
| CMake3.31.6/Ninja1.11.1/Git2.52/curl8.14.1-2+deb13u5 |Versions recorded; official CMake release notes reachable, not exhaustive advisories. **Unresolved** wider mapping. |Trusted builds/artifacts, normal CA/proxy. Keep provisioning/tool security separate from engine correctness. |
|12 pinned Python packages |PyPI version-specific metadata for all installed lock entries HTTP200, zero vulnerabilities returned. **No advisories returned by this feed**, not proof secure. |Keep exact lock/artifact hashes; no unnecessary resolution/upgrade. Full list in security-inventory.json. |
| AArch64 GCC13.3 cross/QEMU8.2.2 distro.18 |Signed official Ubuntu packages; target glibc2.39-0ubuntu8cross1/libstdc++14.2 cross. **Unresolved tool/target advisory applicability**. |Only locally authored trusted ELFs/synthetic input, no binfmt/privileged guest or exposed service. Emulation does not qualify these packages for production. |

No reproduced confirmed-applicable engine exploit, new critical/high production
defect or silent remediation. An affected upstream version is a serious review
input, not automatically a proven reachable exploit or a fixed provider build.
Selected unused API paths can be excluded only for the stated candidate scope.

## Source access, chronology and restrictions

Seven authoritative upstream/CNA sources returned200 (zlib changes/CNA, CPython
3.12.15, Expat2.8.5, OpenSSL3.5 NEWS, LLVM security policy, CMake3.31 notes).
GCC security and Ubuntu notices returned CONNECT failures (curl56/HTTP000);
no retry or unofficial mirror.12 PyPI endpoints returned200/zero listed advisories.
Each request bounded2MiB/20s, normal TLS, no retries. URLs/status/bytes/SHA256 in
security-sources.json. Mutable development headings/future items are not treated
as released fixes on October24. Only dated published release/CNA claims are used.

OpenSSL3.5.9 is already datedSep29, before this review; do not dismiss it as future.
Its crypto/client-specific applicability remains an explicit owner/provider action.
The prior RC_SECURITY_APPLICABILITY.md remains historical evidence, not overwritten.

No arbitrary third-party archives/XML are newly authorized. New library versions
must be justified, supplied through supported provider/environment mechanisms and
regression-qualified; this review does not silently replace the managed interpreter,
TLS libraries, compiler or kernel. Formal security closure requires dated patch/
backport identities, demonstrated path exclusion or explicit scoped owner acceptance
for each remaining item. This session cannot invent provider attestation.
