"""Actual unchanged-source identity fixture and bounded counterexamples."""
import unittest,gzip
from copy import deepcopy
from run import ROOT,read
from tuen_mun_named_original_hospital_identity_20261010 import verify,SPEC,UID,RELATED
D=ROOT/'docs/astra-city/government-import'
P=D/'government-xl-tuen-mun-current-full-cell-preflight-20261009'
ROW=read(P/'selection.json.gz')['rows'][0];PREVIOUS=read(P/'raw-full-cell-proof.json')
FORMS=read(P/'all-current-forms.json.gz')['forms']
PRIMARY=read(D/'government-xl-tuen-mun-special-primary-counterpart-20261009/exact-primary.json')['features']
REFS=read(D/'government-xl-tuen-mun-special-primary-counterpart-20261009/result.json')['evidenceRefs']
SOURCES={uid:(ROOT/next(r['path'] for r in REFS if r['sha256']==spec[2] and '/assets/' in r['path'])).read_bytes() for uid,spec in SPEC.items()}
OWNERS={'official-site-plan-20150518.pdf':(D/'government-xl-tuen-mun-official-site-plan-20261009/official-site-plan-20150518.pdf').read_bytes(),'official-hospital-about.html':(D/'government-xl-tuen-mun-hospital-owner-context-20261009/official-hospital-about.html').read_bytes()}
class ActualHospitalIdentity(unittest.TestCase):
 def values(self):return [deepcopy(PREVIOUS),deepcopy(ROW),dict(SOURCES),deepcopy(FORMS),deepcopy(PRIMARY),dict(OWNERS)]
 def reject(self,mutation):
  a=self.values();mutation(a)
  with self.assertRaises((AssertionError,KeyError,StopIteration)):verify(*a)
 def test_actual_full_original_relationship_identity_only(self):
  r=verify(*self.values());self.assertTrue(r['passed']);self.assertEqual(len([x for x in r['exactCompleteOriginalExcessInterfaces']['contacts'] if x['dimension']>0]),80);self.assertEqual(r['completeOriginalTowerComponentsRetained'],130);self.assertFalse(r['physicalAccepted']);self.assertFalse(r['supportingPodiumIdentityAccepted']);self.assertFalse(r['installationApproved']);self.assertLess(r['supportingPodiumPrimaryCoverage'],.76);self.assertFalse(r['wholePodiumContainmentClaimed']);self.assertFalse(r['commonOccupationPermitClaimed']);self.assertEqual(len(r['allCurrentFormsRetained']),len(FORMS))
 def test_wrong_tower_uid(self):self.reject(lambda a:a[1].update(uid=RELATED))
 def test_wrong_source_model(self):self.reject(lambda a:a[1].update(modelId=SPEC[RELATED][0]))
 def test_wrong_source_sha(self):self.reject(lambda a:a[1].update(sourceSHA256='0'*64))
 def test_original_tower_stream_mutation(self):self.reject(lambda a:a[2].update({UID:SOURCES[UID]+b' '}))
 def test_original_podium_stream_mutation(self):self.reject(lambda a:a[2].update({RELATED:SOURCES[RELATED]+b' '}))
 def test_missing_original_podium(self):self.reject(lambda a:a[2].pop(RELATED))
 def test_missing_owner_plan(self):self.reject(lambda a:a[5].pop('official-site-plan-20150518.pdf'))
 def test_owner_plan_mutation(self):self.reject(lambda a:a[5].update({'official-site-plan-20150518.pdf':b'other site plan'}))
 def test_owner_site_text_mutation(self):self.reject(lambda a:a[5].update({'official-hospital-about.html':b'other campus'}))
 def test_missing_raw_source_graph(self):self.reject(lambda a:a[0]['originalOwnership'].update(sourceGraphVerified=False))
 def test_missing_current_whole_cell(self):self.reject(lambda a:a[0]['geographicCell'].update(targetCoversWholeCell=False))
 def test_missing_original_whole_cell(self):self.reject(lambda a:a[0]['geographicCell'].update(originalProjectionCoversWholeCell=False))
 def test_duplicate_primary(self):self.reject(lambda a:a[4].append(deepcopy(a[4][0])))
 def test_inactive_primary(self):self.reject(lambda a:a[4][0]['attributes'].update(Status='Inactive'))
 def test_wrong_stable_podium_id(self):self.reject(lambda a:a[4][1]['attributes'].update(BuildingID=1))
 def test_wrong_primary_kind(self):self.reject(lambda a:a[4][1]['attributes'].update(BuildingBlockType='Tower'))
 def test_wrong_primary_date(self):self.reject(lambda a:a[4][0]['attributes'].update(DateCreate=0))
 def test_wrong_primary_georef(self):self.reject(lambda a:a[4][0]['attributes'].update(GeoRefNo='1561229778'))
 def test_wrong_primary_named_block(self):self.reject(lambda a:a[4][0]['attributes'].update(BuildingNameEN='Another hospital'))
 def test_wrong_current_podium_identity(self):self.reject(lambda a:next(f for f in a[3] if f['uid']==RELATED).update(buildingCSUID='other'))
 def test_missing_actual_related_actor(self):self.reject(lambda a:a.__setitem__(3,[f for f in a[3] if f['uid']!=RELATED]))
 def test_duplicate_current_actor(self):self.reject(lambda a:a[3].append(deepcopy(a[3][0])))
 def test_another_same_named_campus_actor_remains_foreign(self):
  def foreign(a):
   f=deepcopy(next(f for f in a[3] if f['uid']==RELATED));f.update(uid='different:hospital',buildingCSUID='other');a[3].append(f)
  self.reject(foreign)
 def test_shifted_primary_coverage(self):
  def shifted(a):
   for ring in a[4][0]['geometry']['rings']:
    for p in ring:p[0]+=100
  self.reject(shifted)
 def test_changed_current_target(self):self.reject(lambda a:next(f for f in a[3] if f['uid']==UID)['rings'][0][0].__setitem__(0,-12000))
 def test_other_source_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('original-world-pose-or-bounds');r=verify(*a);self.assertFalse(r['passed']);self.assertIn('original-world-pose-or-bounds',r['reasons'])
 def test_other_cell_failure_preserved(self):
  a=self.values();a[0]['reasons'].append('other-whole-cell-failure');r=verify(*a);self.assertFalse(r['passed']);self.assertIn('other-whole-cell-failure',r['reasons'])
if __name__=='__main__':unittest.main()
