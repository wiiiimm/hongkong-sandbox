import copy,unittest
from original_availability_catalogue_v1_20261027 import verify
class ExactAvailabilityAnnotation(unittest.TestCase):
    def setUp(self):
        self.uid='landsd/3:0';self.group=['landsd/1:0','landsd/2:0','landsd/3:0']
        self.before=dict(schemaVersion=1,models=[dict(uid=self.uid,sha256='a'*64,asset='assets/original.gz',placementReviewed=False,identityReviewApproved=False),dict(uid='landsd/4:0',sha256='b'*64)],counts=dict(packedModels=2))
        self.after=copy.deepcopy(self.before);self.after['models'][0]['activationGroup']=self.group
    def test_exact_annotation_preserves_negative_flags(self):self.assertTrue(verify(self.before,self.after,self.uid,self.group)['existingGeometryAndReviewFieldsUnchanged'])
    def test_review_flag_change_is_rejected(self):
        self.after['models'][0]['placementReviewed']=True
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
    def test_unrelated_entry_change_is_rejected(self):
        self.after['models'][1]['sha256']='c'*64
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
    def test_catalogue_header_change_is_rejected(self):
        self.after['counts']['packedModels']=3
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
    def test_asset_path_change_is_rejected(self):
        self.after['models'][0]['asset']='changed.gz'
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
    def test_prior_group_cannot_be_split(self):
        self.before['models'][0]['activationGroup']=[self.uid,'landsd/4:0']
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
    def test_model_removal_is_rejected(self):
        self.after['models'].pop()
        with self.assertRaises(AssertionError):verify(self.before,self.after,self.uid,self.group)
if __name__=='__main__':unittest.main()
