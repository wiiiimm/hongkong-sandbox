import copy,unittest
from original_supported_catalogue_scope_v1_20261024 import verify


class SupportScope(unittest.TestCase):
    def setUp(self):
        self.sources={'a':'hash-a','b':'hash-b'};self.supports={'b':'a'}
        self.models=[dict(uid='a',sha256='hash-a',buildingCSUID='csuid-a',proceduralWindows=False),dict(uid='b',sha256='hash-b',buildingCSUID='csuid-b',proceduralWindows=False,supportDependencies=[dict(uid='a',state='installed',buildingCSUID='csuid-a',sha256='hash-a')])]
    def test_complete_bound_graph(self):self.assertTrue(verify(self.models,self.sources,self.supports))
    def test_missing_parent(self):
        with self.assertRaises(AssertionError):verify(self.models[1:],self.sources,self.supports)
    def test_changed_parent_hash(self):
        self.models[1]['supportDependencies'][0]['sha256']='wrong'
        with self.assertRaises(AssertionError):verify(self.models,self.sources,self.supports)
    def test_changed_parent_identity(self):
        self.models[1]['supportDependencies'][0]['buildingCSUID']='other'
        with self.assertRaises(AssertionError):verify(self.models,self.sources,self.supports)
    def test_undeclared_dependency(self):
        with self.assertRaises(AssertionError):verify(self.models,self.sources,{})
    def test_suppression_rejected(self):
        self.models[0]['suppressesBuildingUids']=['retained-neighbour']
        with self.assertRaises(AssertionError):verify(self.models,self.sources,self.supports)
    def test_cycle_rejected(self):
        self.models[0]['supportDependencies']=[dict(uid='b',state='installed',buildingCSUID='csuid-b',sha256='hash-b')]
        with self.assertRaises(AssertionError):verify(self.models,self.sources,{'a':'b','b':'a'})

if __name__=='__main__':unittest.main()
