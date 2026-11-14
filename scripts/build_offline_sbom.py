#!/usr/bin/env python3
"""Deterministic source-lock CycloneDX inventory; no install, fetch or advisory claim."""
import argparse,base64,binascii,hashlib,json,os,re,stat,tomllib
from pathlib import Path
from urllib.parse import quote,urlsplit

INPUTS=('requirements-python.lock','terminal/server/requirements.txt','pyproject.toml',
        'terminal/web/package.json','terminal/web/package-lock.json',
        'terminal/tests/package.json','terminal/tests/package-lock.json')
MAX_FILE=2*1024*1024;MAX_TOTAL=8*1024*1024;MAX_COMPONENTS=10000;MAX_OUTPUT=8*1024*1024
PIN=re.compile(r'([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9_.+!-]*)\Z')
NPM_NAME=re.compile(r'(?:@[a-z0-9_.-]+/)?[a-z0-9][a-z0-9_.-]*\Z')
NPM_VERSION=re.compile(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\Z')
class InventoryError(ValueError):pass

def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
def normalize(value):return re.sub('[-_.]+','-',value).lower()
def unique(items):
 out={}
 for key,value in items:
  if key in out:raise InventoryError('sbom_duplicate_json_key')
  out[key]=value
 return out

def read_inputs(root):
 root=Path(root).absolute();out={};total=0
 if root.is_symlink()or not root.is_dir():raise InventoryError('sbom_root')
 for name in INPUTS:
  path=root/name
  if any(p.is_symlink()for p in(path,*path.parents)):raise InventoryError('sbom_input_symlink')
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
  try:
   info=os.fstat(fd)
   if not stat.S_ISREG(info.st_mode)or info.st_size>MAX_FILE:raise InventoryError('sbom_input_budget_or_type')
   with os.fdopen(fd,'rb',closefd=False)as stream:data=stream.read(MAX_FILE+1)
  finally:os.close(fd)
  total+=len(data)
  if len(data)>MAX_FILE or total>MAX_TOTAL:raise InventoryError('sbom_input_budget')
  out[name]=data
 return out

def pins(lines):
 out={}
 for line in lines:
  value=line.strip()
  if not value or value.startswith('#'):continue
  m=PIN.fullmatch(value)
  if not m:raise InventoryError('sbom_exact_python_pin_required')
  name,version=m.groups()
  if len(name)>128 or len(version)>128:raise InventoryError('sbom_python_pin_budget')
  key=normalize(name)
  if key in out:raise InventoryError('sbom_duplicate_python_pin')
  out[key]=version
 return out

def npm_rows(manifest,lock):
 if type(manifest)is not dict or type(lock)is not dict or lock.get('lockfileVersion')!=3 or type(lock.get('packages'))is not dict or ''not in lock['packages']:raise InventoryError('sbom_npm_lock_version_or_structure')
 root=lock['packages']['']
 if type(root)is not dict or any(root.get(k)!=manifest.get(k)for k in('name','version','dependencies','devDependencies','optionalDependencies')):raise InventoryError('sbom_npm_manifest_lock_mismatch')
 for field in('dependencies','devDependencies','optionalDependencies'):
  direct=manifest.get(field,{})
  if type(direct)is not dict:raise InventoryError('sbom_npm_direct_structure')
  for name,version in direct.items():
   if type(name)is not str or not NPM_NAME.fullmatch(name)or type(version)is not str or not NPM_VERSION.fullmatch(version):raise InventoryError('sbom_npm_direct_exact_pin')
   selected=lock['packages'].get('node_modules/'+name)
   if type(selected)is not dict or selected.get('version')!=version:raise InventoryError('sbom_npm_direct_binding')
 if len(lock['packages'])>MAX_COMPONENTS:raise InventoryError('sbom_component_budget')
 out=[]
 for path,row in sorted(lock['packages'].items()):
  if path=='':continue
  if type(path)is not str or len(path)>2048 or not path.startswith('node_modules/')or type(row)is not dict or row.get('link'):raise InventoryError('sbom_npm_package_path_or_link')
  segments=path.removeprefix('node_modules/').split('/node_modules/')
  if any(len(n)>214 or not NPM_NAME.fullmatch(n)or n in('.','..')for n in segments):raise InventoryError('sbom_npm_package_path')
  name=segments[-1];version=row.get('version')
  if type(version)is not str or len(version)>128 or not NPM_VERSION.fullmatch(version):raise InventoryError('sbom_npm_exact_version')
  if 'name'in row and row['name']!=name:raise InventoryError('sbom_npm_alias_unsupported')
  url=row.get('resolved')
  if type(url)is not str or len(url)>4096:raise InventoryError('sbom_npm_registry_required')
  u=urlsplit(url)
  if u.scheme!='https'or u.netloc!='registry.npmjs.org'or u.query or u.fragment or '%'in u.path or '..'in u.path or '\\'in url:raise InventoryError('sbom_npm_registry_scope')
  if u.path!='/'+name+'/-/'+name.split('/')[-1]+'-'+version+'.tgz':raise InventoryError('sbom_npm_artifact_binding')
  sri=row.get('integrity')
  if type(sri)is not str or not sri.startswith('sha512-'):raise InventoryError('sbom_npm_sha512_required')
  try:checksum=base64.b64decode(sri[7:],validate=True)
  except (ValueError,binascii.Error):raise InventoryError('sbom_npm_integrity')from None
  if len(checksum)!=64:raise InventoryError('sbom_npm_integrity')
  if any(k in row and type(row[k])is not bool for k in('dev','optional','devOptional','hasInstallScript')):raise InventoryError('sbom_npm_flags')
  out.append((name,version,path,checksum.hex(),row))
 return out

def build(root,source_commit):
 if type(source_commit)is not str or not re.fullmatch('[0-9a-f]{40}',source_commit):raise InventoryError('sbom_source_commit')
 inputs=read_inputs(root);components={}
 def add(ecosystem,name,version,surface,location,checksum=None,flags=None):
  purl='pkg:'+ecosystem+'/'+quote(name,safe='/')+'@'+quote(version,safe='.')
  row=components.setdefault(purl,{'type':'library','bom-ref':purl,'name':name,'version':version,'purl':purl,'properties':[]})
  record={'surface':surface,'location':location}
  if checksum is not None:record.update(artifact_sha512_from_lock=checksum,artifact_download_verified=False,**{k:flags.get(k,False)for k in('dev','optional','devOptional','hasInstallScript')})
  else:record.update(artifact_digest_available=False)
  row['properties'].append({'name':'gig:source-occurrence','value':canonical(record).decode().strip()})
  if len(components)>MAX_COMPONENTS:raise InventoryError('sbom_component_budget')
 for name in INPUTS[:2]:
  for package,version in pins(inputs[name].decode().splitlines()).items():add('pypi',package,version,name,'exact-pin')
 project=tomllib.loads(inputs['pyproject.toml'].decode())
 if type(project.get('project'))is not dict or type(project.get('build-system'))is not dict:raise InventoryError('sbom_pyproject_structure')
 app_name=project['project'].get('name');app_version=project['project'].get('version')
 if type(app_name)is not str or len(app_name)>128 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',app_name)or type(app_version)is not str or len(app_version)>128 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.+!-]*',app_version):raise InventoryError('sbom_pyproject_identity')
 if 'requires'not in project['build-system']:raise InventoryError('sbom_pyproject_requirements')
 for section,rows in [('project.dependencies',project['project'].get('dependencies',[])),('build-system.requires',project['build-system']['requires'])]:
  if type(rows)is not list or any(type(r)is not str for r in rows):raise InventoryError('sbom_pyproject_requirements')
  for name,version in pins(rows).items():add('pypi',name,version,'pyproject.toml',section)
 for prefix in('terminal/web','terminal/tests'):
  manifest=json.loads(inputs[prefix+'/package.json'],object_pairs_hook=unique);lock=json.loads(inputs[prefix+'/package-lock.json'],object_pairs_hook=unique)
  for name,version,path,checksum,flags in npm_rows(manifest,lock):add('npm',name,version,prefix+'/package-lock.json',path,checksum,flags)
 records=[{'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}for name,data in sorted(inputs.items())]
 for row in components.values():row['properties'].sort(key=lambda p:p['value'])
 result={'bomFormat':'CycloneDX','specVersion':'1.6','version':1,'metadata':{
  'component':{'type':'application','name':project['project']['name'],'version':project['project']['version'],'bom-ref':'gig-source'},
  'properties':[{'name':'gig:source-commit-label','value':source_commit},
   {'name':'gig:source-inputs','value':canonical(records).decode().strip()},
   {'name':'gig:source-inputs-sha256','value':hashlib.sha256(canonical(records)).hexdigest()},
   {'name':'gig:scope','value':'Source-lock inventory only; includes all locked optional/dev platform packages,not installed/runtime reachability. No dependency graph,artifact-download verification,advisory scan,license clearance or target OS/native inventory. Commit is a supplied label; input hashes identify actual bytes.'}]},
  'components':[components[k]for k in sorted(components)]}
 if len(canonical(result))>MAX_OUTPUT:raise InventoryError('sbom_output_budget')
 return result

def write_new(path,data):
 path=Path(path).absolute()
 if any(p.is_symlink()for p in(path,*path.parents)):raise InventoryError('sbom_output_symlink')
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb')as stream:stream.write(data)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--source-commit',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 result=build(args.root,args.source_commit);write_new(args.output,canonical(result));print(json.dumps({'components':len(result['components']),'source_inputs':len(INPUTS),'advisory_clearance':False},sort_keys=True))
if __name__=='__main__':main()
