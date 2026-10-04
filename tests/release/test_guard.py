import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('check_release', Path(__file__).resolve().parents[2]/'scripts/check_release.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ReleaseGuardTests(unittest.TestCase):
    def test_tag_push_cannot_publish(self):
        with self.assertRaisesRegex(ValueError, 'manual'):
            module.validate('1.0.0', True, 'tag', 'v1.0.0', 'hallamlab/SCARAB', event='push')

    def test_branch_can_build_without_publication(self):
        self.assertEqual(module.validate('1.0.0'), '1.0.0')

    def test_publication_requires_matching_tag_and_repository(self):
        for ref_type, ref_name, repository in [('branch','docs/user-guide','hallamlab/SCARAB'),
                                               ('tag','v0.0.1','hallamlab/SCARAB'),
                                               ('tag','v1.0.0','someone/SCARAB')]:
            with self.subTest(ref_type=ref_type, ref_name=ref_name, repository=repository), self.assertRaises(ValueError):
                module.validate('1.0.0', True, ref_type, ref_name, repository)
        self.assertEqual(module.validate('1.0.0', True, 'tag', 'v1.0.0', 'hallamlab/SCARAB'), '1.0.0')

    def test_invalid_version_is_rejected(self):
        for version in ('', '../1.0.0', '1.0.0; echo unsafe', 'latest'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                module.validate(version)
