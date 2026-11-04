"""Draft adverse fixtures for exact host inventory and source-bound mounting context."""
import unittest
import numpy as np
import west_wing26195_visual_mounting_interface_draft_v1_20261012 as H
class Tests(unittest.TestCase):
 def wall(self,x=0):return np.asarray([[[x,0,0],[x,0,1],[x,1,0]]],float)
 def test_whole_finite_edge(self):
  t=self.wall();r=H.diagnose_edge(t,[[0,0,0],[0,1,0]],[0]);self.assertTrue(r['wholePositiveLengthFiniteBandContext']);self.assertFalse(r['visualRoleAccepted'])
 def test_point_only_not_bridge(self):self.assertFalse(H.diagnose_edge(self.wall(),[[0,1,0],[0,2,0]],[0])['wholePositiveLengthFiniteBandContext'])
 def test_partial_host_not_complete(self):self.assertFalse(H.diagnose_edge(self.wall(),[[0,0,0],[0,2,0]],[0])['wholePositiveLengthFiniteBandContext'])
 def test_fixed_band_exceeded(self):self.assertFalse(H.diagnose_edge(self.wall(),[[.101,0,0],[.101,1,0]],[0])['wholePositiveLengthFiniteBandContext'])
 def test_actual_finite_foot_required(self):self.assertFalse(H.diagnose_edge(self.wall(),[[0,2,0],[0,3,0]],[0])['wholePositiveLengthFiniteBandContext'])
 def test_exact_closed_pruning_retains_boundary(self):
  r=H.edge_candidates(self.wall(.1),[[0,0,0],[0,1,0]],[0]);self.assertEqual(r['completeFiniteBandCandidateHostIDs'],[0])
 def test_higher_plane_exclusion_explicit(self):
  t=self.wall()+[0,4,0];r=H.edge_candidates(t,[[0,0,0],[0,1,0]],[0]);self.assertEqual(len(r['allExactClosed3DAABBExclusions']),1)
 def test_all_near_hosts_retained(self):
  t=np.concatenate([self.wall(),self.wall(.05)]);self.assertEqual(H.edge_candidates(t,[[0,0,0],[0,1,0]],[0,1])['completeFiniteBandCandidateHostIDs'],[0,1])
 def test_uncertified_host_not_credit(self):
  p=[dict(strictPositiveFiniteProved=False)];self.assertEqual(H.host_inventory(self.wall(),[0],p)['completeNotStrictHostFaces'],[0])
 def test_invalid_strict_saved_proof_rejected(self):
  p=[dict(strictPositiveFiniteProved=True,ordinaryFiniteProved=False,completeProjectionCovered=True)]
  with self.assertRaises(AssertionError):H.host_inventory(self.wall(),[0],p)
 def test_permutation_roof_included_without_height_change(self):
  t=np.asarray([[[0,0,0],[1,0,0],[0,0,1]]],float);r=H.diagnose_edge(t,[[0,0,0],[1,0,0]],[0]);self.assertTrue(r['wholePositiveLengthFiniteBandContext']);self.assertEqual(r['unchangedWholeSourceEdge'],[[0,0,0],[1,0,0]])
 def test_missing_host_not_complete(self):self.assertFalse(H.diagnose_edge(self.wall(),[[0,0,0],[0,1,0]],[])['wholePositiveLengthFiniteBandContext'])
if __name__=='__main__':unittest.main()
