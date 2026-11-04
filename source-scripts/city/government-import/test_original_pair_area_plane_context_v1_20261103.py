import unittest
from original_pair_area_plane_context_v1_20261103 import plane_context
from original_pair_contact_representation_context_v1_20261103 import exact_triangle
class OriginalPlaneContext(unittest.TestCase):
    def setUp(self):self.a=exact_triangle([[0,0,0],[2,0,0],[0,0,2]])
    def test_coplanar(self):self.assertEqual(plane_context(self.a,self.a)['originalPlaneRelation'],'coplanar')
    def test_tiny_parallel_separation_not_rewritten_zero(self):
        b=exact_triangle([[0,2**-30,0],[2,2**-30,0],[0,2**-30,2]]);r=plane_context(self.a,b);self.assertEqual(r['originalPlaneRelation'],'parallel-separated');self.assertEqual(r['originalNormalRoles'],['horizontal','horizontal'])
    def test_nonparallel(self):
        b=exact_triangle([[0,-1,0],[2,1,0],[0,1,2]]);self.assertEqual(plane_context(self.a,b)['originalPlaneRelation'],'non-parallel')
    def test_degenerate_rejected(self):
        with self.assertRaises(AssertionError):plane_context(self.a,exact_triangle([[0,0,0]]*3))
if __name__=='__main__':unittest.main()
