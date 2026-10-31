"""Unexecuted meaningful surface-partition and seam nomination fixtures."""
import unittest
from fractions import Fraction as F
import numpy as np
from upton_original_tin_current_ring_join_nomination_v1_20261012 import split_rectangle,triangulate,nonzero,packed,boundary_edges,nominated_upper_join,protected_core
class Tests(unittest.TestCase):
 def test_unchanged_inside_source_plane(self):
  f=[[0,2,0],[1,3,0],[0,4,1]];r=split_rectangle(f,[-1,-1,2,2]);self.assertEqual(r['inside'],list(map(tuple,f)));self.assertFalse(r['outside'])
 def test_crossing_clip_preserves_entire_original_affine_plane(self):
  f=[[-1,-1,0],[2,2,0],[0,0,2]];r=split_rectangle(f,[0,0,1,1]);self.assertTrue(r['outside']);self.assertTrue(r['inside'])
  for p in r['inside']+[v for poly in r['outside']for v in poly]:self.assertEqual(p[1],p[0])
  area=lambda t:abs((t[1][0]-t[0][0])*(t[2][2]-t[0][2])-(t[1][2]-t[0][2])*(t[2][0]-t[0][0]))/2
  self.assertEqual(sum(area(t)for poly in [r['inside']]+r['outside']for t in triangulate(poly)),F(3))
 def test_complete_outside_face_keeps_original_points(self):
  f=[[-3,1,0],[-2,2,0],[-2,1,1]];r=split_rectangle(f,[0,0,1,1]);self.assertFalse(r['inside']);self.assertEqual(r['outside'],[list(map(tuple,f))])
 def test_vertical_source_faces_are_not_dropped_as_heightfield(self):
  f=[[0,0,0],[0,2,0],[0,2,1]];r=split_rectangle(f,[-1,-1,1,2]);self.assertTrue(nonzero(r['inside']));self.assertEqual(len(triangulate(r['inside'])),1)
 def test_exact_zero_is_inventory_not_a_join_root(self):
  self.assertFalse(nonzero([[0,0,0],[0,0,0],[0,0,0]]));self.assertEqual(len(triangulate(split_rectangle([[0,0,0]]*3,[-1,-1,1,1])['inside'])),0)
 def test_invalid_domain_rejected(self):
  for d in [[1,0,0,1],[0,0,0,1],[0,0,float('inf'),1]]:
   with self.assertRaises((AssertionError,OverflowError)):split_rectangle([[0,0,0],[1,0,0],[0,0,1]],d)
 def test_complete_unused_or_f32_bounds_cannot_be_omitted(self):
  with self.assertRaises(AssertionError):protected_core([[[0,0,0],[1,1,1]],[[-10,0,0],[-9,1,1]]],[-2,-2,2,2])
 def test_core_margin_is_outward_dyadic_and_strict_inside_domain(self):
  c=protected_core([[[0.1,0,0.1],[1.1,1,1.1]]],[-2,-2,3,3]);self.assertLessEqual(c[0],F(0.1)-1);self.assertGreaterEqual(c[2],F(1.1)+1);self.assertTrue(all((x*1024).denominator==1 for x in c))
 def test_full_boundary_segments_only_not_partial_vertex_mounts(self):
  self.assertEqual(len(boundary_edges([[0,0,0],[0,0,1],[1,0,1]],[0,0,1,1])),2)
 def test_missing_current_finite_seam_coverage_is_hold(self):
  g=np.array([[[10,0,10],[11,0,10],[10,0,11]]],float);r=nominated_upper_join([[0,1,0],[1,1,0]],g);self.assertFalse(r['complete']);self.assertFalse(r['joinNominations'])
 def test_ruled_join_keeps_both_source_and_current_heights(self):
  g=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float);r=nominated_upper_join([[0,2,0],[1,2,0]],g);self.assertTrue(r['complete']);self.assertFalse(r['rawFixedBandProof']['verifiedCompleteOriginalEdgeContactBand']);self.assertTrue(r['joinNominations'][0]['ruled']['generatedFacesAreNotOriginalGovernmentGeometry'])
 def test_upper_surface_crossing_is_partitioned_not_midpoint_bridge(self):
  g=np.array([[[0,0,0],[1,2,0],[0,0,1]],[[0,2,0],[1,0,0],[0,2,1]]],float);r=nominated_upper_join([[0,3,0],[1,3,0]],g);self.assertTrue(r['complete']);self.assertIn(['0','1/2'],[x['exactParameterInterval']for x in r['joinNominations']]);self.assertIn(['1/2','1'],[x['exactParameterInterval']for x in r['joinNominations']])
 def test_packed_precision_is_explicit_not_presumed_exact_surface(self):
  f=[[0,1/3,0],[1,1/3,0],[0,1/3,1]];a=packed(f);self.assertEqual(a.dtype.str,'<f8');self.assertNotEqual(a[0,1],F(1,3))
if __name__=='__main__':unittest.main()
