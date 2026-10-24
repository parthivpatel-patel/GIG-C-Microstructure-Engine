#!/usr/bin/env python3
"""Live-interpreter LSan checkpoint; stock CPython shutdown is separately diagnosed, not suppressed."""
import argparse
import ctypes
import gc
import runpy
import sys
p=argparse.ArgumentParser();p.add_argument('--inject-leak',action='store_true');p.add_argument('script',nargs='?');p.add_argument('arguments',nargs=argparse.REMAINDER);a=p.parse_args()
status=0
if a.script:
    sys.path.insert(0,str(__import__('pathlib').Path(a.script).resolve().parent))
    sys.argv=[a.script]+a.arguments
    try:
        runpy.run_path(a.script,run_name='__main__')
    except SystemExit as error:
        status=0 if error.code is None else (error.code if type(error.code) is int else 1)
library=ctypes.PyDLL(None)
if a.inject_leak:
    allocate=library.malloc;allocate.argtypes=[ctypes.c_size_t];allocate.restype=None
    allocate(12345)  # Deliberate unreachable allocation, only in the negative harness control.
# Materialize the active optimized CPython evaluation frame as a legitimate LSan root.
# Without it, this interpreter can report its live frame scratch area as unreachable.
_lsan_frame_root=sys._getframe()
gc.collect()
check=library.__lsan_do_recoverable_leak_check;check.argtypes=[];check.restype=ctypes.c_int
leaks=check()
print(f'LIVE_LSAN_CHECK={leaks}',flush=True)
raise SystemExit(status or (1 if leaks else 0))
