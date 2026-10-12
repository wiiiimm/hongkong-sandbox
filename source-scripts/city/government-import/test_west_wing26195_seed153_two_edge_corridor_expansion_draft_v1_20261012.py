"""Focused draft schema/source gates; existing exact segment tests remain separate."""
import unittest,copy
import numpy as np
import west_wing26195_seed153_two_edge_corridor_expansion_draft_v1_20261012 as D
class Gates(unittest.TestCase):
 def setUp(self):
  self.w=np.zeros((44546,3,3),dtype='<f8');a=[0,0,0];b=[1,0,0];c=[1,2,0];d=[0,2,0];e=[1,2,-1]
  self.w[153]=[a,b,c];self.w[154]=[c,d,a];self.w[44545]=[c,e,d];self.rows=[None]*44546
  self.rows[154]=dict(strictPositiveFiniteProved=False,ordinaryFiniteProved=True,completeProjectionCovered=True)
  self.rows[44545]=dict(strictPositiveFiniteProved=True,ordinaryFiniteProved=True,completeProjectionCovered=True)
 def run_gate(self):return D.source_context(self.w,self.rows)
 def test_true_edge_ordinary_steep_context(self):self.assertEqual([x['faces']for x in self.run_gate()],[[153,154],[154,44545]])
 def test_failed_ordinary_wall_rejected(self):
  self.rows[154]['ordinaryFiniteProved']=False
  with self.assertRaises(AssertionError):self.run_gate()
 def test_missing_wall_coverage_rejected(self):
  self.rows[154]['completeProjectionCovered']=False
  with self.assertRaises(AssertionError):self.run_gate()
 def test_missing_cap_strict_rejected(self):
  self.rows[44545]['strictPositiveFiniteProved']=False
  with self.assertRaises(AssertionError):self.run_gate()
 def test_missing_cap_coverage_rejected(self):
  self.rows[44545]['completeProjectionCovered']=False
  with self.assertRaises(AssertionError):self.run_gate()
 def test_downward_cap_rejected(self):
  self.w[44545]=self.w[44545,[0,2,1]]
  with self.assertRaises(AssertionError):self.run_gate()
 def test_near_edge_not_exact_incidence(self):
  self.w[44545,2,0]+=2**-20
  with self.assertRaises(AssertionError):self.run_gate()
 def test_third_incident_face_rejected(self):
  self.w[1]=self.w[154]
  with self.assertRaises(AssertionError):self.run_gate()
if __name__=='__main__':unittest.main()
