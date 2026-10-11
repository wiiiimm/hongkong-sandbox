"""Hermetic immutable captured-current adapter counterexamples, not live replay."""
import unittest,copy
from run import read
import lippo_tower_current_basic_complete_role_current_bound_v2_20261011 as k
class CurrentBoundTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.geo=read(k.INPUT/'complete-current-geometry.json.gz');cls.old=read(k.HISTORICAL/'complete-current-geometry.json.gz');cls.receipt=read(k.ROLE/'result.json')
 def reject(self,fn):
  g=copy.deepcopy(self.geo);fn(g)
  with self.assertRaises((AssertionError,KeyError,ValueError,TypeError)):k.geometry_equivalence(g,self.old)
 def test_exact_complete_semantic_geometry_matches_new_global_current(self):self.assertTrue(k.geometry_equivalence(self.geo,self.old))
 def test_false_end_fence(self):self.reject(lambda g:g.update(startAndEndInputHashesVerified=False))
 def test_terrain_edit(self):self.reject(lambda g:g.update(terrainGeometryChanges=1))
 def test_source_edit(self):self.reject(lambda g:g.update(sourceGeometryChanges=1))
 def test_absent_original_podium_root_credit(self):self.reject(lambda g:g.update(originalGovernmentPodiumUsedAsSupport=True))
 def test_source_hash_changed(self):self.reject(lambda g:g['row'].update(sourceSHA256='0'*64))
 def test_actual_literal_unused_position_changed(self):self.reject(lambda g:g['row']['completeLiteralWorldPosition'].__setitem__(-1,0))
 def test_actual_left_float32_position_changed(self):self.reject(lambda g:g['row']['completeExplicitLeftAssociatedFloat32WorldPosition'].__setitem__(0,0))
 def test_actual_balanced_float32_position_changed(self):self.reject(lambda g:g['row']['completeExplicitBalancedFloat32WorldPosition'].__setitem__(0,0))
 def test_actual_mesh_matrix_changed(self):self.reject(lambda g:g['row']['actualRenderMeshes'][0]['matrixWorldFloat64'].__setitem__(12,0))
 def test_current_basic_carrier_face_missing(self):self.reject(lambda g:g['completeCurrentBasicGeometry'][0]['index'].pop())
 def test_current_foreign_basic_omission(self):self.reject(lambda g:g['completeCurrentBasicGeometry'].pop())
 def test_current_foreign_native_omission(self):self.reject(lambda g:g['completeNearbyNativeGeometry'].clear())
 def test_current_native_world_changed(self):self.reject(lambda g:g['completeNearbyNativeGeometry'][0]['completeLiteralWorldPosition'].__setitem__(0,0))
 def test_current_ground_face_changed(self):self.reject(lambda g:g['completeCurrentDrawnTerrain']['position'].__setitem__(0,0))
 def test_current_ground_face_missing(self):self.reject(lambda g:g['completeCurrentDrawnTerrain']['index'].pop())
 def test_original_index_changed(self):self.reject(lambda g:g['row']['completeOriginalIndex'].__setitem__(0,123))
 def test_actual_source_proposal_receipt_all_immediate_pins(self):self.assertTrue(k.receipt_pins(self.receipt))
 def test_receipt_duplicate_ref(self):
  r=copy.deepcopy(self.receipt);r['evidenceRefs'].append(r['evidenceRefs'][0])
  with self.assertRaises(AssertionError):k.receipt_pins(r)
 def test_receipt_bad_sha(self):
  r=copy.deepcopy(self.receipt);r['evidenceRefs'][0]['sha256']='0'*64
  with self.assertRaises(AssertionError):k.receipt_pins(r)
 def test_receipt_path_escape(self):
  r=copy.deepcopy(self.receipt);r['evidenceRefs'][0]['path']='../../outside'
  with self.assertRaises(AssertionError):k.receipt_pins(r)
if __name__=='__main__':unittest.main()
