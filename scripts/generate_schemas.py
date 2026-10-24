#!/usr/bin/env python3
"""Generate/review versioned schema assets from native field descriptors; --check rejects drift."""
import argparse,json
from pathlib import Path
import gig_microstructure as gig
p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'schemas');p.add_argument('--check',action='store_true');a=p.parse_args()
if not a.check:a.output_dir.mkdir(parents=True,exist_ok=True)
for name,value in gig.schema_catalog().items():
    encoded=json.dumps(value,sort_keys=True,indent=2)+'\n';path=a.output_dir/(name+'-v1.schema.json')
    if a.check:
        if not path.exists() or path.read_text()!=encoded:raise SystemExit('schema drift: '+str(path))
    else:path.write_text(encoded)
print('PASS: schema assets match native 1.0 descriptors' if a.check else 'Generated schema assets for review')
