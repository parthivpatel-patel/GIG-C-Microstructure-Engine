"""Selected-compiler metadata regression: fixtures plus actual-run manifest checks."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('engine_baseline', ROOT/'scripts/run_engine_baseline.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class SelectedCompilerTests(unittest.TestCase):
    def test_uses_selected_cache_compiler_with_spaces(self):
        for identity, version in [('GNU','14.2.0'),('Clang','19.1.7')]:
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as temp:
                build=Path(temp);compiler=build/'selected compiler'
                compiler.write_text('#!/bin/sh\nprintf "%s\\n" "'+identity+' '+version+' selected fixture"\n')
                compiler.chmod(0o700)
                metadata=build/'CMakeFiles/3.31.6/CMakeCXXCompiler.cmake';metadata.parent.mkdir(parents=True)
                metadata.write_text('set(CMAKE_CXX_COMPILER "'+str(compiler)+'")\nset(CMAKE_CXX_COMPILER_ID "'+identity+'")\nset(CMAKE_CXX_COMPILER_VERSION "'+version+'")\n')
                (build/'CMakeCache.txt').write_text('CMAKE_CACHE_MAJOR_VERSION:INTERNAL=3\nCMAKE_CACHE_MINOR_VERSION:INTERNAL=31\nCMAKE_CACHE_PATCH_VERSION:INTERNAL=6\n')
                got=baseline.compiler_metadata(build)
                self.assertEqual(got['compiler_executable'],str(compiler))
                self.assertEqual(got['compiler_id'],identity)
                self.assertEqual(got['compiler_version'],version)
                self.assertEqual(got['compiler'].strip(),identity+' '+version+' selected fixture')

    def test_missing_metadata_rejects_without_ambient_fallback(self):
        with tempfile.TemporaryDirectory() as temp:
            build=Path(temp);(build/'CMakeCache.txt').write_text('')
            with self.assertRaises((ValueError,FileNotFoundError)):
                baseline.compiler_metadata(build)


if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--manifest':
        doc=json.loads(Path(sys.argv[2]).read_text());expected=sys.argv[3];env=doc['environment']
        labels = {'GNU': ('gnu','gcc','g++'), 'Clang': ('clang',)}
        if not any(label in env['compiler'].lower() for label in labels[expected]):
            raise SystemExit('FAIL: selected '+expected+' build mislabeled as '+env['compiler'].splitlines()[0])
        if env.get('compiler_id')!=expected:raise SystemExit('FAIL: selected CMake compiler ID missing or incorrect')
        print('PASS: manifest compiler identity matches selected '+expected)
    else:
        unittest.main(verbosity=2)
