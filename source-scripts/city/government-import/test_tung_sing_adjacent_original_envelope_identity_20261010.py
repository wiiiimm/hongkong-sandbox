"""Real source counterexamples for Tung Sing's narrowly named envelope role."""
import unittest
from copy import deepcopy
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_adjacent_original_envelope_identity_20261010 import named_proof,RELATED
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-tung-sing-current-full-cell-preflight-20261010';REL=BASE/'government-xl-tung-sing-lei-tung-original-source-relationship-20261010'
ROW=read(DOC/'selection.json.gz')['rows'][0];PREVIOUS=read(DOC/'raw-full-cell-proof.json');FORMS=read(DOC/'all-current-forms.json.gz')['forms'];D=read(REL/'diagnostic.json.gz')
EVIDENCE={'rows':D['native'],'primaryRecords':D['primary'],'exactRelations':D['exactRelations'],'exactStructures':D['exactStructures'],'primaryPlanSHA256':digest((REL/'ha-estate-layout.pdf').read_bytes()),'primaryFloorPlanSHA256':digest((REL/'ha-tung-sing-floor-plan.pdf').read_bytes()),'completeOverlapFaceIds':D['allOverlapOriginalFaceIds'],'primaryNamedRelationship':{'towerName':'Tung Sing House','towerBlock':'E','adjacentStructure':'Commercial Complex (Carpark Under)','relationship':'adjacent connected source envelopes','legalOwnershipClaim':False,'surveyPrecisionClaim':False,'supportClaim':False}}
TOWER=decode_original_world_triangles((ROOT/ROW['candidate']['path']).read_bytes());PODIUM=decode_original_world_triangles((HERE/'local/xl-terrain-recovery-20261009-support-original-recovery/assets/368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15.glb.gz').read_bytes())
class ActualTungSingFixtures(unittest.TestCase):
 def values(self):return [deepcopy(PREVIOUS),deepcopy(ROW),TOWER.copy(),PODIUM.copy(),deepcopy(FORMS),deepcopy(EVIDENCE)]
 def reject(self,mutate):
  args=self.values();mutate(args)
  with self.assertRaises((AssertionError,KeyError,StopIteration)):named_proof(*args)
 def test_complete_original_identity_only(self):
  p=named_proof(*self.values());self.assertTrue(p['passed']);self.assertEqual(p['completeOriginalComponentsRetained'],365);self.assertEqual(p['originalMainBodyFaceCount'],3878);self.assertEqual(len(p['completeRawOverlapFaceIdsRetained']),65);self.assertFalse(p['occupationPermitRelationEstablished']);self.assertFalse(p['currentPodiumCollisionExemption']);self.assertFalse(p['currentPodiumTerrainExemption']);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['installationApproved']);self.assertEqual(len(p['allOtherCurrentFormsRetained']),len(FORMS));self.assertGreater(p['rawRelatedPodiumOverlapsRetained'][0]['relatedPodiumExcessM2'],20)
 def test_uid(self):self.reject(lambda a:a[1].update(uid=RELATED))
 def test_model(self):self.reject(lambda a:a[1].update(modelId='other'))
 def test_source_sha(self):self.reject(lambda a:a[1].update(sourceSHA256='0'*64))
 def test_y_only_geometry_mutation(self):self.reject(lambda a:a[2].__setitem__((0,0,1),a[2][0,0,1]+.001))
 def test_missing_original_face(self):self.reject(lambda a:a.__setitem__(2,a[2][:-1]))
 def test_changed_original_podium(self):self.reject(lambda a:a[3].__setitem__((0,0,0),a[3][0,0,0]+.001))
 def test_unverified_root(self):self.reject(lambda a:a[0]['originalOwnership'].update(sourceGraphVerified=False))
 def test_cell_not_covered(self):self.reject(lambda a:a[0]['geographicCell'].update(targetCoversWholeCell=False))
 def test_source_cell_not_covered(self):self.reject(lambda a:a[0]['geographicCell'].update(originalProjectionCoversWholeCell=False))
 def test_duplicate_primary(self):self.reject(lambda a:a[5]['primaryRecords'].append(deepcopy(a[5]['primaryRecords'][0])))
 def test_inactive_primary(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(Status='Inactive'))
 def test_wrong_primary_id(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(BuildingID=0))
 def test_wrong_georef(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(GeoRefNo='other'))
 def test_wrong_primary_date(self):self.reject(lambda a:a[5]['primaryRecords'][0]['attributes'].update(DateCreate=0))
 def test_wrong_primary_role(self):self.reject(lambda a:a[5]['primaryRecords'][1]['attributes'].update(BuildingBlockType='Tower'))
 def test_invented_op_relation(self):self.reject(lambda a:a[5]['exactRelations'].append({'invented':True}))
 def test_changed_ha_plan(self):self.reject(lambda a:a[5].update(primaryPlanSHA256='0'*64))
 def test_changed_named_block(self):self.reject(lambda a:a[5]['primaryNamedRelationship'].update(towerBlock='F'))
 def test_legal_ownership_claim(self):self.reject(lambda a:a[5]['primaryNamedRelationship'].update(legalOwnershipClaim=True))
 def test_support_claim(self):self.reject(lambda a:a[5]['primaryNamedRelationship'].update(supportClaim=True))
 def test_missing_overlap_face_accounting(self):self.reject(lambda a:a[5]['completeOverlapFaceIds'].pop())
 def test_wrong_native_podium(self):self.reject(lambda a:a[5]['rows'][1]['model']['asset'].update(sha256='0'*64))
 def test_missing_current_related_actor(self):self.reject(lambda a:a.__setitem__(4,[b for b in a[4] if b['uid']!=RELATED]))
 def test_wrong_current_related_identity(self):self.reject(lambda a:next(b for b in a[4] if b['uid']==RELATED).update(buildingCSUID='other'))
 def test_other_same_named_actor_remains_foreign(self):
  def change(a):
   b=deepcopy(next(b for b in a[4] if b['uid']==RELATED));b.update(uid='foreign:other',name='Tung Sing House');a[4].append(b)
  self.reject(change)
 def test_primary_coverage_shift(self):
  def change(a):
   for ring in a[5]['primaryRecords'][0]['geometry']['rings']:
    for q in ring:q[0]+=100
  self.reject(change)
 def test_nonrelated_raw_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('independent-original-pose-failure');p=named_proof(*a);self.assertFalse(p['passed']);self.assertIn('independent-original-pose-failure',p['reasons'])
if __name__=='__main__':unittest.main()
