"""Mutation checks at the source-specific surveyed-roof publication boundary."""
import copy
import unittest
from run import ROOT,HERE,read
from passenger162768_surveyed_roof_contract_v1_20261030 import verify
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-passenger162768-after-civic-five-'

class ContractTests(unittest.TestCase):
    def setUp(self):
        folder=BASE/(P+'final-source-review-v1-20261030')
        review=read(folder/'ROOT-SOURCE-REVIEW.json')
        self.args=[read(HERE/'local'/(P+'post-preserving-roof-private-preview-v1-20261030')/'catalogue.json')['models'],review,read(folder/'ROOT-PHYSICAL-REVIEW.json'),read(BASE/(P+'six-roof-lifecycle-v1-20261030')/'report.json'),[read(ROOT/r['path'])for r in review['canopyFeatureReviews']],{b['uid']:b for b in read(folder/'form-obligations.json.gz')}]
        self.args=copy.deepcopy(self.args)
    def reject(self):
        with self.assertRaises(AssertionError):verify(*self.args)
    def test_exact_reviewed_case_passes(self):
        self.assertTrue(verify(*self.args)['completeLifecycleVerified'])
    def test_different_original_is_rejected(self):
        self.args[0][0]['sha256']='0'*64;self.reject()
    def test_different_terrain_is_rejected(self):
        self.args[2]['terrainCandidate']['sha256']='0'*64;self.reject()
    def test_new_post_gap_is_rejected(self):
        self.args[2]['surveyedFallbackPosts'][0]['after']['maximumPostBottomAboveGroundM']=.01;self.reject()
    def test_incomplete_post_coverage_is_rejected(self):
        self.args[2]['surveyedFallbackPosts'][0]['after']['uncoveredPostFootprintM2']=.000001;self.reject()
    def test_consistently_changed_survey_identity_is_rejected(self):
        uid='landsd/71245:0';self.args[5][uid]['buildingCSUID']='different'
        self.args[4][0]['exactBasicForm']['buildingCSUID']='different';self.reject()
    def test_missing_roof_fallback_on_failure_is_rejected(self):
        case=next(c for c in self.args[3]['cases']if c['failedUid'])
        row=next(r for r in case['canopyLifecycle']if r['phase']=='failed-download')
        row['canopies'][0]['basicCanopyVisible']=False;self.reject()
    def test_unreviewed_seventh_replacement_is_rejected(self):
        self.args[0][0]['suppressesBuildingUids'].append('landsd/332872:0');self.reject()
    def test_dropped_auxiliary_is_rejected(self):
        self.args[2]['retainedAuxiliaryUids'].pop();self.reject()
    def test_preapproved_input_is_rejected(self):
        self.args[0][0]['publicationApproved']=True;self.reject()

if __name__=='__main__':unittest.main()
