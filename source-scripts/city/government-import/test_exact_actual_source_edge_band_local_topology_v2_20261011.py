import unittest
from fractions import Fraction as F
from exact_faithful_source_step_junction_feasibility_v2_20261011 import native_footprints
from exact_actual_source_edge_band_local_topology_v2_20261011 import infinitesimal_sides,complete_actual_edge_atoms,complete_outer_edge_candidates,directed_boundary_cycles,complete_edge_band_coverage
class Tests(unittest.TestCase):
 def test_genuine_exterior(self):
  n=native_footprints([[(0,1,0),(2,1,0),(0,1,2)]]);r=complete_actual_edge_atoms(n,0,0);self.assertTrue(r['allCompletePositiveEdgeAtoms'][0]['actualDrawnProjectedExteriorBoundary'])
 def test_complete_opposite_side_neighbour(self):
  n=native_footprints([[(0,1,0),(2,1,0),(0,1,2)],[(0,2,0),(0,2,-2),(2,2,0)]]);r=complete_actual_edge_atoms(n,0,0);self.assertTrue(r['allCompletePositiveEdgeAtoms'][0]['bothDrawnSidesCovered']);self.assertEqual(len(r['allCompletePositiveEdgeAtoms'][0]['allCompleteClosedSourceOwners']),2)
 def test_partial_neighbour_splits_complete_edge(self):
  n=native_footprints([[(0,1,0),(2,1,0),(0,1,2)],[(0,1,0),(0,1,-1),(1,1,0)]]);r=complete_actual_edge_atoms(n,0,0);self.assertEqual(r['allExactOrderedParameters'],[F(0),F(1,2),F(1)]);self.assertTrue(r['allCompletePositiveEdgeAtoms'][1]['actualDrawnProjectedExteriorBoundary'])
 def test_point_touch_not_two_sided_credit(self):
  n=native_footprints([[(0,1,0),(2,1,0),(0,1,2)],[(2,1,0),(3,1,-1),(3,1,0)]]);self.assertTrue(complete_actual_edge_atoms(n,0,0)['allCompletePositiveEdgeAtoms'][0]['actualDrawnProjectedExteriorBoundary'])
 def test_vertical_face_and_repeated_projected_vertex_retained(self):
  n=native_footprints([[(0,1,0),(2,1,0),(0,1,2)],[(0,1,0),(0,2,0),(2,2,0)]]);self.assertTrue(complete_actual_edge_atoms(n,0,0)['allCompletePositiveEdgeAtoms'][0]['actualDrawnProjectedExteriorBoundary']);self.assertTrue(complete_actual_edge_atoms(n,1,0)['projectedPointOnly'])
 def test_symbolic_no_epsilon(self):self.assertEqual(infinitesimal_sides([(0,0),(1,0),(0,1)],(F(1,2),0),(0,0),(1,0)),(True,False))
 def test_outer_edge_interior_available_despite_far_vertices(self):
  r=complete_outer_edge_candidates((0,0),[dict(start=(-100,5),end=(100,5))])[0];self.assertEqual(r['exactMinimumL1Distance'],5);self.assertTrue(any(n['parameter']==F(1,2)for n in r['allFiniteBreakpointNominations']))
 def test_outer_edge_far_all_points_rejected(self):self.assertFalse(complete_outer_edge_candidates((0,0),[dict(start=(-100,11),end=(100,11))])[0]['withinTenMetresSomewhere'])
 def test_l1_breakpoint_not_only_euclidean(self):
  r=complete_outer_edge_candidates((0,0),[dict(start=(-20,4),end=(4,10))])[0];self.assertEqual(r['exactMinimumL1Distance'],9)
 def test_outer_zero_edge_rejected(self):
  with self.assertRaises(AssertionError):complete_outer_edge_candidates((0,0),[dict(start=(0,0),end=(0,0))])
 def test_exterior_hole_winding_distinguished(self):
  e=[dict(start=a,end=b)for a,b in [((0,0),(2,0)),((2,0),(0,2)),((0,2),(0,0))]];r=directed_boundary_cycles(e);self.assertTrue(r['completeDirectedCycles'][0]['orientedPositiveUnionExterior']);reverse=[dict(start=x['end'],end=x['start'])for x in e];self.assertTrue(directed_boundary_cycles(reverse)['completeDirectedCycles'][0]['orientedPositiveUnionHole'])
 def test_open_or_branch_cycle_not_pocket_credit(self):
  r=directed_boundary_cycles([dict(start=(0,0),end=(1,0))]);self.assertTrue(r['degreeFailures']);self.assertEqual(r['completeDirectedCycles'],[])
 def test_whole_edge_band_covered(self):self.assertTrue(complete_edge_band_coverage((0,0),(1,0),[[(0,0),(1,0),(1,1),(0,1)]])['wholeProjectedEdgeBandCovered'])
 def test_missing_positive_band_interval_not_credited(self):self.assertFalse(complete_edge_band_coverage((0,0),(2,0),[[(0,0),(1,0),(1,1),(0,1)]])['wholeProjectedEdgeBandCovered'])
if __name__=='__main__':unittest.main()
