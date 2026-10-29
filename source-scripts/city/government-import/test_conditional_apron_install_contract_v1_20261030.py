"""Fail-closed mutation checks around the actual reviewed pier evidence."""
import copy,json,unittest
from run import ROOT
from conditional_apron_install_contract_v1_20261030 import verify
FIXTURE=ROOT/'docs/astra-city/government-import/government-xl-disneyland-eastern75643-apron-current-visual-observations-v1-20261030/apron-install-contract-fixture.json'
class Contract(unittest.TestCase):
 def data(self):return json.loads(FIXTURE.read_text())
 def test_actual_completed_evidence(self):self.assertTrue(verify(**self.data())['completeLifecycleVerified'])
 def test_changed_or_derived_source_rejects(self):
  for field,value in [('sha256','0'*64),('uid','landsd/75642:0'),('variantId','derived'),('verticalPlacementOffsetHKPD',1),('publicationApproved',True)]:
   with self.subTest(field=field):
    d=self.data();d['models'][0][field]=value
    with self.assertRaises(AssertionError):verify(**d)
 def test_scope_expansion_rejects(self):
  d=self.data();d['models'][0]['suppressesBuildingUids'].append('way/1:0')
  with self.assertRaises(AssertionError):verify(**d)
 def test_new_basic_data_does_not_inherit_review(self):
  d=self.data();d['forms']['way/334029318:0']['height']=3
  with self.assertRaises(AssertionError):verify(**d)
 def test_missing_graphic_review_rejects(self):
  d=self.data();d['feature']['graphicInterpretationAccepted']=False
  with self.assertRaises(AssertionError):verify(**d)
 def test_missing_eviction_restore_rejects(self):
  d=self.data();d['lifecycle']['cases'][0]['canopyLifecycle']=[r for r in d['lifecycle']['cases'][0]['canopyLifecycle']if r['phase']!='evicted-return-base-only']
  with self.assertRaises(AssertionError):verify(**d)
 def test_geometry_changes_cannot_inherit_review(self):
  d=self.data();d['physical']['sourceGeometryChanges']=1
  with self.assertRaises(AssertionError):verify(**d)
if __name__=='__main__':unittest.main()
