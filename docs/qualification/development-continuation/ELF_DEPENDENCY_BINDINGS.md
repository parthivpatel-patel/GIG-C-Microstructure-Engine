# Passive ELF dependency bindings

`scripts/inventory_elf_dependencies.py` adds the opt-in offline profile
`EXPLICIT_ELF_NEEDED_BINDINGS_V1`. It supplements the existing local installed
artifact inventory with original-byte dynamic dependency metadata and an explicitly
supplied native dependency graph. It imports no installed extension, executes no
binary or `ldd`, reads no loader environment and performs no search for libraries.
It opens only manifest-named regular files within explicitly supplied roots.

This is one SECURITY03 prerequisite, not complete dependency/runtime/security
qualification. Source-lock inventory, passive installed inventory and this declared
ELF graph remain separate evidence contracts. Existing APIs/defaults are unchanged;
no advisory matching, package upgrade, provider operation or target clearance is
introduced.

## Input and immutable identity

The UTF-8 manifest schema is `gig.security.elf_dependency_manifest.v1`, with exactly:

- `schema` and caller-supplied lowercase 40-character `source_commit_label`;
- `roots`: at most eight explicit absolute directory paths keyed by bounded names;
- `artifacts`: at most 128 `{id,root,path,sha256}` records;
- `root_artifacts`: ordered, unique starting IDs;
- `bindings`: at most 2,048 `{requester,needed,target}` records.

Each artifact names a relative path and expected SHA-256. Input hashes are verified
before parsing. Duplicate paths/IDs/bindings, unsupported keys, traversal, symlinks,
secret/control path names and root escapes reject. Sensitive/control components
are rejected in root paths too, before any artifact file is read. The strict JSON reader rejects
duplicate keys and all numeric tokens; this manifest has no numeric-valued fields.
Numbers are not silently coerced through floating point. Canonical manifest and
result hashes retain the exact source intent. Artifact records are a named set in
the report, while the manifest hash retains caller array order and root order.

The supplied commit label is not independently authenticated or a build attestation.
A file hash binds bytes; it does not establish a publisher, source commit, deployed
runtime or software version.

## Supported ELF interpretation

The parser supports 32-bit and 64-bit ELF ET_EXEC/ET_DYN files in either byte order.
Header versions, class-specific structure sizes, bounded program-header tables and
file-backed segment extents are checked. PT_LOAD file/memory sizes, address range
and declared alignment must agree. An explicit single PT_DYNAMIC segment is parsed
from its file-backed mapping; missing or ambiguous virtual-address mappings reject.
Sections and section-header names are not used to guess dynamic metadata.

DT_STRTAB/DT_STRSZ locate a bounded, terminated original string table through one
unambiguous file-backed load segment. DT_NEEDED, DT_SONAME, DT_RPATH and DT_RUNPATH
strings retain original values and dynamic-entry ordinals. Needed/SONAME values
must be supported bounded ASCII bare object names; paths, token expansion and
unsupported encodings reject instead of acquiring guessed loader semantics.
A DT_NULL terminator is required; bytes beyond it are not interpreted as additional
entries. Duplicate needed names or singleton interpretation tags reject. Extended
program-header counts and broader object types remain explicitly unsupported.

PT_INTERP is retained as a declared pathname, with `interpreter_resolution` always
`NOT_PERFORMED`. RPATH/RUNPATH and `$ORIGIN` text are retained but never expanded or
used as search authority. Filter/auxiliary and recognized audit/configuration
object-loading tags are retained under `unsupported_dependency_semantics`; a
reachable occurrence makes the report status unsupported. Their paths are not opened.
Other relocation/symbol/version and processor-specific semantics are outside this
profile; a full ELF validator or loader implementation is not claimed.

The implementation was independently checked against the public
[gABI ELF header](https://gabi.xinuos.com/elf/02-eheader.html),
[program header](https://gabi.xinuos.com/elf/07-pheader.html) and
[dynamic linking](https://gabi.xinuos.com/elf/08-dynamic.html) references (the current
maintained reference identifies itself as a 4.3 draft), plus
[Linux loader documentation](https://man7.org/linux/man-pages/man8/ld.so.8.html).
Recognized extension constants were corroborated against the installed
`/usr/include/elf.h`. The Linux Foundation mirror returned access-denied pages;
those pages were not used as specification evidence and no access control was
bypassed. This package claims only its tested metadata subset, not complete ABI
conformance.

## Explicit graph semantics

Every binding must name an actual DT_NEEDED value reported by that requester, and
an explicitly supplied ET_DYN target with the exact DT_SONAME. Filename similarity does
not establish equivalence, and a provider without SONAME cannot silently acquire
one. Class, byte order and machine must match across a binding. Those comparisons
are header architecture checks only; symbol versions, OS ABI, processor flags and
loader namespace compatibility are not established.

No edge is automatically bound, even when one supplied file has the requested
SONAME. Missing bindings, absent providers and multiple supplied candidates remain
explicit unresolved states. A caller's explicit choice retains all supplied
candidates and the selected target hash; it does not attest actual loader choice.
Unreachable supplied artifacts remain separately listed. Cycles in explicitly bound
graphs are supported with bounded traversal and reported DFS back edges.

The result schema is `gig.security.elf_dependency_inventory.v1`.
`root_dt_needed_bindings_complete:true` means every DT_NEEDED edge reachable through
the supplied root bindings has an explicit corroborated target. It does **not** mean
all runtime dependencies are discovered or executable. Check the separate
`root_metadata_dependency_scope_supported` and status fields; recognized unsupported
loading semantics prevent a supported report status. Even a verified declared graph
always retains `runtime_loader_resolution_verified:false`,
`target_environment_qualified:false` and advisory `NOT_RUN`.

## Resource and failure bounds

Manifest input is at most 128 KiB. File reading reuses the existing no-symlink,
regular-file and observed-change checks: at most 64 MiB per file, 512 MiB total and
20,000 read files. The graph admits at most 128 artifacts and 2,048 edges. Each ELF
has at most 128 program headers, 4,096 dynamic entries, 128 needed names, a 1-MiB
dynamic string table and 4,096 bytes per interpreted string. Bare object names are
at most 255 ASCII characters. Canonical output is at most 8 MiB.

Malformed or inconsistent input fails before a successful report is published.
Output creation is exclusive, mode 0600 and refuses overwrite/symlinks. No global
filesystem snapshot, hostile concurrent namespace-replacement guarantee or
crash-durable output publication is claimed.

## Reproduction and evidence

```sh
work/venv/bin/python tests/test_elf_dependency_inventory.py
work/venv/bin/python scripts/inventory_elf_dependencies.py --manifest <new-explicit-manifest.json> --output <new-private-receipt.json>
```

Use new output paths. Existing distribution and native files are only read; none are
loaded or executed. A local manifest can name the built GIG SDK extension and native
completion-capsule test, plus individually selected real system library files under an
explicit system root. Name real versioned files directly rather than following
library symlinks; bind each target from exact original SONAME evidence. This is a
reviewable supplied graph, not an inferred runtime search result.

Focused fixtures cover both ELF classes/orders, exact header/segment/string
contracts, duplicate/missing/corrupt dynamic metadata, original byte changes,
architecture and SONAME mismatches, cycles, ambiguous providers, missing bindings,
unsupported loading tags, strict JSON, path/symlink/source bounds and exclusive
receipts. Actual local graph counts and hashes belong to the enclosing evidence
receipt after the native build snapshot is fixed.

To close the stronger SECURITY03 row still requires exact deployed/edge artifacts,
loader/runtime and complete installed reachability, kernel/OS file integrity,
legitimate source/version/backport-aware advisory analysis and target-specific
remediation/retest. No vulnerability absence, target clearance or original-row
completion is inferred from passive graph consistency.

## Interrupted-package recovery review

The recovered implementation and earlier34-test/8-artifact receipt were preserved.
Independent review found that sensitive path components were refused in artifact
paths but not in the supplied root itself. The new root-component guard and
pre-read regression close that inconsistency without broadening filesystem access.
The recovered final suite now contains35 tests. New independent logs and actual
explicit-graph verification are in `work/nov21-elf-recovery/`. This remains passive
local graph evidence; advisory analysis and runtime/target clearance are unverified.
