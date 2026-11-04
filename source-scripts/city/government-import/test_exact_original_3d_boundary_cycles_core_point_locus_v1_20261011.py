import unittest
from fractions import Fraction as F
from exact_original_3d_directed_edge_atom_census_v1_20261011 import census
from exact_original_3d_boundary_cycles_core_point_locus_v1_20261011 import cycles,core_point_locus
class BoundaryLocusTests(unittest.TestCase):
 def test_single_triangle_cycle_complete(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)]]);c=cycles(r['allExact3DAtomicEdges'],1);self.assertEqual(len(c[0]['allCompleteSimpleDirected3DCycles'][0]['allOrderedAtomicEdgeIds']),3)
 def test_pointtouch_components_stay_separate(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)],[(0,0,0),(-1,0,0),(0,0,-1)]]);self.assertEqual(len(cycles(r['allExact3DAtomicEdges'],2)),2)
 def test_branch_fails_not_arbitrarily_walked(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)]]);r['allExact3DAtomicEdges'][0]['allDirectedIncidences'][0]['end']=(F(3),F(0),F(0));e=r['allExact3DAtomicEdges'][0]['allDirectedIncidences'][0];r['allExact3DAtomicEdges'][0]['exactEndpoints']=sorted((e['start'],e['end']));c=cycles(r['allExact3DAtomicEdges'],1);self.assertFalse(c[0]['completeBoundaryCyclePartitionQualified']);self.assertFalse(c[0]['allCompleteSimpleDirected3DCycles'])
 def test_strict_interior(self):self.assertEqual(core_point_locus((F(1,4),F(1,4)),[[(0,0),(1,0),(0,1)]])['location'],'interior-core')
 def test_edge_exterior(self):self.assertEqual(core_point_locus((F(1,2),0),[[(0,0),(1,0),(0,1)]])['location'],'exterior-boundary-of-closed-core')
 def test_vertex_exterior(self):self.assertFalse(core_point_locus((0,0),[[(0,0),(1,0),(0,1)]])['exactFiniteUnionLocalNeighborhoodCovered'])
 def test_shared_diagonal_complementary_cones_interior(self):
  r=core_point_locus((F(1,2),F(1,2)),[[(0,0),(1,0),(1,1)],[(0,0),(1,1),(0,1)]]);self.assertEqual(r['location'],'interior-core');self.assertTrue(r['allAtomicDirectionConeTests'])
 def test_four_vertex_quadrants_cover_full_neighborhood(self):
  t=[[(0,0),(1,0),(0,1)],[(0,0),(0,1),(-1,0)],[(0,0),(-1,0),(0,-1)],[(0,0),(0,-1),(1,0)]];self.assertEqual(core_point_locus((0,0),t)['location'],'interior-core')
 def test_missing_quadrant_remains_exterior(self):
  t=[[(0,0),(1,0),(0,1)],[(0,0),(0,1),(-1,0)],[(0,0),(-1,0),(0,-1)]];self.assertEqual(core_point_locus((0,0),t)['location'],'exterior-boundary-of-closed-core')
 def test_tiny_nonzero_outside_not_buffered(self):self.assertEqual(core_point_locus((F(-1,2**100),0),[[(0,0),(1,0),(0,1)]])['location'],'outside-closed-core')
 def test_clockwise_source_preserved_classification(self):self.assertEqual(core_point_locus((F(1,4),F(1,4)),[[(0,1),(1,0),(0,0)]])['location'],'interior-core')
 def test_zero_projection_not_fake_area(self):
  with self.assertRaises(AssertionError):core_point_locus((0,0),[[(0,0),(1,0),(2,0)]])
if __name__=='__main__':unittest.main()
