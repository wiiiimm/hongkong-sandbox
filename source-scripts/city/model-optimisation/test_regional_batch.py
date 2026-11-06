import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

import regional_batch as regional


class RegionalSafetyTests(unittest.TestCase):
    def test_committed_input_and_staged_replacement_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)
            git('init')
            path = root/'source.json'; path.write_text('original')
            git('add', 'source.json')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-m', 'fixture')
            tree = regional.FrozenTree(root)
            self.assertEqual(tree.read('source.json'), b'original')
            self.assertEqual(tree.hashes['source.json'], hashlib.sha256(b'original').hexdigest())
            path.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'unchanged committed'):
                tree.read('source.json')
            git('add', 'source.json'); path.write_text('original')
            with self.assertRaisesRegex(ValueError, 'Staged source change'):
                regional.FrozenTree(root).read('source.json')
            with self.assertRaisesRegex(ValueError, 'escapes'):
                tree.read('../outside')

    def test_import_closure_rejects_unpinned_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)
            git('init')
            (root/'renderer.js').write_text("import {x} from './helper.js';")
            (root/'helper.js').write_text('export const x=1;')
            git('add', '.')
            git('-c', 'user.name=Test', '-c', 'user.email=test@example.com', 'commit', '-m', 'fixture')
            tree = regional.FrozenTree(root)
            self.assertEqual(set(tree.modules('renderer.js')), {'renderer.js', 'helper.js'})
            (root/'helper.js').write_text('export const x=2;')
            with self.assertRaisesRegex(ValueError, 'unchanged committed'):
                tree.modules('renderer.js')

    def test_outputs_cannot_escape_private_staging(self):
        with self.assertRaisesRegex(ValueError, 'staging'):
            regional.private_directory(regional.ROOT/'3d-viewer/city/data')
        with self.assertRaisesRegex(ValueError, 'escapes'):
            regional.output_path('../outside')


if __name__ == '__main__':
    unittest.main()
