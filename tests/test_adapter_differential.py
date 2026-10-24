import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_adapter_differential as differential


class Diagnostics(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'report.json'
        r = differential.ref
        self.case = differential.case([r.system('O'), r.directory(), r.directory(2), r.add(11)])
        self.document = dict(schema='gig.book_divergence.v1', origin='synthetic',
                             dataset='adapter-differential-v1', negative_control=True,
                             fixture_sha256=self.case['digest'], fixture=dict(flags=0,tick=[1,100],lot=[1,1],
                             payloads_hex=[p.hex() for p in self.case['payloads']]))

    def load(self):
        self.path.write_text(json.dumps(self.document))
        return differential.load(self.path)

    def test_roundtrip(self):
        self.assertEqual(self.load()[1]['digest'], self.case['digest'])

    def test_digest(self):
        self.document['fixture_sha256'] = '0'*64
        with self.assertRaises(ValueError): self.load()

    def test_observed_refused(self):
        self.document['origin'] = 'observed'
        with self.assertRaises(ValueError): self.load()

    def test_oversize(self):
        self.path.write_bytes(b' '*(differential.MAX_INPUT+1))
        with self.assertRaises(ValueError): differential.load(self.path)

    def test_duplicate_fields(self):
        self.path.write_text('{"schema":"a","schema":"b"}')
        with self.assertRaises(ValueError): differential.load(self.path)

    def test_summary_type_rejected(self):
        raw = differential.raw_bytes(self.case['payloads'])
        summary = dict(records=4, accepted=4, native=1, rejected=0, bytes=len(raw),
                       error=0,input_complete=1,l3_complete=False,publication_eligible=False,
                       dataset_hex='adapter-differential-v1'.encode().hex(),
                       input_sha256=differential.hashlib.sha256(raw).hexdigest())
        result = dict(events=copy.deepcopy(self.case['expected']),summary=summary)
        with patch.object(differential,'run',return_value=result):
            self.assertEqual(differential.compare('unused',self.case,7)[1], 'summary.input_complete')

    def test_execution_failure_report(self):
        with patch.object(differential,'run',side_effect=ValueError('authored candidate failure')):
            mismatch = differential.compare('unused',self.case,7)
        self.assertIsNone(mismatch[0]); self.assertEqual(mismatch[1], 'candidate.execution')
        report = differential.report('unused',self.case,mismatch,'adapter-differential-v1',7,False,self.path)
        self.assertIsNone(report['event_index']); self.assertIsNone(report['event_type'])
        self.assertIn('original bounded fixture',report['minimization'])

    def test_no_overwrite(self):
        mismatch=(None,'candidate.execution',{}, {},None)
        differential.report('unused',self.case,mismatch,'adapter-differential-v1',7,False,self.path)
        before=self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            differential.report('unused',self.case,mismatch,'adapter-differential-v1',7,False,self.path)
        self.assertEqual(self.path.read_bytes(),before)


if __name__=='__main__': unittest.main()
