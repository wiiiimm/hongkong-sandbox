import unittest
from fractions import Fraction as F
from exact_source_core_ten_metre_transition_domain_v1_20261011 import domain,atomic,polygon,hull
class Tests(unittest.TestCase):
 def setUp(self):self.square=[[(0,0),(1,0),(0,1)],[(1,0),(1,1),(0,1)]]
 def test_square_exact_width_area(self):
  d=domain(self.square);self.assertEqual(d['exactWholeDomainAreaM2'],241);self.assertEqual(d['exactWholeDomainXZBounds'],[-10,-10,11,11]);self.assertEqual(len(d['combinedAtomicBoundary']['allDirectedCycles']),1)
 def test_all_band_pieces_provenance(self):
  d=domain(self.square);self.assertEqual(len(d['computeBandPolygons']),len(d['allComputeBandSourceBoundaryProvenance']));self.assertFalse(d['terrainCandidateApproved'])
 def test_duplicate_source(self):
  with self.assertRaises(AssertionError):domain(self.square+[self.square[0]])
 def test_tiny_overlap_reject(self):
  with self.assertRaises(AssertionError):domain([[(0,0),(1,0),(0,1)],[(F(1,10**30),0),(2,0),(1,1)]])
 def test_point_bridge_reject(self):
  with self.assertRaises(AssertionError):domain([[(0,0),(1,0),(0,1)],[(1,0),(2,0),(2,1)]])
 def test_tjunction_atomic(self):
  p=[[(0,0),(2,0),(0,2)],[(2,0),(2,1),(1,1)],[(2,1),(2,2),(0,2),(1,1)]];self.assertTrue(atomic(p)['projectedTopologyQualified'])
 def test_nonmanifold(self):self.assertFalse(atomic(self.square+[self.square[0]])['projectedTopologyQualified'])
 def test_disconnected_no_false_onecycle(self):
  d=domain([[(0,0),(1,0),(0,1)],[(100,0),(101,0),(100,1)]]);self.assertEqual(len(d['combinedAtomicBoundary']['allDirectedCycles']),2)
 def test_reversed_source_not_repaired(self):
  with self.assertRaises(AssertionError):domain([list(reversed(self.square[0]))])
 def test_nonconvex_input(self):
  with self.assertRaises(AssertionError):polygon([(0,0),(2,0),(1,F(1,2)),(2,2),(0,2)])
 def test_zero_projected(self):
  with self.assertRaises(AssertionError):domain([[(0,0),(1,0),(2,0)]])
 def test_nonfinite(self):
  with self.assertRaises(ValueError):domain([[('nan',0),(1,0),(0,1)]])
 def test_invalid_width(self):
  with self.assertRaises(AssertionError):domain(self.square,width=11)
 def test_dimension_schema(self):
  with self.assertRaises(AssertionError):polygon([(0,0,0),(1,0,0),(0,1,0)])
 def test_hull_collinear(self):self.assertEqual(hull([(0,0),(1,0),(2,0),(0,1)]),[(F(0),F(0)),(F(2),F(0)),(F(0),F(1))])
if __name__=='__main__':unittest.main()
