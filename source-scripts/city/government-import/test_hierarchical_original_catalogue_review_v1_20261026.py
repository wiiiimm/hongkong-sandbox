import copy
import unittest
from run import ROOT,read
from hierarchical_original_catalogue_review_v1_20261026 import verify_catalogue_review

class CatalogueReviewTests(unittest.TestCase):
    def setUp(self):
        self.original=read(ROOT/'source-scripts/city/government-import/local/government-xl-podium323546-after-beverly-d-three-hierarchical-private-browser-v1-20261026/catalogue.json')
        self.approved=copy.deepcopy(self.original)
        self.approved.update(kind='official-model-catalogue',diagnosticOnly=False,physicalAcceptance=True,publicationApproved=True)
        for m in self.approved['models']:
            m.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceIdentityReview={'path':'test-only-review.json','sha256':'test-only'},placementReview='test only')
    def test_review_only_changes_pass(self):
        self.assertTrue(verify_catalogue_review(self.original,self.approved))
    def test_moved_root_rejected(self):
        self.approved['rootTranslation'][0]+=.01
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)
    def test_changed_source_rejected(self):
        self.approved['models'][0]['sha256']='different'
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)
    def test_added_support_rejected(self):
        self.approved['models'][0]['supportDependencies']=[{'uid':'landsd/1:0'}]
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)
    def test_procedural_windows_rejected(self):
        self.approved['models'][0]['proceduralWindows']=True
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)
    def test_model_reordering_rejected(self):
        self.approved['models'].reverse()
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)
    def test_missing_review_rejected(self):
        self.approved['models'][0]['identityReviewApproved']=False
        with self.assertRaises(AssertionError):verify_catalogue_review(self.original,self.approved)

if __name__=='__main__':unittest.main()
