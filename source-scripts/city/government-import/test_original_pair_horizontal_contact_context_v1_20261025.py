import unittest
from fractions import Fraction as F
from original_pair_horizontal_contact_context_v1_20261025 import horizontal_area
class Area(unittest.TestCase):
 def c(self,pts):return dict(exactPoints=[[str(x),'7',str(z)]for x,z in pts])
 def test_fractional_rectangle(self):self.assertEqual(horizontal_area(self.c([(0,0),(F(1,3),0),(F(1,3),F(1,7)),(0,F(1,7))])),F(1,21))
 def test_permutation_duplicates_and_collinear(self):self.assertEqual(horizontal_area(self.c([(2,1),(1,0),(0,0),(2,0),(0,1),(2,1)])),2)
 def test_tiny_exact_area_is_not_zero(self):self.assertEqual(horizontal_area(self.c([(0,0),(F(1,2**60),0),(0,1)])),F(1,2**61))
 def test_degenerate_rejected(self):
  with self.assertRaises(AssertionError):horizontal_area(self.c([(0,0),(1,0),(2,0)]))
if __name__=='__main__':unittest.main()
