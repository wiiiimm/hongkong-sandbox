"""Actual source fixtures and counterexamples for one named podium interpretation."""
import unittest
from copy import deepcopy
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from yoho_eight_related_original_podium_identity_20261009 import named_proof,RELATED
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-yoho-eight-current-full-cell-preflight-20261009'
ROW=read(DOC/'selection.json.gz')['rows'][0];PREVIOUS=read(DOC/'raw-full-cell-proof.json');FORMS=read(DOC/'all-current-forms.json.gz')['forms'];EVIDENCE=read(BASE/'government-xl-yoho-eight-primary-podium-discovery-20261009/original-source-lookup.json.gz')
TOWER=decode_original_world_triangles((ROOT/ROW['candidate']['path']).read_bytes());PODIUM=decode_original_world_triangles((HERE/'local/government-xl-five-more-original-supports-current-inputs-20261007/assets/d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167.glb.gz').read_bytes())
class ActualYohoFixtures(unittest.TestCase):
 def values(self):return [deepcopy(PREVIOUS),deepcopy(ROW),TOWER.copy(),PODIUM.copy(),deepcopy(FORMS),deepcopy(EVIDENCE)]
 def reject(self,mutate):
  args=self.values();mutate(args)
  with self.assertRaises((AssertionError,KeyError,StopIteration)):named_proof(*args)
 def test_actual_complete_originals(self):
  p=named_proof(*self.values());self.assertTrue(p['passed']);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['installationApproved']);self.assertEqual(p['completeOriginalComponentsRetained'],953);self.assertEqual(p['knownOriginalUnattachedComponentsRetained'],143);self.assertGreater(p['primaryChildOutsideCarvedPodiumM2'],350);self.assertEqual(len(p['allOtherCurrentFormsRetained']),len(FORMS));self.assertFalse(p['currentPodiumCollisionExemption']);self.assertFalse(p['currentPodiumTerrainExemption'])
 def test_wrong_uid(self):self.reject(lambda a:a[1].update(uid='landsd/121143:0'))
 def test_wrong_model(self):self.reject(lambda a:a[1].update(modelId='B218383358801063C0'))
 def test_wrong_original_sha(self):self.reject(lambda a:a[1].update(sourceSHA256='0'*64))
 def test_y_only_original_mutation(self):self.reject(lambda a:a[2].__setitem__((0,0,1),a[2][0,0,1]+.001))
 def test_face_removed(self):self.reject(lambda a:a.__setitem__(2,a[2][:-1]))
 def test_podium_world_mutation(self):self.reject(lambda a:a[3].__setitem__((0,0,2),a[3][0,0,2]+.001))
 def test_source_graph_missing(self):self.reject(lambda a:a[0]['originalOwnership'].update(sourceGraphVerified=False))
 def test_current_whole_cell_missing(self):self.reject(lambda a:a[0]['geographicCell'].update(targetCoversWholeCell=False))
 def test_original_whole_cell_missing(self):self.reject(lambda a:a[0]['geographicCell'].update(originalProjectionCoversWholeCell=False))
 def test_duplicate_primary(self):self.reject(lambda a:a[5]['primaryRecords'].append(deepcopy(a[5]['primaryRecords'][0])))
 def test_inactive_primary(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(Status='Inactive'))
 def test_wrong_primary_building_id(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(BuildingID=1))
 def test_wrong_creation_date(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(DateCreate=0))
 def test_wrong_georef(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(GeoRefNo='2179133650'))
 def test_wrong_primary_type(self):self.reject(lambda a:a[5]['primaryRecords'][1]['attributes'].update(BuildingBlockType='Tower'))
 def test_missing_specific_structure(self):self.reject(lambda a:a[5]['exactRelations'].pop())
 def test_wrong_relation_structure(self):self.reject(lambda a:a[5]['exactRelations'][0]['attributes'].update(BuildingStructureID=5285253))
 def test_same_permit_wrong_structure_role(self):self.reject(lambda a:a[5]['exactStructures'][1]['attributes'].update(OPBlockType='Tower'))
 def test_wrong_specific_permit(self):self.reject(lambda a:a[5]['exactStructures'][0]['attributes'].update(OPNo='NT73/91'))
 def test_wrong_original_podium_sha(self):self.reject(lambda a:a[5]['rows'][1]['model']['asset'].update(sha256='0'*64))
 def test_wrong_original_podium_key(self):self.reject(lambda a:a[5]['rows'][1].update(sourceKey='other/Podium'))
 def test_missing_actual_current_podium(self):self.reject(lambda a:a.__setitem__(4,[b for b in a[4] if b['uid']!=RELATED]))
 def test_current_podium_wrong_type(self):self.reject(lambda a:next(b for b in a[4] if b['uid']==RELATED).update(structureType='Tower'))
 def test_current_podium_wrong_stable_identity(self):self.reject(lambda a:next(b for b in a[4] if b['uid']==RELATED).update(buildingCSUID='2187833636P20060609'))
 def test_changed_current_source_form(self):self.reject(lambda a:next(b for b in a[4] if b['uid']==ROW['uid'])['rings'][0][0].__setitem__(0,-12000))
 def test_shifted_primary_coverage(self):
  def move(a):
   for ring in a[5]['primaryRecords'][0]['geometry']['rings']:
    for point in ring:point[0]+=100
  self.reject(move)
 def test_same_name_and_permit_actor_is_still_foreign(self):
  def foreign(a):
   b=deepcopy(next(b for b in a[4] if b['uid']==RELATED));b.update(uid='foreign:same-site',name='Yoho Town Block 8',OPNo='NT21/2004(OP)',buildingCSUID='foreign');a[4].append(b)
  self.reject(foreign)
 def test_other_source_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('original-world-pose-or-bounds');p=named_proof(*a);self.assertFalse(p['passed']);self.assertIn('original-world-pose-or-bounds',p['reasons'])
 def test_other_cell_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('different-whole-cell-failure');p=named_proof(*a);self.assertFalse(p['passed']);self.assertIn('different-whole-cell-failure',p['reasons'])
if __name__=='__main__':unittest.main()
