# Security, dependency and supply-chain qualification

October24,2026. **Review/hardening completed within bounded local scope; full
security clearance remains BLOCKED.** No new reachable critical/high engine exploit
was established. Sanitizer success and empty advisory feeds are not security proof.

[evidence/dependency_inventory.json](evidence/dependency_inventory.json) inventories
12 exact Python pins plus native zlib, compiler/standard library, CPython/linked
OpenSSL/Expat, build tools and action dependencies with source/license/update/risk.
Installed Python distributions and downloaded wheel digests were checked against
fresh version-specific PyPI TLS metadata:12 responses, no active advisories returned,
no mismatches/missing wheels. This feed is not a comprehensive supply-chain audit.
Seven retained official/CNA sources from the same dated environment review were
rehash-verified against their receipts; not reclassified as new vulnerability scans.
GCC/Ubuntu advisory endpoints previously blocked were not repeatedly retried.

## Prioritized register

| Priority / status | Evidence and applicability | Disposition |
|---|---|---|
|High / unresolved provider applicability|Managed OpenSSL3.5.8 precedes documented3.5.9 security fixes; CPython3.12.14 precedes3.12.15; Expat2.8.3 precedes2.8.5. Prior official source URLs/hashes and named paths retained in PHASE10_SECURITY_APPLICABILITY.md.|Obtain provider patch/backport identity or qualify supported patched runtime. No silent interpreter/TLS replacement. No broad hostile archive/XML clearance.|
|Medium / partial upstream exclusion|CVE-2026-22184 CNA limits overflow to contrib/untgz; that tool is not deployed. zlib Copy/combine fixes concern APIs not called by bounded inflater.|Specific path exclusion only, not blanket core or package clearance. Maintain native/fixture zlib identities separately.|
|Medium / partial upstream exclusion|Expat CVE-2026-93990 addresses UTF16 path; evidence intake forces UTF8/NUL/DTD/entity rejection.|Does not clear every Expat issue or provider build. Keep authenticated local evidence restriction.|
|Medium / operational hardening applied|Six native run annotations identified deprecated checkout Node20 runtime.|Official actions/checkout v6.1.0 tag resolves to d23441a48e516b6c34aea4fa41551a30e30af803; action.yml declares Node24, MIT license and maintained runtime requirements. Both workflows use that immutable SHA and persist-credentials:false. Hosted execution of this update NOT RUN.|
|Low / reproduced and repaired|New Phase1 receipt verifier rejected leaf symlinks/escapes but accepted an internal parent-directory symlink, contrary to its strict no-symlink policy.|Added parent/leaf controls: before1 failure/8, after8/8. Every artifact path component is now checked. No external escape or memory corruption was reproduced. Concurrent adversarial filesystem mutation remains outside trusted-local receipt scope.|
|Unresolved / inventory coverage|Managed kernel, libc, compilers, CMake, Ninja and transitive action bundle do not have a complete dated vendor applicability manifest.|Owner/provider/vendor evidence required; trusted project source/builds only, no arbitrary compilation service or paid scanner inferred.|

## Action update verification and controls

Official git ls-remote identifies v6.1.0 and moving v6 at the same immutable SHA.
Four official immutable files (action.yml/package.json/LICENSE/README) were fetched
with verified HTTPS, bounded2MiB/20s and zero retries; identities archived privately
and SHA-bound in the inventory. action.yml uses node24. Upstream npm metadata still
says5.0.0; it is recorded as metadata, not invented as the action release version.
README documents runner minimum2.327.1 for Node24 and2.329.0 for authenticated Git
inside container actions. These workflows do not use container actions. Existing
GitHub run already reported forced Node24 for old checkout; new revision execution
still requires separately authorized hosted validation. No action or workflow was
launched during this program.

Permissions remain contents:read, actions pinned, no pull_request_target, no secrets
in test commands, no third-party artifact upload/cache. Untrusted fork tests execute
on disposable hosted infrastructure with read-only scope; no privileged runner or
paid label added. Persisted checkout credentials are unnecessary for local Git
provenance/builds and are disabled. ARM remains workflow_dispatch-only, owner
free-usage-gated and feature-ref restricted; original six compiler cases and all
count/hash requirements retained. No claim of authenticated artifact signatures.
Public visibility is no software/data license grant; THIRD_PARTY_NOTICES.md corrected
that outdated private-repository statement without granting distribution rights.

## Source-sensitive boundary review

Reviewed BinaryFile length/record/offset ceilings (src/itch/binary_file.cpp),
DecoderView field/enum checks (src/itch/decoder.cpp), pending/prepared transaction
ownership (src/itch/context.cpp and reconstruction.cpp), gzip output/member/CRC
limits (src/itch/gzip.cpp), exact arithmetic/flow/execution bounds, journal logical
atomicity (src/replay/replay.cpp), bounded native deserialization and Python export
name/hash/reference handling (python/gig_microstructure/__init__.py).
Existing independent malformed/adversarial/allocation tests were exercised in the
fresh157-case suite; this is finite source review, not proof every path is safe.
User-asserted digests and initialization claims are not external authentication.
Filesystem exports have incomplete markers and no-overwrite files, not crash-safe
multi-file transactions or durable directory fsync guarantees. No disk journal,
HA, live credentials or broker connection exists; those are declared exclusions.

Validation: fresh Phase1 full157 outcomes/all8 identities retained; two workflow
YAML/permission/pin/matrix/trigger checks and all shell syntax pass;4 diagnostic
controls,3 packaging-pattern controls,8 receipt controls pass. Only workflow,
notice and receipt-tool/test changes; no engine arithmetic/book/journal behavior
change, so expensive native matrices are not repeated. Full hosted execution of
the new action is an explicitly unresolved verification item, not a claimed pass.
