"""DRAFT adverse/positive topology tests; no terrain candidate acceptance."""
import unittest,numpy as np
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import atomic_boundary,one_edge_ring
def tri(points,y=0):return [[x,y,z]for x,z in points]
def square(x=0,z=0,y=0):return [tri([(x,z),(x+1,z),(x,z+1)],y),tri([(x+1,z),(x+1,z+1),(x,z+1)],y)]
class BoundaryTests(unittest.TestCase):
 def test_triangle_closed_cycle(self):
  r=atomic_boundary([tri([(0,0),(1,0),(0,1)])]);self.assertTrue(r['topologyQualified']);self.assertEqual(len(r['completeSimpleDirectedBoundaryCycles']),1)
 def test_square_exact_internal_edge(self):
  r=atomic_boundary(square());self.assertTrue(r['oneGenuine3DSharedEdgeComponent']);self.assertEqual(len(r['allInternalAtomicEdges']),1);self.assertEqual(len(r['allBoundaryAtomicEdges']),4)
 def test_actual_t_junction_subdivision(self):
  left=[tri([(-1,0),(0,0),(-1,2)]),tri([(0,0),(0,2),(-1,2)])];right=square(0,0)+square(0,1);r=atomic_boundary(left+right);self.assertTrue(r['topologyQualified']);self.assertTrue(r['oneGenuine3DSharedEdgeComponent']);self.assertEqual(len(r['completeSimpleDirectedBoundaryCycles']),1)
 def test_disconnected_not_genuine_connected(self):
  r=atomic_boundary(square()+square(3,0));self.assertFalse(r['oneGenuine3DSharedEdgeComponent']);self.assertEqual(len(r['genuineNonzero3DSharedEdgeFaceComponents']),2)
 def test_point_bridge_rejected(self):
  r=atomic_boundary([tri([(0,0),(1,0),(0,1)]),tri([(1,0),(2,0),(1,-1)])]);self.assertFalse(r['topologyQualified']);self.assertEqual(len(r['genuineNonzero3DSharedEdgeFaceComponents']),2)
 def test_duplicate_overlap_rejected(self):
  f=tri([(0,0),(1,0),(0,1)]);r=atomic_boundary([f,f]);self.assertFalse(r['topologyQualified']);self.assertTrue(r['completePositiveProjectedOverlapPairs'])
 def test_hidden_positive_overlap_rejected(self):
  r=atomic_boundary([tri([(0,0),(2,0),(0,2)]),tri([(.2,.2),(.4,.2),(.2,.4)])]);self.assertFalse(r['topologyQualified'])
 def test_internal_height_gap_rejected(self):
  a=square();a[1]=tri([(1,0),(1,1),(0,1)],1);r=atomic_boundary(a);self.assertFalse(r['topologyQualified']);self.assertTrue(r['invalidAtomicIncidences'])
 def test_nonmanifold_triplicate_rejected(self):
  f=tri([(0,0),(1,0),(0,1)]);r=atomic_boundary([f,f,f]);self.assertFalse(r['topologyQualified']);self.assertTrue(r['invalidAtomicIncidences'])
 def test_nonfinite_schema(self):
  f=tri([(0,0),(1,0),(0,1)]);f[0][1]=np.nan
  with self.assertRaises(AssertionError):atomic_boundary([f])
 def test_projected_zero_schema(self):
  with self.assertRaises(AssertionError):atomic_boundary([tri([(0,0),(1,0),(2,0)])])
 def test_reversed_input_winding_normalizes_geometry_only(self):
  a=square();a[1]=a[1][::-1];r=atomic_boundary(a);self.assertTrue(r['topologyQualified']);self.assertTrue(r['oneGenuine3DSharedEdgeComponent'])
 def test_ring_point_only_excluded(self):
  r=one_edge_ring([tri([(0,0),(1,0),(0,1)])],[tri([(1,0),(2,0),(2,1)])]);self.assertEqual(r['completeOnePositiveEdgeAdjacentRetainedFaceIds'],[])
 def test_ring_wrong_height_not_3d_credit(self):
  r=one_edge_ring([tri([(0,0),(1,0),(0,1)])],[tri([(1,0),(1,1),(0,1)],1)]);self.assertEqual(r['completeOnePositiveEdgeAdjacentRetainedFaceIds'],[0]);self.assertTrue(all(not x['exactCurrent3DCompatible']for x in r['allExactPositiveAdjacentIntervals']))
 def test_ring_one_layer_does_not_expand(self):
  r=one_edge_ring(square(),square(1,0)+square(2,0));self.assertTrue(r['completeOnePositiveEdgeAdjacentRetainedFaceIds']);self.assertTrue(all(i<2 for i in r['completeOnePositiveEdgeAdjacentRetainedFaceIds']));self.assertFalse(r['terrainCandidateApproved'])
 def test_ring_same_side_duplicate_not_adjacent(self):
  f=tri([(0,0),(1,0),(0,1)]);r=one_edge_ring([f],[f]);self.assertEqual(r['completeOnePositiveEdgeAdjacentRetainedFaceIds'],[])
if __name__=='__main__':unittest.main()
