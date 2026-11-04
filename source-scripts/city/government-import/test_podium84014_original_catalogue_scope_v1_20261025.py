import unittest
from copy import deepcopy
from run import read
from podium84014_original_catalogue_scope_v1_20261025 import BASELINE,verify_metadata

class Podium84014ScopeTests(unittest.TestCase):
    def setUp(self):self.models=read(BASELINE)['models']
    def rejects(self,change):
        models=deepcopy(self.models);change(models)
        with self.assertRaises(AssertionError):verify_metadata(models)
    def test_exact_private_entries_pass(self):self.assertTrue(verify_metadata(self.models))
    def test_review_metadata_does_not_change_rendering(self):
        for m in self.models:m.update(placementReviewed=True,publicationApproved=True)
        self.assertTrue(verify_metadata(self.models))
    def test_duplicate_uid_is_rejected(self):self.rejects(lambda m:m.append(deepcopy(m[0])))
    def test_wrong_source_hash_is_rejected(self):self.rejects(lambda m:m[0].update(sha256='0'*64))
    def test_root_translation_change_is_rejected(self):self.rejects(lambda m:m[0].update(rootTranslation=[-834499,0,816500]))
    def test_vertical_offset_is_rejected(self):self.rejects(lambda m:m[0].update(verticalPlacementOffsetHKPD=1))
    def test_embedded_geometry_is_rejected(self):self.rejects(lambda m:m[0].update(embeddedBuildingUids=['landsd/210816:0']))
    def test_suppression_is_rejected(self):self.rejects(lambda m:m[0].update(suppressesBuildingUids=['landsd/210816:0']))
    def test_wrong_support_is_rejected(self):self.rejects(lambda m:m[1]['supportDependencies'][0].update(uid='landsd/210816:0'))
    def test_missing_support_is_rejected(self):self.rejects(lambda m:m[1].pop('supportDependencies'))
    def test_wrong_csuid_is_rejected(self):self.rejects(lambda m:m[0].update(buildingCSUID='wrong'))
    def test_procedural_windows_are_rejected(self):self.rejects(lambda m:m[0].update(proceduralWindows=True))
    def test_unreviewed_material_change_is_rejected(self):self.rejects(lambda m:m[0].update(materialStyle='different'))

if __name__=='__main__':unittest.main()
