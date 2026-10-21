"""Adversarial export/verification reference tests against public installed interfaces."""
from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import unittest
import gig_microstructure as gig
import python_fixtures as f


def manifest(inputs, schemas, run_id='python-simulation-run'):
    info = gig.native_build_info()
    data = {'run_id': run_id,
      'code': {'commit_sha': 'c'*40, 'dirty': True, 'source_tree_sha256': 'a'*64},
      'build': {'compiler': info['compiler'], 'flags': info['config_flags'],
                'architecture': 'x86_64', 'os': 'synthetic-test', 'dependencies': {'pybind11': info['pybind11']}},
      'inputs': [{'identity': name, 'sha256': hashlib.sha256(value).hexdigest(),
                  'license_reference': 'synthetic-fixture:no-external-data', 'origin': 'synthetic',
                  'source': 'export-contract-test', 'transformation': 'generated', 'local_file': None}
                 for name, value in inputs.items()],
      'parents': [], 'schema_versions': schemas, 'instrument_rules': [f.rules()],
      'policies': {'ordering': 'capture ordinal', 'sequence': 'strict', 'recovery': 'complete snapshot',
                   'clock': 'declared synthetic UTC', 'precision': 'nanoseconds'},
      'parameters': {}, 'seeds': ['0'],
      'coverage': {'start_ns': f.known('0'), 'end_ns': f.known('1000'), 'records': '1'},
      'outputs': [], 'errors': [], 'complete': True}
    return gig.run_manifest(data)


def rewrite_output(path, transform):
    """Keep file hashes self-consistent while injecting a semantic contradiction."""
    doc = gig.loads((path/'output.json').read_bytes()).to_dict()
    transform(doc)
    encoded = gig.dumps(doc).encode()
    (path/'output.json').write_bytes(encoded)
    m = gig.loads((path/'manifest.json').read_bytes()).to_dict()
    m['data']['outputs'][0]['sha256'] = hashlib.sha256(encoded).hexdigest()
    (path/'manifest.json').write_text(gig.dumps(m))


class ExportReferenceTests(unittest.TestCase):
    def test_missing_vwap_profile_rejects_before_writing(self):
        inputs = {'unrelated-input': b'x'}
        plan = gig.vwap(f.plan_config(), ['1','2','1'], 'missing-profile', '0')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'run'
            with self.assertRaisesRegex(gig.SchemaError, 'export.profile_artifact_not_retained'):
                gig.export_run(path, manifest(inputs, {'gig.execution_schedule':'1.0'}),
                               {'output.json':plan}, input_artifacts=inputs)
            self.assertFalse(path.exists())

    def test_verifier_checks_profile_references_read_only(self):
        inputs = {'profile': b'1,2,1'}
        plan = gig.vwap(f.plan_config(), ['1','2','1'], 'profile', '0')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'run'
            gig.export_run(path, manifest(inputs, {'gig.execution_schedule':'1.0'}),
                           {'output.json':plan}, input_artifacts=inputs)
            self.assertTrue(gig.verify_export(path)['data']['complete'])
            rewrite_output(path, lambda doc: doc['data']['profile'].update(value='missing-profile'))
            before = {str(p):p.read_bytes() for p in path.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(gig.SchemaError, 'export.profile_artifact_not_retained'):
                gig.verify_export(path)
            self.assertEqual(before, {str(p):p.read_bytes() for p in path.rglob('*') if p.is_file()})

    def test_pov_volume_and_oracle_profile_references(self):
        for oracle in [False, True]:
            inputs = {'profile': b'weights'}
            plan = gig.vwap(f.plan_config(), ['1','2','1'], 'profile', '1000' if oracle else '0', oracle=oracle)
            m = manifest(inputs, {'gig.execution_schedule':'1.0'}).to_dict()
            m['data']['parameters']['oracle_benchmark'] = oracle
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp)/'run'
                gig.export_run(path, gig.run_manifest(m['data']), {'output.json':plan}, input_artifacts=inputs)
                self.assertTrue(gig.verify_export(path)['data']['complete'])
        plan = gig.pov(f.plan_config(), [{'available_at':'1','lots':'100','source_artifact':'volume','ordinal':'1'}], '1','10')
        for present in [False, True]:
            inputs = {'volume' if present else 'unrelated-input': b'100 lots at time1'}
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp)/'run'
                if present:
                    gig.export_run(path, manifest(inputs, {'gig.execution_schedule':'1.0'}), {'output.json':plan}, input_artifacts=inputs)
                    self.assertTrue(gig.verify_export(path)['data']['complete'])
                else:
                    with self.assertRaisesRegex(gig.SchemaError, 'export.volume_artifact_not_retained'):
                        gig.export_run(path, manifest(inputs, {'gig.execution_schedule':'1.0'}), {'output.json':plan}, input_artifacts=inputs)
                    self.assertFalse(path.exists())
        # TWAP has no profile dependency; absence must not be invented as a required input.
        with tempfile.TemporaryDirectory() as temp:
            inputs = {'unrelated-input': b'x'};path=Path(temp)/'run'
            gig.export_run(path, manifest(inputs, {'gig.execution_schedule':'1.0'}), {'output.json':gig.twap(f.plan_config())}, input_artifacts=inputs)
            self.assertTrue(gig.verify_export(path)['data']['complete'])


class ExportDigestTests(unittest.TestCase):
    def event_document(self, kind, digest):
        doc = f.event()
        provenance = doc['data']['metadata']['provenance']
        provenance['dataset']['value']['sha256'] = f.known(hashlib.sha256(b'dataset').hexdigest())
        provenance['parents'] = [{'identity':'parent-artifact', 'sha256':f.known(hashlib.sha256(b'parent').hexdigest())}]
        field = provenance['dataset']['value'] if kind == 'dataset' else provenance['parents'][0]
        field['sha256'] = digest
        return gig.event(doc, f.rules())

    def test_export_rejects_known_digest_contradictions_before_writing(self):
        inputs = {'python-synthetic': b'dataset', 'parent-artifact': b'parent'}
        for kind in ['dataset', 'parent']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                path = Path(temp)/'run'
                with self.assertRaisesRegex(gig.SchemaError, 'export.'+kind+'_digest_mismatch'):
                    gig.export_run(path, manifest(inputs, {'gig.event':'1.0'}),
                                   {'output.json':self.event_document(kind, f.known('0'*64))}, input_artifacts=inputs)
                self.assertFalse(path.exists())

    def test_verify_rejects_self_consistently_rehashed_contradictions(self):
        inputs = {'python-synthetic': b'dataset', 'parent-artifact': b'parent'}
        for kind in ['dataset', 'parent']:
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                path = Path(temp)/'run'
                digest = hashlib.sha256(inputs['python-synthetic' if kind=='dataset' else 'parent-artifact']).hexdigest()
                doc = self.event_document(kind, f.known(digest))
                gig.export_run(path, manifest(inputs, {'gig.event':'1.0'}), {'output.json':doc}, input_artifacts=inputs)
                self.assertTrue(gig.verify_export(path)['data']['complete'])
                def contradict(value):
                    provenance = value['data']['metadata']['provenance']
                    field = provenance['dataset']['value'] if kind=='dataset' else provenance['parents'][0]
                    field['sha256'] = f.known('0'*64)
                rewrite_output(path, contradict)
                before = {str(p):p.read_bytes() for p in path.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(gig.SchemaError, 'export.'+kind+'_digest_mismatch'):
                    gig.verify_export(path)
                self.assertEqual(before, {str(p):p.read_bytes() for p in path.rglob('*') if p.is_file()})

    def test_matching_and_unavailable_digests_preserved(self):
        inputs = {'python-synthetic': b'dataset', 'parent-artifact': b'parent'}
        for kind in ['dataset','parent']:
            for digest in [f.missing(), f.known(hashlib.sha256(inputs['python-synthetic' if kind=='dataset' else 'parent-artifact']).hexdigest())]:
                with self.subTest(kind=kind, digest=digest), tempfile.TemporaryDirectory() as temp:
                    path = Path(temp)/'run';doc=self.event_document(kind, digest)
                    gig.export_run(path, manifest(inputs, {'gig.event':'1.0'}), {'output.json':doc}, input_artifacts=inputs)
                    self.assertTrue(gig.verify_export(path)['data']['complete'])
                    self.assertEqual(gig.loads((path/'output.json').read_bytes()).to_dict(), doc.to_dict())


if __name__ == '__main__':
    unittest.main(verbosity=2)
