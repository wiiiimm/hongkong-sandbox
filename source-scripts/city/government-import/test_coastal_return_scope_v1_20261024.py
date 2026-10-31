import unittest
import shapely
from coastal_return_scope_v1_20261024 import verify_return_scope

class ReturnScopeTests(unittest.TestCase):
    def setUp(self):self.core=shapely.box(0,0,1,1)
    def test_external_blended_return_is_derived(self):
        p=[[2,1,0],[3,1,0],[2,1,1]]
        r=verify_return_scope(p,[0,1,2],[dict(kind='original-inset-or-return')],[0],self.core)
        self.assertEqual(r['minimumFaceDistanceFromProtectedCoreM'],1)
    def test_vertices_outside_but_face_crossing_core_rejected(self):
        p=[[-1,1,-1],[3,1,-1],[-1,1,3]]
        with self.assertRaises(AssertionError):verify_return_scope(p,[0,1,2],[dict(kind='original-inset-or-return')],[0],self.core)
    def test_even_parent_fragment_inside_core_rejected(self):
        p=[[.1,1,.1],[.9,1,.1],[.1,1,.9]]
        with self.assertRaises(AssertionError):verify_return_scope(p,[0,1,2],[dict(kind='parent-fragment')],[0],self.core)
    def test_unknown_lineage_rejected(self):
        with self.assertRaises(AssertionError):verify_return_scope([[2,1,0],[3,1,0],[2,1,1]],[0,1,2],[dict(kind='unknown')],[0],self.core)

if __name__=='__main__':unittest.main()
