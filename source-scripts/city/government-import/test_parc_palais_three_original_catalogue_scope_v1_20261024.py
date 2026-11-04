import copy
import unittest
from parc_palais_three_original_catalogue_scope_v1_20261024 import PARENT,SOURCES,SUPPORTS,PARENT_SHA,PARENT_CSUID,verify_metadata,verify_support_scope


class ExactInstalledParentContract(unittest.TestCase):
    def setUp(self):
        self.models=[dict(uid=u,sha256=sha,rootTranslation=[-834500,0,816500],proceduralWindows=False,supportDependencies=[dict(uid=PARENT,state='installed',buildingCSUID=PARENT_CSUID,sha256=PARENT_SHA)])for u,sha in SOURCES.items()]
    def reject(self,change):
        models=copy.deepcopy(self.models);change(models[0])
        with self.assertRaises(AssertionError):verify_metadata(models)
    def test_exact_external_native_dependency(self):
        self.assertTrue(verify_metadata(self.models))
    def test_missing_support_rejected(self):self.reject(lambda m:m.pop('supportDependencies'))
    def test_other_support_rejected(self):self.reject(lambda m:m['supportDependencies'][0].update(uid='landsd/1:0'))
    def test_changed_parent_source_rejected(self):self.reject(lambda m:m['supportDependencies'][0].update(sha256='0'*64))
    def test_changed_parent_csuid_rejected(self):self.reject(lambda m:m['supportDependencies'][0].update(buildingCSUID='wrong'))
    def test_candidate_parent_rejected(self):self.reject(lambda m:m['supportDependencies'][0].update(state='candidate'))
    def test_source_or_pose_change_rejected(self):
        for update in [dict(sha256='0'*64),dict(rootTranslation=[-834500,1,816500]),dict(verticalPlacementOffsetHKPD=1),dict(scale=2)]:
            with self.subTest(update=update):self.reject(lambda m:m.update(update))
    def test_partial_suppressed_embedded_source_rejected(self):
        for key in ['partialSource','partialGeometry','sourceWorldBounds','suppressesBuildingUids','embeddedModels','retainedBasicSupportDependencies','renderGroups']:
            with self.subTest(key=key):self.reject(lambda m:m.update({key:['x']}))
    def test_other_sources_or_graph_rejected(self):
        for sources,supports in [({},SUPPORTS),(SOURCES,{}),(SOURCES,{u:u for u in SOURCES})]:
            with self.assertRaises(AssertionError):verify_support_scope(self.models,sources,supports)

    def test_missing_tower_rejected(self):
        with self.assertRaises(AssertionError):verify_metadata(self.models[:-1])
    def test_duplicate_tower_rejected(self):
        self.models[-1]=copy.deepcopy(self.models[0])
        with self.assertRaises(AssertionError):verify_metadata(self.models)
    def test_unreviewed_extra_source_rejected(self):
        self.models.append(dict(uid='landsd/1:0',sha256='0'*64))
        with self.assertRaises(AssertionError):verify_metadata(self.models)


if __name__=='__main__':unittest.main()
