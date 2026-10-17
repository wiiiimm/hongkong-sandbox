import unittest
from fractions import Fraction as F
from exact_band_cell_authentic_edge_integration_v1_20261011 import complete_graph,source_boundary_integration
R=lambda x,y,w=1,h=1:[(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
O=lambda a,b:[dict(start=a,end=b)]
class Tests(unittest.TestCase):
 def test_complete_shared_edge(self):
  r=complete_graph([R(0,0),R(1,0)],O((2,0),(2,1)));self.assertEqual(r['positiveEdgeAdjacency']['0'],[1]);self.assertTrue(r['projectedPartitionGraphQualified'])
 def test_point_only_no_connection(self):self.assertEqual(len(complete_graph([R(0,0),R(1,1)],[])['completePositiveEdgeComponents']),2)
 def test_partial_tjunction_edges_retained(self):
  r=complete_graph([R(0,0,1,2),R(1,0),R(1,1)],[]);self.assertEqual(r['positiveEdgeAdjacency']['0'],[1,2]);self.assertIn((F(1),F(1)),r['canonicalSharedProjectedNodes'])
 def test_duplicate_source_cells_not_partition_credit(self):self.assertFalse(complete_graph([R(0,0),R(0,0)],[])['projectedPartitionGraphQualified'])
 def test_positive_area_overlap_not_partition_credit(self):self.assertTrue(complete_graph([R(0,0),R(F(1,2),0)],[])['completePositiveInteriorOverlapPairs'])
 def test_nonconvex_cell_rejected(self):
  with self.assertRaises(AssertionError):complete_graph([[(0,0),(2,0),(1,1),(2,2),(0,2)]],[])
 def test_wrong_winding_rejected(self):
  with self.assertRaises(AssertionError):complete_graph([list(reversed(R(0,0)))],[])
 def test_repeated_edge_rejected(self):
  with self.assertRaises(AssertionError):complete_graph([[(0,0),(1,0),(1,0),(0,1)]],[])
 def test_outer_point_touch_receives_no_link(self):self.assertEqual(complete_graph([R(0,0)],O((1,1),(2,1)))['outerLinkedCells'],[])
 def test_whole_source_boundary_and_band_path_distinct(self):
  c=[R(0,0),R(1,0)];g=complete_graph(c,O((2,0),(2,1)));r=source_boundary_integration(c,g,dict(exactXZEndpoints=[(0,0),(0,1)]),dict(completePositiveIntervals=[dict(allBandOwners=[0])]));self.assertTrue(r['wholeProjectedDirectBoundaryCovered']);self.assertEqual(r['deterministicPositiveEdgeBandPathToOuter'],[0,1]);self.assertTrue(r['noRouteCredit'])
 def test_partial_direct_source_boundary_not_whole_seam(self):
  c=[R(0,0)];g=complete_graph(c,O((1,0),(1,1)));r=source_boundary_integration(c,g,dict(exactXZEndpoints=[(0,0),(0,2)]),dict(completePositiveIntervals=[dict(allBandOwners=[0])]));self.assertFalse(r['wholeProjectedDirectBoundaryCovered']);self.assertEqual(r['deterministicPositiveEdgeBandPathToOuter'],[0])
 def test_no_seed_no_path(self):
  c=[R(0,0)];r=source_boundary_integration(c,complete_graph(c,[]),dict(exactXZEndpoints=[(0,0),(0,1)]),dict(completePositiveIntervals=[]));self.assertIsNone(r['deterministicPositiveEdgeBandPathToOuter'])
 def test_unknown_seed_rejected(self):
  c=[R(0,0)]
  with self.assertRaises(AssertionError):source_boundary_integration(c,complete_graph(c,[]),dict(exactXZEndpoints=[(0,0),(0,1)]),dict(completePositiveIntervals=[dict(allBandOwners=[1])]))
 def test_deterministic_path(self):
  c=[R(0,0),R(1,0),R(2,0)];g=complete_graph(c,O((3,0),(3,1)));a=dict(exactXZEndpoints=[(0,0),(0,1)]);m=dict(completePositiveIntervals=[dict(allBandOwners=[0])]);self.assertEqual(source_boundary_integration(c,g,a,m),source_boundary_integration(c,g,a,m))
 def test_one_pair_chunks_equal_complete_graph(self):
  class CP:
   def map(self,label,items,compute):return [r for x in items for r in compute([x])]
  c=[R(0,0),R(1,0),R(1,1)];self.assertEqual(complete_graph(c,[]),complete_graph(c,[],CP()))
 def test_two_pair_chunks_equal_all_pairs(self):
  class CP:
   def map(self,label,items,compute):return [r for i in range(0,len(items),2)for r in compute(items[i:i+2])]
  c=[R(0,0),R(1,0),R(1,1),R(2,0)];self.assertEqual(complete_graph(c,O((3,0),(3,1))),complete_graph(c,O((3,0),(3,1)),CP()))
 def test_missing_checkpoint_pair_rejected(self):
  class CP:
   def map(self,label,items,compute):return []
  with self.assertRaises(AssertionError):complete_graph([R(0,0),R(1,0)],[],CP())
if __name__=='__main__':unittest.main()
