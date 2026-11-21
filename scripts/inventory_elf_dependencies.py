#!/usr/bin/env python3
"""Passive original-byte ELF dependency bindings; no execution or loader search."""
import argparse,hashlib,json,os,re,struct
from pathlib import Path
try:
 from .inventory_local_artifacts import Reader,InventoryError,canonical,inside,no_links,relative,write_new
except ImportError:
 from inventory_local_artifacts import Reader,InventoryError,canonical,inside,no_links,relative,write_new

PROFILE='EXPLICIT_ELF_NEEDED_BINDINGS_V1'
MAX_MANIFEST=128*1024;MAX_ROOTS=8;MAX_ARTIFACTS=128;MAX_EDGES=2048;MAX_OUTPUT=8*1024*1024
MAX_PHDRS=128;MAX_DYNAMIC=4096;MAX_STRINGS=1024*1024;MAX_NEEDED=128;MAX_STRING=4096
ID=re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}')
HASH=re.compile(r'[0-9a-f]{64}')
OBJECT_NAME=re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.+@-]{0,254}')
UNSUPPORTED_OBJECT_TAGS={0x7ffffffd:'DT_AUXILIARY',0x7fffffff:'DT_FILTER',0x6ffffefa:'DT_CONFIG',0x6ffffefb:'DT_DEPAUDIT',0x6ffffefc:'DT_AUDIT'}

def fail(code):raise InventoryError(code)
def exact(value,keys,code):
 if type(value)is not dict or set(value)!=set(keys):fail(code)
def identifier(v):return type(v)is str and ID.fullmatch(v)is not None
def reject_number(_):fail('elf_manifest_numbers_unsupported')
def unique(pairs):
 out={}
 for k,v in pairs:
  if k in out:fail('elf_manifest_duplicate_key')
  out[k]=v
 return out

def load_manifest(raw):
 if type(raw)is not bytes or not 1<=len(raw)<=MAX_MANIFEST:fail('elf_manifest_budget')
 try:return json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_int=reject_number,parse_float=reject_number,parse_constant=reject_number)
 except (UnicodeError,json.JSONDecodeError,RecursionError):raise InventoryError('elf_manifest_json')from None

def extent(offset,size,total,code='elf_file_extent'):
 if offset<0 or size<0 or offset>total or size>total-offset:fail(code)

def parse_elf(raw):
 """Supported ET_EXEC/ET_DYN program/dynamic metadata; section headers unused."""
 if type(raw)is not bytes or len(raw)<16 or raw[:4]!=b'\x7fELF'or raw[4]not in(1,2)or raw[5]not in(1,2)or raw[6]!=1:fail('elf_identity')
 bits=32 if raw[4]==1 else 64;order='<'if raw[5]==1 else'>';size=52 if bits==32 else 64
 extent(0,size,len(raw),'elf_header_extent')
 fields=struct.unpack_from(order+('16sHHIIIIIHHHHHH'if bits==32 else'16sHHIQQQIHHHHHH'),raw)
 _,kind,machine,version,_entry,phoff,_shoff,flags,ehsize,phentsize,phnum,_shentsize,_shnum,_shstrndx=fields
 if kind not in(2,3):fail('elf_object_type_unsupported')
 if not machine or version!=1 or ehsize!=size:fail('elf_header_contract')
 if phnum==0xffff:fail('elf_extended_program_header_count_unsupported')
 expected=32 if bits==32 else 56
 if not 1<=phnum<=MAX_PHDRS or phentsize!=expected or phoff<size:fail('elf_program_header_contract')
 extent(phoff,phnum*phentsize,len(raw),'elf_program_header_extent')
 loads=[];dynamics=[];interpreters=[]
 for i in range(phnum):
  p=struct.unpack_from(order+('IIIIIIII'if bits==32 else'IIQQQQQQ'),raw,phoff+i*phentsize)
  if bits==32:typ,offset,vaddr,_paddr,filesz,memsz,pflags,align=p
  else:typ,pflags,offset,vaddr,_paddr,filesz,memsz,align=p
  if typ==0:continue # PT_NULL's remaining fields are undefined.
  if filesz:extent(offset,filesz,len(raw),'elf_segment_extent')
  record={'ordinal':i,'offset':offset,'virtual_address':vaddr,'file_bytes':filesz,'memory_bytes':memsz,'flags':pflags}
  if typ==1:
   if filesz>memsz or vaddr+memsz>2**bits or align not in(0,1)and(align&(align-1)or vaddr%align!=offset%align):fail('elf_load_contract')
   loads.append(record)
  elif typ==2:dynamics.append(record)
  elif typ==3:interpreters.append(record)
 if not loads:fail('elf_load_segment_required')
 if len(dynamics)>1 or len(interpreters)>1:fail('elf_multiple_dynamic_or_interpreter_segments')
 def mapped(address,length):
  candidates=[s for s in loads if s['virtual_address']<=address and length<=s['file_bytes']-(address-s['virtual_address'])]
  if len(candidates)!=1:fail('elf_virtual_mapping_missing_or_ambiguous')
  s=candidates[0];offset=s['offset']+address-s['virtual_address'];extent(offset,length,len(raw));return offset
 interpreter=None
 if interpreters:
  p=interpreters[0]
  if not 2<=p['file_bytes']<=MAX_STRING:fail('elf_interpreter_budget')
  data=raw[p['offset']:p['offset']+p['file_bytes']]
  if data[-1:]!=b'\0'or b'\0'in data[:-1]:fail('elf_interpreter_string')
  try:interpreter=data[:-1].decode('ascii')
  except UnicodeError:raise InventoryError('elf_interpreter_string')from None
  if not interpreter.startswith('/')or any(ord(c)<33 or ord(c)>126 for c in interpreter):fail('elf_interpreter_string')
 out={'bits':bits,'byte_order':'little'if order=='<'else'big','machine':machine,'object_type':kind,'os_abi':raw[7],'abi_version':raw[8],'processor_flags':flags,'program_headers':phnum,'interpreter':interpreter,'interpreter_resolution':'NOT_PERFORMED','dynamic_segment':None,'soname':None,'needed':[],'rpath':None,'runpath':None,'unsupported_dependency_semantics':[]}
 if not dynamics:
  out['dynamic_status']='NO_PT_DYNAMIC_SEGMENT';return out
 d=dynamics[0];entry_size=8 if bits==32 else 16
 if not d['file_bytes']or d['file_bytes']%entry_size or d['file_bytes']//entry_size>MAX_DYNAMIC:fail('elf_dynamic_budget_or_alignment')
 if mapped(d['virtual_address'],d['file_bytes'])!=d['offset']:fail('elf_dynamic_mapping_mismatch')
 values={};entries=[];terminated=False
 for i in range(d['file_bytes']//entry_size):
  tag,value=struct.unpack_from(order+('iI'if bits==32 else'qQ'),raw,d['offset']+i*entry_size)
  if tag==0:
   terminated=True;break
  entries.append((tag,value,i))
  if tag in(5,10,14,15,29):
   if tag in values:fail('elf_duplicate_dynamic_singleton')
   values[tag]=value
 if not terminated:fail('elf_dynamic_terminator_missing')
 needed=[e for e in entries if e[0]==1]
 if len(needed)>MAX_NEEDED:fail('elf_needed_budget')
 strings_required=any(tag in(1,14,15,29)or tag in UNSUPPORTED_OBJECT_TAGS for tag,_,_ in entries)
 if strings_required and(5 not in values or 10 not in values):fail('elf_string_table_required')
 if (5 in values)!=(10 in values):fail('elf_incomplete_string_table')
 table=None
 if 5 in values:
  length=values[10]
  if not 1<=length<=MAX_STRINGS:fail('elf_string_table_budget')
  table=mapped(values[5],length)
  if raw[table]!=0 or raw[table+length-1]!=0:fail('elf_string_table_boundary')
 def string(index,name=False):
  if table is None or index>=values[10]:fail('elf_string_offset')
  begin=table+index;end=raw.find(b'\0',begin,min(table+values[10],begin+MAX_STRING+1))
  if end<0:fail('elf_string_termination_or_budget')
  try:text=raw[begin:end].decode('ascii')
  except UnicodeError:raise InventoryError('elf_string_encoding_unsupported')from None
  if any(ord(c)<32 or ord(c)>126 for c in text):fail('elf_string_control')
  if name and(not OBJECT_NAME.fullmatch(text)or text in('.','..')):fail('elf_object_name_unsupported')
  return text
 seen=set()
 for _,index,ordinal in needed:
  name=string(index,True)
  if name in seen:fail('elf_duplicate_needed_name')
  seen.add(name);out['needed'].append({'name':name,'dynamic_entry_ordinal':ordinal,'string_table_offset':index})
 for tag,key in((14,'soname'),(15,'rpath'),(29,'runpath')):
  if tag in values:out[key]=string(values[tag],tag==14)
 for tag,value,ordinal in entries:
  if tag in UNSUPPORTED_OBJECT_TAGS:out['unsupported_dependency_semantics'].append({'tag':UNSUPPORTED_OBJECT_TAGS[tag],'declared_string':string(value),'dynamic_entry_ordinal':ordinal})
 out['dynamic_status']='PARSED_SUPPORTED_METADATA';out['dynamic_segment']={'file_offset':d['offset'],'bytes':d['file_bytes'],'parsed_entries':len(entries),'terminator_entry_ordinal':len(entries),'string_table_file_offset':table,'string_table_bytes':values.get(10)}
 return out

def build(manifest):
 exact(manifest,('schema','source_commit_label','roots','artifacts','root_artifacts','bindings'),'elf_manifest_contract')
 if manifest['schema']!='gig.security.elf_dependency_manifest.v1'or type(manifest['source_commit_label'])is not str or not re.fullmatch('[0-9a-f]{40}',manifest['source_commit_label']):fail('elf_manifest_identity')
 roots=manifest['roots'];artifacts=manifest['artifacts'];root_ids=manifest['root_artifacts'];bindings=manifest['bindings']
 if type(roots)is not dict or not 1<=len(roots)<=MAX_ROOTS:fail('elf_root_budget')
 approved={}
 for key,value in roots.items():
  if not identifier(key)or type(value)is not str or len(value)>1024 or not value.startswith('/')or any(ord(c)<33 or ord(c)>126 for c in value)or '..'in Path(value).parts:fail('elf_root_contract')
  path=Path(value)
  if any(part.casefold()in('.aws','.ssh','.git','.codex','.agents','.env')or part.casefold().endswith('.env')for part in path.parts):fail('elf_root_sensitive_path')
  no_links(path)
  if not path.is_dir():fail('elf_root_missing')
  approved[key]=path
 if type(artifacts)is not list or not 1<=len(artifacts)<=MAX_ARTIFACTS or type(bindings)is not list or len(bindings)>MAX_EDGES:fail('elf_artifact_or_binding_budget')
 if type(root_ids)is not list or not 1<=len(root_ids)<=MAX_ARTIFACTS or any(not identifier(i)for i in root_ids)or len(set(root_ids))!=len(root_ids):fail('elf_root_artifacts')
 reader=Reader();nodes={};paths=set()
 for a in artifacts:
  exact(a,('id','root','path','sha256'),'elf_artifact_contract')
  if not identifier(a['id'])or a['id']in nodes or not identifier(a['root'])or a['root']not in approved or type(a['sha256'])is not str or not HASH.fullmatch(a['sha256']):fail('elf_artifact_identity')
  path=inside(approved[a['root']]/relative(a['path']),approved[a['root']])
  if path in paths:fail('elf_duplicate_artifact_path')
  paths.add(path);raw=reader.read(path);digest=hashlib.sha256(raw).hexdigest()
  if digest!=a['sha256']:fail('elf_original_digest_mismatch')
  nodes[a['id']]={'id':a['id'],'root':a['root'],'path':a['path'],'sha256':digest,'bytes':len(raw),'elf':parse_elf(raw)}
 if any(i not in nodes for i in root_ids):fail('elf_root_artifact_missing')
 declared={}
 for binding in bindings:
  exact(binding,('requester','needed','target'),'elf_binding_contract')
  source,name,target=(binding[k]for k in('requester','needed','target'))
  if not identifier(source)or not identifier(target)or source not in nodes or target not in nodes or type(name)is not str or not OBJECT_NAME.fullmatch(name):fail('elf_binding_identity')
  key=(source,name)
  if key in declared:fail('elf_duplicate_binding')
  if name not in{v['name']for v in nodes[source]['elf']['needed']}:fail('elf_binding_not_declared_by_source')
  consumer=nodes[source]['elf'];provider=nodes[target]['elf']
  if provider['object_type']!=3:fail('elf_binding_provider_object_type')
  if provider['soname']!=name:fail('elf_binding_provider_soname')
  if any(consumer[k]!=provider[k]for k in('bits','byte_order','machine')):fail('elf_binding_architecture')
  declared[key]=target
 if len(canonical(manifest))>MAX_MANIFEST:fail('elf_manifest_budget')
 edges=[]
 for source in sorted(nodes):
  for needed in nodes[source]['elf']['needed']:
   name=needed['name'];target=declared.get((source,name));candidates=sorted(i for i,node in nodes.items()if node['elf']['soname']==name)
   edge={'requester':source,'needed':name,'dynamic_entry_ordinal':needed['dynamic_entry_ordinal'],'requester_sha256':nodes[source]['sha256'],'target':target,'target_sha256':nodes[target]['sha256']if target else None,'supplied_soname_candidates':candidates,'status':'BOUND_EXPLICIT_INPUT'if target else'AMBIGUOUS_SUPPLIED_PROVIDERS'if len(candidates)>1 else'EXPLICIT_BINDING_REQUIRED'if candidates else'NO_SUPPLIED_PROVIDER','authority':'Caller-supplied binding corroborated by original SONAME and header architecture only;not runtime loader attestation'}
   edges.append(edge)
   if len(edges)>MAX_EDGES:fail('elf_edge_budget')
 reachable=set(root_ids);pending=list(root_ids);adj={i:[]for i in nodes}
 for edge in edges:adj[edge['requester']].append(edge)
 while pending:
  source=pending.pop()
  for e in adj[source]:
   if e['target']and e['target']not in reachable:reachable.add(e['target']);pending.append(e['target'])
 unresolved=[e for e in edges if e['requester']in reachable and e['target']is None]
 unsupported=sorted(i for i in reachable if nodes[i]['elf']['unsupported_dependency_semantics'])
 colors={};back_edges=[]
 def visit(source):
  colors[source]=1
  for e in adj[source]:
   target=e['target']
   if not target:continue
   if colors.get(target)==1:back_edges.append({'requester':source,'target':target,'needed':e['needed']})
   elif not colors.get(target):visit(target)
  colors[source]=2
 for source in root_ids:
  if not colors.get(source):visit(source)
 result={'schema':'gig.security.elf_dependency_inventory.v1','profile':PROFILE,'source_commit_label':manifest['source_commit_label'],'manifest_sha256':hashlib.sha256(canonical(manifest)).hexdigest(),'scope':'EXPLICIT_LOCAL_DT_NEEDED_BINDINGS_ONLY','roots':dict(sorted(roots.items())),'root_artifacts':list(root_ids),'artifacts':[nodes[i]for i in sorted(nodes)],'edges':edges,'reachable_artifacts':sorted(reachable),'unreachable_supplied_artifacts':sorted(set(nodes)-reachable),'unresolved_reachable_edges':unresolved,'unsupported_reachable_artifacts':unsupported,'root_dt_needed_bindings_complete':not unresolved,'root_metadata_dependency_scope_supported':not unsupported,'status':'UNSUPPORTED_DEPENDENCY_SEMANTICS'if unsupported else'INCOMPLETE_EXPLICIT_BINDINGS'if unresolved else'EXPLICIT_DT_NEEDED_BINDINGS_VERIFIED','declared_graph_back_edges':back_edges,'runtime_loader_resolution_verified':False,'target_environment_qualified':False,'advisory_analysis':'NOT_RUN','execution_performed':False,'provider_requested':False,'coverage_gaps':['No automatic loader search,interpreter pathname attestation,LD environment,cache,preload or namespace qualification','No relocation,symbol/version/OS-ABI resolution,constructor behavior or dlopen dependency qualification','No software version inferred from SONAME,filename or ELF header;no advisory/backport comparison','Explicit local source/hash consistency and header matching do not authenticate a publisher,build,deployed target or edge']}
 result['sha256']=hashlib.sha256(canonical(result)).hexdigest()
 if len(canonical(result))>MAX_OUTPUT:fail('elf_output_budget')
 return result

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 manifest=load_manifest(Reader().read(args.manifest.absolute(),MAX_MANIFEST));result=build(manifest);write_new(args.output,canonical(result));print(json.dumps({'artifacts':len(result['artifacts']),'edges':len(result['edges']),'unresolved':len(result['unresolved_reachable_edges']),'status':result['status'],'inventory_sha256':result['sha256'],'target_qualified':False,'advisory_analysis':'NOT_RUN'},sort_keys=True))
if __name__=='__main__':main()
