import unittest
from fractions import Fraction as F
import numpy as np
from exact_faithful_source_step_junction_feasibility_v2_20261011 import native_footprints,native_query_inventory,whole_actual_source_edge,bounded_outer_corner_ray,vertical_junction
class Tests(unittest.TestCase):
 def test_oblique_exact_edge(self):
  n=native_footprints([[(0,2,0),(3,2,7),(4,2,0)]])
  self.assertEqual(native_query_inventory(n,(F(1),F(7,3)))['allIndexedFiniteOwners'],[0])
 def test_binary64_edge_query_outside_is_not_coverage_hole(self):
  n=native_footprints([[(0,2,0),(3,2,7),(4,2,0)]])
  self.assertEqual(native_query_inventory(n,(1,float(F(7,3))))['allIndexedFiniteOwners'],[])
 def test_float32_query_can_move_back_inside(self):
  n=native_footprints([[(0,2,0),(3,2,7),(4,2,0)]])
  self.assertEqual(native_query_inventory(n,(1,float(np.float32(float(F(7,3))))))['allIndexedFiniteOwners'],[0])
 def test_projected_tiny_drawn_not_indexed(self):
  n=native_footprints([[(0,1,0),(1e-6,1,0),(0,1,1e-6)]]);r=native_query_inventory(n,(0,0));self.assertEqual(r['allIndexedFiniteOwners'],[]);self.assertEqual(r['allDrawnNonzeroProjectionOwners'],[0])
 def test_vertical_drawn_not_height_branch(self):
  n=native_footprints([[(0,1,0),(0,2,0),(0,2,1)]]);self.assertFalse(n['indexed'][0]);self.assertEqual(native_query_inventory(n,(0,0))['allIndexedFiniteOwners'],[])
 def test_all_overlap_owners_retained(self):
  n=native_footprints([[(0,y,0),(1,y,0),(0,y,1)]for y in[1,3]]);self.assertEqual(native_query_inventory(n,(F(1,4),F(1,4)))['allIndexedFiniteOwners'],[0,1])
 def test_nonfinite_source_rejected(self):
  with self.assertRaises(AssertionError):native_footprints([[(0,0,0),(np.nan,0,1),(1,0,0)]])
 def test_complete_original_shared_edge(self):
  n=native_footprints([[(0,2,0),(3,2,7),(4,2,0)]]);self.assertTrue(whole_actual_source_edge(n,0,(0,2,0),(3,2,7))['wholeEdgeQualified'])
 def test_cast_partial_oblique_edge_not_snapped(self):
  n=native_footprints([[(0,2,0),(3,2,7),(4,2,0)]]);self.assertFalse(whole_actual_source_edge(n,0,(0,2,0),(1,2,F(7,3)))['wholeEdgeQualified'])
 def test_band_ray_complete(self):
  r=bounded_outer_corner_ray((0,0),[dict(start=(1,0),end=(1,1))],[[(0,0),(0,1),(-1,0)]],[[(0,0),(1,0),(1,1),(0,1)]]);self.assertNotIn('noBoundedWholeBandOnlyRay',r)
 def test_ray_core_reentry_rejected(self):
  r=bounded_outer_corner_ray((0,0),[dict(start=(1,0),end=(1,1))],[[(0,0),(2,0),(0,2)]],[[(0,0),(1,0),(1,1),(0,1)]]);self.assertTrue(r['noBoundedWholeBandOnlyRay'])
 def test_ray_missing_band_interval_rejected(self):
  r=bounded_outer_corner_ray((0,0),[dict(start=(1,0),end=(1,1))],[],[[(F(3,4),0),(1,0),(1,1),(F(3,4),1)]]);self.assertTrue(r['noBoundedWholeBandOnlyRay'])
 def test_outer_node_beyond_ten_metres_not_used(self):
  r=bounded_outer_corner_ray((0,0),[dict(start=(11,0),end=(11,1))],[],[[(0,0),(11,0),(11,1),(0,1)]]);self.assertEqual(r['finiteOuterNodesEnumerated'],0)
 def test_vertical_junction_positive_area_unpaired_termination_explicit(self):
  r=vertical_junction((0,0),2,1,(1,4,0));self.assertGreater(r['exactPositive3DAreaSquared'],0);self.assertEqual(r['exactProjectedArea'],0);self.assertTrue(r['sourceCoreInnerVerticalTerminationUnpaired'])
 def test_equal_source_height_and_point_only_outer_rejected(self):
  with self.assertRaises(AssertionError):vertical_junction((0,0),1,1,(1,4,0))
  with self.assertRaises(AssertionError):vertical_junction((0,0),2,1,(0,4,0))
if __name__=='__main__':unittest.main()
