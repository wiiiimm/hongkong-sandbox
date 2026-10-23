import unittest
import numpy as np
from fractions import Fraction as F
from finite_native_boundary_strip_v1_20261023 import strip_report


class Strips(unittest.TestCase):
    def setUp(self):
        self.face=np.array([[0,3,0],[0,3,2],[0,3.000001,2]],float);self.curve=[(F(0),F(2),F(3),F(3),0)]
    def check(self,face=None,curve=None):return strip_report(self.face if face is None else face,0,0,self.curve if curve is None else curve,F(0),F(2))
    def test_entire_thin_rendered_strip_matches_without_height_credit(self):
        r=self.check();self.assertFalse(r['heightFieldCredit']);self.assertFalse(r['structuralSupportCredit'])
    def test_large_vertical_strip_rejected(self):
        f=self.face.copy();f[2,1]=3.1
        with self.assertRaises(AssertionError):self.check(f)
    def test_nonrendering_triangle_cannot_claim_strip(self):
        f=self.face.copy();f[:,1]=3
        with self.assertRaises(AssertionError):self.check(f)
    def test_off_plane_triangle_rejected(self):
        f=self.face.copy();f[2,0]=.001
        with self.assertRaises(AssertionError):self.check(f)
    def test_curve_gap_rejected(self):
        with self.assertRaises(AssertionError):self.check(curve=[(F(0),F(1),F(3),F(3),0)])
    def test_interior_upper_envelope_kink_rejected(self):
        with self.assertRaises(AssertionError):self.check(curve=[(F(0),F(2),F(3),F(4),0),(F(0),F(2),F(4),F(3),1)])
    def test_isolated_height_spike_is_not_hidden(self):
        with self.assertRaises(AssertionError):self.check(curve=self.curve+[(F(1),F(1),F(4),F(4),1)])


if __name__=='__main__':unittest.main()
