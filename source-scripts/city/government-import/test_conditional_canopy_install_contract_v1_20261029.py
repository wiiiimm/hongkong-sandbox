import copy
import unittest
from conditional_canopy_install_contract_v1_20261029 import verify,form_sha

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.uid='landsd/1:0';self.basic='landsd/2:0';self.sha='source'
        self.forms={self.uid:dict(uid=self.uid),self.basic:dict(uid=self.basic,structureType='Open-sided Structure',heightSource='estimated',baseHeightHKPD=None,topHeightHKPD=None)}
        replacement=dict(sourceUid=self.uid,basicUid=self.basic,sourceSHA256=self.sha,sourceFormSHA256=form_sha(self.forms[self.uid]),basicFormSHA256=form_sha(self.forms[self.basic]),onlyWhileExactOwnerActive=True,approved=True)
        self.review=dict(sourceSHA256ByUid={self.uid:self.sha},identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,sourceGeometryChanges=0,sourcePoseChanges=0,currentManifest='manifest',conditionalCanopyReplacement=replacement)
        self.physical=copy.deepcopy(self.review)
        self.feature=dict(currentManifest='manifest',exactBasicForm=copy.deepcopy(self.forms[self.basic]),privateCanopyExperimentApproved=True,publication=False,installationApproved=False,sourceUid=self.uid,basicUid=self.basic,sourceSHA256=self.sha)
        self.models=[dict(uid=self.uid,sha256=self.sha,triangles=11,suppressesBuildingUids=[self.basic],proceduralWindows=False,publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)]
        cases=[]
        for width,failed in [(1280,None),(390,self.uid)]:
            phases=['original-active','base-only','auto-restored','evicted-return-base-only']+(['failed-download']if failed else [])
            cases.append(dict(width=width,failedUid=failed,completeGroupEvicted=True,baseOnlyRestoredCompleteGroup=True,audit=dict(violations=[]),sources=[dict(uid=self.uid,sha256=self.sha,triangles=11,active=True)],failureKeptAllBasics=True,canopyLifecycle=[dict(phase=p,ownerActive=p in ['original-active','auto-restored'],basicCanopyVisible=p not in ['original-active','auto-restored'])for p in phases]))
        self.lifecycle=dict(passed=True,pageErrors=[],publication=False,cases=cases)
    def check(self):return verify(self.models,self.review,self.physical,self.lifecycle,self.feature,self.forms)
    def test_exact_case(self):self.assertTrue(self.check()['completeLifecycleVerified'])
    def test_additional_suppression_rejected(self):
        self.models[0]['suppressesBuildingUids'].append('landsd/3:0')
        with self.assertRaises(AssertionError):self.check()
    def test_changed_canopy_form_rejected(self):
        self.forms[self.basic]['height']=9
        with self.assertRaises(AssertionError):self.check()
    def test_surveyed_canopy_rejected(self):
        self.forms[self.basic]['baseHeightHKPD']=2
        with self.assertRaises(AssertionError):self.check()
    def test_missing_identity_rejected(self):
        self.review['identityAccepted']=False
        with self.assertRaises(AssertionError):self.check()
    def test_changed_source_rejected(self):
        self.models[0]['sha256']='other'
        with self.assertRaises(AssertionError):self.check()
    def test_stale_manifest_rejected(self):
        self.physical['currentManifest']='other'
        with self.assertRaises(AssertionError):self.check()
    def test_missing_eviction_case_rejected(self):
        self.lifecycle['cases'][0]['canopyLifecycle'].pop()
        with self.assertRaises(AssertionError):self.check()
    def test_fallback_not_restored_rejected(self):
        self.lifecycle['cases'][0]['canopyLifecycle'][1]['basicCanopyVisible']=False
        with self.assertRaises(AssertionError):self.check()
    def test_duplicate_phase_rejected(self):
        self.lifecycle['cases'][0]['canopyLifecycle'].append(self.lifecycle['cases'][0]['canopyLifecycle'][0])
        with self.assertRaises(AssertionError):self.check()
    def test_dependency_addition_rejected(self):
        self.models[0]['supportDependencies']=['unknown']
        with self.assertRaises(AssertionError):self.check()
    def test_source_geometry_edit_rejected(self):
        self.review['sourceGeometryChanges']=1
        with self.assertRaises(AssertionError):self.check()

if __name__=='__main__':unittest.main()
