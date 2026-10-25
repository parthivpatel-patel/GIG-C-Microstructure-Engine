# Third-party notices

Public repository visibility does not itself grant a new redistribution license or release.
These notices concern dependencies, not a license grant for project code.

pybind11 2.13.6 (pinned native binding headers), BSD-style license below. Runtime
jsonschema 4.23.0 uses the MIT license; its Python distribution carries its COPYING
notice and transitive dependencies retain their own distributions/notices.
scikit-build-core 0.11.6 (MIT) is a pinned build dependency, not a runtime service.
CMake/Ninja/compiler/standard-library licenses remain those of their toolchains.
No third-party source or restricted market dataset is vendored into the repository.
The package includes compiled pybind11 header code, so its complete notice follows.

## pybind11 distribution LICENSE

```text
Copyright (c) 2016 Wenzel Jakob <wenzel.jakob@epfl.ch>, All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Please also refer to the file .github/CONTRIBUTING.md, which clarifies licensing of
external contributions to this project including patches, pull requests, etc.

```

## Optional native synthetic streaming dependency: zlib

The separate `GIG_BUILD_ITCH_STREAMING` feature uses the system zlib library;
the validated installation is1.3.1. No zlib source is vendored or altered here.
The optional native target links the system library; ordinary Python wheels leave
this feature OFF and do not add a zlib linkage to the Python extension. Distribution
of an enabled native application must account for its actual library/toolchain
packaging. This notice is not an unrestricted license for project or market data.

Upstream zlib1.3.1 notice, as supplied in the inspected `zlib.h`:

```text
Copyright (C) 1995-2024 Jean-loup Gailly and Mark Adler

This software is provided 'as-is', without any express or implied
warranty.  In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.

Jean-loup Gailly        Mark Adler
jloup@gzip.org          madler@alumni.caltech.edu
```

## Optional institutional research terminal

Pinned package locks and `docs/evidence/terminal_dependency_inventory.json` identify
this optional consumer's tested dependency versions, registry integrity and license
metadata. React/React DOM, Vite/plugin-react and Three.js use MIT licenses;
TypeScript and Playwright use Apache-2.0. The Python gateway uses Starlette,
uvicorn, httpx and websockets plus their pinned transitive closure; consult the
installed distributions' license files and the inventory for exact notices.
Dependency metadata is not a grant of project redistribution or provider data rights.
No vendor source/data is embedded, and no public release is made by this work.
