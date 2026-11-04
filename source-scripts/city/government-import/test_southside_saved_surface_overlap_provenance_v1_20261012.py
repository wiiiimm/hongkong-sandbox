"""Draft focused tests; no invocation authorised by drafting."""
import unittest
from fractions import Fraction as F
import southside_saved_surface_overlap_provenance_v1_20261012 as proof
class Overlap(unittest.TestCase):
 A=[[0,0,0],[2,0,0],[0,0,2]]
 def test_same_and_reversed(self):
  for b in [self.A,list(reversed(self.A))]:
   q=proof.classify(self.A,b);self.assertEqual(q['classification'],'coincident-plane');self.assertEqual(F(q['exactProjectedArea']),2)
 def test_distinct_layer(self):
  b=[[x,3,z]for x,y,z in self.A];q=proof.classify(self.A,b);self.assertEqual(q['classification'],'second-at-or-above-first');self.assertEqual(set(q['exactFirstMinusSecondHeightAtVertices']),{'-3'})
 def test_crossing_planes(self):
  b=[[0,-1,0],[2,1,0],[0,-1,2]];self.assertEqual(proof.classify(self.A,b)['classification'],'crossing-height-planes')
 def test_boundary_only(self):
  b=[[2,0,0],[4,0,0],[2,0,2]];self.assertFalse(proof.classify(self.A,b)['positiveProjectedArea'])
 def test_vertical_preserved_as_no_projected_area(self):
  b=[[0,0,0],[0,1,0],[0,1,2]];self.assertFalse(proof.classify(self.A,b)['positiveProjectedArea'])
 def test_tiny_real_not_dropped(self):
  t=[[0,0,0],[F(1,10**200),0,0],[0,0,F(1,10**200)]];self.assertGreater(F(proof.classify(t,t)['exactProjectedArea']),0)
 def test_disjoint_broadplane(self):
  b=[[10,0,10],[12,0,10],[10,0,12]];self.assertFalse(proof.classify(self.A,b)['positiveProjectedArea'])
 def test_invalid_triangle(self):
  with self.assertRaises(AssertionError):proof.classify(self.A,self.A[:2])
if __name__=='__main__':unittest.main()
