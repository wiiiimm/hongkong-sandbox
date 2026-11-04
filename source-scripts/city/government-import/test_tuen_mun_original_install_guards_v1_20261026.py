"""Preserve canonical installation fencing while binding the reviewed source schema."""
import ast
from pathlib import Path
import unittest
HERE=Path(__file__).parent

def functions(text):
    return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

class InstallationGuardTests(unittest.TestCase):
    def test_every_installer_function_preserved_after_exact_schema_alias(self):
        original=(HERE/'selected_original_retained_live_install_v8_20261023.py').read_text()
        original=original.replace("read(guard.REVIEW/'ROOT-PHYSICAL-REVIEW.json')['retainedNativeRegression']","read(stage.SOURCE/'ROOT-SOURCE-REVIEW.json')['retainedNativeRegression']")
        self.assertEqual(functions(original),functions((HERE/'tuen_mun_original_install_v1_20261026.py').read_text()))
    def test_publisher_lock_and_lease_functions_unchanged(self):
        old=functions((HERE/'selected_original_retained_guarded_publish_v7.py').read_text());new=functions((HERE/'tuen_mun_original_guarded_publish_v1_20261026.py').read_text())
        for name in ['main','assert_publication_idle','check']:self.assertEqual(old[name],new[name],name)
    def test_both_live_browsers_match_tested_private_origin_harness(self):
        tree=ast.parse((HERE/'tuen_mun_original_install_v1_20261026.py').read_text())
        for name in ['BROWSER','FOCUSED']:
            matches=[n.value.right.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
            self.assertEqual(matches,['ronsdale_three_live_browser_v15_20261026.mjs'])
    def test_qualified_stage_retains_canonical_replacement_dry_run(self):
        text=(HERE/'tuen_mun_original_qualified_stage_v2_20261026.py').read_text()
        self.assertIn("HERE.parent/'island-detail-integration/publish.py'",text)
        self.assertIn("assert read(dest)==read(source)",text)
        self.assertIn("assert set(resources)==set(physical['leaseResources'])",text)
        self.assertIn("verify_support_scope(cat['models'],sources,CONFIG['supportByUid'])",text)

if __name__=='__main__':unittest.main()
