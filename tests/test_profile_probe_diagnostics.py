"""Independent child-failure and diagnostic-rejection controls for the probe checker."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'profile_checker', Path(__file__).resolve().parents[1] / 'scripts/check_itch_profile_probe.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Diagnostics(unittest.TestCase):
    def check_failure(self, error):
        output = io.BytesIO()
        stream = io.TextIOWrapper(output, encoding='utf-8')
        with patch.object(sys, 'argv', ['checker', 'synthetic-child']), \
                patch.object(checker.subprocess, 'run', side_effect=error), \
                contextlib.redirect_stderr(stream):
            with self.assertRaises(type(error)):
                checker.main()
        stream.flush()
        self.assertEqual(output.getvalue(), error.stderr)

    def test_timeout_retains_completed_phases(self):
        self.check_failure(subprocess.TimeoutExpired('synthetic-child', 180,
                                                    stderr=b'completed phase evidence\n'))

    def test_child_failure_retains_sanitizer_diagnostic(self):
        self.check_failure(subprocess.CalledProcessError(1, 'synthetic-child',
                                                        stderr=b'AddressSanitizer failure evidence\n'))

    def check_rejected(self, trace):
        result = subprocess.CompletedProcess(['synthetic-child'], 0, b'{}', b'unexpected diagnostic\n')
        with patch.object(sys, 'argv', ['checker', 'synthetic-child']), \
                patch.object(checker.subprocess, 'run', return_value=result), \
                patch.dict(os.environ, {'GIG_PROFILE_TRACE': trace}):
            with self.assertRaises(AssertionError):
                checker.main()

    def test_unexpected_nontrace_output_rejected(self):
        self.check_rejected('0')

    def test_unexpected_trace_output_rejected(self):
        self.check_rejected('1')


if __name__ == '__main__':
    unittest.main()
