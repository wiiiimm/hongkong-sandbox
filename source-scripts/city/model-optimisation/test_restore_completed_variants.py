from pathlib import Path
import tempfile
import unittest

from restore_completed_variants import private_path


class RestorePathTests(unittest.TestCase):
    def test_only_immutable_private_cache_paths_are_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            good = 'source-scripts/city/model-optimisation/staging/batch/artifacts/hash.glb.gz'
            self.assertEqual(private_path(root, good), root/good)
            for bad in ['../other', '/etc/passwd', '3d-viewer/city/data/manifest.json',
                    'source-scripts/city/model-optimisation/staging/../../../../secret']:
                with self.assertRaises(ValueError):
                    private_path(root, bad)
            staging = root/'source-scripts/city/model-optimisation/staging'
            staging.mkdir(parents=True)
            (staging/'escape').symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                private_path(root, str((staging/'escape/private').relative_to(root)))
