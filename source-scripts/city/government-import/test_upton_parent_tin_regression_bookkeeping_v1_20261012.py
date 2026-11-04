"""Small adverse fixtures, no actor decoding/current capture/DB."""
import unittest
import numpy as np
from upton_parent_tin_regression_bookkeeping_v1_20261012 import closed_face_scope,ground_roi,finite_record,comparison,sha
class Tests(unittest.TestCase):
 def setUp(self):
  self.g=np.array([[[0,0,0],[0,0,2],[2,0,0]],[[2,0,0],[0,0,2],[2,0,2]]],float)
  self.f=np.array([[.2,1,.2],[.2,1,.5],[.5,1,.2]])
 def test_closed_touch_never_omitted(self):
  a=np.array([[[1,0,0],[2,0,0],[1,0,1]],[[3,0,0],[4,0,0],[3,0,1]]]);r=closed_face_scope(a,[0,0,1,1]);self.assertEqual(r['selectedFaceIDs'],[0]);self.assertEqual(r['strictClosedBoundsDisjointFaceIDs'],[1])
 def test_crossing_bounds_are_not_triangle_clip(self):
  r=closed_face_scope(np.array([[[-1,0,.5],[2,0,.5],[0,1,.5]]]),[0,0,1,1]);self.assertEqual(r['selectedFaceIDs'],[0]);self.assertFalse(r['wholeFaceWithinCapturedDomain'][0]);self.assertTrue(r['noTriangleClipping'])
 def test_unused_scope_does_not_drop_zero_triangle(self):
  r=closed_face_scope(np.array([[[0,1,0]]*3,[[4,1,4]]*3]),[0,0,1,1]);self.assertEqual(r['completeFaces'],2);self.assertEqual(r['selectedFaceIDs'],[0])
 def test_nonfinite_world_rejected(self):
  a=np.array([self.f]);a[0,0,0]=np.nan
  with self.assertRaises(AssertionError):closed_face_scope(a,[0,0,1,1])
 def test_ground_roi_preserves_order_duplicates_and_vertical(self):
  g=np.concatenate([self.g,self.g[:1],np.array([[[0,0,0],[0,1,0],[0,1,1]]])]);ids,r=ground_roi(g,[[0,-10,0],[1,10,1]]);self.assertEqual(ids.tolist(),[0,1,2,3]);np.testing.assert_array_equal(r,g)
 def test_missing_ground_is_explicit_negative(self):
  r=finite_record(self.f,np.empty((0,3,3)));self.assertFalse(r['ordinaryBoundProved']);self.assertFalse(r['projectionCovered']);self.assertIsNone(r['exactLowerM'])
 def test_remote_ground_is_not_coverage(self):
  r=finite_record(self.f,self.g+np.array([10,0,10]));self.assertFalse(r['ordinaryBoundProved']);self.assertTrue(r['missingFiniteCandidate'])
 def test_existing_fixed_bound_accepts_minus_half(self):
  f=self.f.copy();f[:,1]=-.5;r=finite_record(f,self.g);self.assertTrue(r['ordinaryBoundProved'])
 def test_burial_below_fixed_bound_stays_negative(self):
  f=self.f.copy();f[:,1]=-.51;r=finite_record(f,self.g);self.assertFalse(r['ordinaryBoundProved'])
 def test_same_facet_different_ground_regression_not_hidden(self):
  a=finite_record(self.f,self.g);b=finite_record(self.f,self.g+np.array([0,2,0]));r=comparison(a,b,True);self.assertTrue(r['currentClearOriginalTINUnproved']);self.assertFalse(r['currentUnprovedOriginalTINClear'])
 def test_reuse_requires_exact_facet_and_ground(self):
  q=finite_record(self.f,self.g);old=dict(coarse=q['coarse'],paired=q['paired'],projectionCovered=q['projectionCovered'],ordinaryBoundProved=q['ordinaryBoundProved']);self.assertTrue(finite_record(self.f,self.g,old)['reusedImmutableFullProofVerbatim'])
  with self.assertRaises(AssertionError):finite_record(self.f+np.array([0,.01,0]),self.g,old)
  with self.assertRaises(AssertionError):finite_record(self.f,self.g+np.array([0,.01,0]),old)
 def test_outside_extraction_failure_not_declared_runtime_hole(self):
  a=finite_record(self.f,np.empty((0,3,3)));b=finite_record(self.f,self.g);r=comparison(a,b,False);self.assertTrue(r['currentUncoveredOutsideCapturedDomainIsNotRuntimeGap'])
 def test_different_facet_comparison_rejected(self):
  with self.assertRaises(AssertionError):comparison(finite_record(self.f,self.g),finite_record(self.f+np.array([0,.01,0]),self.g),True)
if __name__=='__main__':unittest.main()
