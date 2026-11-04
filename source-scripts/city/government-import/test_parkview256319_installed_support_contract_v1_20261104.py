"""Adverse checks for the exact original, parent-audit and adjacent-seam route."""
from copy import deepcopy
import unittest
from run import ROOT,read
import parkview256319_installed_support_contract_v1_20261104 as c
import original_installed_support_model_only_contract_v1_20261027 as generic
class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=ROOT/'docs/astra-city/government-import';cfg=read(b/'government-xl-parkview256319-installation-plan-v1-20261104/config.json');cls.cfg=cfg
        cls.current={m['uid']:m for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
        cls.models=read(ROOT/'source-scripts/city/government-import/local'/cfg['browser']/'catalogue.json')['models']
        cls.original={r['uid']:r['candidate']['entry']for r in read(b/cfg['originalSelection']/'selection.json.gz')['rows']}
        cls.audit=read(b/cfg['parentApprovalAudit']/'audit.json');cls.scope=read(b/cfg['scope']/'summary.json');cls.contacts=read(b/cfg['nativeContacts']/'summary.json');cls.review=read(b/cfg['physical']/'ROOT-PHYSICAL-REVIEW.json')
    def metadata(self,models=None,audit=None,current=None):
        return c.verify_metadata(models if models is not None else self.models,self.cfg['sources'],self.cfg['supportByUid'],self.original,current if current is not None else self.current,audit if audit is not None else self.audit)
    def native(self,scope=None,contacts=None,review=None):
        return c.verify_native_scope(scope if scope is not None else self.scope,contacts if contacts is not None else self.contacts,self.current,self.cfg['sources'],self.cfg['supportByUid'],set(self.cfg['retainedNativeUids']),7108,review if review is not None else self.review)
    def test_exact_case_passes_without_mutation(self):
        before=deepcopy([self.models,self.current,self.audit,self.scope,self.contacts,self.review]);self.assertTrue(self.metadata());self.assertTrue(self.native());self.assertEqual(before,[self.models,self.current,self.audit,self.scope,self.contacts,self.review])
    def test_changed_source_or_render_metadata_fails(self):
        for field,value in [('sha256','0'*64),('rootTranslation',[-834500,1,816500]),('proceduralWindows',True),('verticalPlacementOffsetHKPD',1),('sourceWorldBounds',[[0,0,0],[1,1,1]])]:
            with self.subTest(field=field):
                models=deepcopy(self.models);models[0][field]=value
                with self.assertRaises(AssertionError):self.metadata(models=models)
    def test_missing_or_conflicting_parent_review_fails(self):
        for field,value in [('noLaterHoldOrRejection',False),('sourceSHA256','0'*64),('catalogueSHA256','0'*64),('reviewState','held'),('catalogueChanged',True),('optimisationApproval',True)]:
            with self.subTest(field=field):
                audit=deepcopy(self.audit);audit[field]=value
                with self.assertRaises(AssertionError):self.metadata(audit=audit)
    def test_unreviewed_parent_flag_changes_fail(self):
        current=deepcopy(self.current);current[c.PARENT]['identityReviewApproved']=False
        with self.assertRaises(AssertionError):self.metadata(current=current)
    def test_missing_or_extra_native_obligation_fails(self):
        for mode in ['missing','extra']:
            scope=deepcopy(self.scope)
            if mode=='missing':scope['rows'][0]['nearbyNativeActors'].pop()
            else:scope['rows'][0]['nearbyNativeActors'].append(deepcopy(scope['rows'][0]['nearbyNativeActors'][0]))
            with self.assertRaises(AssertionError):self.native(scope=scope)
    def test_unreviewed_adjacent_contact_fails(self):
        review=deepcopy(self.review);review['acceptedAdjacentNativeContacts'][0]['physicalInterpretationAccepted']=False
        with self.assertRaises(AssertionError):self.native(review=review)
    def test_forged_contact_counts_fail_even_if_review_copied(self):
        contacts=deepcopy(self.contacts);review=deepcopy(self.review);row=next(r for r in contacts['rows']if r['nativeUid']==c.PEER);row['modes'][0]['areaContactPairs']=0;review['acceptedAdjacentNativeContacts'][0]['rawContactSummary']=deepcopy(row)
        with self.assertRaises(AssertionError):self.native(contacts=contacts,review=review)
    def test_absent_wall_review_or_changed_seam_fails(self):
        review=deepcopy(self.review);review['boundedSourceContext']['sourceSpecificBuriedWallInterpretationAccepted']=False
        with self.assertRaises(AssertionError):self.native(review=review)
        review=deepcopy(self.review);row=next(r for r in review['completeCurrentNativeContactRoles']if r['nativeUid']==c.PEER);row['contactBounds'][1][2]+=.01
        with self.assertRaises(AssertionError):self.native(review=review)
    def test_generic_parent_and_unreviewed_foreign_gates_still_reject(self):
        with self.assertRaises(AssertionError):generic.verify_metadata(self.models,self.cfg['sources'],self.cfg['supportByUid'],self.original,self.current)
        with self.assertRaises(AssertionError):generic.verify_native_scope(self.scope,self.contacts,self.current,self.cfg['sources'],self.cfg['supportByUid'],set(self.cfg['retainedNativeUids']),7108,self.review)
if __name__=='__main__':unittest.main()
