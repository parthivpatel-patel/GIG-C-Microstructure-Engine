# Non-destructive private deployment qualification

Source: `62d8d50e2dd629db181114eaceb5845509a137b6`.
Implementation: `terminal/verification/deployment.py`, CLI
`scripts/qualify_private_deployment.py`, additive health receipt in
`terminal/server/app.py`. No auth/proxy/permission policy changed.

## Offline procedure and results

The qualifier requires an independently supplied full 40-character candidate SHA;
a short SHA is rejected. It checks the actual checkout, tracked changes, untracked
runtime source, a bounded Vite manifest and actual index/entry file hashes. It
compares all 17 direct runtime pins and inventories installed distribution names,
versions and dependency names/conditional/direct-reference flags. It never imports
those packages to run their code, dumps provider environment, reads private SEC
configuration, upgrades packages, installs dependencies or fetches advisories.
Dependency URLs/paths/marker text are not echoed. `pip check` complements the
inventory with offline installed-requirement resolution.

Actual clean-code-commit run: `PASS_OFFLINE_CHECKS_ONLY`, no failures, all direct
pins match, 19 installed distributions inventoried. `pip check`: no broken
requirements. Inventory and dependency metadata are not CVE clearance.
See [runtime-offline.json](evidence/runtime-offline.json),
[toolchains.json](evidence/toolchains.json), [pip-check.log](evidence/pip-check.log).
CPython 3.12.14, OpenSSL 3.5.8, SQLite 3.53.1, Expat 2.8.3, Node 24.19.0,
npm 11.9.0, GCC 14.2.0; Linux x86_64. These are this environment's versions,
not a claim about the owner's Codespace or every native binary's build compiler.

Default invocation makes **zero network requests**. Explicit
`--check-local-server` adds only a fixed `127.0.0.1:8787/api/v1/health` read:
2-second socket timeout, 64KiB conservative response cap, no redirects or environment
proxy, no arbitrary URL, mutations or state/market-record retrieval. It rejects
oversized declared responses before reading; exact-cap unknown-length responses
are rejected without reading beyond the cap. JSON output whitelists release fields.

A fresh loopback native-backed fixture server was started and stopped by this
sprint. Its frozen source/index/entry receipt matched the clean implementation
checkout: [runtime-local.json](evidence/runtime-local.json). Private configuration
was not loaded: the fixture passed an explicit empty StockWorkspace environment.
This is **not the owner's target and not GitHub authentication**.

## Startup versus checkout

`application_release` is captured once when `create_app()` constructs the server.
Subsequent `/health` calls do not recalculate it from a newer checkout. The qualifier
compares startup SHA, tracked-clean flag, index hash and entry hash with current
disk state; mismatch blocks qualification. Tests also change an asset after capture
and demonstrate a stale receipt rejection. This is a process-start observation,
not a cryptographic attestation of every loaded Python module, native library or
dynamic JS chunk. Build, stop the old server and restart before final acceptance.

Default dist paths must be ordinary bounded files, not symlink escapes. Missing
assets, dirty checkout, unexpected runtime source, wrong SHA, pin mismatches,
missing old-server receipt and invalid launcher metadata are explicit failures.
Artifacts are exclusively created mode0600; existing output is never overwritten.
Use a fresh ignored output filename on each run. Filesystem tools assume an
owner-controlled directory, not a privileged service protecting against a hostile
concurrent rename of its ancestor directories. Output writes are fsynced exclusive
writes, not a crash-atomic multi-file attestation transaction.

## Origin / Host and HTTPS / WSS

The existing policy remains exact configured Origin plus exact Host/proof binding.
Launcher configuration derives only from server-owned Codespaces metadata, never
incoming forwarding headers. The qualifier reads only the four public launcher
variables and rejects an expanded origin list for this one-origin Codespaces
qualification profile. It does not modify settings or turn a local bind public.
55 local policy cases exercise unauthorized origins, forged forwarding metadata,
wrong authority, proof replay/expiry and bootstrap boundaries. Three dedicated
TLS-verified local proxy cohorts exercise real HTTP/WebSocket upgrades, Origin/Host
rewriting, proof authorization and reconnect paths: 20 checks pass.

Certificate verification was enabled with a dedicated ephemeral test CA. No TLS
verification, Origin/Host validation or private forwarding control was disabled.
Forwarded headers do not expand allowed origins. Proxy fixtures do not identify
which component rewrites the owner's request, authenticate a GitHub user, prove
an unauthenticated request is denied at the GitHub edge or confirm private visibility.

## Target-only gates and dependency clearance

The final owner-run procedure is in [FINAL_OWNER_ACCEPTANCE.md](FINAL_OWNER_ACCEPTANCE.md).
It requires actual private-port settings, logged-in GitHub forwarding, a fresh
unauthenticated-browser denial, real HTTPS/WSS diagnostics/reconnection and exact
candidate source receipt. Do not publish cookies, proofs, tickets or full headers.
Do not change port visibility to public, add localhost to external allowed Origins,
or use a wildcard. A local successful probe never substitutes for this gate.

Runtime security remains **PARTIAL / target clearance required**. Review actual
owner Python/system patch/backport evidence, the exact lockfiles and frontend
dependency graph, browser/Node versions, and immutable GitHub Actions dependencies
against applicable advisories. This sprint did not access a live advisory service;
Sprint 1's npm zero-advisory receipt is historical evidence, not today's clearance.
The two new source archives were checked without extraction for intended members,
content equality and private/build exclusions. No dependency version was changed
blindly and no paid scanner or cloud runner was used.
