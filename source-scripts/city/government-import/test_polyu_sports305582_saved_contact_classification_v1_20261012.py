import unittest
from fractions import Fraction as F
from polyu_sports305582_saved_contact_classification_helper_v1_20261012 import classify
class Tests(unittest.TestCase):
 def setUp(self):self.a=[(0,0,0),(2,0,0),(0,2,0)]
 def record(self,points,dimension,coplanar):return dict(exactPoints=[[str(v)for v in p]for p in points],dimension=dimension,nonzeroExactCoplanarPlanes=coplanar)
 def test_whole_duplicate(self):self.assertTrue(classify(self.record(self.a,2,True),self.a,self.a)['exactEqualWholeFiniteTriangleVertexSets'])
 def test_reversed_duplicate(self):self.assertTrue(classify(self.record(self.a,2,True),self.a,self.a[::-1])['exactEqualWholeFiniteTriangleVertexSets'])
 def test_partial_patch_not_duplicate(self):
  b=[(0,0,0),(1,0,0),(0,1,0)];x=classify(self.record(b,2,True),self.a,b);self.assertFalse(x['exactEqualWholeFiniteTriangleVertexSets']);self.assertFalse(x['entireSourceTriangleContainedInActorTriangle']);self.assertTrue(x['entireActorTriangleContainedInSourceTriangle'])
 def test_proper_noncoplanar_segment(self):
  b=[(F(1,2),-1,-1),(F(1,2),3,-1),(F(1,2),1,1)];x=classify(self.record([(F(1,2),0,0),(F(1,2),F(3,2),0)],1,False),self.a,b);self.assertTrue(x['noncoplanarBothRelativeInteriorSegment'])
 def test_boundary_line_not_proper(self):
  b=[(0,0,0),(2,0,0),(1,0,1)];self.assertFalse(classify(self.record([(0,0,0),(2,0,0)],1,False),self.a,b)['noncoplanarBothRelativeInteriorSegment'])
 def test_point_cannot_be_proper(self):
  b=[(0,0,0),(0,0,1),(1,0,1)];self.assertFalse(classify(self.record([(0,0,0)],0,False),self.a,b)['noncoplanarBothRelativeInteriorSegment'])
 def test_offplane_saved_witness_rejected(self):
  with self.assertRaises(AssertionError):classify(self.record([(0,0,F(1,1000000))],0,True),self.a,self.a)
 def test_changed_dimension_rejected(self):
  with self.assertRaises(AssertionError):classify(self.record(self.a,1,True),self.a,self.a)
if __name__=='__main__':unittest.main()
