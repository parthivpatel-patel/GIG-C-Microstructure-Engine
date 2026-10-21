#!/usr/bin/env python3
"""One benchmark child per worker; wait-accounted RSS may include inherited pre-exec floor."""
import hashlib,json,resource,subprocess,sys
from pathlib import Path
if not sys.platform.startswith('linux'):raise SystemExit('peak RSS units currently validated only on Linux')
if len(sys.argv)<2:raise SystemExit('usage: executable [arguments]')
r=subprocess.run(sys.argv[1:],text=True,capture_output=True,check=True)
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
print(json.dumps({'raw':json.loads(r.stdout),'peak_process_rss_bytes':usage.ru_maxrss*1024,
'process_user_seconds':usage.ru_utime,'process_system_seconds':usage.ru_stime,
'executable_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()}))
