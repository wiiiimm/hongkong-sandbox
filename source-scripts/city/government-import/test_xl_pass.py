"""The bounded XL pass selects uninstalled, uniquely matched forms without changing order."""
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('xl',Path(__file__).with_name('xl-pass.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class XLPassTests(unittest.TestCase):
    def test_selection_skips_unmatched_installed_and_duplicate_viewer_forms(self):
        inventory=[('a','A',None),('b','B','landsd/1:0'),('c','C','landsd/2:0'),('d','D','landsd/2:0'),('e','E','landsd/3:0')]
        self.assertEqual(module.select_entries(inventory,{'landsd/1:0':{}},2),[inventory[2],inventory[4]])
    def test_selection_requires_the_full_authorised_count(self):
        with self.assertRaises(ValueError):module.select_entries([('a','A','landsd/1:0')],{},2)
    def test_clean_original_still_uses_scripted_acceptance(self):
        entry={'uid':'landsd/1:0','buildingCSUID':'one','objectId':1,'recordedBaseHeight':2,'recordedTopHeight':22,'sha256':'hash','overlapOfSmallerFootprint':1,'footprintCentroidDistanceMetres':.5}
        native={'model':{'candidate':entry,'state':'packed-needs-placement-review'}}
        source={'building':{'uid':'landsd/1:0','buildingCSUID':'one','objectId':1,'baseHeightHKPD':2,'topHeightHKPD':22}}
        self.assertEqual(module.initial_reason(native,source,None,None),('in-process',[]))

if __name__=='__main__':unittest.main()
