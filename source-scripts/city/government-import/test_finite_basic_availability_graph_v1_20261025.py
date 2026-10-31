import copy
import unittest
from finite_basic_availability_graph_v1_20261025 import expected_dependencies

class AvailabilityGraph(unittest.TestCase):
    def setUp(self):
        self.models = [dict(uid='landsd/1:0',sha256='a'*64,buildingCSUID='F'),
                       dict(uid='landsd/2:0',sha256='b'*64,buildingCSUID='E')]
        self.bindings = [dict(uid=m['uid'],sourceSHA256=m['sha256'],supportUid='landsd/3:0',
                              mustRemainBasicAndUnsuppressed=True,
                              futureReplacementRequiresDependentRevalidation=True) for m in self.models]
        self.replacements = {'landsd/1:0':'landsd/2:0'}
    def test_typed_podium_and_exact_original_neighbour(self):
        result = expected_dependencies(self.models,self.bindings,self.replacements,include_basic=True)
        self.assertEqual(result['landsd/1:0'],[dict(uid='landsd/2:0',state='installed',buildingCSUID='E',sha256='b'*64),dict(uid='landsd/3:0',state='surveyed-footprint-fallback')])
        self.assertEqual(result['landsd/2:0'],[dict(uid='landsd/3:0',state='surveyed-footprint-fallback')])
    def test_private_dependency_has_same_original_binding(self):
        result = expected_dependencies(self.models,self.bindings,self.replacements,include_basic=False)
        self.assertEqual(result['landsd/2:0'],[])
        self.assertEqual(result['landsd/1:0'][0]['sha256'],'b'*64)
    def test_cycles_and_self_dependency_rejected(self):
        for mapping in [{'landsd/1:0':'landsd/1:0'},{'landsd/1:0':'landsd/2:0','landsd/2:0':'landsd/1:0'}]:
            with self.assertRaises(AssertionError):expected_dependencies(self.models,self.bindings,mapping,include_basic=True)
    def test_external_neighbour_rejected(self):
        with self.assertRaises(AssertionError):expected_dependencies(self.models,self.bindings,{'landsd/1:0':'landsd/99:0'},include_basic=True)
    def test_stale_source_rejected(self):
        bindings=copy.deepcopy(self.bindings);bindings[0]['sourceSHA256']='c'*64
        with self.assertRaises(AssertionError):expected_dependencies(self.models,bindings,self.replacements,include_basic=True)
    def test_podium_cannot_be_an_imported_candidate(self):
        bindings=copy.deepcopy(self.bindings);bindings[0]['supportUid']='landsd/2:0'
        with self.assertRaises(AssertionError):expected_dependencies(self.models,bindings,self.replacements,include_basic=True)
    def test_missing_or_duplicate_binding_rejected(self):
        for bindings in [self.bindings[:1],[self.bindings[0],self.bindings[0]]]:
            with self.assertRaises(AssertionError):expected_dependencies(self.models,bindings,self.replacements,include_basic=True)
    def test_support_lifetime_cannot_be_dropped(self):
        bindings=copy.deepcopy(self.bindings);bindings[0]['futureReplacementRequiresDependentRevalidation']=False
        with self.assertRaises(AssertionError):expected_dependencies(self.models,bindings,self.replacements,include_basic=True)
if __name__=='__main__':unittest.main()
