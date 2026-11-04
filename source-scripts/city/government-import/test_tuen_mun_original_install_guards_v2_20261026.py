import unittest
from test_tuen_mun_original_install_guards_v1_20261026 import HERE,functions

class CorrectedAdapterGuardTests(unittest.TestCase):
    def test_publisher_every_function_unchanged(self):
        self.assertEqual(functions((HERE/'tuen_mun_original_guarded_publish_v1_20261026.py').read_text()),functions((HERE/'tuen_mun_original_guarded_publish_v2_20261026.py').read_text()))
    def test_installer_locks_rollback_cli_and_browser_checks_preserved(self):
        old=functions((HERE/'tuen_mun_original_install_v1_20261026.py').read_text());new=functions((HERE/'tuen_mun_original_install_v2_20261026.py').read_text())
        self.assertEqual(set(old),set(new))
        for k in set(old)-{'owned','load'}:self.assertEqual(old[k],new[k],k)
    def test_owned_only_changes_exact_tested_terrain_assertion(self):
        text=(HERE/'tuen_mun_original_install_v2_20261026.py').read_text()
        text=text.replace("assert set(read(ROOT/'3d-viewer'/planned[0]['destination'])['meta']['targetUids'])==set(replacement['retainedUids'])|{'landsd/280350:0'}\n   assert read(ROOT/'3d-viewer'/planned[0]['destination'])==read(ROOT/planned[0]['source']), 'Require exactly the tested whole terrain, not expanded routing metadata'","assert set(read(ROOT/'3d-viewer'/planned[0]['destination'])['meta']['targetUids'])==set(replacement['retainedUids'])|set(stage.SOURCES)")
        self.assertEqual(functions(text)['owned'],functions((HERE/'tuen_mun_original_install_v1_20261026.py').read_text())['owned'])

if __name__=='__main__':unittest.main()
