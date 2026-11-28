"""Explicit local artifacts only: no package imports, sockets or target clearance."""
import base64,csv,hashlib,io,json,os,shutil,socket,stat,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts import inventory_local_artifacts as inv
SHA='7cd99d4afd98f58330732ecfc0fd0b3303c49a3b'

def header(bits=64,endian='little'):
 data=bytearray(64 if bits==64 else 52);data[:7]=b'\x7fELF'+bytes([2 if bits==64 else 1,1 if endian=='little'else 2,1]);order='<'if endian=='little'else'>'
 struct.pack_into(order+'HHI',data,16,3,62 if bits==64 else 3,1);struct.pack_into(order+'H',data,52 if bits==64 else 40,len(data));return bytes(data)
def sha(raw):return 'sha256='+base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('=')

class LocalArtifacts(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.site=self.root/'env/lib/site-packages';self.site.mkdir(parents=True);self.info=self.site/'demo_pkg-1.2.3.dist-info';self.info.mkdir();self.native=self.root/'native.so';self.native.write_bytes(header());self.release=self.root/'os-release';self.release.write_text('ID=authored\nNAME="Authored OS"\nVERSION_ID="1.0"\nHOME_URL="https://example.invalid"\n')
  self.install()
 def install(self):
  (self.info/'METADATA').write_bytes(b'Metadata-Version: 2.1\nName: Demo_Pkg\nVersion: 1.2.3\n\n')
  (self.site/'demo.py').write_bytes(b'raise RuntimeError("PACKAGE_CODE_MUST_NOT_EXECUTE")\n')
  self.rows=[['demo.py',sha((self.site/'demo.py').read_bytes()),str((self.site/'demo.py').stat().st_size)],['demo_pkg-1.2.3.dist-info/METADATA',sha((self.info/'METADATA').read_bytes()),str((self.info/'METADATA').stat().st_size)],['demo_pkg-1.2.3.dist-info/RECORD','','']];self.record()
 def record(self):
  out=io.StringIO(newline='');csv.writer(out,lineterminator='\n').writerows(self.rows);(self.info/'RECORD').write_text(out.getvalue())
 def build(self,**kw):
  return inv.build(self.root,'env','env/lib/site-packages',kw.pop('native',['native.so']),SHA,**kw)
 def dpkg_selection(self):
  payload=b'authored installed executable'
  target=self.root/'usr/bin/demo';target.parent.mkdir(parents=True);target.write_bytes(payload)
  status=self.root/'var/lib/dpkg/status';info=status.parent/'info';info.mkdir(parents=True)
  status.write_text('Package: demo\nVersion: 1.2.3\nArchitecture: amd64\n'
                    'Status: install ok installed\nMulti-Arch: same\n')
  sums=info/'demo:amd64.md5sums'
  recorded=hashlib.md5(payload,usedforsecurity=False).hexdigest()
  sums.write_text(f'{recorded}  usr/bin/demo\n')
  request={'schema':'gig.security.selected_dpkg_files.v1',
           'status_sha256':hashlib.sha256(status.read_bytes()).hexdigest(),
           'packages':[{'package':'demo','architecture':'amd64','version':'1.2.3',
                        'md5sums_sha256':hashlib.sha256(sums.read_bytes()).hexdigest(),
                        'files':['usr/bin/demo']}]}
  return status,sums,target,request

 def test_selected_dpkg_file_binds_status_control_and_observed_bytes(self):
  status,sums,target,request=self.dpkg_selection()
  (self.root/'selected.json').write_text(json.dumps(request))
  result=self.build(dpkg_status_path=status,dpkg_file_request='selected.json')
  selected=result['dpkg_file_integrity']
  package=selected['packages'][0]
  self.assertEqual(selected['files_checked'],1)
  self.assertEqual(package['md5sums_sha256'],request['packages'][0]['md5sums_sha256'])
  self.assertEqual(package['files'][0]['observed_sha256'],hashlib.sha256(target.read_bytes()).hexdigest())
  self.assertEqual(package['md5sums_path'],'var/lib/dpkg/info/demo:amd64.md5sums')
  self.assertEqual(result['os_packages']['package_file_integrity'],'VERIFIED_EXPLICIT_SELECTION_ONLY')
  self.assertFalse(selected['publisher_authenticated'])
  self.assertNotIn('dpkg_file_integrity',self.build(dpkg_status_path=status))

 def test_selected_dpkg_file_rejects_byte_substitution_and_symlink(self):
  status,sums,target,request=self.dpkg_selection()
  path=self.root/'selected.json';path.write_text(json.dumps(request))
  native=target.read_bytes()
  target.write_bytes(b'changed')
  with self.assertRaisesRegex(inv.InventoryError,'file_digest_mismatch'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)
  target.unlink();target.symlink_to(self.native)
  with self.assertRaisesRegex(inv.InventoryError,'inventory_symlink'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)
  target.unlink();target.write_bytes(native)
  sums.write_bytes(sums.read_bytes()+b'\n')
  with self.assertRaisesRegex(inv.InventoryError,'md5sums_digest_mismatch'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)
  status.write_bytes(status.read_bytes()+b'\n')
  with self.assertRaisesRegex(inv.InventoryError,'status_digest_mismatch'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)

 def test_selected_dpkg_request_rejects_duplicate_keys_and_unlisted_files(self):
  status,_,_,request=self.dpkg_selection()
  path=self.root/'selected.json'
  path.write_text(json.dumps(request)[:-1]+',"packages":[]}')
  with self.assertRaisesRegex(inv.InventoryError,'duplicate_key'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)
  request['packages'][0]['files']=['usr/bin/other']
  path.write_text(json.dumps(request))
  with self.assertRaisesRegex(inv.InventoryError,'file_unlisted'):
   self.build(dpkg_status_path=status,dpkg_file_request=path.name)

 def test_exact_installed_identity_receipts_and_explicit_coverage(self):
  with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(socket.socket,'bind',side_effect=AssertionError('NO_SERVER')):p=self.build(os_release_path=self.release)
  self.assertEqual(p['python_distributions'][0]['name'],'demo-pkg');self.assertEqual(p['python_distributions'][0]['declared_name'],'Demo_Pkg');self.assertEqual(p['python_distributions'][0]['version'],'1.2.3');self.assertEqual(p['python_scope']['unique_recorded_artifacts'],3);self.assertEqual(p['python_scope']['records_without_declared_digest'],1)
  self.assertEqual(p['explicit_native_artifacts'][0]['header']['bits'],64);self.assertEqual(p['os_release']['fields'],{'ID':'authored','NAME':'Authored OS','VERSION_ID':'1.0'});self.assertFalse(p['target_environment_qualified']);self.assertEqual(p['advisories']['status'],'NOT_RUN');self.assertFalse(p['provider_requested']);body={k:v for k,v in p.items()if k!='sha256'};self.assertEqual(p['sha256'],hashlib.sha256(inv.canonical(body)).hexdigest())
 def test_deterministic_under_relocation_and_unrecorded_files_not_claimed(self):
  first=self.build();other=self.root/'copy';shutil.copytree(self.root/'env',other/'env');shutil.copyfile(self.native,other/'native.so');second=inv.build(other,'env','env/lib/site-packages',['native.so'],SHA)
  self.assertEqual(inv.canonical(first),inv.canonical(second));(self.site/'not-in-record.py').write_text('authored');self.assertEqual(self.build(),first);self.assertEqual(first['python_scope']['unrecorded_site_files'],'NOT_SCANNED')
 def test_record_hash_and_size_binding_reject_alteration(self):
  (self.site/'demo.py').write_bytes(b'tampered')
  with self.assertRaisesRegex(inv.InventoryError,'record_size|digest_mismatch'):self.build()
  self.rows[0][2]='8';self.record()
  with self.assertRaisesRegex(inv.InventoryError,'digest_mismatch'):self.build()
 def test_supported_sha384_and_sha512_record_digests(self):
  for algorithm in ('sha384','sha512'):
   raw=(self.site/'demo.py').read_bytes();self.rows[0][1]=algorithm+'='+base64.urlsafe_b64encode(hashlib.new(algorithm,raw).digest()).decode().rstrip('=');self.record();self.assertTrue(self.build()['python_distributions'][0]['artifacts'][0]['record_digest_verified'])
 def test_unsupported_or_malformed_record_hashes(self):
  for value in ('md5=abc','sha256=','sha256=invalid!','sha256=abc=def','sha256=a'):
   self.rows[0][1]=value;self.record()
   with self.subTest(value=value),self.assertRaisesRegex(inv.InventoryError,'record_hash|digest_mismatch'):self.build()
 def test_record_size_requires_exact_unsigned_decimal(self):
  for size in ('1.0','1e1','-1','+10','9007199254740993',''):
   self.rows[0][2]=size;self.record()
   if size=='':self.assertFalse(next(x for x in self.build()['python_distributions'][0]['artifacts']if x['path'].endswith('demo.py'))['record_size_verified'])
   else:
    with self.subTest(size=size),self.assertRaisesRegex(inv.InventoryError,'record_size'):self.build()
 def test_duplicate_record_paths_and_missing_required_members(self):
  self.rows.append(self.rows[0]);self.record()
  with self.assertRaisesRegex(inv.InventoryError,'duplicate_record_path'):self.build()
  self.rows=self.rows[:1];self.record()
  with self.assertRaisesRegex(inv.InventoryError,'required_record_members'):self.build()
 def test_record_csv_malformed_columns(self):
  for text in ('"unterminated','demo.py,hash\n','demo.py,hash,1,extra\n'):
   (self.info/'RECORD').write_text(text)
   with self.subTest(text=text),self.assertRaisesRegex(inv.InventoryError,'record_csv|record_columns'):self.build()
 def test_metadata_duplicate_missing_malformed_identities(self):
  for raw in (b'Name: Demo\nName: Evil\nVersion: 1\n',b'Name: Demo\n',b'Name: ../secret\nVersion: 1\n',b'Name: Demo\nVersion: 1\nVersion: 2\n'):
   (self.info/'METADATA').write_bytes(raw)
   with self.subTest(raw=raw),self.assertRaisesRegex(inv.InventoryError,'metadata_identity'):self.build()
 def test_duplicate_normalized_distribution_names(self):
  other=self.site/'other-1.dist-info';other.mkdir();(other/'METADATA').write_text('Name: demo-pkg\nVersion: 1.2.3\n');(other/'RECORD').write_text('')
  with self.assertRaisesRegex(inv.InventoryError,'duplicate_distribution'):self.build()
 def test_relative_paths_and_escape_fail_closed(self):
  for location in ('/etc/passwd','demo/../secret','./demo.py','demo//x','demo\\x','../../../outside','demo name.py','demo\x00.py'):
   self.rows[0][0]=location;self.record()
   with self.subTest(location=location),self.assertRaisesRegex(inv.InventoryError,'relative_path|record_path|path_scope'):self.build()
 def test_leading_parent_record_path_allowed_only_inside_explicit_venv(self):
  binary=self.root/'env/bin/demo';binary.parent.mkdir();binary.write_bytes(b'passive entry point')
  self.rows.append(['../../bin/demo',sha(binary.read_bytes()),str(binary.stat().st_size)]);self.record();p=self.build();self.assertEqual(p['python_scope']['unique_recorded_artifacts'],4)
 def test_sensitive_names_reject_before_their_files_are_opened(self):
  for name in ('.env','.aws/credentials','project.env','.ssh/id_rsa','.git/config'):
   self.rows[0][0]=name;self.record()
   with self.subTest(name=name),patch('scripts.inventory_local_artifacts.os.open',wraps=os.open)as opened:
    with self.assertRaisesRegex(inv.InventoryError,'sensitive_path'):self.build()
    self.assertFalse(any(str(call.args[0]).endswith(name)for call in opened.call_args_list))
 def test_symlink_record_file_parent_distribution_and_native_reject(self):
  original=self.site/'demo.py';body=original.read_bytes();original.unlink();original.symlink_to(self.native)
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):self.build()
  original.unlink();original.write_bytes(body);target=self.root/'real-info';self.info.rename(target);self.info.symlink_to(target,target_is_directory=True)
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):self.build()
  self.info.unlink();target.rename(self.info);self.native.unlink();self.native.symlink_to(original)
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):self.build()
 def test_native_identity_header_and_duplicate_admission(self):
  for bits in (32,64):
   for order in ('little','big'):
    self.native.write_bytes(header(bits,order));p=self.build();self.assertEqual(p['explicit_native_artifacts'][0]['header']['bits'],bits);self.assertEqual(p['explicit_native_artifacts'][0]['header']['byte_order'],order)
  for raw in (b'',b'not an ELF',b'\x7fELF'+b'\x02\x01\x01'+b'\x00'*20,header()[:51]):
   self.native.write_bytes(raw)
   with self.subTest(raw=raw[:8]),self.assertRaisesRegex(inv.InventoryError,'elf_header'):self.build()
  self.native.write_bytes(header())
  with self.assertRaisesRegex(inv.InventoryError,'duplicate_native'):self.build(native=['native.so','native.so'])
 def test_elf_header_version_and_declared_size_reject(self):
  for offset in (6,20,52):
   raw=bytearray(header());raw[offset]=2;self.native.write_bytes(raw)
   with self.subTest(offset=offset),self.assertRaisesRegex(inv.InventoryError,'elf_header'):self.build()
 def test_resource_bounds_and_no_partial_output(self):
  for name,value,code in [('MAX_FILE',20,'budget'),('MAX_TOTAL',20,'budget'),('MAX_FILES',1,'file_count'),('MAX_DISTRIBUTIONS',0,'distribution_budget'),('MAX_NATIVE',0,'native_count'),('MAX_OUTPUT',1,'output_budget')]:
   with self.subTest(name=name),patch.object(inv,name,value),self.assertRaisesRegex(inv.InventoryError,code):self.build()
  self.assertFalse((self.root/'result.json').exists())
 def test_nonregular_files_reject_without_blocking(self):
  path=self.site/'demo.py';path.unlink();os.mkfifo(path)
  with self.assertRaisesRegex(inv.InventoryError,'file_type_or_budget'):self.build()
 def test_os_release_is_passive_filtered_and_fail_closed(self):
  for raw in ('ID=authored\nID=other\n','ID="unterminated\n','ID=$(touch forbidden)\n','ID=authored\nNAME=`id`\n','NAME="missing identifier"\n','ID=authored\nBROKEN LINE\n'):
   self.release.write_text(raw)
   with self.subTest(raw=raw),self.assertRaisesRegex(inv.InventoryError,'os_'):self.build(os_release_path=self.release)
 def test_os_source_cannot_be_symlink(self):
  self.release.unlink();self.release.symlink_to(self.info/'METADATA')
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):self.build(os_release_path=self.release)
 def test_strict_root_revision_and_native_input_types(self):
  for revision in ('main','',None,123,SHA.upper()):
   with self.subTest(revision=revision),self.assertRaisesRegex(inv.InventoryError,'root_or_revision'):inv.build(self.root,'env','env/lib/site-packages',[],revision)
  for natives in (None,'native.so',[1]):
   with self.subTest(natives=natives),self.assertRaisesRegex(inv.InventoryError,'native_count'):self.build(native=natives)
 def test_site_packages_must_remain_inside_explicit_venv(self):
  for site in ('elsewhere','../escape','env','env/../outside'):
   with self.subTest(site=site),self.assertRaisesRegex(inv.InventoryError,'scope|relative_path'):inv.build(self.root,'env',site,[],SHA)
 def test_exclusive_private_output_and_symlink_rejection(self):
  out=self.root/'result.json';inv.write_new(out,b'original');self.assertEqual(stat.S_IMODE(out.stat().st_mode),0o600)
  with self.assertRaises(FileExistsError):inv.write_new(out,b'replacement')
  self.assertEqual(out.read_bytes(),b'original');link=self.root/'link.json';link.symlink_to(out)
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):inv.write_new(link,b'replacement')
 def test_site_enumeration_is_bounded_before_full_directory_consumption(self):
  def many(_path):
   for _ in range(4097):yield self.site/'authored'
   raise AssertionError('UNBOUNDED_DIRECTORY_ENUMERATION')
  with patch.object(Path,'iterdir',many),self.assertRaisesRegex(inv.InventoryError,'site_entry_budget'):self.build()
 def test_os_release_cannot_be_an_arbitrary_external_path(self):
  other=tempfile.TemporaryDirectory();self.addCleanup(other.cleanup);path=Path(other.name)/'public-release';path.write_text('ID=authored\n')
  with self.assertRaisesRegex(inv.InventoryError,'path_scope'):self.build(os_release_path=path)
 def dpkg(self,package='demo',version='1:1.2.3-4',architecture='amd64',status='install ok installed'):
  return f'Package: {package}\nVersion: {version}\nArchitecture: {architecture}\nStatus: {status}\nDescription: Authored package\n retained multiline field\n'
 def test_passive_os_packages_bind_source_versions_status_and_multiarch(self):
  path=self.root/'dpkg-status';raw=self.dpkg()+ '\n'+self.dpkg(architecture='arm64',status='hold reinstreq installed')+'\n'+self.dpkg(package='removed',status='deinstall ok config-files');path.write_text(raw)
  with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch('subprocess.run',side_effect=AssertionError('NO_COMMAND')):p=self.build(os_release_path=self.release,dpkg_status_path=path)
  d=p['os_packages'];self.assertEqual(d['records'],3);self.assertEqual(d['installed_state_records'],2);self.assertEqual(d['installed_ok_records'],1);self.assertEqual(d['packages'][0]['version'],'1:1.2.3-4');self.assertEqual(d['sha256'],hashlib.sha256(raw.encode()).hexdigest());self.assertEqual(p['os_release']['package_database_inventory'],'INCLUDED_DPKG_STATUS_ONLY');self.assertEqual(d['package_file_integrity'],'NOT_VERIFIED');self.assertFalse(any('description'in row for row in d['packages']))
 def test_os_database_missing_identity_status_and_duplicates_reject(self):
  path=self.root/'dpkg-status';good=self.dpkg()
  for raw in ('',good.replace('Version: 1:1.2.3-4\n',''),good.replace('Status: install ok installed','Status: install ok guessed'),good+'\n'+good,good+'status: install ok installed\n',good.replace('Package: demo','Package: BAD NAME'),good.replace('Architecture: amd64','Architecture: amd64 bogus')):
   path.write_text(raw)
   with self.subTest(raw=raw[:80]),self.assertRaises(inv.InventoryError):self.build(dpkg_status_path=path)
 def test_os_database_field_case_and_source_stanzas_preserve_order(self):
  path=self.root/'dpkg-status';path.write_text(self.dpkg(package='zulu').replace('Package:','package:')+'\n'+self.dpkg(package='alpha'))
  rows=self.build(dpkg_status_path=path)['os_packages']['packages'];self.assertEqual([x['package']for x in rows],['alpha','zulu']);self.assertEqual([x['source_stanza']for x in rows],[2,1])
 def test_os_database_malformed_control_continuation_and_simple_fields(self):
  path=self.root/'dpkg-status';good=self.dpkg()
  for raw in (' continuation without field\n'+good,good.replace('Package: demo','bad field: demo'),good.replace('Package: demo','Package: de\x00mo'),good.replace('Version: 1:1.2.3-4','Version: 1:1.2.3-4\n continuation'),good.replace('Status: install ok installed','Status: install  ok installed')):
   path.write_text(raw)
   with self.subTest(raw=raw[:80]),self.assertRaisesRegex(inv.InventoryError,'dpkg_'):self.build(dpkg_status_path=path)
  path.write_bytes(b'Package: \xff\n')
  with self.assertRaisesRegex(inv.InventoryError,'dpkg_utf8'):self.build(dpkg_status_path=path)
 def test_os_database_resource_limits_and_symlinks(self):
  path=self.root/'dpkg-status';path.write_text(self.dpkg())
  for name,value,code in [('MAX_OS_DATABASE',1,'budget'),('MAX_OS_PACKAGES',0,'package_budget'),('MAX_OS_STANZA',1,'stanza_budget'),('MAX_OS_FIELD',1,'field_budget')]:
   with self.subTest(name=name),patch.object(inv,name,value),self.assertRaisesRegex(inv.InventoryError,code):self.build(dpkg_status_path=path)
  path.unlink();path.symlink_to(self.release)
  with self.assertRaisesRegex(inv.InventoryError,'symlink'):self.build(dpkg_status_path=path)
 def test_long_legitimate_os_description_is_bounded_and_not_exported(self):
  path=self.root/'dpkg-status';path.write_text(self.dpkg()+' '+('x'*96000)+'\n');p=self.build(dpkg_status_path=path);self.assertEqual(p['os_packages']['records'],1);self.assertNotIn('x'*100,inv.canonical(p).decode())
  path.write_text(self.dpkg()+' '+('x'*inv.MAX_OS_FIELD)+'\n')
  with self.assertRaisesRegex(inv.InventoryError,'field_budget'):self.build(dpkg_status_path=path)
 def test_os_database_does_not_read_arbitrary_external_or_sensitive_paths(self):
  other=tempfile.TemporaryDirectory();self.addCleanup(other.cleanup);path=Path(other.name)/'status';path.write_text(self.dpkg())
  with self.assertRaisesRegex(inv.InventoryError,'path_scope'):self.build(dpkg_status_path=path)
  secret=self.root/'.env';secret.write_text(self.dpkg())
  with self.assertRaisesRegex(inv.InventoryError,'sensitive_path'):self.build(dpkg_status_path=secret)
 def test_os_source_selection_retains_precedence_and_standard_alias_only(self):
  preferred=self.root/'etc/os-release';vendor=self.root/'usr/lib/os-release';preferred.parent.mkdir(parents=True);vendor.parent.mkdir(parents=True);preferred.write_text('ID=preferred\n');vendor.write_text('ID=vendor\n')
  self.assertEqual(inv.select_os_release(preferred,vendor),preferred);preferred.unlink();preferred.symlink_to('../usr/lib/os-release')
  self.assertEqual(inv.select_os_release(preferred,vendor),vendor);preferred.unlink();preferred.symlink_to(self.release)
  with self.assertRaisesRegex(inv.InventoryError,'os_source_selector'):inv.select_os_release(preferred,vendor)
  preferred.unlink();vendor.unlink();self.assertIsNone(inv.select_os_release(preferred,vendor))
 def test_os_release_identity_and_bare_special_values_reject(self):
  for raw in ('ID="not valid"\n','ID=AUTHORED\n','ID=authored\nID_LIKE="valid BAD"\n','ID=authored\nNAME=bare spaces\n'):
   self.release.write_text(raw)
   with self.subTest(raw=raw),self.assertRaisesRegex(inv.InventoryError,'os_identity|os_release'):self.build(os_release_path=self.release)
 def test_changed_during_read_rejects_before_caching(self):
  reader=inv.Reader();original=os.fstat;calls=0
  def changed(fd):
   nonlocal calls
   calls+=1;r=original(fd)
   if calls==2:
    data=list(r);data[6]+=1;return os.stat_result(data)
   return r
  with patch('scripts.inventory_local_artifacts.os.fstat',side_effect=changed),self.assertRaisesRegex(inv.InventoryError,'changed_during_read'):reader.read(self.native)

if __name__=='__main__':unittest.main(verbosity=2)
