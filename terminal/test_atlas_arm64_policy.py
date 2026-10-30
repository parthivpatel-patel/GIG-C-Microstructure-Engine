"""Static manual-only candidate workflow checks;not ARM64 execution evidence."""
import unittest,ast,re,json
from pathlib import Path
class AtlasARM(unittest.TestCase):
 def test_candidate_workflow_is_free_owner_gated_manual_and_branch_scoped(self):
  s=Path('.github/workflows/atlas-native-arm64.yml').read_text()
  self.assertIn('\non:\n  workflow_dispatch:',s)
  for event in ('push','pull_request','schedule','workflow_run'):self.assertNotIn('\n  '+event+':',s)
  self.assertIn("inputs.free_usage_verified && github.ref == 'refs/heads/feat/atlas-final-release'",s);self.assertIn('default: false',s);self.assertIn('runs-on: ubuntu-24.04-arm',s);self.assertIn('test "$(uname -m)" = aarch64',s)
 def test_six_native_cases_canonical_checks_and_automated_terminal_coverage_remain(self):
  s=Path('.github/workflows/atlas-native-arm64.yml').read_text()
  for required in ('compiler: [gcc, clang]','preset: [debug, release, asan-ubsan]','canonical identity mismatch: ','terminal/tests/run_native_suite.py --expected-tests 274','terminal/tests/run_live_market_suite.py','terminal/tests/run_source_qualification_suite.py','GIG_SEC_ENABLED: \'0\'','GIG_ALPACA_ENABLED: \'0\'','persist-credentials: false'):
   self.assertIn(required,s)
  expected=ast.literal_eval(re.search(r'expected = (\{.*?\n\s*\})',s,re.S)[1])
  frozen=json.loads(Path('docs/evidence/continuous_engineering.json').read_text())['reused_full_native_matrix']['canonical_hashes']
  self.assertEqual(expected,frozen);self.assertEqual(len(expected),8)
