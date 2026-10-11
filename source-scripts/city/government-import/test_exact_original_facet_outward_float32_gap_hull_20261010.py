import unittest
from fractions import Fraction as F
from exact_original_facet_outward_float32_gap_hull_20261010 import propose,cross
class Tests(unittest.TestCase):
 def face(self):return [[0,0,0],[100,100,0],[0,0,100]]
 def test_long_diagonal_seam_does_not_credit_axis_aligned_rectangle(self):
  p=propose([[1.000001,1.000001],[40.000001,40.000001],[40.000001,40.000002]],self.face());self.assertLess(F(p['fullProposedProjectedAreaM2']),F(1,100));self.assertGreater(F(p['fullProposedProjectedAreaM2']),0)
 def test_every_exact_original_gap_vertex_closed_inside_hull(self):
  gap=[[F(1,3),F(1,3)],[F(2,3),F(2,3)],[F(2,3),F(2,3)+F(1,10**12)]];p=propose(gap,self.face());h=[tuple(map(F,q)) for q in p['exactConvexOutwardHullXZ']];self.assertTrue(all(all(cross(a,b,q)>=0 for a,b in zip(h,h[1:]+h[:1])) for q in gap))
 def test_point_gets_actual_nonzero_declared_extent(self):self.assertGreater(F(propose([[1,1]],self.face())['fullProposedProjectedAreaM2']),0)
 def test_interval_gets_declared_finite_area(self):self.assertGreater(F(propose([[1,1],[40,40]],self.face())['fullProposedProjectedAreaM2']),0)
 def test_source_finite_boundary_crossing_rejects(self):
  with self.assertRaises(AssertionError):propose([[50,50],[50.1,50]],self.face())
 def test_sloping_heights_bound_actual_source_plane_quantization(self):
  p=propose([[1.1,1.1],[2.1,2.1]],self.face());self.assertEqual(p['exactSourcePlaneVertexHeightsM'],[str(F(v[0])) for v in p['proposedVertices']])
 def test_reversed_source_winding_same_height(self):self.assertEqual(propose([[1,1],[2,2]],self.face())['proposedVertices'],propose([[1,1],[2,2]],self.face()[::-1])['proposedVertices'])
 def test_no_source_building_or_approval_credit(self):
  p=propose([[1,1]],self.face());self.assertTrue(p['terrainProposalGeometryChanged']);self.assertEqual(p['buildingGeometryChanges'],0);self.assertFalse(p['sourcePlaneExtrapolation']);self.assertFalse(p['installationApproved'])
if __name__=='__main__':unittest.main()
