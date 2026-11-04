import copy,unittest
from original_terrain_obligation_union_v1_20261024 import merge

class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.model={'landsd/1:0':{'uid':'landsd/1:0','base':4}}
        self.forms=[self.model['landsd/1:0'],{'uid':'way/2','base':5}]
        self.scope=dict(currentNativeActors=6884,uids=['landsd/1:0'],touchingNativeUids=[],terrainContacts=[],positiveAreaTerrainOverlaps=0,intersectingForms=2)
    def run_merge(self):return merge(self.model,self.forms,self.scope,native_count=6884,target_uids=['landsd/1:0'],expected_count=2)
    def test_adds_outer_terrain_form_without_mutating_inputs(self):
        before=copy.deepcopy([self.model,self.forms,self.scope]);r=self.run_merge();self.assertEqual(set(r),{'landsd/1:0','way/2'});self.assertEqual(before,[self.model,self.forms,self.scope])
    def test_rejects_conflicting_current_form(self):
        self.forms=copy.deepcopy(self.forms);self.forms[0]['base']=99
        with self.assertRaises(AssertionError):self.run_merge()
    def test_rejects_duplicate_and_missing_domain_forms(self):
        for forms in [[self.forms[0],self.forms[0]],[self.forms[0]]]:
            self.forms=forms
            with self.assertRaises(AssertionError):self.run_merge()
    def test_rejects_unreviewed_native_or_prior_terrain(self):
        for key,value in [('touchingNativeUids',['landsd/3:0']),('terrainContacts',[{'uid':'patch'}]),('positiveAreaTerrainOverlaps',1)]:
            old=copy.deepcopy(self.scope);self.scope[key]=value
            with self.assertRaises(AssertionError):self.run_merge()
            self.scope=old
    def test_rejects_stale_inventory_or_wrong_targets(self):
        for key,value in [('currentNativeActors',6883),('uids',['landsd/4:0'])]:
            old=copy.deepcopy(self.scope);self.scope[key]=value
            with self.assertRaises(AssertionError):self.run_merge()
            self.scope=old

if __name__=='__main__':unittest.main()
