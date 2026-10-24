"""Adversarial metadata/graph checks for the supported model-only route."""
from copy import deepcopy
import unittest
from original_supported_model_only_contract_v1_20261025 import verify_metadata


class SupportedModelOnlyContractTests(unittest.TestCase):
    def setUp(self):
        self.sources = {'landsd/1:0':'a', 'landsd/2:0':'b'}
        self.supports = {'landsd/1:0':'landsd/2:0'}
        self.original = {u:dict(uid=u,sha256=s,buildingCSUID='cs'+s,rootTranslation=[-834500,0,816500],triangles=5,asset='cache/'+s) for u,s in self.sources.items()}
        self.models = [dict(**deepcopy(e),priority='landmark',proceduralWindows=False) for e in self.original.values()]
        for m in self.models:m['asset']='assets/'+m['sha256']+'.glb.gz'
        self.models[0]['supportDependencies']=[dict(uid='landsd/2:0',state='installed',buildingCSUID='csb',sha256='b')]
    def check(self):return verify_metadata(self.models,self.sources,self.supports,self.original)
    def test_exact_entries_pass(self):self.assertTrue(self.check())
    def test_review_metadata_does_not_change_rendering(self):
        self.models[0].update(placementReviewed=True,publicationApproved=True,placementReview='review')
        self.assertTrue(self.check())
    def test_geometry_and_placement_edits_fail(self):
        for key,value in [('verticalPlacementOffsetHKPD',1),('scale',2),('rotation',[1,0,0]),('triangles',6),('worldBounds',[[0,0,0],[1,1,1]])]:
            with self.subTest(key=key):
                before=deepcopy(self.models);self.models[0][key]=value
                with self.assertRaises(AssertionError):self.check()
                self.models=before
    def test_missing_dependency_fails(self):
        self.models[0].pop('supportDependencies')
        with self.assertRaises(AssertionError):self.check()
    def test_wrong_parent_hash_fails(self):
        self.models[0]['supportDependencies'][0]['sha256']='wrong'
        with self.assertRaises(AssertionError):self.check()
    def test_cycle_fails(self):
        self.supports['landsd/2:0']='landsd/1:0'
        self.models[1]['supportDependencies']=[dict(uid='landsd/1:0',state='installed',buildingCSUID='csa',sha256='a')]
        with self.assertRaises(AssertionError):self.check()
    def test_parent_cannot_be_external(self):
        self.supports['landsd/1:0']='landsd/3:0'
        with self.assertRaises(AssertionError):self.check()
    def test_suppression_or_basic_support_credit_fails(self):
        for key,value in [('suppressesBuildingUids',['landsd/3:0']),('retainedBasicSupportDependencies',[{'uid':'landsd/3:0'}])]:
            with self.subTest(key=key):
                before=deepcopy(self.models);self.models[0][key]=value
                with self.assertRaises(AssertionError):self.check()
                self.models=before
    def test_changed_source_colour_or_material_fails(self):
        self.models[0]['material']='replacement'
        with self.assertRaises(AssertionError):self.check()
    def test_duplicate_uid_fails(self):
        self.models.append(deepcopy(self.models[0]))
        with self.assertRaises(AssertionError):self.check()
    def test_standalone_contract_is_not_relaxed(self):
        self.supports={}
        self.models[0].pop('supportDependencies')
        with self.assertRaises(AssertionError):self.check()


if __name__=='__main__':unittest.main()
