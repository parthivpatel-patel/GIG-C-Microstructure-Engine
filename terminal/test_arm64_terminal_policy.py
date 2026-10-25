"""Offline manual workflow policy checks; not evidence that ARM64 executed."""
import ast,re,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Policy(unittest.TestCase):
    def setUp(self):self.text=(ROOT/'.github/workflows/native-arm64.yml').read_text()
    def test_manual_free_usage_and_feature_guard_preserved(self):
        self.assertIn('\non:\n  workflow_dispatch:',self.text)
        for event in ('push','pull_request','schedule'):self.assertNotIn('\n  '+event+':',self.text)
        self.assertIn("inputs.free_usage_verified && github.ref == 'refs/heads/feat/bootstrap-cpp20-engine'",self.text)
        self.assertIn('runs-on: ubuntu-24.04-arm',self.text);self.assertIn('default: false',self.text)
    def test_terminal_step_only_gcc_release_with_exact_count_and_live_disabled(self):
        step=self.text.split('      - name: Native-backed terminal fixture qualification',1)[1].split('      - name:',1)[0]
        self.assertIn("matrix.compiler == 'gcc' && matrix.preset == 'release'",step)
        self.assertIn("GIG_LIVE_ENABLED: '0'",step);self.assertIn("GIG_COINBASE_ENABLED: '0'",step)
        self.assertIn('GIG_TERMINAL_NATIVE_BUILD: ${{ github.workspace }}/build/release',step)
        self.assertIn('--expected-tests 224',step);self.assertIn('terminal/server/requirements.txt',step)
        self.assertNotIn('workflow_dispatch',step);self.assertNotIn('gh workflow',step)
    def test_existing_six_matrix_and_canonical_guards_unchanged(self):
        self.assertIn('compiler: [gcc, clang]',self.text);self.assertIn('preset: [debug, release, asan-ubsan]',self.text)
        self.assertIn('(158 if python_enabled else 155)',self.text)
        expected=ast.literal_eval(re.search(r'expected = (\{.*?\n\s*\})',self.text,re.S)[1])
        frozen=json.loads((ROOT/'docs/evidence/continuous_engineering.json').read_text())['reused_full_native_matrix']['canonical_hashes']
        self.assertEqual(expected,frozen)
        self.assertEqual(len(expected),8)
        self.assertEqual(expected['itch.independent_reference'],'142217bb7c7a51dbcbc7d54108247d7bec62575cf036293425b40cd205061b3e')

if __name__=='__main__':unittest.main()
