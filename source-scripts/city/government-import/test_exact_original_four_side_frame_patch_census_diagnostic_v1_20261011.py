import unittest
import numpy as np
from exact_original_four_side_frame_patch_census_diagnostic_v1_20261011 import verify
def synthetic_frame():
 rings=[np.array([[0,0,z],[2,0,z],[2,1,z],[0,1,z]],float)for z in [0,.07,.14]];faces=[]
 for lower,upper in zip(rings,rings[1:]):
  for i in range(4):
   j=(i+1)%4;faces.extend([[lower[i],lower[j],upper[j]],[lower[i],upper[j],upper[i]]])
 return np.asarray(faces)
class CompleteFramePatchTests(unittest.TestCase):
 def test_complete_original_four_side_partition(self):
  w=synthetic_frame();r=verify(w,list(range(16)));self.assertTrue(r['verifiedCompleteFourSidePatchPartition']);self.assertEqual([len(p['completeOriginalPatchFacetIds'])for p in r['allFourCompleteOriginalSidePatches']],[4]*4);self.assertEqual(len(r['completeOppositePatchPairs']),2)
 def test_missing_facet_no_partial_patch_credit(self):self.assertFalse(verify(synthetic_frame(),list(range(15)))['verifiedCompleteFourSidePatchPartition'])
 def test_exact_zero_facet_no_bridge(self):
  w=synthetic_frame();w[0,2]=w[0,1];self.assertFalse(verify(w,list(range(16)))['verifiedCompleteFourSidePatchPartition'])
 def test_detached_side_no_patch(self):
  w=synthetic_frame();w[0]+=5;self.assertFalse(verify(w,list(range(16)))['verifiedCompleteFourSidePatchPartition'])
 def test_duplicate_facet_changes_topology(self):
  w=synthetic_frame();w[0]=w[1];self.assertFalse(verify(w,list(range(16)))['verifiedCompleteFourSidePatchPartition'])
 def test_duplicate_indices_rejected(self):
  with self.assertRaises(AssertionError):verify(synthetic_frame(),[0,0])
 def test_nonfinite_rejected(self):
  w=synthetic_frame();w[0,0,0]=float('inf')
  with self.assertRaises(AssertionError):verify(w,list(range(16)))
 def test_rotation_and_winding_do_not_create_role(self):
  w=synthetic_frame()[:,:,::-1][:,::-1];r=verify(w,list(range(16)));self.assertTrue(r['verifiedCompleteFourSidePatchPartition']);self.assertFalse(r['authoredRoleAccepted']);self.assertFalse(r['structuralRootOrBridgeCredit'])
if __name__=='__main__':unittest.main()
