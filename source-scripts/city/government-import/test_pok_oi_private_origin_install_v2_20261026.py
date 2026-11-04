"""The live retry must preserve canonical guards and use the tested loopback origin."""
import ast
import unittest
from urllib.parse import urlparse
from run import HERE, ROOT, read


class PrivateOriginRetry(unittest.TestCase):
    def functions(self, name):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse((HERE/name).read_text()).body if isinstance(n,ast.FunctionDef)}

    def test_every_installer_function_remains_canonical(self):
        self.assertEqual(self.functions('pok_oi_original_install_v2_20261026.py'),
                         self.functions('independent_model_only_live_install_v1_20261024.py'))

    def test_every_publisher_function_remains_reviewed(self):
        self.assertEqual(self.functions('pok_oi_original_publish_v2_20261026.py'),
                         self.functions('pok_oi_original_publish_v1_20261026.py'))

    def test_both_live_browser_paths_support_explicit_origin(self):
        tree=ast.parse((HERE/'pok_oi_original_install_v2_20261026.py').read_text())
        assignments={}
        for n in tree.body:
            if isinstance(n,ast.Assign):
                for t in n.targets:
                    if isinstance(t,ast.Name):assignments[t.id]=ast.unparse(n.value)
        for name in ['BROWSER','FOCUSED']:
            self.assertIn('ronsdale_three_live_browser_v13_20261025.mjs',assignments[name])
        config=read(HERE/'accepted/government-xl-pok-oi-original-v1-qualified-stage-v1-20261026/live-browser-config.json')
        url=urlparse(config['viewerURL']);self.assertEqual((url.hostname,url.port),('127.0.0.1',4177))

    def test_retry_is_separate_from_archived_failed_attempt(self):
        text=(HERE/'pok_oi_original_publish_v2_20261026.py').read_text()
        self.assertIn("'-original-installed-v2-'",text)
        folder=ROOT/'docs/astra-city/government-import/government-xl-pok-oi-original-v1-original-installed-v1-20261026'
        failure=read(folder/'failure-recovery.json')
        self.assertTrue(failure['allPublicDestinationsRestored'])
        self.assertFalse(failure['derivedInstalledReviewHistoryRetained'])
        self.assertEqual(failure['rollbackErrors'],[])
        self.assertFalse((folder/'result.json').exists())


if __name__=='__main__':
    unittest.main()
