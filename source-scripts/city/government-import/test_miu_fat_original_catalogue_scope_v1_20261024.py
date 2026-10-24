"""The exact gateway nomination cannot bypass source or native support guards."""
import copy,unittest
from miu_fat_original_catalogue_scope_v1_20261024 import SOURCES,PRIMARY,HALL,GATE,verify_metadata

class ScopedGatewayTests(unittest.TestCase):
    def setUp(self):
        self.models=[dict(uid=u,sha256=h,buildingCSUID='parent-csuid'if u==PRIMARY else u,rootTranslation=[-834500,0,816500],proceduralWindows=False)for u,h in SOURCES.items()]
        self.by={m['uid']:m for m in self.models};self.by[PRIMARY]['suppressesBuildingUids']=[GATE]
        self.by[HALL]['supportDependencies']=[dict(uid=PRIMARY,state='installed',buildingCSUID='parent-csuid',sha256=SOURCES[PRIMARY])]
        self.coverage=dict(sourceSHA256=SOURCES[PRIMARY],secondaryUid=GATE,requiredOriginalAssembly=SOURCES.copy(),coverageApprovedForStagedValidation=True,stagedProposal=dict(uid=PRIMARY,suppressesBuildingUids=[GATE]),completeFourWorldCoverage=[dict(mode=mode,completeSourceProjectionCoversRecord=True)for mode in ['original','literal','leftF32','balancedF32']],allInstalledActorsChecked=6873,installedSupportUsers=[],sourceGeometryChanges=0,sourcePoseChanges=0)
    def rejects(self):
        with self.assertRaises(AssertionError):verify_metadata(self.models,self.coverage)
    def test_exact_scope_preserves_input_and_support_graph(self):
        before=copy.deepcopy((self.models,self.coverage));self.assertTrue(verify_metadata(self.models,self.coverage));self.assertEqual(before,(self.models,self.coverage))
    def test_extra_hidden_record_rejected(self):self.by[PRIMARY]['suppressesBuildingUids'].append('landsd/6393:0');self.rejects()
    def test_companion_cannot_hide_record(self):self.by[HALL]['suppressesBuildingUids']=[GATE];self.rejects()
    def test_changed_source_rejected(self):self.by[PRIMARY]['sha256']='0'*64;self.rejects()
    def test_changed_parent_csuid_rejected(self):self.by[HALL]['supportDependencies'][0]['buildingCSUID']='wrong';self.rejects()
    def test_missing_parent_rejected(self):self.models.remove(self.by[PRIMARY]);self.rejects()
    def test_new_dependency_rejected(self):self.by[PRIMARY]['supportDependencies']=[dict(uid=HALL,state='installed')];self.rejects()
    def test_one_failed_coordinate_world_rejected(self):self.coverage['completeFourWorldCoverage'][2]['completeSourceProjectionCoversRecord']=False;self.rejects()
    def test_different_secondary_rejected(self):self.coverage['secondaryUid']='landsd/6393:0';self.rejects()
    def test_existing_support_user_rejected(self):self.coverage['installedSupportUsers']=[HALL];self.rejects()
    def test_vertical_move_rejected(self):self.by[PRIMARY]['verticalPlacementOffsetHKPD']=1;self.rejects()
    def test_retained_basic_dependency_cannot_sneak_in(self):self.by[PRIMARY]['retainedBasicSupportDependencies']=[dict(supportUid=GATE)];self.rejects()

if __name__=='__main__':unittest.main()
