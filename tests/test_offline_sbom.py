"""Source-only CycloneDX inventory regressions; no installs or registry requests."""
import copy,hashlib,json,os,shutil,socket,stat,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.build_offline_sbom import INPUTS,InventoryError,build,canonical,write_new
SHA='2edef0115f1d2a3f33ccabce87f5ad1505b07005'

class OfflineSBOM(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  for name in INPUTS:
   target=self.root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
 def edit_lock(self,mutate):
  path=self.root/'terminal/web/package-lock.json';v=json.loads(path.read_bytes());mutate(v);path.write_text(json.dumps(v))
 def test_deterministic_relocation_and_source_bound_purls(self):
  with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')):
   first=build(ROOT,SHA);second=build(self.root,SHA)
  self.assertEqual(canonical(first),canonical(second));self.assertEqual(first['bomFormat'],'CycloneDX');self.assertEqual(first['specVersion'],'1.6')
  purls=[row['purl']for row in first['components']];self.assertEqual(purls,sorted(set(purls)));self.assertIn('pkg:pypi/typing-extensions@4.16.0',purls);self.assertIn('pkg:npm/react@19.1.1',purls);self.assertIn('pkg:npm/%40types/node@24.5.2',purls)
  properties={p['name']:p['value']for p in first['metadata']['properties']};records=json.loads(properties['gig:source-inputs']);self.assertEqual(len(records),7);self.assertEqual(properties['gig:source-inputs-sha256'],hashlib.sha256(canonical(records)).hexdigest())
 def test_original_input_bytes_change_identity_even_without_pin_change(self):
  first=build(self.root,SHA);p=self.root/'requirements-python.lock';p.write_bytes(p.read_bytes()+b'\n# authored provenance\n');second=build(self.root,SHA)
  self.assertEqual(first['components'],second['components']);self.assertNotEqual(first['metadata']['properties'],second['metadata']['properties'])
 def test_exact_python_pins_and_duplicate_normalized_names_reject(self):
  p=self.root/'requirements-python.lock'
  for text in('httpx>=0.28\n','httpx @ https://example.invalid/pkg\n','typing_extensions==4.16.0\ntyping-extensions==4.16.0\n'):
   p.write_text(text)
   with self.assertRaises(InventoryError):build(self.root,SHA)
 def test_npm_root_and_direct_package_binding_reject_missing_or_changed_lock(self):
  self.edit_lock(lambda v:v['packages'][''].update(version='9.9.9'))
  with self.assertRaisesRegex(InventoryError,'manifest_lock_mismatch'):build(self.root,SHA)
  shutil.copyfile(ROOT/'terminal/web/package-lock.json',self.root/'terminal/web/package-lock.json');self.edit_lock(lambda v:v['packages'].pop('node_modules/react'))
  with self.assertRaisesRegex(InventoryError,'direct_binding'):build(self.root,SHA)
 def test_duplicate_json_keys_and_future_lock_version_reject(self):
  p=self.root/'terminal/web/package-lock.json';p.write_text('{"lockfileVersion":3,"lockfileVersion":3}')
  with self.assertRaisesRegex(InventoryError,'duplicate_json_key'):build(self.root,SHA)
  shutil.copyfile(ROOT/'terminal/web/package-lock.json',p);self.edit_lock(lambda v:v.update(lockfileVersion=99))
  with self.assertRaisesRegex(InventoryError,'lock_version'):build(self.root,SHA)
 def test_invalid_integrity_registry_and_artifact_identity_reject(self):
  for field,value,code in [('integrity','sha512-bad','integrity'),('integrity','sha1-'+('x'*30),'sha512'),('resolved','https://secret@example.invalid/react.tgz','registry_scope'),('resolved','https://registry.npmjs.org/react/-/react-0.0.1.tgz','artifact_binding')]:
   with self.subTest(field=field,value=value):
    shutil.copyfile(ROOT/'terminal/web/package-lock.json',self.root/'terminal/web/package-lock.json');self.edit_lock(lambda v:v['packages']['node_modules/react'].update({field:value}))
    with self.assertRaisesRegex(InventoryError,code):build(self.root,SHA)
 def test_workspace_links_path_traversal_and_aliases_reject(self):
  for mutation in(lambda v:v['packages']['node_modules/react'].update(link=True),lambda v:v['packages'].update({'node_modules/../escape':copy.deepcopy(v['packages']['node_modules/react'])}),lambda v:v['packages']['node_modules/react'].update(name='different-name')):
   shutil.copyfile(ROOT/'terminal/web/package-lock.json',self.root/'terminal/web/package-lock.json');self.edit_lock(mutation)
   with self.assertRaises(InventoryError):build(self.root,SHA)
 def test_inputs_cannot_follow_symlinks_or_exceed_budget(self):
  p=self.root/'requirements-python.lock';p.unlink();p.symlink_to(ROOT/'requirements-python.lock')
  with self.assertRaisesRegex(InventoryError,'input_symlink'):build(self.root,SHA)
  p.unlink();shutil.copyfile(ROOT/'requirements-python.lock',p)
  with patch('scripts.build_offline_sbom.MAX_FILE',12),self.assertRaisesRegex(InventoryError,'input_budget'):build(self.root,SHA)
 def test_output_exclusive_private_and_symlink_refusal(self):
  path=self.root/'inventory.json';write_new(path,b'authored');self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)
  with self.assertRaises(FileExistsError):write_new(path,b'replacement')
  self.assertEqual(path.read_bytes(),b'authored');link=self.root/'symlink.json';link.symlink_to(path)
  with self.assertRaisesRegex(InventoryError,'output_symlink'):write_new(link,b'replacement')
  self.assertEqual(path.read_bytes(),b'authored')
 def test_strict_revision_and_component_budget(self):
  for value in('',SHA.upper(),None,'main'):
   with self.assertRaisesRegex(InventoryError,'source_commit'):build(self.root,value)
  with patch('scripts.build_offline_sbom.MAX_COMPONENTS',1),self.assertRaisesRegex(InventoryError,'component_budget'):build(self.root,SHA)
 def test_output_budget_is_enforced_without_writing(self):
  with patch('scripts.build_offline_sbom.MAX_OUTPUT',100),self.assertRaisesRegex(InventoryError,'output_budget'):build(self.root,SHA)
  self.assertFalse((self.root/'inventory.json').exists())
 def test_pyproject_identity_must_remain_valid_bom_text(self):
  p=self.root/'pyproject.toml';p.write_text('[project]\nname=["authored"]\nversion="1.0.0"\n[build-system]\nrequires=[]\n')
  with self.assertRaisesRegex(InventoryError,'pyproject_identity'):build(self.root,SHA)
 def test_declared_pin_and_lock_flags_cannot_use_implicit_coercion(self):
  self.edit_lock(lambda v:v['packages']['node_modules/react'].update(optional='false'))
  with self.assertRaisesRegex(InventoryError,'npm_flags'):build(self.root,SHA)

if __name__=='__main__':unittest.main(verbosity=2)
