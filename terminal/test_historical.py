import asyncio
import json
import sys
import unittest
from terminal.historical import bounded_native, run_authored_validation


class AuthoredNativeDiagnostics(unittest.IsolatedAsyncioTestCase):
    async def test_itch_restart(self):
        result = await run_authored_validation('itch')
        self.assertEqual(result['origin'], 'HISTORICAL_SYNTHETIC')
        self.assertFalse(result['observed_data_accessed'])
        self.assertTrue(result['native_report']['restart_verified'])

    async def test_lobster_unknown_state(self):
        result = await run_authored_validation('lobster')
        self.assertEqual(result['native_report']['rows'], 10)
        self.assertFalse(result['native_report']['full_l3_complete'])
        self.assertEqual(result['native_report']['initialization'], 'unknown')
        self.assertEqual(result['native_report']['unsupported'], 1)

    async def test_reject_arbitrary_profile(self):
        with self.assertRaises(ValueError):
            await run_authored_validation('../../private-data')

    async def test_output_limit(self):
        with self.assertRaisesRegex(ValueError, 'native_output_budget'):
            await bounded_native([sys.executable, '-c', 'import sys;sys.stdout.write("x"*400000)'])

    async def test_nonzero_child(self):
        with self.assertRaises(ValueError):
            await bounded_native([sys.executable, '-c', 'raise SystemExit(1)'])

    async def test_json_success(self):
        self.assertEqual(await bounded_native([sys.executable, '-c', 'print("{}")']), {})


if __name__ == '__main__':
    unittest.main()
