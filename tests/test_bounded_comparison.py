import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_bounded_comparison as harness
import check_initialization_manifest as policy
import check_itch_l3_reference as ref
DRIVER=sys.argv.pop(1) if len(sys.argv)>1 else 'build/phase9-clean-debug/gig_itch_l3_reference_driver'

class BoundedComparison(unittest.TestCase):
    def setUp(self):
        self.m=policy.load(Path(__file__).parent/'fixtures/market_seed_manifest.json')
        self.events=[ref.execute(11,2,71),ref.replace(12,13,9,101),ref.system('E'),ref.system('C')]
        self.raw=harness.framed(self.events);self.bind()
    def bind(self):
        self.m['source_sha256']=hashlib.sha256(self.raw).hexdigest();self.m['capture_end']=self.m['event_boundary']['frame_offset']+len(self.raw)
    def compare(self,**kw):return harness.compare(self.m,self.raw,DRIVER,self.m['source_sha256'],self.m['snapshot_sha256'],**kw)
    def test_seeded(self):
        r=self.compare();self.assertEqual(r['status'],'reference_agreement');self.assertEqual((r['source_records'],r['accepted_records'],r['rejected_records']),(4,4,0));self.assertFalse(r['observed_validated'])
    def test_empty_complete(self):
        self.m.update(mode='complete',snapshot={'orders':[],'retired_references':[],'matches':[]},snapshot_sha256=None,session_stage=0,last_timestamp=None,capture_start=0,event_boundary=dict(frame_offset=0,payload_offset=2,ordinal=0))
        self.raw=harness.framed([ref.system('O'),ref.directory(),ref.directory(2),ref.add(11,10,100),*[ref.system(c) for c in 'SQMEC']]);self.bind()
        self.assertEqual(self.compare()['status'],'reference_agreement')
    def test_unknown_and_observed_blocked(self):
        self.m['mode']='unknown';self.assertEqual(self.compare()['status'],'initialization_blocked')
        self.m['mode']='seeded';self.m['origin']='observed';self.assertEqual(self.compare()['status'],'initialization_blocked')
        self.m['origin']='synthetic';self.m['last_timestamp']=None
        with self.assertRaises(ValueError):self.compare()
    def test_corrupt_snapshot(self):
        self.m['snapshot']['orders'][0]['remaining']=99
        with self.assertRaises(ValueError):self.compare()
    def test_missing_events(self):
        self.raw=harness.framed(self.events[1:])
        with self.assertRaises(ValueError):self.compare()
    def test_duplicate_and_unknown(self):
        for p in (ref.add(11,1,100),ref.execute(999,1,77)):
            self.raw=harness.framed([p]);self.bind();r=self.compare();self.assertEqual(r['status'],'accepted_prefix_agreement_with_rejection');self.assertEqual(r['rejection_reasons'],{'context':1})
    def test_unsupported(self):
        self.raw=harness.framed([b'?'+b'\0'*11]);self.bind();r=self.compare();self.assertEqual(r['unsupported_events'],1);self.assertEqual(r['accepted_records'],0)
    def test_budgets(self):
        for kwargs in (dict(max_records=1),dict(max_events=1),dict(max_bytes=1)):
            with self.assertRaises(ValueError):self.compare(**kwargs)
        self.assertEqual(self.compare(max_memory=4096)['status'],'candidate_error')
    def test_framing_truncation_and_trailing(self):
        for raw in (b'\0',b'\0\x02A',self.raw+b'?'):
            with self.assertRaises(ValueError):harness.frames(raw,512,512)
    def test_report_minimization_and_reproduce(self):
        r=self.compare(inject=True);self.assertEqual(r['status'],'divergence')
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'divergence.json';report=harness.write_divergence(path,r,self.m,self.raw,DRIVER,True)
            self.assertEqual(report['event_index'],0);self.assertEqual(report['event_type'],'E');self.assertIn('verified authored first-diverging prefix',report['minimization'])
            repro=subprocess.run(report['reproduction_argv'],capture_output=True,text=True)
            self.assertEqual(repro.returncode,3,repro.stderr);self.assertEqual(json.loads(repro.stdout)['first_difference'],r['first_difference'])
            with self.assertRaises(FileExistsError):harness.write_divergence(path,r,self.m,self.raw,DRIVER,True)
    def test_bounded_read(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'data';p.write_bytes(self.raw)
            self.assertEqual(harness.read_bounded(p,len(self.raw)),self.raw)
            for cap in (-1,0,len(self.raw)-1):
                with self.assertRaises(ValueError):harness.read_bounded(p,cap)
    def test_real_child_timeout(self):
        with self.assertRaises(TimeoutError):harness.run([sys.executable,'-c','import time;time.sleep(1)'],b'',timeout=.01)

if __name__=='__main__':unittest.main()
