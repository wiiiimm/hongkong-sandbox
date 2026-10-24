"""DRAFT branch and finite rendered seam counterexamples; awaits ROOT execution approval."""
import unittest
from fractions import Fraction as F
from exact_branch_aware_rendered_nodes_seams_v1_20261011 import BranchNodes,actual_point,whole_rendered_seam
class NodesSeams(unittest.TestCase):
 def test_shared_node_once(self):
  n=BranchNodes();self.assertIs(n.add((0,0),'a',1),n.add((0,0),'a',1))
 def test_same_branch_conflict(self):
  n=BranchNodes();n.add((0,0),'a',1)
  with self.assertRaises(AssertionError):n.add((0,0),'a',2)
 def test_unbound_split(self):
  n=BranchNodes();n.add((0,0),'a',1)
  with self.assertRaises(AssertionError):n.add((0,0),'b',2)
 def test_bound_original_step(self):
  n=BranchNodes({(F(0),F(0)):dict(sourceInducedDifferentBranches=True,sourceFacetIDs=[5,9],exactBranchHeights={'a':1,'b':2})});n.add((0,0),'a',1);self.assertEqual(n.add((0,0),'b',2)['exactPoint'][1],2)
 def test_wrong_bound_height(self):
  n=BranchNodes({(F(0),F(0)):dict(sourceInducedDifferentBranches=True,sourceFacetIDs=[5,9],exactBranchHeights={'a':1,'b':2})});n.add((0,0),'a',1)
  with self.assertRaises(AssertionError):n.add((0,0),'b',3)
 def test_nonfinite(self):
  with self.assertRaises(AssertionError):actual_point((0,float('inf'),0))
 def test_whole_exact_opposite(self):self.assertTrue(whole_rendered_seam((0,0,0),(2,0,0),[((2,0,0),(0,0,0))])['wholeFiniteRenderedSeamCovered'])
 def test_complete_tjunction(self):self.assertTrue(whole_rendered_seam((0,0,0),(2,0,0),[((2,0,0),(1,0,0)),((1,0,0),(0,0,0))])['wholeFiniteRenderedSeamCovered'])
 def test_partial_interval(self):self.assertFalse(whole_rendered_seam((0,0,0),(2,0,0),[((1,0,0),(0,0,0))])['wholeFiniteRenderedSeamCovered'])
 def test_point_only(self):self.assertFalse(whole_rendered_seam((0,0,0),(2,0,0),[((2,0,0),(3,0,0))])['wholeFiniteRenderedSeamCovered'])
 def test_wrong_height(self):self.assertFalse(whole_rendered_seam((0,0,0),(2,0,0),[((2,F(1,1024),0),(0,F(1,1024),0))])['wholeFiniteRenderedSeamCovered'])
 def test_same_direction(self):self.assertFalse(whole_rendered_seam((0,0,0),(2,0,0),[((0,0,0),(2,0,0))])['wholeFiniteRenderedSeamCovered'])
 def test_cast_cut_not_on_whole_original(self):
  a=(0,0,0);b=(1,0,3);p=(F(1,3),0,1)
  self.assertFalse(whole_rendered_seam(a,b,[(b,p),(p,a)])['wholeFiniteRenderedSeamCovered'])
if __name__=='__main__':unittest.main()
