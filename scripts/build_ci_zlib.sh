#!/usr/bin/env bash
# Private Linux CI dependency prefix. Never replaces the system zlib or lowers
# the engine's qualified minimum. Optional archive permits verified offline use.
set -euo pipefail
if [[ $# -lt 1 || $# -gt 2 || "$1" != /* ]]; then
  printf 'usage: build_ci_zlib.sh ABSOLUTE_NEW_PREFIX [OFFICIAL_ARCHIVE]\n' >&2
  exit 2
fi
prefix=$1
work="${prefix}.work"
if [[ -e "$prefix" || -e "$work" ]]; then
  printf 'refusing to overwrite existing dependency prefix or work directory\n' >&2
  exit 2
fi
mkdir -p -- "$work/source"
archive="$work/source.tar.gz"
if [[ $# -eq 2 ]]; then
  if [[ ! -f "$2" || $(stat -Lc '%s' -- "$2") -gt 2097152 ]]; then
    printf 'offline archive must be a regular file no larger than 2 MiB\n' >&2
    exit 2
  fi
  cp -- "$2" "$archive"
else
  curl --proto '=https' --tlsv1.2 --fail --location --silent --show-error \
    --connect-timeout 10 --max-time 60 --max-filesize 2097152 \
    --output "$archive" \
    https://codeload.github.com/madler/zlib/tar.gz/refs/tags/v1.3.1
fi
expected=17e88863f3600672ab49182f217281b6fc4d3c762bde361935e436a95214d05c
actual=$(sha256sum -- "$archive")
actual=${actual%% *}
if [[ "$actual" != "$expected" ]]; then
  printf 'official zlib archive checksum mismatch; installation not attempted\n' >&2
  exit 1
fi
tar -xzf "$archive" --directory "$work/source" --strip-components=1
cmake -S "$work/source" -B "$work/build" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$prefix" \
  -DZLIB_BUILD_EXAMPLES=OFF
cmake --build "$work/build" --parallel 2
cmake --install "$work/build"
cat > "$work/version.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include <zlib.h>
int main(void) {
    printf("zlib header=%s runtime=%s\n", ZLIB_VERSION, zlibVersion());
    return strcmp(ZLIB_VERSION, "1.3.1") || strcmp(zlibVersion(), "1.3.1");
}
EOF
"${CC:-cc}" "$work/version.c" -I"$prefix/include" -L"$prefix/lib" \
  -Wl,-rpath,"$prefix/lib" -lz -o "$work/version"
"$work/version"
printf 'verified private zlib prefix: %s\n' "$prefix"
