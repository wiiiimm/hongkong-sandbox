import copy
import unittest
from ocean_four_original_physical_review_v2_20261027 import verify_upper_attachment,MODES
from run import ROOT,read
class ExactUpperScopeTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import/government-xl-ocean-upper-buried-facet-attachment-v2-20261027';cls.saved={m:read(base/(m+'.json.gz'))for m in MODES};cls.ids=read(ROOT/'docs/astra-city/government-import/government-xl-ocean-upper-compound-role-views-v2-20261027/summary.json')['flaggedFaces']
 def test_actual_four_worlds_pass(self):self.assertTrue(verify_upper_attachment(self.saved,self.ids))
 def test_missing_coordinate_version_rejected(self):
  data=copy.deepcopy(self.saved);data.pop('literal')
  with self.assertRaises(AssertionError):verify_upper_attachment(data,self.ids)
 def test_duplicate_witness_hiding_missing_vertex_rejected(self):
  data=copy.deepcopy(self.saved);data['original']['rows'][0]=copy.deepcopy(data['original']['rows'][1])
  with self.assertRaises(AssertionError):verify_upper_attachment(data,self.ids)
 def test_added_path_rise_rejected(self):
  data=copy.deepcopy(self.saved);data['original']['rows'][0]['riseAboveEndpointsM']=.000001
  with self.assertRaises(AssertionError):verify_upper_attachment(data,self.ids)
 def test_different_parent_rejected(self):
  data=copy.deepcopy(self.saved);data['original']['rows'][0]['terminal']['contact']['peerUid']='landsd/1:0'
  with self.assertRaises(AssertionError):verify_upper_attachment(data,self.ids)
 def test_incidence_gate_cannot_expand(self):
  data=copy.deepcopy(self.saved);data['original']['rows'][0]['maximumResidualM']=.00101
  with self.assertRaises(AssertionError):verify_upper_attachment(data,self.ids)
if __name__=='__main__':unittest.main()
