import copy,unittest
from original_independent_model_only_contract_v1_20261024 import verify_native_scope

class NativeContractTests(unittest.TestCase):
    def setUp(self):
        self.current={'landsd/2:0':{'uid':'landsd/2:0','sha256':'old'}};self.sources={'landsd/1:0':'new'}
        self.scope=dict(uids=list(self.sources),rows=[dict(uid='landsd/1:0',sourceSHA256='new',currentNativeActorsChecked=6894,nearbyNativeActors=[dict(uid='landsd/2:0',sourceSHA256='old')])])
        self.contacts=dict(rows=[dict(uid='landsd/1:0',nativeUid='landsd/2:0',sourceSHA256='new',nativeSHA256='old',rawCurrentNativeEntry=copy.deepcopy(self.current['landsd/2:0']),modes=[dict(mode=m,finiteContactPairs=0,positiveSurfaceContactPairs=0,areaContactPairs=0)for m in ['original','literal','leftF32','balancedF32']])])
    def check(self):return verify_native_scope(self.scope,self.contacts,self.current,self.sources,{'landsd/2:0'},6894)
    def test_complete_unchanged_four_world_zero_contacts(self):self.assertTrue(self.check())
    def test_rejects_omitted_neighbour_or_proof(self):
        self.contacts['rows']=[]
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_missing_coordinate_world(self):
        self.contacts['rows'][0]['modes'].pop()
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_even_point_contact(self):
        self.contacts['rows'][0]['modes'][0]['finiteContactPairs']=1
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_changed_retained_metadata(self):
        self.current['landsd/2:0']['supportDependencies']=['landsd/3:0']
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_stale_inventory_count(self):
        self.scope['rows'][0]['currentNativeActorsChecked']=6893
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_mismatched_source_hash(self):
        self.contacts['rows'][0]['sourceSHA256']='different'
        with self.assertRaises(AssertionError):self.check()
    def test_rejects_undeclared_retained_actor(self):
        self.scope['rows'][0]['nearbyNativeActors'].append(dict(uid='landsd/3:0',sourceSHA256='unknown'))
        with self.assertRaises(AssertionError):self.check()

if __name__=='__main__':unittest.main()
