import unittest
from fractions import Fraction as F
from exact_original_3d_directed_edge_atom_census_v1_20261011 import census,parameter
class EdgeAtomTests(unittest.TestCase):
 def test_square_opposed_internal(self):
  r=census([[(0,0,0),(1,0,0),(1,0,1)],[(0,0,0),(1,0,1),(0,0,1)]]);self.assertEqual(len(r['allPositive3DBoundaryAtomIds']),4);self.assertFalse(r['allTwoSameDirectionAtomIds'])
 def test_same_winding_negative(self):
  r=census([[(0,0,0),(1,0,0),(1,0,1)],[(0,0,0),(0,0,1),(1,0,1)]]);self.assertEqual(len(r['allTwoSameDirectionAtomIds']),1)
 def test_nonmanifold_negative(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)],[(1,0,0),(0,0,0),(0,0,-1)],[(0,0,0),(1,0,0),(0,1,0)]]);self.assertEqual(len(r['allNonmanifoldAtomIds']),1)
 def test_partial_tjunction_positive(self):
  r=census([[(0,0,0),(2,0,0),(0,0,1)],[(1,0,0),(0,0,0),(0,0,-1)]]);self.assertTrue(any(x['incidenceCount']==2 for x in r['allExact3DAtomicEdges']));self.assertIn(F(1,2),r['allCompleteDirectedEdgeCutProofs'][0]['allExactOrderedCutParameters'])
 def test_wrong_height_not_joined(self):
  r=census([[(0,0,0),(2,0,0),(0,0,1)],[(1,F(1,2**70),0),(0,F(1,2**70),0),(0,0,-1)]]);self.assertTrue(all(x['incidenceCount']==1 for x in r['allExact3DAtomicEdges']))
 def test_point_contact_not_bridge(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)],[(0,0,0),(-1,0,0),(0,0,-1)]]);self.assertEqual(len(r['allPositive3DBoundaryAtomIds']),6)
 def test_crossing_without_original_vertex_no_edge_bridge(self):
  r=census([[(-1,0,0),(1,0,0),(0,0,1)],[(0,-1,0),(0,1,0),(0,0,-1)]]);self.assertTrue(all(x['incidenceCount']==1 for x in r['allExact3DAtomicEdges']))
 def test_vertical_real_face_preserved(self):
  r=census([[(0,0,0),(0,1,0),(0,1,1)]]);self.assertEqual(r['completeNonzeroFaces'],1);self.assertEqual(len(r['allPositive3DBoundaryAtomIds']),3)
 def test_zero_real_primitive_retained_no_bridge(self):
  r=census([[(0,0,0),(1,0,0),(2,0,0)]]);self.assertEqual(r['allExactZeroOriginalFaceIds'],[0]);self.assertFalse(r['allExact3DAtomicEdges'])
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):census([[(0,0,0),(float('inf'),1,0),(0,0,1)]])
 def test_exact_parameter_not_near(self):
  self.assertIsNone(parameter((F(0),F(0),F(0)),(F(2),F(0),F(0)),(F(1),F(1,2**100),F(0))))
 def test_negative_bucket_tjunction(self):
  r=census([[(-5,0,0),(5,0,0),(0,0,1)],[(0,0,0),(-5,0,0),(0,0,-1)]]);self.assertTrue(any(x['incidenceCount']==2 for x in r['allExact3DAtomicEdges']))
 def test_generated_join_two_source_edges_opposed(self):
  old=[(0,0,0),(1,0,0),(0,0,1)];new=[(1,1,0),(0,1,0),(0,1,-1)];join1=[(0,0,0),(1,1,0),(1,0,0)];join2=[(0,0,0),(0,1,0),(1,1,0)];r=census([old,new,join1,join2]);self.assertFalse(r['allTwoSameDirectionAtomIds']);self.assertFalse(r['allNonmanifoldAtomIds']);self.assertTrue(any(x['exactOpposedTwoIncidences']for x in r['allExact3DAtomicEdges']))
 def test_source_same_orientation_cannot_fake_join(self):
  old=[(0,0,0),(1,0,0),(0,0,1)];new=[(0,1,0),(1,1,0),(0,1,-1)];r=census([old,new,[(0,0,0),(1,1,0),(1,0,0)],[(0,0,0),(0,1,0),(1,1,0)]]);self.assertTrue(r['allTwoSameDirectionAtomIds'])
 def test_fractional_generated_endpoint_source_cut_exact(self):
  r=census([[(0,0,0),(1,0,0),(0,0,1)],[(F(1,3),0,0),(0,0,0),(0,1,0)]]);self.assertIn(F(1,3),r['allCompleteDirectedEdgeCutProofs'][0]['allExactOrderedCutParameters'])
 def test_checkpoint_reordered_partition_rejected(self):
  class Bad:
   def map(self,label,items,compute):return list(reversed(compute(items)))
  with self.assertRaises(AssertionError):census([[(0,0,0),(1,0,0),(0,0,1)]],Bad())
if __name__=='__main__':unittest.main()
