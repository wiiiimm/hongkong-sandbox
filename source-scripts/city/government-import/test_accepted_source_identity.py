import copy
import unittest
from accepted_source_identity import reuse_identity

class ReuseTest(unittest.TestCase):
    def inputs(self):
        form={'uid':'landsd/1:0','objectId':1,'buildingCSUID':'abc','rings':[[[0,0],[1,0],[1,1]]],'base':2,'height':10}
        model={**{k:form[k] for k in ('uid','objectId','buildingCSUID')},'modelId':'Babc','sha256':'source',
               'worldBounds':[[0,2,0],[1,12,1]],'rootTranslation':[-834500,0,816500],
               'recordedBaseHeight':2,'recordedTopHeight':12,'sourceIdentityReviewed':True,
               'identityReviewApproved':True,'placementReviewed':True}
        return dict(current_form=form,accepted_form=copy.deepcopy(form),candidate=copy.deepcopy(model),installed_model=model,
                    catalogue_sha='catalogue',acceptance_sha='acceptance',acceptance={'uid':form['uid'],'sourceSHA256':'source','catalogueSHA256':'catalogue'},
                    review={'uid':form['uid'],'review_state':'installed-verified','source_sha256':'source',
                            'snapshot_id':'snapshot','result':{'source_sha256':'source','sha256':'acceptance'}})
    def test_unchanged_receipts_reuse_identity_only(self):
        proof=reuse_identity(**self.inputs());self.assertTrue(proof['identityAccepted']);self.assertIn('contacts',proof['qualification'])
    def test_changed_form_rejected(self):
        d=self.inputs();d['current_form']['height']=11
        with self.assertRaises(AssertionError):reuse_identity(**d)
    def test_source_transform_and_receipts_rejected(self):
        for key,value in [('sha256','other'),('rootTranslation',[0,0,0]),('objectId',2)]:
            d=self.inputs();d['candidate'][key]=value
            with self.assertRaises(AssertionError):reuse_identity(**d)
        for key in ('acceptance_sha','catalogue_sha'):
            d=self.inputs();d[key]='changed'
            with self.assertRaises(AssertionError):reuse_identity(**d)
    def test_uninstalled_or_unapproved_rejected(self):
        d=self.inputs();d['review']['review_state']='approved-for-integration'
        with self.assertRaises(AssertionError):reuse_identity(**d)
        d=self.inputs();d['installed_model']['identityReviewApproved']=False
        with self.assertRaises(AssertionError):reuse_identity(**d)

if __name__=='__main__':unittest.main()
