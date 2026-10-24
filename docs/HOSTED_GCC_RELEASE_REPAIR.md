# GCC Release compilation repair

Reviewed October23,2026 (America/New_York).

**Local repair validated; actual hosted outcome remains unverified.** Starting
feature HEAD was `6d9f7f21ea8ce02a57acf43e263a0898981baf34`, with a clean working tree.
The final repair commit is **`3e8761a73fc7d4553700f7281461a0975c9e09c1`**. The delivery
also includes this evidence documentation; its containing branch HEAD is verified
after push and reported separately, rather than embedding a self-referential hash.
Main remains `165c5038336887116d69160b0d8e5a1a5ef59d16`.

## Hosted evidence and limitation

The owner reports C++ CI run number117: five matrix jobs passed and GCC Release
failed during compilation. That run number is not a GitHub API run ID. Its complete
log, exact runner/compiler versions, flags and other job conclusions could not be
independently retrieved.

One authorized request was attempted through the inherited proxy:

```sh
gh api 'repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs?branch=feat%2Fbootstrap-cpp20-engine&per_page=10'
```

Exit1, stderr:

```text
Get "https://api.github.com/repos/parthivpatel-patel/GIG-C-Microstructure-Engine/actions/runs?branch=feat%2Fbootstrap-cpp20-engine&per_page=10": Forbidden
```

No authenticated origin HTTP status or run ID was obtained. The current managed
runtime reports `api.github.com` absent from its effective allowlist; policy state
is unknown. No proxy/TLS bypass, configuration change or repeated blocked request
was attempted. Git read/push availability is separate from Actions API access.
The screenshot description mentions `__builtin_memmove`; the independently
reproduced diagnostic below is `__builtin_memset`. They must not be presented as
an exact hosted-log match without the missing log.

## Failing-before reproduction and exact diagnostic

Used the existing official Ubuntu24.04 qualification container, with an isolated
source export of the starting commit. No prior container source/build was replaced.
Observed local toolchain:

- GCC/g++13.3.0-6ubuntu2~24.04.1, libstdc++13 development headers.
- libstdc++6 runtime14.2.0-4ubuntu2~24.04.1; compiler and runtime versions are distinct.
- CMake3.28.3, CPython3.12.3; existing private zlib1.3.1.

The workflow selects Ubuntu24.04 and `CXX=g++`, and the repository Release preset
requires warnings as errors. This is a relevant Ubuntu toolchain reproduction,
not proof of the inaccessible hosted compiler's exact version. The CMake build
used Release, testing/benchmarks/streaming ON and Python ON, as for hosted GCC
Release. Before repair, compiling the original admin object through Ninja failed
with exit1. Exact object-build flags:

```text
-O3 -DNDEBUG -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror
```

Includes were the exported source root and its include directory. Diagnostic:

```text
inlined from 'constexpr void std::vector<_Tp, _Alloc>::resize(size_type) [with _Tp = std::byte; _Alloc = std::allocator<std::byte>]' at /usr/include/c++/13/bits/stl_vector.h:1016:21,
inlined from 'void {anonymous}::wire()' at tests/test_itch_admin.cpp:27:87:
/usr/include/c++/13/bits/stl_algobase.h:951:25: error: 'void* __builtin_memset(void*, int, long unsigned int)' offset 1 is out of the bounds [0, 1] [-Werror=array-bounds=]
cc1plus: all warnings being treated as errors
```

The full template trace, verbose CMake compiler command, configuration commands
and source hashes are retained in `build/hosted-gcc-repair/evidence/` and indexed
by the [structured evidence](HOSTED_GCC_RELEASE_REPAIR_EVIDENCE.json).
A separate direct strict GCC13 object compile also failed before and passed after.
Original GCC13 Debug object compilation and original GCC14.2 optimized object
compilation both succeeded. Two generic reduced vector examples did not reproduce
the diagnostic; the retained failing reproducer is the complete original test
translation unit, not a claimed minimal upstream compiler reproducer.

## Root cause and safety assessment

The affected fixture copied a valid vector and resized that copy for every invalid
message length. L/V/W/h/N original lengths are26/35/12/21/20 bytes. The loop covers
0 through original length+1, excluding the valid length: **119 malformed buffers**.

The reviewed operations are defined: vector copy owns separate storage, resize
uses bounded lengths at most36, there are no escaped iterators or borrowed spans
across reallocation, and the original message remains alive. The decoder rejects
empty or mismatched lengths before reading typed fields. No integer overflow,
invalid lifetime or unsafe container access was found in this path. Runtime
sanitizer comparison also found no violation.

**Confirmed classification:** toolchain/optimized-compilation compatibility failure
in the copy-then-resize test idiom. Source semantics and compiler/configuration
controls support an optimization-related bounds-diagnostic false positive. This is
not a claim that a particular upstream GCC bug or the inaccessible hosted warning
has been conclusively identified. No production decoder defect was reproduced.

## Minimal repair

Only `tests/test_itch_admin.cpp` changes in the implementation commit:

```cpp
Bytes bad(n,std::byte{});
std::copy_n(b.begin(),std::min(n,b.size()),bad.begin());
```

Added an explicit `<algorithm>` include. Constructing the requested final extent
makes both copy bounds explicit and avoids the problematic copy/resize optimizer
path. The available prefix is preserved; the one-byte extension remains zero.
All prior type, length, profile, enum and decoder assertions remain. No diagnostic
suppression, warning flag, CMake/workflow policy, production source, schema or
canonical representation changes were made.

A separate ASan+UBSan fixture-equivalence executable ran both old and new
construction methods. An independently authored Python byte oracle checked all119
outputs against declared field layouts/values, including empty input and the
zero-extended long case. Every byte matched; a deliberately corrupted expectation
was detected. This supplies semantic regression evidence beyond compilation.

## Executed regression results

| Local configuration | Final passed CTest outcomes | Failed /skipped /disabled |
|---|---:|---:|
| GCC14.2 Debug |154|0 /0 /0|
| GCC14.2 Release |154|0 /0 /0|
| GCC14.2 ASan+UBSan |154|0 /0 /0|
| Clang19.1.7 Debug |154|0 /0 /0|
| Clang19.1.7 Release |154|0 /0 /0|
| Ubuntu24.04 GCC13.3 Release, Python ON |157|0 /0 /0|
| **Total final outcomes** |**1,081**|**0 /0 /0**|

All eight prior canonical identities match in all seven configurations, including
independent wire/context/L3/streaming/demo/HY/admin/auction references. The existing
128-prefix journal differential control also remains passing. No assertions were
weakened or tests removed.

The first Ubuntu archive-only CTest attempt passed156/157 and failed the Python
provenance assertion because the test runner had neither Git metadata nor an
independently verified archive-commit declaration. That failure is preserved.
The runner was repaired using an authenticated local Git bundle of the starting
commit; the only dirty file was the test repair. No source identity or clean state
was fabricated. Rerunning the full configuration then passed157/157. The Python
assertion and production code were unchanged. The build itself had already passed.

Both existing Phase5 checkout-built and source-built installed-wheel environments
were rechecked:8 interface plus6 export cases each, **28 passing checks**. These
are revalidated existing wheels, not newly rebuilt artifacts. The sole test-source
change does not alter compiled Python/native production sources or the API/ABI.
The Ubuntu Release configuration additionally rebuilt the Python extension and
passed its three CTest groups. Other optional Python configurations were not
needlessly rebuilt for this test-only change.

A fresh source distribution contains the corrected test and passed inventory:
**303 intended, safe, byte-identical regular members** before closure documents.
All three existing packaging contamination regressions passed. Final report files
are later documentation additions; no claim is made that the earlier archive
contains them. No wheel or source archive was published.

## Hosted verification and exact owner action

The workflow is unchanged and triggers on the validated feature-branch push.
Actual new run ID, tested hosted SHA, GCC Release outcome, other five outcomes,
and hosted compiler/dependency versions remain **unavailable**, not passed by
inference. The owner's earlier five successful jobs remain user-reported evidence.
Local container execution shares this managed host and is not a GitHub runner or
independent-machine qualification.

Smallest next action: inspect the new **C++ CI** run for the delivered branch SHA
and provide the full GCC Release build log plus run/job IDs, head SHA and all six
conclusions. Include compiler identification, verbose compile flags, dependency
versions, CTest/JUnit and canonical summaries. The earlier run117 full failure log
would establish whether its intrinsic/diagnostic exactly matches this reproduction.
Alternatively, publish/attach the supported environment configuration allowing
`api.github.com`; authorized private Actions-read access may also be required after
network access succeeds. Supply credentials only through supported configuration,
never in chat or committed files.

The local repair is complete. Hosted success remains an explicit external gate.
No market-data download, main change, merge, tag, release, paid provisioning,
network-policy change or live integration occurred.
