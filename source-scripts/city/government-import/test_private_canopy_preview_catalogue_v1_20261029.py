import unittest
from copy import deepcopy
from private_canopy_preview_catalogue_v1_20261029 import apply
class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.models=[dict(uid='landsd/1:0',sha256='a'*64,asset='immutable.glb.gz',publicationApproved=False,placementReviewed=False,identityReviewApproved=False,sourceIdentityReviewed=False)]
        self.sources={'landsd/1:0':'a'*64};self.forms={'landsd/2:0':dict(uid='landsd/2:0',structureType='Open-sided Structure',baseHeightHKPD=None,topHeightHKPD=None,heightSource='estimated')}
        self.review=dict(privateCanopyExperimentApproved=True,installationApproved=False,publication=False,sourceUid='landsd/1:0',basicUid='landsd/2:0',sourceSHA256='a'*64,exactBasicForm=deepcopy(self.forms['landsd/2:0']),proposedSuppression=dict(ownerUid='landsd/1:0',sourceSHA256='a'*64,suppressesBuildingUids=['landsd/2:0'],onlyWhileExactOwnerActive=True))
    def check(self):return apply(self.models,self.sources,self.forms,self.review)
    def test_only_visibility_metadata_added(self):
        old=deepcopy(self.models);out=self.check();self.assertEqual(self.models,old);out[0].pop('suppressesBuildingUids');self.assertEqual(out,old)
    def test_source_revision_mismatch(self):
        self.review['sourceSHA256']='b'*64
        with self.assertRaises(AssertionError):self.check()
    def test_publication_not_authorised(self):
        self.review['publication']=True
        with self.assertRaises(AssertionError):self.check()
    def test_installation_not_authorised(self):
        self.review['installationApproved']=True
        with self.assertRaises(AssertionError):self.check()
    def test_unreviewed_experiment_rejected(self):
        self.review['privateCanopyExperimentApproved']=False
        with self.assertRaises(AssertionError):self.check()
    def test_changed_form_rejected(self):
        self.forms['landsd/2:0']['extra']=True
        with self.assertRaises(AssertionError):self.check()
    def test_more_suppression_rejected(self):
        self.review['proposedSuppression']['suppressesBuildingUids'].append('landsd/3:0')
        with self.assertRaises(AssertionError):self.check()
    def test_approved_catalogue_rejected(self):
        self.models[0]['publicationApproved']=True
        with self.assertRaises(AssertionError):self.check()
    def test_existing_suppression_rejected(self):
        self.models[0]['suppressesBuildingUids']=['landsd/4:0']
        with self.assertRaises(AssertionError):self.check()
    def test_asset_revision_rejected(self):
        self.models[0]['sha256']='b'*64
        with self.assertRaises(AssertionError):self.check()
if __name__=='__main__':unittest.main()
