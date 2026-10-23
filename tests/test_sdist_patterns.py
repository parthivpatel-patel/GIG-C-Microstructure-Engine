"""Packaging-only regression; run with the pinned build-backend environment."""
import os
from pathlib import Path
import tempfile
import tomllib
import unittest
from scikit_build_core.build._file_processor import each_unignored_file

ROOT = Path(__file__).resolve().parents[1]


class SourceDistributionPatterns(unittest.TestCase):
    def inventory(self, includes):
        with tempfile.TemporaryDirectory() as temporary:
            previous = Path.cwd()
            try:
                os.chdir(temporary)
                Path('.gitignore').write_text('build/\n__pycache__/\n*.pyc\n')
                for name in ['CMakeLists.txt', 'README.md', 'src/engine.cpp',
                             'python/gig_microstructure/__init__.py',
                             'python/gig_microstructure/__pycache__/cache.pyc',
                             'build/private/README.md', 'build/private/CMakeLists.txt']:
                    path = Path(name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('synthetic packaging sentinel\n')
                return {str(p) for p in each_unignored_file(Path(), include=includes)}
            finally:
                os.chdir(previous)

    def test_negative_control_unanchored_basename_leaks(self):
        self.assertIn('build/private/README.md', self.inventory(['README.md']))

    def test_negative_control_recursive_override_leaks_cache(self):
        self.assertIn('python/gig_microstructure/__pycache__/cache.pyc',
                      self.inventory(['/python/**']))

    def test_current_patterns_preserve_sources_and_exclude_private_outputs(self):
        configuration = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        actual = self.inventory(configuration['tool']['scikit-build']['sdist']['include'])
        self.assertTrue({'CMakeLists.txt', 'README.md', 'src/engine.cpp',
                         'python/gig_microstructure/__init__.py'} <= actual)
        self.assertFalse(any(p.startswith('build/') or '__pycache__' in p for p in actual))


if __name__ == '__main__':
    unittest.main()
