import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verifier', ROOT / 'scripts/verify_reproduction.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class Receipts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.document = json.loads((ROOT / 'docs/evidence/reproduction_manifest.json').read_text())
        self.document['artifacts'] = [x for x in self.document['artifacts'] if x['path'] == 'tests.xml']
        source = Path(os.environ.get('GIG_REPRO_ARTIFACTS', ROOT / 'build/four-phase/phase1'))
        (self.root / 'tests.xml').write_bytes((source / 'tests.xml').read_bytes())
        self.manifest = self.root / 'manifest.json'

    def run_verify(self):
        self.manifest.write_text(json.dumps(self.document))
        return verifier.verify(self.manifest, self.root)

    def test_valid(self):
        self.assertEqual(self.run_verify()['tests'], 157)

    def test_hash(self):
        self.document['artifacts'][0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError): self.run_verify()

    def test_path(self):
        self.document['artifacts'][0]['path'] = '../tests.xml'
        with self.assertRaises(ValueError): self.run_verify()

    def test_parent_symlink(self):
        (self.root / 'real').mkdir()
        (self.root / 'real' / 'tests.xml').write_bytes((self.root / 'tests.xml').read_bytes())
        (self.root / 'alias').symlink_to(self.root / 'real', target_is_directory=True)
        self.document['artifacts'][0]['path'] = 'alias/tests.xml'
        self.document['reproducible']['junit'] = 'alias/tests.xml'
        with self.assertRaises(ValueError): self.run_verify()

    def test_leaf_symlink(self):
        (self.root / 'linked.xml').symlink_to(self.root / 'tests.xml')
        self.document['artifacts'][0]['path'] = 'linked.xml'
        self.document['reproducible']['junit'] = 'linked.xml'
        with self.assertRaises(ValueError): self.run_verify()

    def test_aggregate_budget_before_hashing(self):
        from unittest.mock import patch
        items = []
        for index in range(3):
            path = self.root / f'large-{index}.bin'
            with path.open('wb') as stream:
                stream.truncate(64 * 1024 * 1024)  # Sparse, authored local input.
            items.append({'path': path.name, 'sha256': '0' * 64})
        self.document['artifacts'] = items
        with patch.object(verifier.hashlib, 'sha256', side_effect=AssertionError('hash must not run')):
            with self.assertRaisesRegex(ValueError, 'aggregate artifact budget'):
                self.run_verify()

    def test_artifact_count_budget(self):
        self.document['artifacts'] *= 257
        with self.assertRaisesRegex(ValueError, 'artifact count budget'):
            self.run_verify()

    def test_count(self):
        self.document['reproducible']['ctest_counts']['tests'] -= 1
        with self.assertRaises(ValueError): self.run_verify()

    def test_canonical(self):
        key = next(iter(self.document['reproducible']['canonical_sha256']))
        self.document['reproducible']['canonical_sha256'][key] = '0' * 64
        with self.assertRaises(ValueError): self.run_verify()

    def test_dtd(self):
        xml = b'<!DOCTYPE testsuite [<!ENTITY x "bad">]><testsuite/>'
        (self.root / 'tests.xml').write_bytes(xml)
        self.document['artifacts'][0]['sha256'] = hashlib.sha256(xml).hexdigest()
        with self.assertRaises(ValueError): self.run_verify()


if __name__ == '__main__': unittest.main()
