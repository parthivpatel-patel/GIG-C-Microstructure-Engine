"""Independent adversarial controls for readiness refusal and strict envelopes."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('readiness', ROOT/'scripts/check_observed_l3_readiness.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Readiness(unittest.TestCase):
    def fixture(self):
        return {'schema':m.SCHEMA,'origin':'observed','initialization':'unknown',
                'gates':dict.fromkeys(m.GATES,'missing')}

    def test_missing_facts_block(self):
        r=m.evaluate(self.fixture());self.assertFalse(r['observed_certified']);self.assertEqual(r['assessment'],'BLOCKED')

    def test_all_forged_claims_still_block(self):
        f=self.fixture();f['gates']=dict.fromkeys(m.GATES,'claimed');f['initialization']='complete_seed_claim'
        r=m.evaluate(f);self.assertFalse(r['observed_certified']);self.assertIn('implementation.observed_adapter',r['reasons'])

    def test_synthetic_never_relabelled(self):
        f=self.fixture();f['origin']='synthetic';self.assertIn('observed_origin_not_established',m.evaluate(f)['reasons'])

    def test_missing_and_unknown_gates_rejected(self):
        for key in m.GATES:
            f=self.fixture();del f['gates'][key]
            with self.assertRaises(ValueError):m.evaluate(f)
        f=self.fixture();f['gates']['production_ready']='claimed'
        with self.assertRaises(ValueError):m.evaluate(f)

    def test_boolean_strings_and_numbers_not_coerced(self):
        for value in (True,1,'verified','PASS',None,[],{}):
            f=self.fixture();f['gates']['complete_capture']=value
            with self.assertRaises(ValueError):m.evaluate(f)

    def test_invalid_envelopes(self):
        for field,value in [('schema','future'),('origin','OBSERVED'),('initialization','market_open')]:
            f=self.fixture();f[field]=value
            with self.assertRaises(ValueError):m.evaluate(f)
        for f in ({},[],None):
            with self.assertRaises(ValueError):m.evaluate(f)

    def test_actual_prefix_is_blocked(self):
        f=json.loads((ROOT/'docs/NASDAQ_SECOND_PREFIX_EVIDENCE.json').read_text())
        r=m.evaluate(m.from_prefix(f));self.assertFalse(r['observed_certified']);self.assertIn('initial_state_not_established',r['reasons'])

    def test_cli_exit_refuses_certification(self):
        r=subprocess.run([sys.executable,str(ROOT/'scripts/check_observed_l3_readiness.py'),'--from-second-prefix',str(ROOT/'docs/NASDAQ_SECOND_PREFIX_EVIDENCE.json')],capture_output=True,text=True)
        self.assertEqual(r.returncode,1);self.assertEqual(json.loads(r.stdout)['assessment'],'BLOCKED')

    def test_report_does_not_expose_mutable_global_state(self):
        report=m.evaluate(self.fixture());report['implementation_capabilities']['observed_adapter']=True
        self.assertFalse(m.CAPABILITIES['observed_adapter'])

    def test_contradictory_completion_claims_never_enable_observed_books(self):
        # A complete-state claim conflicts with absent/failed initialization evidence.
        # Refusal, rather than certification, is the independently declared oracle.
        for initial in ('unknown', 'incomplete', 'empty_boundary_claim', 'complete_seed_claim'):
            for origin in ('observed', 'synthetic', 'unknown'):
                for gate in m.GATES:
                    f=self.fixture();f['origin']=origin;f['initialization']=initial
                    f['gates']=dict.fromkeys(m.GATES,'claimed');f['gates'][gate]='failed'
                    out=m.evaluate(f)
                    self.assertEqual(out['assessment'],'BLOCKED');self.assertIs(out['observed_certified'],False)
                    self.assertIn('evidence.'+gate+'.failed',out['reasons'])

    def test_bounded_adversarial_claim_oracle(self):
        import random
        rng=random.Random(559173)
        for _ in range(2048):
            f=self.fixture();f['origin']=rng.choice(('observed','synthetic','unknown'))
            f['initialization']=rng.choice(('unknown','incomplete','empty_boundary_claim','complete_seed_claim'))
            f['gates']={gate:rng.choice(('missing','partial','claimed','failed')) for gate in m.GATES}
            before=copy.deepcopy(f);out=m.evaluate(f)
            self.assertEqual(f,before);self.assertIs(out['observed_certified'],False)
            self.assertEqual(out['assessment'],'BLOCKED');self.assertEqual(out,m.evaluate(f))

    def test_oversize_and_malformed_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json'
            for raw in (b'x'*65537,b'{bad',b'{"schema":1,"schema":2}'):
                p.write_bytes(raw)
                with self.assertRaises(ValueError):m.bounded_json(p)


if __name__=='__main__':
    if len(sys.argv)>1:
        driver=sys.argv.pop(1)
        analysis=sys.argv.pop(1) if len(sys.argv)>1 else None
        subprocess.run([driver],check=True)
        subprocess.run([sys.executable,str(ROOT/'scripts/check_lobster_reference.py'),driver],check=True)
        if analysis:subprocess.run([sys.executable,str(ROOT/'scripts/check_lobster_reconstruction.py'),analysis],check=True)
    unittest.main()
