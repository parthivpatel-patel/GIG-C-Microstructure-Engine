# Passive local installed-artifact inventory

The opt-in `scripts/inventory_local_artifacts.py` developer tool inventories an
explicit local virtual environment, explicitly named native files and standard
passive OS metadata. It imports no installed package code, executes no package or
system commands, opens no network socket and starts no application. Existing source
lock SBOM behavior, dependency pins, native interfaces and defaults are unchanged.

This closes a concrete SECURITY03 engineering prerequisite: a current local
installed-file/version/hash inventory distinct from declared source pins. It does
**not** establish complete target security clearance. SECURITY03 remains PARTIAL.

## Supported source contract

The canonical JSON schema is `gig.security.local_artifact_inventory.v1`, profile
`PASSIVE_RECORDED_ARTIFACTS_DPKG_V1`. The source-commit label is an explicitly supplied
40-character lowercase hexadecimal string. It is not independently authenticated,
and neither native filename nor ELF header proves that a binary was built from that
commit. A separate build/deployment attestation is required for that relationship.

The root, virtual-environment path and site-packages path are explicit. Only direct
`.dist-info` children are discovered. Each has one exact Name/Version in METADATA and
a CSV RECORD; normalized duplicate project identities reject. Original declared project spelling is
retained separately from its normalized comparison key. Every RECORD member
must remain within the named environment, including legitimate leading parent
segments used for its installed `bin` scripts. Internal traversal, absolute paths,
symlinks, duplicate members and sensitive credential/control names reject. METADATA
and RECORD must themselves be listed. No unrecorded site file or arbitrary directory
is promoted into coverage.

Every recorded regular file receives a SHA-256 digest. Existing RECORD SHA-256,
SHA-384 or SHA-512 digests and declared byte lengths are checked exactly. Missing
RECORD hashes/sizes are counted explicitly and are not called verified. Project
versions are retained exact metadata strings; the tool does not infer publisher
trust, verify a registry signature, resolve dependency reachability or claim that
RECORD self-consistency proves authenticity. Installed package code is never imported.

Each explicitly selected native artifact must be a regular ELF file. Its original
bytes, SHA-256, class, byte order, object type, machine value and header format version
are retained. Declared ELF header size/version must agree with its class. This is
bounded header identification, not full ELF structural validation, dynamic-library
resolution, software-version authority or native ARM64 execution evidence.

OS identity comes from `/etc/os-release`, or its standard vendor file
`/usr/lib/os-release`. The normal `/etc/os-release -> ../usr/lib/os-release` alias is
validated explicitly. Arbitrary symlink targets, vendor symlink chains and changed
source precedence reject; no arbitrary system path is followed. A supported passive
assignment subset retains selected OS fields and the original source hash. Repeated
keys, shell expansions, escapes/concatenation outside that subset and malformed ID
values reject explicitly. No shell is used. The specification permits broader
escaped strings; this tool does not claim support for those interpretations.

When `/var/lib/dpkg/status` is present, its exact source hash and bounded Debian
control stanzas are read passively. Exact Package, Version, Architecture and Status
are retained with the original stanza number. Duplicate fields are checked case
insensitively; duplicate package/architecture identities, malformed fields/statuses,
unsupported missing identity fields and bounds reject. Multi-architecture instances
remain separate. Desired action, error flag and installation state remain distinct;
`installed_state_records` does not imply `installed_ok_records`. Non-installed rows
remain in the inventory. Long package descriptions are bounded but not exported.
This is status-database coverage, not installed OS package-file integrity, package
manager command output, kernel inventory or advisory matching. Other package managers
and an absent status database remain explicitly outside coverage.

Authoritative formats independently consulted during this package:

- [Installed distribution RECORD](https://packaging.python.org/en/latest/specifications/recording-installed-packages/) and [PEP 376](https://peps.python.org/pep-0376/).
- [os-release identity and precedence](https://www.freedesktop.org/software/systemd/man/latest/os-release.html).
- [Debian control syntax](https://www.debian.org/doc/debian-policy/ch-controlfields.html) and [dpkg-query status fields](https://manpages.debian.org/bookworm/dpkg/dpkg-query.1.en.html).

These documentation references are not provider qualification or vulnerability
advisory evidence. No market-data or SEC service was accessed for this package.

## Bounds and failure behavior

Each file is at most 64 MiB, total unique original bytes at most 512 MiB and original
file count at most 20,000. Python metadata/RECORD files are at most 2 MiB; direct site
entries are sampled only through the 4,097th entry before a 4,096-entry limit is
rejected. At most 256 distributions and 32 explicitly named native artifacts are
admitted. All relative paths are bounded to 1,024 printable characters. Reads reject
nonregular files and observed size/identity/time changes; a hostile concurrent
namespace replacement guarantee is not claimed.

The dpkg database is at most 8 MiB / 20,000 records / 256 KiB per stanza / 128 fields
per stanza / 128 KiB per field. The field limit supports the real executor's 94-KiB
texlive description; that body is never exported. The OS identity file is at most
64 KiB. Canonical output is capped at 16 MiB. A failure returns no successful
inventory result. CLI output creation is exclusive, mode 0600, and refuses symlinks
or overwriting an existing file. Crash-safe durable publication is not claimed.

## Developer reproduction and acceptance

From the repository root, using already installed tools:

```sh
work/venv/bin/python tests/test_local_artifact_inventory.py
work/venv/bin/python scripts/inventory_local_artifacts.py --root /workspace/gig-development --venv work/venv --site-packages work/venv/lib/python3.12/site-packages --native-artifact build/recovery-release/python/gig_microstructure/_native.cpython-312-x86_64-linux-gnu.so --native-artifact build/recovery-release/gig_itch_source_recovery_tests --source-commit eb83f8a5086d606b5f5177d30aefde0e14650a0f --output work/security-local-recovery/local-inventory-combined.json
```

Use a new output path and the actual intended commit label when reproducing. No
installation, scanner download, dependency upgrade or external target is required.
The native files must be explicitly built/available; missing inputs fail closed.

The focused suite covers exact original hashes/versions, altered bytes/sizes,
malformed or unsupported hashes, duplicate distributions/members, required metadata,
path traversal/secret names/symlinks, allowed environment entry points, FIFO rejection,
observed read changes, native headers, OS source precedence, dpkg multiarch/status and
source ordering, 96-KiB legitimate description retention bounds, malformed UTF-8,
resource excess, deterministic relocation and exclusive private output.

Actual final local counts/hashes belong to the enclosing source/evidence receipt.
The result always says `CURRENT_LOCAL_EXECUTOR_ONLY`,
`target_environment_qualified:false` and advisory `NOT_RUN`. It does not supply
private-edge configuration/authentication, full ELF dependency closure, kernel/OS
package-file integrity, advisory/backport/reachability analysis, physical browser or
owner-target verification. These remain exact SECURITY03 acceptance dependencies;
no whole-row promotion or vulnerability-absence claim follows from this inventory.
