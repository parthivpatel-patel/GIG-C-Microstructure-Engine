import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_initialization_manifest as policy

class Initialization(unittest.TestCase):
    def setUp(self):self.m=policy.load(Path(__file__).parent/'fixtures/market_seed_manifest.json')
    def assess(self,m=None):
        m=self.m if m is None else m
        return policy.validate(m,m['source_sha256'],m['snapshot_sha256'])
    def test_valid_seed(self):self.assertTrue(self.assess()['full_l3_eligible'])
    def test_observed_declaration_not_proof(self):
        self.m['origin']='observed';self.assertFalse(self.assess()['full_l3_eligible'])
    def test_witness_required(self):self.assertFalse(policy.validate(self.m)['full_l3_eligible'])
    def test_unknown(self):
        self.m['mode']='unknown';self.assertEqual(self.assess()['status'],'context_only')
    def test_incomplete_and_invalid(self):
        self.m['missing_data']=True;self.assertFalse(self.assess()['full_l3_eligible'])
        self.m['mode']='invalid';self.assertEqual(self.assess()['status'],'invalid')
    def test_empty(self):
        self.m.update(mode='complete',snapshot={'orders':[],'retired_references':[],'matches':[]},snapshot_sha256=None,session_stage=0,last_timestamp=None)
        self.m['event_boundary']['ordinal']=0;self.assertTrue(self.assess()['full_l3_eligible'])
    def test_mutations(self):
        variants=[('quantity0',lambda m:m['snapshot']['orders'][0].update(remaining=0)),('negative',lambda m:m['snapshot']['orders'][0].update(remaining=-1)),('overflow',lambda m:m['snapshot']['orders'][0].update(remaining=2**32)),('price',lambda m:m['snapshot']['orders'][0].update(price4=0)),('side',lambda m:m['snapshot']['orders'][0].update(side='?')),('instrument',lambda m:m['snapshot']['orders'][0].update(locate=99)),('priority',lambda m:m['snapshot']['orders'][1].update(priority=4)),('duplicate',lambda m:m['snapshot']['orders'][1].update(reference=11)),('boundary',lambda m:m['event_boundary'].update(payload_offset=4097)),('arrival',lambda m:m['snapshot']['orders'][0].update(arrival=100)),('date',lambda m:m.update(session_date='2025-02-29')),('digest',lambda m:m.update(snapshot_sha256='f'*64)),('sequence',lambda m:m.update(sequence_info={'unit':'exchange_sequence','next':100}))]
        for name,mutate in variants:
            with self.subTest(name=name):
                m=copy.deepcopy(self.m);mutate(m)
                with self.assertRaises(ValueError):self.assess(m)
    def test_permutation_and_independent_digest(self):
        expected=hashlib.sha256(json.dumps(self.m['snapshot'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(expected,self.m['snapshot_sha256'])
        self.m['snapshot']['orders'].reverse();self.assertEqual(self.assess()['snapshot_sha256'],expected)
    def test_missing_sequence_explicit(self):self.assertFalse(self.assess()['sequence_information_available'])
    def test_byte_cap_duplicate(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'manifest.json';p.write_bytes(b' '*(policy.MAX_BYTES+1))
            with self.assertRaises(ValueError):policy.load(p)
            p.write_text('{"mode":"a","mode":"b"}')
            with self.assertRaises(ValueError):policy.load(p)
    def test_pure_failure(self):
        self.m['snapshot']['orders'][0]['remaining']=0;before=copy.deepcopy(self.m)
        with self.assertRaises(ValueError):self.assess()
        self.assertEqual(self.m,before)

if __name__=='__main__':unittest.main()
