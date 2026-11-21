#!/usr/bin/env python3
"""Bounded installed-artifact inventory; no imports, execution, network or clearance."""
import argparse,base64,binascii,csv,hashlib,io,itertools,json,os,re,stat,struct,sys
from email.parser import BytesParser
from pathlib import Path,PurePosixPath

MAX_FILE=64*1024*1024;MAX_TOTAL=512*1024*1024;MAX_METADATA=2*1024*1024
MAX_FILES=20000;MAX_DISTRIBUTIONS=256;MAX_NATIVE=32;MAX_OUTPUT=16*1024*1024
MAX_OS_DATABASE=8*1024*1024;MAX_OS_PACKAGES=20000;MAX_OS_STANZA=256*1024;MAX_OS_FIELD=128*1024
class InventoryError(ValueError):pass
def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n').encode()
def normalize(name):return re.sub('[-_.]+','-',name).lower()
def text(value,pattern):
 if type(value)is not str or len(value)>128 or not re.fullmatch(pattern,value):raise InventoryError('inventory_metadata_identity')
 return value
def relative(value,*,record=False):
 if type(value)is not str or not 1<=len(value)<=1024 or '\\'in value or value.startswith('/')or any(ord(c)<33 or ord(c)>126 for c in value):raise InventoryError('inventory_relative_path')
 parts=value.split('/')
 if any(p in('','.')or not re.fullmatch(r'[A-Za-z0-9_.+@()=-]+',p)for p in parts):raise InventoryError('inventory_relative_path')
 if any(p.casefold()in('.aws','.ssh','.git','.codex','.agents','.env')or p.casefold().endswith('.env')for p in parts):raise InventoryError('inventory_sensitive_path')
 if '..'in parts:
  if not record:raise InventoryError('inventory_relative_path')
  index=next((i for i,p in enumerate(parts)if p!='..'),len(parts))
  if index==len(parts)or '..'in parts[index:]:raise InventoryError('inventory_record_path')
 return PurePosixPath(value)
def no_links(path):
 if any(p.is_symlink()for p in(path,*path.parents)):raise InventoryError('inventory_symlink')
def inside(path,root):
 # abspath normalizes leading RECORD ../ segments; it never resolves a symlink.
 path=Path(os.path.abspath(path))
 if not path.is_relative_to(root):raise InventoryError('inventory_path_scope')
 no_links(path);return path

class Reader:
 def __init__(self):self.total=0;self.files={}
 def read(self,path,limit=MAX_FILE):
  no_links(path)
  if path in self.files:
   data=self.files[path]
   if len(data)>limit:raise InventoryError('inventory_file_budget')
   return data
  if len(self.files)>=MAX_FILES:raise InventoryError('inventory_file_count')
  fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
  try:
   before=os.fstat(fd)
   if not stat.S_ISREG(before.st_mode)or not 0<=before.st_size<=min(limit,MAX_FILE):raise InventoryError('inventory_file_type_or_budget')
   if self.total+before.st_size>MAX_TOTAL:raise InventoryError('inventory_total_budget')
   with os.fdopen(fd,'rb',closefd=False)as stream:data=stream.read(min(limit,MAX_FILE)+1)
   after=os.fstat(fd)
   if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)or len(data)!=before.st_size:raise InventoryError('inventory_changed_during_read')
  finally:os.close(fd)
  self.total+=len(data);self.files[path]=data;return data

def metadata(raw):
 try:message=BytesParser().parsebytes(raw)
 except (ValueError,UnicodeError):raise InventoryError('inventory_metadata')from None
 if message.defects or len(message.get_all('Name',[]))!=1 or len(message.get_all('Version',[]))!=1:raise InventoryError('inventory_metadata_identity')
 name=text(message['Name'],r'[A-Za-z0-9][A-Za-z0-9_.-]*');version=text(message['Version'],r'[A-Za-z0-9][A-Za-z0-9_.+!-]*')
 return name,normalize(name),version

def elf(data):
 if len(data)<52 or data[:4]!=b'\x7fELF'or data[4]not in(1,2)or data[5]not in(1,2)or data[6]!=1:raise InventoryError('inventory_elf_header')
 order='<'if data[5]==1 else'>';kind,machine,version=struct.unpack_from(order+'HHI',data,16)
 expected=52 if data[4]==1 else 64
 if len(data)<expected or version!=1 or struct.unpack_from(order+'H',data,40 if data[4]==1 else 52)[0]!=expected:raise InventoryError('inventory_elf_header')
 return {'format':'ELF','bits':32 if data[4]==1 else 64,'byte_order':'little'if data[5]==1 else'big','object_type':kind,'machine':machine,'elf_format_version':version}

def os_release(reader,path):
 raw=reader.read(path,64*1024);values={};allowed={'ID','ID_LIKE','NAME','VERSION','VERSION_ID','PRETTY_NAME','BUILD_ID','VARIANT','VARIANT_ID'}
 try:lines=raw.decode('utf-8').splitlines()
 except UnicodeError:raise InventoryError('inventory_os_release')from None
 for line in lines:
  if not line or line.startswith('#'):continue
  match=re.fullmatch(r'([A-Z][A-Z0-9_]*)=(.*)',line)
  if not match:raise InventoryError('inventory_os_release')
  key,value=match.groups()
  if key in values:raise InventoryError('inventory_os_duplicate')
  # Parse the passive os-release assignment subset without shell interpretation.
  quoted=value[:1]in('"',"'")
  if quoted:
   quote=value[0]
   if len(value)<2 or value[-1]!=quote:raise InventoryError('inventory_os_release')
   value=value[1:-1]
  if len(value)>512 or any(ord(c)<32 for c in value)or '\\'in value or '$'in value or '`'in value or '"'in value or "'"in value:raise InventoryError('inventory_os_release')
  if not quoted and not re.fullmatch(r'[A-Za-z0-9_.-]*',value):raise InventoryError('inventory_os_release')
  values[key]=value
 if not values.get('ID')or not re.fullmatch(r'[a-z0-9._-]+',values['ID'])or any(not re.fullmatch(r'[a-z0-9._-]+',part)for part in values.get('ID_LIKE','').split()):raise InventoryError('inventory_os_identity')
 return {'source':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'fields':{k:values[k]for k in sorted(values)if k in allowed},'vendor_advisory_match':'NOT_RUN','package_database_inventory':'NOT_INCLUDED'}

def approved_system_or_fixture(path,root,approved):
 path=Path(os.path.abspath(path))
 if path not in approved:path=inside(path,root)
 if path.is_relative_to(root):relative(path.relative_to(root).as_posix())
 return path

def select_os_release(preferred=Path('/etc/os-release'),vendor=Path('/usr/lib/os-release')):
 """Only the explicit standard etc-to-vendor alias is admitted; no arbitrary links."""
 if preferred.is_symlink():
  target=Path(os.path.abspath(preferred.parent/os.readlink(preferred)))
  if target!=vendor.absolute()or vendor.is_symlink()or not vendor.is_file():raise InventoryError('inventory_os_source_selector')
  no_links(vendor);return vendor
 if preferred.exists():
  no_links(preferred)
  if not preferred.is_file():raise InventoryError('inventory_os_source_selector')
  return preferred
 if vendor.exists():
  no_links(vendor)
  if not vendor.is_file():raise InventoryError('inventory_os_source_selector')
  return vendor
 return None

def dpkg_status(reader,path):
 """Read a bounded passive status database, retaining exact identity/status fields."""
 raw=reader.read(path,MAX_OS_DATABASE)
 try:lines=raw.decode('utf-8').splitlines()
 except UnicodeError:raise InventoryError('inventory_dpkg_utf8')from None
 packages=[];identities=set();fields={};current=None;stanza_bytes=0
 def finish():
  nonlocal fields,current,stanza_bytes
  if not fields:return
  if len(packages)>=MAX_OS_PACKAGES:raise InventoryError('inventory_os_package_budget')
  if not {'package','version','architecture','status'}<=set(fields):raise InventoryError('inventory_dpkg_required_fields')
  name,version,architecture,status=(fields[k]for k in('package','version','architecture','status'))
  if not re.fullmatch(r'[a-z0-9][a-z0-9+.-]{0,127}',name)or not re.fullmatch(r'[A-Za-z0-9.+:~_-]{1,256}',version)or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',architecture):raise InventoryError('inventory_dpkg_identity')
  tokens=status.split(' ')
  if len(tokens)!=3 or tokens[0]not in('unknown','install','hold','deinstall','purge')or tokens[1]not in('ok','reinstreq')or tokens[2]not in('not-installed','config-files','half-installed','unpacked','half-configured','triggers-awaited','triggers-pending','installed'):raise InventoryError('inventory_dpkg_status')
  identity=(name,architecture)
  if identity in identities:raise InventoryError('inventory_duplicate_os_package')
  identities.add(identity);packages.append({'package':name,'version':version,'architecture':architecture,'status':status,'selection':tokens[0],'error_flag':tokens[1],'installation_state':tokens[2],'source_stanza':len(packages)+1})
  fields={};current=None;stanza_bytes=0
 for line in lines:
  if not line:finish();continue
  if any(ord(c)<32 and c!='\t'for c in line):raise InventoryError('inventory_dpkg_control')
  stanza_bytes+=len(line.encode('utf-8'))+1
  if stanza_bytes>MAX_OS_STANZA:raise InventoryError('inventory_os_stanza_budget')
  if line[0]in(' ','\t'):
   if current is None:raise InventoryError('inventory_dpkg_continuation')
   fields[current]+='\n'+line
  else:
   match=re.fullmatch(r'([A-Za-z][A-Za-z0-9-]*):[ \t]*(.*)',line)
   if not match:raise InventoryError('inventory_dpkg_field')
   current,value=match.groups();current=current.casefold()
   if current in fields:raise InventoryError('inventory_dpkg_duplicate_field')
   if len(fields)>=128:raise InventoryError('inventory_dpkg_field_count')
   fields[current]=value.strip(' \t')
  if len(fields[current])>MAX_OS_FIELD:raise InventoryError('inventory_os_field_budget')
 finish()
 if not packages:raise InventoryError('inventory_dpkg_empty')
 return {'schema':'gig.security.dpkg_status_inventory.v1','source':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'records':len(packages),'installed_state_records':sum(p['installation_state']=='installed'for p in packages),'installed_ok_records':sum(p['installation_state']=='installed'and p['error_flag']=='ok'for p in packages),'packages':sorted(packages,key=lambda p:(p['package'],p['architecture'])),'scope':'Exact Package,Version,Architecture,Status from this supplied dpkg status database; source stanza retained; not every machine or package manager','package_file_integrity':'NOT_VERIFIED','vendor_advisory_match':'NOT_RUN'}

def build(root,venv,site_packages,native_artifacts,source_commit,*,os_release_path=None,dpkg_status_path=None):
 root=Path(root).absolute();no_links(root)
 if not root.is_dir()or type(source_commit)is not str or not re.fullmatch('[0-9a-f]{40}',source_commit):raise InventoryError('inventory_root_or_revision')
 env=inside(root/relative(venv),root);site=inside(root/relative(site_packages),env)
 if not env.is_dir()or not site.is_dir()or env==site:raise InventoryError('inventory_site_scope')
 if type(native_artifacts)is not list or len(native_artifacts)>MAX_NATIVE or any(type(p)is not str for p in native_artifacts):raise InventoryError('inventory_native_count')
 reader=Reader();distributions=[];names=set();all_paths={};unhashed=0
 # Only direct dist-info children are discovered; package code is never imported.
 entries=list(itertools.islice(site.iterdir(),4097))
 if len(entries)>4096:raise InventoryError('inventory_site_entry_budget')
 entries.sort(key=lambda p:p.name)
 infos=[p for p in entries if p.name.endswith('.dist-info')]
 if len(infos)>MAX_DISTRIBUTIONS:raise InventoryError('inventory_distribution_budget')
 for info in infos:
  info=inside(info,env)
  if not info.is_dir():raise InventoryError('inventory_dist_info_type')
  meta=reader.read(info/'METADATA',MAX_METADATA);declared_name,name,version=metadata(meta)
  if name in names:raise InventoryError('inventory_duplicate_distribution')
  names.add(name);record_raw=reader.read(info/'RECORD',MAX_METADATA);artifacts=[];seen=set()
  try:rows=list(csv.reader(io.StringIO(record_raw.decode('utf-8'),newline=''),strict=True))
  except (csv.Error,UnicodeError):raise InventoryError('inventory_record_csv')from None
  if not 1<=len(rows)<=MAX_FILES:raise InventoryError('inventory_record_count')
  for row in rows:
   if len(row)!=3:raise InventoryError('inventory_record_columns')
   location,declared_hash,declared_size=row;path=inside(site/relative(location,record=True),env);label=path.relative_to(root).as_posix()
   if label in seen:raise InventoryError('inventory_duplicate_record_path')
   seen.add(label);data=reader.read(path);digest=hashlib.sha256(data).hexdigest()
   if declared_size and(not re.fullmatch('[0-9]{1,12}',declared_size)or int(declared_size)!=len(data)):raise InventoryError('inventory_record_size')
   if declared_hash:
    try:
     algorithm,encoded=declared_hash.split('=',1)
     if algorithm not in('sha256','sha384','sha512')or not re.fullmatch('[A-Za-z0-9_-]+',encoded):raise ValueError()
     decoded=base64.b64decode(encoded+'='*(-len(encoded)%4),altchars=b'-_',validate=True)
    except (ValueError,binascii.Error):raise InventoryError('inventory_record_hash')from None
    if decoded!=hashlib.new(algorithm,data).digest():raise InventoryError('inventory_record_digest_mismatch')
   else:unhashed+=1
   artifact={'path':label,'bytes':len(data),'sha256':digest,'record_digest_verified':bool(declared_hash),'record_size_verified':bool(declared_size)}
   if data.startswith(b'\x7fELF'):artifact['native_header']=elf(data)
   artifacts.append(artifact)
   if label in all_paths and all_paths[label]!=digest:raise InventoryError('inventory_artifact_conflict')
   all_paths[label]=digest
  if not {str((info/'METADATA').relative_to(root)),str((info/'RECORD').relative_to(root))}<=seen:raise InventoryError('inventory_required_record_members')
  distributions.append({'name':name,'declared_name':declared_name,'version':version,'metadata_sha256':hashlib.sha256(meta).hexdigest(),'record_sha256':hashlib.sha256(record_raw).hexdigest(),'artifacts':sorted(artifacts,key=lambda r:r['path'])})
 natives=[];seen=set()
 for name in sorted(native_artifacts):
  path=inside(root/relative(name),root)
  if name in seen:raise InventoryError('inventory_duplicate_native')
  seen.add(name);data=reader.read(path);natives.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'header':elf(data),'software_version':None,'version_authority':'Not independently encoded by an ELF header;no version inferred from filename','dynamic_dependencies':'NOT_RESOLVED_OR_EXECUTED'})
 release_path=approved_system_or_fixture(os_release_path,root,(Path('/etc/os-release'),Path('/usr/lib/os-release')))if os_release_path is not None else None
 status_path=approved_system_or_fixture(dpkg_status_path,root,(Path('/var/lib/dpkg/status'),))if dpkg_status_path is not None else None
 system_packages=dpkg_status(reader,status_path)if status_path is not None else None
 release=os_release(reader,release_path)if release_path is not None else None
 if release is not None and system_packages is not None:release['package_database_inventory']='INCLUDED_DPKG_STATUS_ONLY'
 result={'schema':'gig.security.local_artifact_inventory.v1','profile':'PASSIVE_RECORDED_ARTIFACTS_DPKG_V1','source_commit_label':source_commit,'scope':'CURRENT_LOCAL_EXECUTOR_ONLY','target_environment_qualified':False,'python_runtime':{'version':sys.version,'implementation':sys.implementation.name,'cache_tag':sys.implementation.cache_tag,'executable_artifact_hashed':False},'python_scope':{'venv':venv,'site_packages':site_packages,'distributions':len(distributions),'unique_recorded_artifacts':len(all_paths),'records_without_declared_digest':unhashed,'unrecorded_site_files':'NOT_SCANNED','stdlib_interpreter_and_system_libraries':'NOT_INCLUDED'},'python_distributions':distributions,'explicit_native_artifacts':natives,'os_release':release,'os_packages':system_packages,'advisories':{'status':'NOT_RUN','retained_source_supplied':False,'vulnerability_absence_established':False},'coverage_gaps':['No deployed target or private edge evidence','No unrecorded-file,OS package-file integrity,ELF dependency closure or kernel inventory','RECORD verification is self-consistency,not registry or publisher authentication','No vulnerability database supplied or matched;no security clearance','No concurrent hostile namespace replacement guarantee'],'provider_requested':False}
 result['sha256']=hashlib.sha256(canonical(result)).hexdigest()
 if len(canonical(result))>MAX_OUTPUT:raise InventoryError('inventory_output_budget')
 return result

def write_new(path,data):
 path=Path(path).absolute();no_links(path)
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb')as stream:stream.write(data)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True);parser.add_argument('--venv',required=True);parser.add_argument('--site-packages',required=True);parser.add_argument('--native-artifact',action='append',default=[]);parser.add_argument('--source-commit',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 # Fixed passive OS sources only. The normal etc-to-vendor alias is validated.
 release=select_os_release();status_path=Path('/var/lib/dpkg/status');status_path=status_path if status_path.exists()or status_path.is_symlink()else None
 result=build(args.root,args.venv,args.site_packages,args.native_artifact,args.source_commit,os_release_path=release,dpkg_status_path=status_path);write_new(args.output,canonical(result));print(json.dumps({'distributions':result['python_scope']['distributions'],'artifacts':result['python_scope']['unique_recorded_artifacts'],'native_artifacts':len(result['explicit_native_artifacts']),'os_package_records':result['os_packages']['records']if result['os_packages']is not None else None,'os_installed_ok':result['os_packages']['installed_ok_records']if result['os_packages']is not None else None,'inventory_sha256':result['sha256'],'advisory_scan':'NOT_RUN','target_qualified':False},sort_keys=True))
if __name__=='__main__':main()
