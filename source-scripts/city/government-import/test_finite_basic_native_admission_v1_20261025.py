"""Exercise finite-profile refusal paths using exact frozen evidence, without DB writes."""
import copy,json,unittest
from unittest.mock import patch
from pathlib import Path
import finite_basic_native_admission_v1_20261025 as admission
BASE=admission.BASE
CFG=admission.read(BASE/'government-xl-beverly-k-finite-original-install-config-v1-20261025.json')
REVIEW=admission.read(BASE/CFG['review']/'ROOT-PHYSICAL-REVIEW.json')

def local_receipt(folder):
 result=admission.read(folder/'result.json')
 return result,{r['path']:r['sha256']for r in result['evidenceRefs']}

class FiniteAdmission(unittest.TestCase):
 def run_profile(self,review=None,change=None):
  original=admission.read
  def read(path):
   data=original(path)
   return change(path,data)if change else data
  with patch.object(admission,'authenticate',side_effect=local_receipt),patch.object(admission,'read',side_effect=read):return admission.replay(CFG,review or copy.deepcopy(REVIEW))
 def test_complete_frozen_profile_replays(self):self.assertTrue(self.run_profile())
 def test_canonical_result_cannot_be_relabelled(self):
  q=copy.deepcopy(REVIEW);q['completeFourWorldCanonicalRetainedBasicSupport']=True
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_missing_finite_approval(self):
  q=copy.deepcopy(REVIEW);q['completeFourWorldFiniteRetainedBasicSupport']=False
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_changed_source_rejected(self):
  q=copy.deepcopy(REVIEW);q['sourceSHA256ByUid'][next(iter(CFG['sources']))]='0'*64
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_retained_native_approval_not_rewritten(self):
  q=copy.deepcopy(REVIEW);q['retainedNativeEntries']['landsd/255939:0']['publicationApproved']=True
  with self.assertRaises(AssertionError):self.run_profile(q)
 def test_omitted_mode_rejected(self):
  def change(path,data):
   if str(path).endswith('mode-checks.json.gz'):data['rows'].pop()
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_finite_native_scan_must_be_complete(self):
  def change(path,data):
   if str(path).endswith('255543:0--255939:0--original.json.gz'):data['sourceFacesOmitted']=1
   return data
  with self.assertRaises(AssertionError):self.run_profile(change=change)
 def test_missing_retained_image_rejected(self):
  q=copy.deepcopy(REVIEW);q['retainedImagesActuallyViewed'].pop()
  with self.assertRaises(AssertionError):self.run_profile(q)
if __name__=='__main__':unittest.main()
