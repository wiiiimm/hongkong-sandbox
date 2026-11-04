import unittest
from fractions import Fraction as F
from exact_pinch_local_positive_edge_expansion_v1_20261011 import select
class Tests(unittest.TestCase):
 def setUp(self):self.b={'allBoundaryAtomicEdges':[{'allOriginalIncidences':[{'start':[0,0],'end':[2,0]}]}]};self.r={'boundaryAtom':0,'retainedFace':7,'oppositeDirectedBoundaryEdge':True,'exactPositiveParameterInterval':[F(0),F(1,2)],'exactCurrent3DCompatible':False}
 def run_select(self,p,r=None):return select(self.b,[self.r if r is None else r],p)['completeSelectedRetainedFaces']
 def test_endpoint(self):self.assertEqual(self.run_select([(0,0)]),[7])
 def test_interval_endpoint(self):self.assertEqual(self.run_select([(1,0)]),[7])
 def test_exact_interior(self):self.assertEqual(self.run_select([(F(1,3),0)]),[7])
 def test_no_close_snap(self):self.assertEqual(self.run_select([(1,F(1,10**30))]),[])
 def test_partial_not_at_pinch(self):self.assertEqual(self.run_select([(2,0)]),[])
 def test_foreign_boundary(self):self.assertEqual(self.run_select([(3,0)]),[])
 def test_same_side(self):self.assertEqual(self.run_select([(0,0)],dict(self.r,oppositeDirectedBoundaryEdge=False)),[])
 def test_point_only_rejected(self):
  with self.assertRaises(AssertionError):self.run_select([(0,0)],dict(self.r,exactPositiveParameterInterval=[0,0]))
 def test_wrong_height_is_not_support_credit(self):
  d=select(self.b,[self.r],[(0,0)]);self.assertEqual(d['completeSelectedRetainedFaces'],[7]);self.assertFalse(d['current3DCompatibilityCredited'])
 def test_deterministic_dedup(self):self.assertEqual(select(self.b,[self.r,self.r],[(1,0),(0,0)])['completeSelectedRetainedFaces'],[7])
if __name__=='__main__':unittest.main()
