"""Hermetic complete actual-source counterexamples; NOT current production replay."""
import copy, unittest
from lippo_tower_current_basic_mainbody_join_actual_fixture_v1_20261011 import fixture
from lippo_tower_current_basic_mainbody_join_role_v1_20261011 import verify, WORLD, NONRENDER
class ActualSourceJoinTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.base=fixture()
 def reject(self,fn):
  x=copy.deepcopy(self.base);fn(x)
  with self.assertRaises((AssertionError,KeyError,ValueError,IndexError,TypeError)):verify(x)
 def test_actual_complete_proposal(self):
  r=verify(self.base);self.assertFalse(r['physicalAccepted']);self.assertFalse(r['installationApproved']);self.assertFalse(r['governmentPodiumUsedAsRuntimeSupport']);self.assertEqual(len(r['rows']),4)
  for row in r['rows']:
   self.assertEqual(row['sourceZeroAreaUncredited'],NONRENDER);self.assertTrue(row['completeMainbodyNonzeroEdgePathProved']);self.assertTrue(any(p['completeExteriorFragments'] for p in row['allLowerFragments']))
 def test_source_hash(self):self.reject(lambda x:x.update(sourceSHA256='0'*64))
 def test_wrong_tower_uid(self):self.reject(lambda x:x['towerCurrentForm'].update(uid='landsd/1:0'))
 def test_wrong_tower_stable_id(self):self.reject(lambda x:x['towerCurrentForm'].update(buildingCSUID='other'))
 def test_wrong_tower_building_id(self):self.reject(lambda x:x['towerCurrentForm'].update(buildingId=1))
 def test_wrong_tower_type(self):self.reject(lambda x:x['towerCurrentForm'].update(structureType='Podium'))
 def test_changed_join_height(self):self.reject(lambda x:x['towerCurrentForm'].update(baseHeightHKPD=18.7))
 def test_wrong_carrier_uid(self):self.reject(lambda x:x['carrierCurrentForm'].update(uid='landsd/1:0'))
 def test_wrong_carrier_stable_id(self):self.reject(lambda x:x['carrierCurrentForm'].update(buildingCSUID='other'))
 def test_wrong_carrier_type(self):self.reject(lambda x:x['carrierCurrentForm'].update(structureType='Tower'))
 def test_changed_carrier_top(self):self.reject(lambda x:x['carrierCurrentForm'].update(topHeightHKPD=18.7))
 def test_changed_carrier_base(self):self.reject(lambda x:x['carrierCurrentForm'].update(baseHeightHKPD=4.2))
 def test_nonidentity_basic_matrix(self):self.reject(lambda x:x['carrierIdentityModelMatrix'].__setitem__(12,1))
 def test_source_mainbody_vertex_edit(self):self.reject(lambda x:x['worlds']['providerOriginal'].__setitem__((19,0,1),17.0))
 def test_actual_literal_vertex_edit(self):self.reject(lambda x:x['worlds']['actualLiteral'].__setitem__((19,0,1),17.0))
 def test_F32_vertex_edit(self):self.reject(lambda x:x['worlds']['explicitLeftAssociatedF32ModelMatrix'].__setitem__((19,0,1),17.0))
 def test_basic_vertex_edit(self):self.reject(lambda x:x['basic'].__setitem__((70,0,1),18.7))
 def test_current_ground_change(self):self.reject(lambda x:x.update(groundSHA256='0'*64))
 def test_missing_foreign_actor(self):self.reject(lambda x:x['otherForeignActors'].pop())
 def test_wrong_foreign_actor(self):self.reject(lambda x:x['otherForeignActors'][0].update(uid='landsd/999999:0'))
 def test_foreign_collision(self):self.reject(lambda x:x['otherForeignActors'][0]['trials'][0].update(completeContacts=[{'sourceFaceA':1}]))
 def test_foreign_record_omission(self):self.reject(lambda x:x['otherForeignActors'][0]['trials'][0].update(foreignFacesOmitted=1))
 def test_whole_BASIC_reapproval(self):self.reject(lambda x:x['carrierPaths'].update(wholeBasicReaccepted=True))
 def test_absent_government_podium_credit(self):self.reject(lambda x:x['carrierPaths'].update(originalGovernmentPodiumUsedAsSupport=True))
 def test_missing_grade_route(self):self.reject(lambda x:x['basicGraph']['strictlyExposedGradeWallToCapRoutes'].pop())
 def test_false_grade_exposure(self):self.reject(lambda x:x['basicGraph']['strictlyExposedGradeWallToCapRoutes'][0]['wallExposedOriginalVertexProof'].update(exactExposureLowerBoundM='0'))
 def test_upward_bottom_as_roof(self):self.reject(lambda x:x['basicFinite']['strictUpwardTopCapIDs'].append(17))
 def test_missing_full_source_facet(self):self.reject(lambda x:x['finite']['providerOriginal']['allOwnedFaces'].pop())
 def test_missing_lower_source_face(self):self.reject(lambda x:x['partition']['rows'][0]['completeSourceFacesBelowCurrentBasicTop'].pop())
 def test_missing_actual_lower_fragment(self):self.reject(lambda x:x['partition']['rows'][0]['completeFiniteClosedPrismIntersections'].pop())
 def test_zero_area_bridge_claim(self):self.reject(lambda x:x['partition']['rows'][0].update(zeroAreaRootOrBridgeCredit=True))
 def test_missing_zero_area_inventory(self):self.reject(lambda x:x['partition']['rows'][0]['completeNonrenderingOriginalSourceFaceIDs'].pop())
 def test_detached_part_interior_claim(self):self.reject(lambda x:x['partition']['rows'][0].update(originalComponentsWithGenuineCurrentBasicInterior=[6,7]))
 def test_literal_depth_cannot_round_to_1_5(self):self.reject(lambda x:x['partition']['rows'][1].update(maximumExactDepthBelowCurrentBasicTop='3/2'))
 def test_contact_omission_with_adjusted_count(self):
  def change(x):
   r=x['carrierContacts']['providerOriginal'];a=r['completeContacts'].pop();r['positiveFiniteContacts']-=int(a['positiveFiniteContact'])
  self.reject(change)
 def test_wrong_exact_contact_point(self):self.reject(lambda x:x['carrierContacts']['providerOriginal']['completeContacts'][0]['exactPoints'][0].__setitem__(1,'18'))
 def test_internal_component_interface_omission(self):self.reject(lambda x:x['carrierPaths']['upperRows'][0]['exactInternalOwnedPositiveInterfaces'].clear())
if __name__=='__main__':unittest.main()
