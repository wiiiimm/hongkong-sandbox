import unittest,numpy as np
from fractions import Fraction as F
from exact_original_triangle_pair_column_gap_20261010 import verify
class Tests(unittest.TestCase):
 def tri(self,y):return np.array([[0.,y,0.],[1.,y,0.],[0.,y,1.]])
 def gap(self,s,g):return F(verify(s,g)['exactMinimumFiniteColumnGapM'])
 def test_flat_gap(self):self.assertEqual(self.gap(self.tri(1),self.tri(0)),1)
 def test_sloping_local_not_global_extrema(self):
  s=self.tri(0);s[1,1]=10;g=s.copy();g[:,1]-=.05;self.assertAlmostEqual(float(self.gap(s,g)),.05)
 def test_true_upward_burial(self):self.assertEqual(self.gap(self.tri(0),self.tri(1)),-1)
 def test_collapsed_ground_high_vertex_outside_source(self):
  s=np.array([[0.,1.,0.],[.1,1.,0.],[0.,1.,.1]]);g=np.array([[0.,0.,0.],[10.,10.,0.],[0.,0.,0.]]);self.assertAlmostEqual(float(self.gap(s,g)),.9)
 def test_vertical_ground_true_top_burial(self):
  g=np.array([[0.,0.,0.],[0.,2.,0.],[0.,0.,1.]]);self.assertEqual(self.gap(self.tri(1),g),-1)
 def test_vertical_source_local_lower_edge(self):
  s=np.array([[0.,0.,0.],[0.,2.,0.],[0.,2.,1.]]);g=np.array([[0.,0.,.9],[0.,0.,1.],[0.,0.,.95]]);self.assertAlmostEqual(float(self.gap(s,g)),1.8)
 def test_both_collapsed_vertical(self):
  s=np.array([[0.,3.,0.],[0.,4.,0.],[0.,4.,1.]]);g=np.array([[0.,1.,0.],[0.,2.,0.],[0.,2.,1.]]);self.assertEqual(self.gap(s,g),1)
 def test_point_ground_all_weights_feasible(self):self.assertEqual(self.gap(self.tri(1),np.array([[0.,0.,0.]]*3)),1)
 def test_point_source_same_column_top(self):self.assertEqual(self.gap(np.array([[0.,1.,0.]]*3),self.tri(0)),1)
 def test_closed_edge_touch_accounted(self):
  g=self.tri(0)+[1,0,0];self.assertTrue(verify(self.tri(1),g)['exactClosedHorizontalProjectionsMeet'])
 def test_disjoint_projections(self):self.assertFalse(verify(self.tri(1),self.tri(0)+[2,0,2])['exactClosedHorizontalProjectionsMeet'])
 def test_rank_inconsistent_parallel_lines(self):
  s=np.array([[0.,1.,0.],[0.,1.,1.],[0.,2.,1.]]);g=s+[1,-1,0];self.assertFalse(verify(s,g)['exactClosedHorizontalProjectionsMeet'])
 def test_reversed_winding_same_geometry(self):self.assertEqual(self.gap(self.tri(1)[::-1],self.tri(0)),1)
 def test_no_acceptance(self):
  r=verify(self.tri(1),self.tri(0));self.assertFalse(r['rootOrContactCredit']);self.assertFalse(r['installationApproved'])
 def test_nonfinite_rejects(self):
  s=self.tri(1);s[0,0]=np.nan
  with self.assertRaises(AssertionError):verify(s,self.tri(0))
if __name__=='__main__':unittest.main()
