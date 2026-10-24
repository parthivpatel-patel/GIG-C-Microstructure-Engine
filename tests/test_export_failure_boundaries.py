"""Controlled filesystem failures; no claim of crash-safe or physical disk tests."""
import errno
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import gig_microstructure as gig
import python_fixtures as fixtures
from test_export_contracts import manifest


class ExportFailureBoundaries(unittest.TestCase):
    def exercise(self, operation):
        inputs = {'profile': b'1,2,1'}
        plan = gig.vwap(fixtures.plan_config(), ['1', '2', '1'], 'profile', '0')
        declared = manifest(inputs, {'gig.execution_schedule': '1.0'})
        before = declared.dumps()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'run'
            with patch('gig_microstructure.os.' + operation,
                       side_effect=OSError(errno.ENOSPC, 'authored disk-full fault')):
                with self.assertRaises(OSError) as failure:
                    gig.export_run(path, declared, {'output.json': plan}, input_artifacts=inputs)
            self.assertEqual(failure.exception.errno, errno.ENOSPC)
            self.assertTrue((path / 'manifest.incomplete.json').exists())
            self.assertFalse((path / 'manifest.json').exists())
            with self.assertRaises(gig.SchemaError):
                gig.verify_export(path)
            self.assertEqual(declared.dumps(), before)

    def test_input_fsync_failure(self):
        self.exercise('fsync')

    def test_manifest_link_failure(self):
        self.exercise('link')


if __name__ == '__main__': unittest.main()
