import unittest
import numpy as np
from exact_current_parent_finite_region_clip_feasibility_20261011 import diagnose
class ClipFeasibility(unittest.TestCase):
 def make(self,parent,r=None):
  r=r or [[0,0],[1,0],[0,1]]
  return diagnose(parent,[r],[r])
 def test_literal_plane_exact(self):
  q=self.make([[[0,0,0],[2,2,0],[0,0,2]]]);self.assertTrue(q['allPackedFacetsExactlyOnOriginalParentPlanes']);self.assertEqual(len(q['packedClippedFacets']),1)
 def test_actual_quantization_plane_not_credited(self):
  q=self.make([[[0,0,0],[3,1,0],[0,0,3]]]);self.assertFalse(q['allPackedFacetsExactlyOnOriginalParentPlanes']);self.assertTrue(q['actualFloat32PlaneFailures']);self.assertFalse(q['physicalAccepted'])
 def test_all_parent_faces_inventoried(self):
  q=self.make([[[0,0,0],[2,0,0],[0,0,2]],[[5,0,5],[6,0,5],[5,0,6]]]);self.assertEqual(len(q['allOriginalParentFacetDispositions']),2);self.assertEqual(q['allOriginalParentFacetDispositions'][1]['finiteRegionClips'],[])
 def test_vertical_facet_preserved_as_finite_surface(self):
  q=self.make([[[0,0,0],[0,1,0],[0,0,1]]]);self.assertEqual(q['allOriginalParentFacetDispositions'][0]['completeOriginalPrimitiveDimension'],2);self.assertEqual(len(q['packedClippedFacets']),1)
 def test_zero_area_line_retained_uncredited(self):
  q=self.make([[[0,0,0],[1,0,0],[.5,0,0]]]);self.assertEqual(q['allOriginalParentFacetDispositions'][0]['completeOriginalPrimitiveDimension'],1);self.assertEqual(q['packedClippedFacets'],[])
 def test_zero_area_point_retained_uncredited(self):
  q=self.make([[[0,0,0]]*3]);self.assertEqual(q['allOriginalParentFacetDispositions'][0]['completeOriginalPrimitiveDimension'],0)
 def test_tiny_nonzero_parent_retained(self):
  d=2**-80;q=self.make([[[0,0,0],[d,0,0],[0,0,d]]]);self.assertEqual(q['allOriginalParentFacetDispositions'][0]['completeOriginalPrimitiveDimension'],2);self.assertEqual(len(q['packedClippedFacets']),1)
 def test_negative_nonfinite(self):
  with self.assertRaises(AssertionError):self.make([[[0,0,0],[float('nan'),0,0],[0,0,1]]])
 def test_negative_missing_region_facet(self):
  with self.assertRaises(AssertionError):diagnose([[[0,0,0],[2,0,0],[0,0,2]]],[[[0,0],[1,0],[1,1],[0,1]]],[[[0,0],[1,0],[0,1]]])
 def test_negative_duplicate_region(self):
  r=[[0,0],[1,0],[0,1]]
  with self.assertRaises(AssertionError):diagnose([[[0,0,0],[2,0,0],[0,0,2]]],[r],[r,r])
 def test_contact_boundary_only_does_not_gain_area(self):
  q=self.make([[[1,0,0],[2,0,0],[1,0,1]]]);self.assertEqual(q['packedClippedFacets'],[]);self.assertTrue(q['allOriginalParentFacetDispositions'][0]['finiteRegionClips'])
 def test_reverse_parent_orientation_preserved(self):
  q=self.make([[[0,0,2],[2,2,0],[0,0,0]]]);self.assertTrue(q['allPackedFacetsExactlyOnOriginalParentPlanes'])
if __name__=='__main__':unittest.main()
