#!/usr/bin/env python3
"""Read-only pinned dependency inventory/PyPI advisory and downloaded-wheel hash review."""
import argparse,datetime,hashlib,importlib.metadata as md,json,re,subprocess,urllib.parse,urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
from packaging.utils import canonicalize_name,parse_wheel_filename
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--wheels',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():raise SystemExit('refusing overwrite of review evidence')
pins={}
for line in (ROOT/'requirements-python.lock').read_text().splitlines():
 if not line or line.startswith('#'):continue
 if not re.fullmatch(r'[A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+',line):raise SystemExit('invalid exact lock entry')
 name,version=line.split('==');pins[canonicalize_name(name)]=(name,version)
files={}
for wheel in a.wheels.glob('*.whl'):
 name,version,_,_=parse_wheel_filename(wheel.name);files.setdefault(canonicalize_name(name),[]).append((str(version),wheel))
records=[];integrity_errors=[];unavailable=[];active=[]
for key,(name,version) in sorted(pins.items()):
 d=md.distribution(name)
 if d.version!=version:raise SystemExit(f'installed version differs from lock: {name}')
 record={'name':name,'version':version,'requires_python':d.metadata.get('Requires-Python'),'license_expression':d.metadata.get('License-Expression'),'license_metadata':d.metadata.get('License'),'license_classifiers':[x for x in d.metadata.get_all('Classifier',[]) if x.startswith('License')],'license_files':[str(f) for f in d.files or [] if any(s in str(f).upper() for s in ['LICENSE','COPYING'])]}
 url='https://pypi.org/pypi/'+urllib.parse.quote(name,safe='-_.')+'/'+urllib.parse.quote(version,safe='.-')+'/json';record['metadata_endpoint']=url
 try:
  with urllib.request.urlopen(url,timeout=20) as response:metadata=json.load(response)
  if canonicalize_name(metadata['info']['name'])!=key or metadata['info']['version']!=version:raise RuntimeError('registry identity/version mismatch')
  advisories=[v for v in metadata.get('vulnerabilities',[]) if not v.get('withdrawn')]
  record['advisory_query']='verified_response';record['active_advisories']=[{'id':v.get('id'),'aliases':v.get('aliases',[]),'fixed_in':v.get('fixed_in',[]),'link':v.get('link')} for v in advisories]
  if advisories:active.append(key)
  expected={f['filename']:f['digests']['sha256'] for f in metadata['urls']};verified=[]
  for found_version,path in files.get(key,[]):
   checksum=hashlib.sha256(path.read_bytes()).hexdigest();matched=found_version==version and expected.get(path.name)==checksum
   verified.append({'filename':path.name,'bytes':path.stat().st_size,'sha256':checksum,'matches_registry_digest':matched})
   if not matched:integrity_errors.append(path.name)
  if not verified:integrity_errors.append(key+':missing-wheel')
  record['downloaded_wheels']=verified
 except Exception as error:
  record['advisory_query']='unavailable';record['error_type']=type(error).__name__;unavailable.append(key)
 records.append(record)
result={'reviewed_at':datetime.datetime.now(ZoneInfo('America/New_York')).isoformat(),'code_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),'lock_sha256':hashlib.sha256((ROOT/'requirements-python.lock').read_bytes()).hexdigest(),'review_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'packages':records,'active_advisory_packages':active,'integrity_errors':integrity_errors,'unavailable_metadata':unavailable,'scope':'PyPI version-specific advisory metadata snapshot and TLS-delivered registry SHA256 matching, installed license metadata; not a guarantee of all vulnerabilities, signatures or source authenticity; no audit of platform compiler/CPython/kernel advisories'}
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps({'packages':len(records),'active_advisory_packages':active,'integrity_errors':integrity_errors,'unavailable_metadata':unavailable}))
if integrity_errors or active:raise SystemExit(1)
