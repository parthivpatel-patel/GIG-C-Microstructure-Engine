"""Authored ELF metadata and explicit bindings; no native execution or loader search."""
import copy,hashlib,json,os,socket,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts import inventory_elf_dependencies as elf
SHA='a'*40

def fixture(*,needed=(),soname=None,rpath=None,runpath=None,bits=64,byte_order='little',machine=62,dynamic=True,interpreter=None,extra_strings=()):
 order='<'if byte_order=='little'else'>';ehsize=52 if bits==32 else 64;phsize=32 if bits==32 else 56;dynsize=8 if bits==32 else 16;base=0x400000;dynoff=0x400;stroff=0x2000
 strings=bytearray(b'\0')
 def add(value):
  offset=len(strings);strings.extend(value.encode()+b'\0');return offset
 entries=[(1,add(name))for name in needed]
 for tag,value in((14,soname),(15,rpath),(29,runpath)):
  if value is not None:entries.append((tag,add(value)))
 for tag,value in extra_strings:entries.append((tag,add(value)))
 entries.extend([(5,base+stroff),(10,len(strings)),(0,0)])
 total=max(stroff+len(strings),dynoff+len(entries)*dynsize)+16;data=bytearray(total);ident=b'\x7fELF'+bytes([1 if bits==32 else 2,1 if order=='<'else 2,1])+b'\0'*9
 phnum=1+int(dynamic)+int(interpreter is not None);fields=(ident,3,machine,1,0,ehsize,0,0,ehsize,phsize,phnum,0,0,0)
 struct.pack_into(order+('16sHHIIIIIHHHHHH'if bits==32 else'16sHHIQQQIHHHHHH'),data,0,*fields)
 def ph(i,typ,offset,address,size,mem=None,align=1):
  values=(typ,offset,address,address,size,size if mem is None else mem,4,align)if bits==32 else(typ,4,offset,address,address,size,size if mem is None else mem,align)
  struct.pack_into(order+('IIIIIIII'if bits==32 else'IIQQQQQQ'),data,ehsize+i*phsize,*values)
 ph(0,1,0,base,total,align=4096)
 if dynamic:
  ph(1,2,dynoff,base+dynoff,len(entries)*dynsize)
  for i,(tag,value)in enumerate(entries):struct.pack_into(order+('iI'if bits==32 else'qQ'),data,dynoff+i*dynsize,tag,value)
 if interpreter is not None:
  raw=interpreter.encode()+b'\0';data[0x200:0x200+len(raw)]=raw;ph(2 if dynamic else 1,3,0x200,base+0x200,len(raw))
 data[stroff:stroff+len(strings)]=strings
 return bytes(data),{'order':order,'bits':bits,'ehsize':ehsize,'phsize':phsize,'dynsize':dynsize,'dynoff':dynoff,'stroff':stroff,'entries':entries,'base':base,'string_bytes':len(strings)}

def edit(raw,info,offset,value,fmt):
 data=bytearray(raw);struct.pack_into(info['order']+fmt,data,offset,value);return bytes(data)
def dynedit(raw,info,index,*,tag=None,value=None):
 data=bytearray(raw);offset=info['dynoff']+index*info['dynsize'];oldtag,oldvalue=struct.unpack_from(info['order']+('iI'if info['bits']==32 else'qQ'),raw,offset)
 struct.pack_into(info['order']+('iI'if info['bits']==32 else'qQ'),data,offset,oldtag if tag is None else tag,oldvalue if value is None else value);return bytes(data)

class ElfMetadata(unittest.TestCase):
 def test_both_classes_and_byte_orders_retain_declared_names_and_order(self):
  for bits in(32,64):
   for order in('little','big'):
    raw,_=fixture(bits=bits,byte_order=order,needed=['libb.so','liba.so'],soname='source.so',rpath='$ORIGIN',runpath='/declared-only',interpreter='/approved/path/loader.so')
    out=elf.parse_elf(raw);self.assertEqual(out['bits'],bits);self.assertEqual(out['byte_order'],order);self.assertEqual([r['name']for r in out['needed']],['libb.so','liba.so']);self.assertEqual([r['dynamic_entry_ordinal']for r in out['needed']],[0,1]);self.assertEqual(out['soname'],'source.so');self.assertEqual(out['rpath'],'$ORIGIN');self.assertEqual(out['runpath'],'/declared-only');self.assertEqual(out['interpreter'],'/approved/path/loader.so');self.assertEqual(out['interpreter_resolution'],'NOT_PERFORMED')
 def test_static_no_dynamic_segment_is_an_explicit_metadata_state(self):
  raw,_=fixture(dynamic=False);out=elf.parse_elf(raw);self.assertEqual(out['dynamic_status'],'NO_PT_DYNAMIC_SEGMENT');self.assertEqual(out['needed'],[]);self.assertIsNone(out['soname'])
 def test_invalid_identity_header_and_object_type(self):
  raw,i=fixture()
  for altered in(b'',b'not ELF',raw[:40],raw[:4]+b'\x03'+raw[5:],edit(raw,i,16,1,'H'),edit(raw,i,18,0,'H'),edit(raw,i,20,2,'I'),edit(raw,i,40 if i['bits']==32 else 52,1,'H')):
   with self.subTest(raw=altered[:20]),self.assertRaises(elf.InventoryError):elf.parse_elf(altered)
 def test_program_table_size_count_extent_and_extended_count(self):
  raw,i=fixture()
  for offset,value,fmt in((32,len(raw),'Q'),(54,8,'H'),(56,0,'H'),(56,0xffff,'H'),(56,elf.MAX_PHDRS+1,'H')):
   with self.subTest(offset=offset,value=value),self.assertRaisesRegex(elf.InventoryError,'program_header'):elf.parse_elf(edit(raw,i,offset,value,fmt))
 def test_load_extents_memory_size_and_alignment_reject(self):
  raw,i=fixture();ph=i['ehsize']
  for offset,value,fmt in((ph+32,len(raw)+1,'Q'),(ph+40,1,'Q'),(ph+48,3,'Q'),(ph+16,i['base']+1,'Q'),(ph+16,2**64-1,'Q')):
   with self.subTest(offset=offset,value=value),self.assertRaises(elf.InventoryError):elf.parse_elf(edit(raw,i,offset,value,fmt))
 def test_ignored_pt_null_fields_do_not_gain_semantics(self):
  raw,i=fixture();data=bytearray(raw);struct.pack_into(i['order']+'I',data,i['ehsize']+i['phsize'],0);out=elf.parse_elf(bytes(data));self.assertEqual(out['dynamic_status'],'NO_PT_DYNAMIC_SEGMENT')
 def test_missing_dynamic_terminator_and_duplicate_singletons(self):
  raw,i=fixture(soname='one.so');last=len(i['entries'])-1
  for altered in(dynedit(raw,i,last,tag=1,value=0),dynedit(raw,i,0,tag=5,value=i['base']+i['stroff'])):
   with self.assertRaisesRegex(elf.InventoryError,'terminator|singleton'):elf.parse_elf(altered)
 def test_dynamic_entry_bounds_and_virtual_mapping_are_independent(self):
  raw,i=fixture(needed=['libb.so']);ph=i['ehsize']+i['phsize']
  for offset,value,fmt in((ph+8,i['dynoff']+8,'Q'),(ph+16,i['base']+len(raw)+1,'Q'),(ph+32,1,'Q')):
   with self.subTest(offset=offset),self.assertRaises(elf.InventoryError):elf.parse_elf(edit(raw,i,offset,value,fmt))
 def test_string_table_presence_bounds_boundaries_and_offsets(self):
  raw,i=fixture(needed=['libb.so']);strtab=1;strsize=2
  cases=[dynedit(raw,i,strtab,tag=12),dynedit(raw,i,strtab,value=i['base']+len(raw)),dynedit(raw,i,strsize,value=0),dynedit(raw,i,strsize,value=elf.MAX_STRINGS+1),dynedit(raw,i,0,value=i['string_bytes'])]
  for offset in(i['stroff'],i['stroff']+i['string_bytes']-1):cases.append(raw[:offset]+b'X'+raw[offset+1:])
  for altered in cases:
   with self.subTest(sha=hashlib.sha256(altered).hexdigest()),self.assertRaises(elf.InventoryError):elf.parse_elf(altered)
 def test_names_do_not_infer_paths_empty_or_unsupported_encodings(self):
  for name in('', '../secret','/usr/lib/liba.so','bad name.so','lib\n.so','é.so'):
   raw,_=fixture(needed=[name])
   with self.subTest(name=name),self.assertRaises(elf.InventoryError):elf.parse_elf(raw)
 def test_duplicate_needed_names_and_needed_budget_reject(self):
  raw,_=fixture(needed=['same.so','same.so'])
  with self.assertRaisesRegex(elf.InventoryError,'duplicate_needed'):elf.parse_elf(raw)
  raw,_=fixture(needed=['lib%d.so'%i for i in range(3)])
  with patch.object(elf,'MAX_NEEDED',2),self.assertRaisesRegex(elf.InventoryError,'needed_budget'):elf.parse_elf(raw)
 def test_filter_and_auxiliary_are_retained_as_explicit_unsupported_semantics(self):
  raw,_=fixture(extra_strings=[(0x7fffffff,'filter.so'),(0x7ffffffd,'aux.so'),(0x6ffffefc,'$ORIGIN/audit.so:other.so')]);out=elf.parse_elf(raw);self.assertEqual([p['tag']for p in out['unsupported_dependency_semantics']],['DT_FILTER','DT_AUXILIARY','DT_AUDIT']);self.assertEqual(out['unsupported_dependency_semantics'][-1]['declared_string'],'$ORIGIN/audit.so:other.so')
 def test_dynamic_and_string_resource_budgets_reject_before_interpretation(self):
  raw,_=fixture(needed=['libb.so'])
  for key,limit in(('MAX_DYNAMIC',1),('MAX_STRINGS',1),('MAX_STRING',1)):
   with self.subTest(key=key),patch.object(elf,key,limit),self.assertRaises(elf.InventoryError):elf.parse_elf(raw)
 def test_interpreter_termination_is_checked_without_following_its_path(self):
  raw,i=fixture(interpreter='/never/opened/loader.so');offset=0x200+len('/never/opened/loader.so');data=raw[:offset]+b'X'+raw[offset+1:]
  with self.assertRaisesRegex(elf.InventoryError,'interpreter_string'):elf.parse_elf(data)
 def test_duplicate_dynamic_segments_and_ambiguous_load_mappings_reject(self):
  raw,i=fixture(interpreter='/loader.so');ph3=i['ehsize']+2*i['phsize'];copy_dynamic=bytearray(raw);copy_dynamic[ph3:ph3+i['phsize']]=raw[i['ehsize']+i['phsize']:i['ehsize']+2*i['phsize']]
  with self.assertRaisesRegex(elf.InventoryError,'multiple_dynamic'):elf.parse_elf(bytes(copy_dynamic))
  duplicate_load=bytearray(raw);duplicate_load[ph3:ph3+i['phsize']]=raw[i['ehsize']:i['ehsize']+i['phsize']]
  with self.assertRaisesRegex(elf.InventoryError,'virtual_mapping_missing_or_ambiguous'):elf.parse_elf(bytes(duplicate_load))
 def test_terminator_stops_dynamic_interpretation(self):
  raw,i=fixture();ph=i['ehsize']+i['phsize'];data=bytearray(raw);end=i['dynoff']+len(i['entries'])*i['dynsize'];struct.pack_into(i['order']+'qQ',data,end,1,0);struct.pack_into(i['order']+'Q',data,ph+32,(len(i['entries'])+1)*i['dynsize']);out=elf.parse_elf(bytes(data));self.assertEqual(out['needed'],[])

class ExplicitBindings(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.manifest={'schema':'gig.security.elf_dependency_manifest.v1','source_commit_label':SHA,'roots':{'authored':str(self.root)},'artifacts':[],'root_artifacts':['root'],'bindings':[{'requester':'root','needed':'libb.so','target':'b'},{'requester':'b','needed':'libc.so','target':'c'}]}
  self.node('root','root.so',needed=['libb.so'],soname='root.so');self.node('b','b.so',needed=['libc.so'],soname='libb.so');self.node('c','c.so',soname='libc.so')
 def node(self,id,path,**kw):
  raw,_=fixture(**kw);(self.root/path).write_bytes(raw);row={'id':id,'root':'authored','path':path,'sha256':hashlib.sha256(raw).hexdigest()};self.manifest['artifacts']=[r for r in self.manifest['artifacts']if r['id']!=id]+[row]
 def build(self):return elf.build(self.manifest)
 def test_explicit_source_bound_graph_never_executes_or_mutates_inputs(self):
  before=copy.deepcopy(self.manifest)
  with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch('subprocess.run',side_effect=AssertionError('NO_EXECUTION')):out=self.build()
  self.assertEqual(self.manifest,before);self.assertEqual(out['status'],'EXPLICIT_DT_NEEDED_BINDINGS_VERIFIED');self.assertTrue(out['root_dt_needed_bindings_complete']);self.assertEqual(out['reachable_artifacts'],['b','c','root']);self.assertFalse(out['runtime_loader_resolution_verified']);self.assertFalse(out['target_environment_qualified']);self.assertEqual(out['advisory_analysis'],'NOT_RUN');self.assertEqual(out['sha256'],hashlib.sha256(elf.canonical({k:v for k,v in out.items()if k!='sha256'})).hexdigest())
 def test_missing_binding_is_not_automatically_resolved_from_a_unique_provider(self):
  self.manifest['bindings']=[];out=self.build();self.assertEqual(out['unresolved_reachable_edges'][0]['status'],'EXPLICIT_BINDING_REQUIRED');self.assertFalse(out['root_dt_needed_bindings_complete']);self.assertEqual(out['reachable_artifacts'],['root'])
 def test_unavailable_provider_and_duplicate_candidates_remain_unresolved(self):
  self.manifest['bindings']=[];self.manifest['artifacts']=[r for r in self.manifest['artifacts']if r['id']!='b'];out=self.build();self.assertEqual(out['unresolved_reachable_edges'][0]['status'],'NO_SUPPLIED_PROVIDER')
  self.node('b','b.so',soname='libb.so');self.node('b2','b2.so',soname='libb.so');out=self.build();self.assertEqual(out['unresolved_reachable_edges'][0]['status'],'AMBIGUOUS_SUPPLIED_PROVIDERS')
 def test_explicit_choice_retains_other_supplied_candidates_without_runtime_claim(self):
  self.node('b2','b2.so',soname='libb.so');out=self.build();edge=next(e for e in out['edges']if e['requester']=='root');self.assertEqual(edge['target'],'b');self.assertEqual(edge['supplied_soname_candidates'],['b','b2']);self.assertEqual(out['unreachable_supplied_artifacts'],['b2']);self.assertFalse(out['runtime_loader_resolution_verified'])
 def test_binding_missing_source_target_duplicate_or_unreported_needed_reject(self):
  good=copy.deepcopy(self.manifest)
  for binding in({'requester':'absent','needed':'libb.so','target':'b'},{'requester':'root','needed':'absent.so','target':'b'},{'requester':'root','needed':'libb.so','target':'absent'}):
   self.manifest=copy.deepcopy(good);self.manifest['bindings']=[binding]
   with self.subTest(binding=binding),self.assertRaises(elf.InventoryError):self.build()
  self.manifest=good;self.manifest['bindings'].append(copy.deepcopy(self.manifest['bindings'][0]))
  with self.assertRaisesRegex(elf.InventoryError,'duplicate_binding'):self.build()
 def test_binding_requires_actual_soname_and_architecture_not_filename_similarity(self):
  for kwargs in({'soname':'wrong.so'},{'soname':None},{'soname':'libb.so','bits':32},{'soname':'libb.so','byte_order':'big'},{'soname':'libb.so','machine':183}):
   self.node('b','b.so',**kwargs)
   with self.subTest(kwargs=kwargs),self.assertRaisesRegex(elf.InventoryError,'soname|architecture'):self.build()
 def test_provider_must_be_shared_object_even_when_rehashed_soname_matches(self):
  path=self.root/'b.so';raw=bytearray(path.read_bytes());struct.pack_into('<H',raw,16,2);path.write_bytes(raw)
  next(r for r in self.manifest['artifacts']if r['id']=='b')['sha256']=hashlib.sha256(raw).hexdigest()
  with self.assertRaisesRegex(elf.InventoryError,'provider_object_type'):self.build()
 def test_changed_original_and_rehashed_wrong_provider_reject(self):
  path=self.root/'b.so';path.write_bytes(path.read_bytes()+b'changed')
  with self.assertRaisesRegex(elf.InventoryError,'original_digest_mismatch'):self.build()
  self.node('b','b.so',soname='wrong.so')
  with self.assertRaisesRegex(elf.InventoryError,'provider_soname'):self.build()
 def test_declaration_cycles_are_bounded_and_reported(self):
  self.node('b','b.so',needed=['root.so'],soname='libb.so');self.manifest['bindings'][1]={'requester':'b','needed':'root.so','target':'root'};out=self.build();self.assertTrue(out['root_dt_needed_bindings_complete']);self.assertEqual(out['declared_graph_back_edges'],[{'requester':'b','target':'root','needed':'root.so'}])
 def test_unsupported_object_dependency_semantics_never_claim_supported_scope(self):
  self.node('b','b.so',soname='libb.so',extra_strings=[(0x7fffffff,'filter.so')]);self.manifest['bindings']=self.manifest['bindings'][:1];out=self.build();self.assertEqual(out['status'],'UNSUPPORTED_DEPENDENCY_SEMANTICS');self.assertEqual(out['unsupported_reachable_artifacts'],['b'])
 def test_root_and_artifact_paths_no_symlinks_traversal_or_secret_names(self):
  good=copy.deepcopy(self.manifest)
  for path in('/etc/passwd','../escape','.env','secret/../b.so'):
   self.manifest=copy.deepcopy(good);self.manifest['artifacts'][0]['path']=path
   with self.subTest(path=path),self.assertRaises(elf.InventoryError):self.build()
  self.manifest=good;path=self.root/'b.so';path.unlink();path.symlink_to(self.root/'c.so')
  with self.assertRaisesRegex(elf.InventoryError,'symlink'):self.build()
 def test_sensitive_directory_in_root_is_rejected_before_any_file_read(self):
  for name in('.aws','.ssh','.git','.codex','.agents','.env','project.env'):
   root=self.root/name;root.mkdir();self.manifest['roots']['authored']=str(root)
   with self.subTest(name=name),patch.object(elf.Reader,'read',side_effect=AssertionError('NO_SENSITIVE_FILE_READ')),self.assertRaisesRegex(elf.InventoryError,'root_sensitive_path'):self.build()
 def test_duplicate_paths_ids_and_wrong_types_reject(self):
  good=copy.deepcopy(self.manifest)
  for mutate in(lambda m:m['artifacts'].append(copy.deepcopy(m['artifacts'][0])),lambda m:m['artifacts'][0].update(root=[]),lambda m:m['root_artifacts'].append('root'),lambda m:m['artifacts'][0].update(sha256='bad'),lambda m:m['artifacts'][0].update(extra=True)):
   self.manifest=copy.deepcopy(good);mutate(self.manifest)
   with self.assertRaises(elf.InventoryError):self.build()
  self.manifest=copy.deepcopy(good);self.manifest['artifacts'].append({**self.manifest['artifacts'][0],'id':'another'})
  with self.assertRaisesRegex(elf.InventoryError,'duplicate_artifact_path'):self.build()
 def test_deterministic_named_set_order_preserves_manifest_identity(self):
  first=self.build();self.assertEqual(self.build(),first);self.manifest['artifacts'].reverse();second=self.build();self.assertEqual(first['artifacts'],second['artifacts']);self.assertEqual(first['edges'],second['edges']);self.assertNotEqual(first['manifest_sha256'],second['manifest_sha256'])
 def test_input_and_output_resource_limits_are_exact(self):
  for name,value,code in(('MAX_ROOTS',0,'root_budget'),('MAX_ARTIFACTS',1,'artifact_or_binding_budget'),('MAX_EDGES',0,'artifact_or_binding_budget'),('MAX_OUTPUT',1,'output_budget')):
   with self.subTest(name=name),patch.object(elf,name,value),self.assertRaisesRegex(elf.InventoryError,code):self.build()
 def test_manifest_duplicate_keys_numbers_unicode_and_unknown_contract_reject(self):
  for raw in(b'{"a":1,"a":2}',b'{"a":1.0000000000000001}',b'{"a":1e0}',b'{"a":NaN}',b'\xff',b'[]'):
   with self.subTest(raw=raw),self.assertRaises(elf.InventoryError):
    parsed=elf.load_manifest(raw);elf.build(parsed)
  raw=json.dumps(self.manifest).encode();self.assertEqual(elf.load_manifest(raw),self.manifest)
  with patch.object(elf,'MAX_MANIFEST',1),self.assertRaisesRegex(elf.InventoryError,'manifest_budget'):elf.load_manifest(raw)
 def test_duplicate_json_keys_reject_independently_of_numeric_token_policy(self):
  with self.assertRaisesRegex(elf.InventoryError,'manifest_duplicate_key'):elf.load_manifest(b'{"schema":"one","schema":"two"}')
 def test_declared_binding_edge_limit_and_manifest_budget_are_enforced(self):
  self.manifest['bindings']=[]
  with patch.object(elf,'MAX_EDGES',1),self.assertRaisesRegex(elf.InventoryError,'edge_budget'):self.build()
  with patch.object(elf,'MAX_MANIFEST',1),self.assertRaisesRegex(elf.InventoryError,'manifest_budget'):self.build()
 def test_exclusive_output_preserves_existing_receipt(self):
  path=self.root/'receipt.json';elf.write_new(path,b'original')
  with self.assertRaises(FileExistsError):elf.write_new(path,b'replacement')
  self.assertEqual(path.read_bytes(),b'original')

if __name__=='__main__':unittest.main(verbosity=2)
