#!/usr/bin/env python3
"""Require actual LSan detection of the intended leak, rejecting crashes/unrelated failures."""
from pathlib import Path
import subprocess,sys
r=subprocess.run([sys.executable,str(Path(__file__).with_name('run_python_sanitized.py')),'--inject-leak'],capture_output=True,text=True)
if r.returncode!=1 or '12345 byte(s)' not in r.stderr or 'ERROR: LeakSanitizer' not in r.stderr or 'LIVE_LSAN_CHECK=1' not in r.stdout:
    raise SystemExit(f'Leak checker control failed: exit={r.returncode}\n{r.stdout}\n{r.stderr}')
print('PASS: live LSan checkpoint detected the deliberate 12345-byte leak; exit and intended diagnostic verified')
