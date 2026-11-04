import unittest
from fractions import Fraction as F
from exact_original_terrain_overlap_plane_classification_v1_20261011 import classify

def face(xz,h):return [(F(x),F(h(x,z)),F(z))for x,z in xz]
A=[(0,0),(2,0),(0,2)]
class Tests(unittest.TestCase):
 def test_duplicate_reversed(self):
  a=face(A,lambda x,z:x+z);r=classify(a,list(reversed(a)));self.assertTrue(r['exactDuplicateUnordered3DVertices']);self.assertTrue(r['exactClosedOverlapPlanesIdentical'])
 def test_coplanar_different_domains(self):
  r=classify(face(A,lambda x,z:x+z),face([(0,0),(1,0),(0,1)],lambda x,z:x+z));self.assertTrue(r['exactClosedOverlapPlanesIdentical']);self.assertFalse(r['exactDuplicateUnordered3DVertices'])
 def test_parallel_distinct(self):
  r=classify(face(A,lambda x,z:0),face(A,lambda x,z:3));self.assertEqual(r['exactHeightDifferenceLowerM'],-3);self.assertEqual(r['exactHeightDifferenceUpperM'],-3)
 def test_crossing_planes(self):
  r=classify(face(A,lambda x,z:0),face(A,lambda x,z:x-1));self.assertEqual((r['exactHeightDifferenceLowerM'],r['exactHeightDifferenceUpperM']),(-1,1));self.assertTrue(r['distinctPlaneHeightsCrossWithinOverlap'])
 def test_tiny_gap_not_waived(self):
  r=classify(face(A,lambda x,z:0),face(A,lambda x,z:F(1,2**90)));self.assertFalse(r['exactClosedOverlapPlanesIdentical'])
 def test_edge_only_rejected(self):
  with self.assertRaises(AssertionError):classify(face(A,lambda x,z:0),face([(2,0),(2,2),(0,2)],lambda x,z:0))
 def test_point_only_rejected(self):
  with self.assertRaises(AssertionError):classify(face(A,lambda x,z:0),face([(2,0),(3,0),(2,1)],lambda x,z:0))
 def test_zero_projection_rejected(self):
  with self.assertRaises(AssertionError):classify([(0,0,0),(0,1,0),(0,0,1)],face(A,lambda x,z:0))
 def test_nonfinite_rejected(self):
  with self.assertRaises((ValueError,OverflowError)):classify([(0,0,0),(1,float('inf'),0),(0,0,1)],face(A,lambda x,z:0))
if __name__=='__main__':unittest.main()
