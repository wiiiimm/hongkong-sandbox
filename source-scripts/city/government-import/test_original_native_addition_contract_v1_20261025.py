import copy,unittest
from original_native_addition_contract_v1_20261025 import verify
class ContractTests(unittest.TestCase):
 def fixture(self):
  forms=[{'uid':'landsd/new:0'},{'uid':'landsd/old:0'}]
  return dict(model_forms={f['uid']:f for f in forms},terrain_forms=forms,scope=dict(currentNativeActors=10,uids=['landsd/new:0'],terrainContacts=[],positiveAreaTerrainOverlaps=0,touchingNativeUids=['landsd/old:0'],intersectingForms=2),model_scope=dict(uids=['landsd/new:0'],rows=[dict(uid='landsd/new:0',currentNativeActorsChecked=10,nearbyNativeActors=[])]),regression=dict(uids=['landsd/new:0'],basicFlags=[],requiredNativeUids=['landsd/old:0'],nativeResolved=['landsd/old:0'],nativeRows=[dict(uid='landsd/old:0',passed=True,triangles=25,terrain=dict(newlyWhollyBuried=0,newlyUpwardWhollyBuried=0))]),retained_entries={'landsd/old:0':dict(triangles=25,publicationApproved=False)},sources={'landsd/new:0':'a'*64},terrain_targets=['landsd/new:0'],native_count=10,expected_count=2)
 def test_complete_proof_keeps_held_native_flag(self):
  a=self.fixture();before=copy.deepcopy(a['retained_entries']);self.assertEqual(len(verify(**a)),2);self.assertEqual(a['retained_entries'],before)
 def test_missing_native_is_rejected(self):
  a=self.fixture();a['retained_entries']={}
  with self.assertRaises(AssertionError):verify(**a)
 def test_failed_native_check_is_rejected(self):
  a=self.fixture();a['regression']['nativeRows'][0]['passed']=False
  with self.assertRaises(AssertionError):verify(**a)
 def test_incomplete_native_geometry_is_rejected(self):
  a=self.fixture();a['regression']['nativeRows'][0]['triangles']=24
  with self.assertRaises(AssertionError):verify(**a)
 def test_new_burial_is_rejected(self):
  for key in ['newlyWhollyBuried','newlyUpwardWhollyBuried']:
   a=self.fixture();a['regression']['nativeRows'][0]['terrain'][key]=1
   with self.assertRaises(AssertionError):verify(**a)
 def test_actual_model_contact_needs_different_review(self):
  a=self.fixture();a['model_scope']['rows'][0]['nearbyNativeActors']=[{'uid':'landsd/old:0'}]
  with self.assertRaises(AssertionError):verify(**a)
 def test_positive_terrain_overlap_needs_replacement_path(self):
  a=self.fixture();a['scope']['positiveAreaTerrainOverlaps']=1
  with self.assertRaises(AssertionError):verify(**a)
 def test_omitted_form_or_duplicate_native_is_rejected(self):
  a=self.fixture();a['terrain_forms']=a['terrain_forms'][:1]
  with self.assertRaises(AssertionError):verify(**a)
  a=self.fixture();a['regression']['nativeRows']*=2
  with self.assertRaises(AssertionError):verify(**a)
if __name__=='__main__':unittest.main()
