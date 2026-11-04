import copy,unittest
from verified_disjoint_manifest_rebind_20261009 import verify
class DisjointRebindTests(unittest.TestCase):
 def setUp(self):
  self.old=dict(officialModelCatalogues=['old'],terrainPatches=[],terrain='base');self.new={**self.old,'officialModelCatalogues':['old','new']}
  self.before=dict(terrain=[],native=[dict(id='a',completeWorldXZBounds=[-1,-1,1,1],source='a')]);self.after=copy.deepcopy(self.before);self.after['native'].append(dict(id='b',completeWorldXZBounds=[20,20,21,21],source='b'))
  self.hashes={'manifest':'old','source':'fixed','drawn-ground':'fixed'};self.current={**self.hashes,'manifest':'new'}
 def check(self):return verify(self.old,self.new,self.before,self.after,[-2,-2,2,2],expected_old_hashes=self.hashes,current_old_input_hashes=self.current,manifest_path='manifest',old_manifest_sha='old',new_manifest_sha='new')
 def test_disjoint_new_actor_leaves_all_numeric_inputs_unchanged(self):self.assertTrue(self.check()['verifiedDisjointGlobalManifestRebind'])
 def test_changed_current_drawn_ground_rejects(self):
  self.current['drawn-ground']='changed'
  with self.assertRaisesRegex(AssertionError,'input changed'):self.check()
 def test_source_change_rejects(self):
  self.current['source']='changed'
  with self.assertRaises(AssertionError):self.check()
 def test_omitted_original_input_rejects(self):
  self.current.pop('source')
  with self.assertRaisesRegex(AssertionError,'Omitted'):self.check()
 def test_new_actor_boundary_touch_rejects(self):
  self.after['native'][1]['completeWorldXZBounds']=[2,0,3,1]
  with self.assertRaisesRegex(AssertionError,'touches'):self.check()
 def test_removed_regional_actor_rejects(self):
  self.after['native'].pop(0)
  with self.assertRaisesRegex(AssertionError,'touches'):self.check()
 def test_new_regional_terrain_rejects(self):
  self.after['terrain']=[dict(id='surface',completeWorldXZBounds=[-3,-3,3,3],source='x')]
  with self.assertRaisesRegex(AssertionError,'touches'):self.check()
 def test_base_rendering_metadata_change_rejects(self):
  self.new['terrain']='other'
  with self.assertRaisesRegex(AssertionError,'Unclassified'):self.check()
 def test_duplicate_inventory_actor_rejects(self):
  self.after['native'].append(copy.deepcopy(self.after['native'][0]))
  with self.assertRaisesRegex(AssertionError,'Duplicate'):self.check()
 def test_nonfinite_new_actor_bounds_rejects(self):
  self.after['native'][1]['completeWorldXZBounds'][0]=float('nan')
  with self.assertRaisesRegex(AssertionError,'finite'):self.check()
if __name__=='__main__':unittest.main()
