# Deterministic offline source-lock inventory

`build_offline_sbom.py` complements the existing network advisory/wheel review in
`review_dependencies.py`. It emits a source-bound CycloneDX 1.6 JSON inventory with
no network, install, upgrade, provider or application operation. It covers these
seven current source inputs:

- requirements-python.lock and terminal/server/requirements.txt;
- pyproject.toml project dependencies and build-system requirements;
- terminal/web and terminal/tests package.json/package-lock.json pairs.

Python names are normalized and exact pins are required. npm v3 package entries
include every locked platform/dev/optional package, deduplicated by package URL and
version while retaining each source occurrence. Exact direct declarations must
match the root lock and selected locked package. Registry host, artifact name/version
path, SHA512 integrity form, flags and source structure are validated. Workspace
links, npm aliases, alternate registries and unpinned Python inputs are deliberately
unsupported. This is an explicit bounded source contract, not a generic package-manager
resolver. Existing independent surfaces may pin different versions; separate versions
remain separate components, rather than being silently merged.

Each input contributes its SHA256 and byte size to a canonical input-manifest hash.
Component provenance preserves lock-only artifact SHA512 values and explicit false
artifact_download_verified flags. No retrieval or authenticity is inferred from a
lock hash. The supplied source-commit value is labeled as a caller revision label;
the actual byte hashes remain authoritative if the checkout is dirty. No timestamp,
absolute path, installed-environment metadata or random UUID affects deterministic
output. Canonical bytes therefore agree across equivalent relocated source trees.

Limits: 2 MiB per input, 8 MiB total input, 10,000 unique components/lock records,
8 MiB emitted JSON, and bounded package/version/path text. Inputs reject symlinks,
nonregular files, duplicate JSON keys, malformed/future lock structures and
contradictory same-source Python pins. Output uses exclusive creation, no symlink
following and owner-private0600mode. Existing evidence is never overwritten. It is
not a crash-durability/journal contract; after an interrupted output write, inspect
and choose a new output path. Ancestor-symlink checks are not a general defense
against concurrently hostile filesystem namespace replacement.

Example (developer source access only):

```
work/venv/bin/python scripts/build_offline_sbom.py \
  --source-commit FULL_VERIFIED_GIT_SHA \
  --output work/new-source-sbom.json
work/venv/bin/python tests/test_offline_sbom.py
```

The current source run emits85components from7inputs. Thirteen offline regressions
cover deterministic relocation/provenance, exact declarations, direct lock binding,
duplicate keys, future versions, malformed integrity, hostile source URLs/paths,
links/aliases/symlinks, resource limits, exclusive private publication and revision
labels. Socket connection is prohibited in the representative generation test.

This is source-lock coverage only. It does not claim the installed/runtime dependency
graph, native/OS/CPython/OpenSSL inventory, artifact-download verification, license
clearance, vulnerability scanning, a fresh advisory database or deployed target
security clearance. Optional and dev dependencies are not asserted reachable in
production. SECURITY03 must remain PARTIAL pending target-specific evidence. No
schema certification, package-version upgrade or advisory result is invented.
