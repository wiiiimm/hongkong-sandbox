"""Independent complete-source/current spatial counterexamples, no physical credit."""
import copy,unittest
from test_no1_garden_original_overhead_roof_edge_identity_20261010 import fixture
from no1_garden_original_overhead_roof_edge_identity_20261010 import named_proof,UID,FOREIGN
class SpatialGuards(unittest.TestCase):
 def test_other_foreign_actor_stays_foreign(self):
  x=fixture();f=copy.deepcopy(next(b for b in x[4] if b['uid']==FOREIGN));f['uid']='unrelated-real-overlap-fixture';x[4].append(f);p=named_proof(*x);self.assertFalse(p['passed']);self.assertIn('complete-source-current-spatial-bound',p['reasons'])
 def test_current_target_missing_coverage_stays_failure(self):
  x=fixture();b=next(b for b in x[4] if b['uid']==UID);b['rings'].append([[1000,1000],[1010,1000],[1010,1010],[1000,1010],[1000,1000]]);x[1]['source']['building']=copy.deepcopy(b);p=named_proof(*x);self.assertFalse(p['passed']);self.assertLess(p['independentFullSourceSpatialChecks']['current']['targetCoverage'],.95)
 def test_separate_foreign_identity_mismatch_rejected(self):
  x=fixture();next(b for b in x[4] if b['uid']==FOREIGN)['buildingCSUID']='3396115261P20060312'
  with self.assertRaises(AssertionError):named_proof(*x)
 def test_foreign_faces_missing_rejected(self):
  x=fixture();x[3]=x[3][:-1]
  with self.assertRaises(AssertionError):named_proof(*x)
 def test_all_actual_actors_remain_and_no_whole_body_overhead(self):
  x=fixture();p=named_proof(*x);self.assertEqual(p['completeCurrentForeignActorsRetained'],x[4]);self.assertLess(x[2][p['completeOriginalMainBodyFaceIds'],:,1].min(),x[3][:,:,1].max());self.assertFalse(p['foreignRemoval']);self.assertFalse(p['foreignTerrainExemption']);self.assertFalse(p['foreignCollisionExemption']);self.assertFalse(p['physicalAccepted'])
if __name__=='__main__':unittest.main()
