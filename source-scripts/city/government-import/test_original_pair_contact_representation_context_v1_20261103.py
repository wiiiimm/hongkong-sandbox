from fractions import Fraction as F
import unittest
from original_pair_contact_representation_context_v1_20261103 import barycentric,displacement_context
class ExactAffineContact(unittest.TestCase):
    def setUp(self):self.t=[[F(v)for v in p]for p in [[0,0,0],[2,0,0],[0,2,0]]]
    def test_face_interior(self):self.assertEqual(barycentric(self.t,[F(1,2),F(1,2),F(0)]),[F(1,2),F(1,4),F(1,4)])
    def test_off_face_rejected(self):
        with self.assertRaises(AssertionError):barycentric(self.t,[F(1,2),F(1,2),F(1,1000000)])
    def test_outside_rejected(self):
        with self.assertRaises(AssertionError):barycentric(self.t,[F(2),F(2),F(0)])
    def test_exact_shift_bound(self):
        shifted=[[v+(F(1,1024)if i==2 else 0)for i,v in enumerate(p)]for p in self.t];d,b=displacement_context(self.t,shifted,[F(1,2),F(1,2),F(1,1024)]);self.assertEqual(d,[0,0,F(1,1024)]);self.assertEqual(b,d)
    def test_zero_shift(self):self.assertEqual(displacement_context(self.t,self.t,[F(0)]*3),([0,0,0],[0,0,0]))
    def test_line(self):self.assertEqual(barycentric([[F(0)]*3,[F(2),F(0),F(0)],[F(0)]*3],[F(1),F(0),F(0)]),[F(1,2),F(1,2),F(0)])
    def test_line_uses_full_convex_hull(self):
        t=[[F(0)]*3,[F(1),F(0),F(0)],[F(-2),F(0),F(0)]];w=barycentric(t,[F(-1),F(0),F(0)]);self.assertEqual(w,[F(0),F(1,3),F(2,3)])
    def test_point(self):self.assertEqual(barycentric([[F(0)]*3]*3,[F(0)]*3),[F(1),F(0),F(0)])
if __name__=='__main__':unittest.main()
