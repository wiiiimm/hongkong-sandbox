"""Focused adverse fixtures; associations remain context, never opening/root credit."""
import unittest
import numpy as np
import west_wing26195_body108_113_strict_host_association_draft_v1_20261012 as H
from test_complete_original_lower_opening_mounts_v2_20261011 import box,roof
class Tests(unittest.TestCase):
 def run108(self,b=None,h=None):
  b=box()[:8] if b is None else b;h=roof() if h is None else h;t=np.concatenate([b,h]);ids=list(range(len(b)));hs=list(range(len(b),len(t)));return H.associate(t,ids,hs,'body108-minimum-edge-context',expected_binding=H.binding(t,ids,hs))
 def test_two_cycles_retained_not_opening(self):
  r=self.run108();self.assertTrue(r['allFourMinimumEdgesWithinFixedBandContextOnly']);self.assertTrue(r['unchangedOpeningV3Rejection']['rejected']);self.assertFalse(r['completeLowerOpeningAssociated']);self.assertEqual(len(r['completeSourceTopology']['completeDirectedBoundaryCycles']),2)
 def test_nonplanar_higher_cycle_retained(self):
  b=box()[:8];b[:,:,1]=np.where(b[:,:,1]==1,1+b[:,:,0]*.02+b[:,:,2]*.03,b[:,:,1]);self.assertTrue(self.run108(b)['higherOpeningClosed'] is False)
 def test_disconnected_closed_tetrahedron_rejected(self):
  b=box()[:8];p=np.array([[3,0,0],[4,0,0],[3,1,0],[3,0,1]],float);extra=p[[[0,2,1],[0,1,3],[0,3,2],[1,2,3]]]
  with self.assertRaises(AssertionError):self.run108(np.concatenate([b,extra]))
 def test_nonmanifold_rejected(self):
  b=box()[:8]
  with self.assertRaises(AssertionError):self.run108(np.concatenate([b,b[:1]]))
 def test_winding_rejected(self):
  b=box()[:8];b[0]=b[0,::-1]
  with self.assertRaises(AssertionError):self.run108(b)
 def test_point_host_not_complete(self):self.assertFalse(self.run108(h=np.array([[[-1,0,-1],[0,0,0],[-1,0,0]]]))['allFourMinimumEdgesWithinFixedBandContextOnly'])
 def test_partial_host_not_complete(self):self.assertFalse(self.run108(h=roof(xhi=.5))['allFourMinimumEdgesWithinFixedBandContextOnly'])
 def test_outside_fixed_band(self):self.assertFalse(self.run108(box(bottom=.11)[:8])['allFourMinimumEdgesWithinFixedBandContextOnly'])
 def test_multiple_height_planes_not_nearest_only(self):self.assertFalse(self.run108(h=np.concatenate([roof(),roof(y=.5)]))['allFourMinimumEdgesWithinFixedBandContextOnly'])
 def test_changed_source_binding(self):
  t=np.concatenate([box()[:8],roof()]);pin=H.binding(t,list(range(8)),[8,9]);t[0,0,1]+=.001
  with self.assertRaises(AssertionError):H.associate(t,list(range(8)),[8,9],'body108-minimum-edge-context',expected_binding=pin)
 def test_whole_two_faces(self):
  t=np.concatenate([roof(y=.01),roof()]);r=H.associate(t,[0,1],[2,3],'body113-whole-two-face-surface-context',expected_binding=H.binding(t,[0,1],[2,3]));self.assertTrue(r['completeTwoFaceFixedBandAssociationContextOnly']);self.assertFalse(r['wholeBodySupportCredit'])
 def test_two_face_hole(self):
  t=np.concatenate([roof(y=.01),roof(xhi=.5)]);r=H.associate(t,[0,1],[2,3],'body113-whole-two-face-surface-context',expected_binding=H.binding(t,[0,1],[2,3]));self.assertFalse(r['completeTwoFaceFixedBandAssociationContextOnly'])
 def test_strict_host_selection_all_overlapping_planes(self):
  t=np.concatenate([box()[:8],roof(),roof(y=.5),roof()+[3,0,0]]);records=[dict(strictPositiveFiniteProved=True,ordinaryFiniteProved=True,completeProjectionCovered=True)for _ in t];r=H.strict_hosts(t,list(range(8,14)),list(range(8)),records);self.assertEqual(r['selectedWholeFiniteHostIDs'],[8,9,10,11]);self.assertEqual(r['allExcludedStrictHostIDs'],[12,13])
 def test_uncertified_host_excluded(self):
  t=np.concatenate([box()[:8],roof()]);records=[dict(strictPositiveFiniteProved=False)for _ in t];self.assertEqual(H.strict_hosts(t,[8,9],list(range(8)),records)['selectedWholeFiniteHostIDs'],[])
if __name__=='__main__':unittest.main()
