"""Actual original mall/station fixtures and adverse identity counterexamples."""
import unittest,copy,numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from southside_named_original_station_envelope_identity_20261010 import named_proof,UID,RELATED
REL=ROOT/'docs/astra-city/government-import/government-xl-southside-station-original-relationship-20261010'
RAW=REL.parent/'government-xl-southside-current-full-cell-preflight-20261010'
D=read(REL/'diagnostic.json.gz');ROW=read(RAW/'selection.json.gz')['rows'][0];PREVIOUS=read(RAW/'raw-full-cell-proof.json');FORMS=read(RAW/'all-current-forms.json.gz')['forms']
SOURCES=[decode_original_world_triangles((ROOT/next(k for k,v in D['inputHashes'].items() if k.endswith('.glb.gz') and v==n['model']['asset']['sha256'])).read_bytes()) for n in D['native']]
EVIDENCE={'rows':D['native'],'primaryRecords':D['primary'],'exactRelations':D['exactRelations'],'exactStructures':D['exactStructures'],'completeOverlapFaceIds':D['allOverlapOriginalFaceIds'],'primaryMTRPageSHA256':D['primaryURLs'][0]['sha256'],'primaryOwnerPageSHA256':D['primaryURLs'][1]['sha256'],'primaryStationPlanSHA256':D['primaryURLs'][2]['sha256'],'primaryNamedRelationship':{'mallName':'The Southside','stationName':'Wong Chuk Hang Station','relationship':'documented direct connection / unchanged intersecting source envelopes','legalOwnershipClaim':False,'commonOPClaim':False,'allFacesL1Claim':False,'surveyPrecisionClaim':False,'supportClaim':False}}
class TestNamedOriginalStationEnvelope(unittest.TestCase):
 def fixture(self):return copy.deepcopy(PREVIOUS),copy.deepcopy(ROW),[q.copy() for q in SOURCES],copy.deepcopy(FORMS),copy.deepcopy(EVIDENCE)
 def call(self,f):a,b,c,d,e=f;return named_proof(a,b,c[0],c[1],d,e)
 def negative(self,mutate):
  f=self.fixture();mutate(*f)
  with self.assertRaises((AssertionError,KeyError,StopIteration)):self.call(f)
 def test_full_original_sources_positive(self):
  p=self.call(self.fixture());self.assertTrue(p['passed']);self.assertEqual(p['completeOriginalFaceCount'],11699);self.assertEqual(p['completeOriginalComponentsRetained'],157);self.assertEqual(len(p['completeRawOverlapFaceIdsRetained']),34);self.assertFalse(p['physicalAccepted']);self.assertFalse(p['currentPodiumCollisionExemption'])
 def test_source_byte_mutation(self):self.negative(lambda a,b,c,d,e:b.update(sourceSHA256='0'*64))
 def test_mall_y_mutation(self):self.negative(lambda a,b,c,d,e:c[0].__setitem__((0,0,1),c[0][0,0,1]+.001))
 def test_station_y_mutation(self):self.negative(lambda a,b,c,d,e:c[1].__setitem__((0,0,1),c[1][0,0,1]+.001))
 def test_source_face_omission(self):self.negative(lambda a,b,c,d,e:c.__setitem__(0,c[0][:-1]))
 def test_related_face_omission(self):self.negative(lambda a,b,c,d,e:c.__setitem__(1,c[1][:-1]))
 def test_mall_translation(self):self.negative(lambda a,b,c,d,e:c[0].__iadd__(np.array([.02,0,0])))
 def test_target_uid_substitution(self):self.negative(lambda a,b,c,d,e:b.update(uid='landsd/1:0'))
 def test_target_model_substitution(self):self.negative(lambda a,b,c,d,e:b.update(modelId='B_OTHER'))
 def test_missing_source_graph(self):self.negative(lambda a,b,c,d,e:a['originalOwnership'].update(sourceGraphVerified=False))
 def test_missing_whole_target_cell(self):self.negative(lambda a,b,c,d,e:a['geographicCell'].update(targetCoversWholeCell=False))
 def test_missing_whole_original_cell(self):self.negative(lambda a,b,c,d,e:a['geographicCell'].update(originalProjectionCoversWholeCell=False))
 def test_primary_inactive(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'][0]['attributes'].update(Status='Demolished'))
 def test_primary_stable_id_changed(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'][0]['attributes'].update(BuildingID=1))
 def test_primary_date_changed(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'][1]['attributes'].update(DateCreate=0))
 def test_primary_type_changed(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'][1]['attributes'].update(BuildingBlockType='Tower'))
 def test_primary_georef_changed(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'][0]['attributes'].update(GeoRefNo='0000000000'))
 def test_duplicate_primary(self):self.negative(lambda a,b,c,d,e:e['primaryRecords'].append(copy.deepcopy(e['primaryRecords'][0])))
 def test_invented_station_op(self):self.negative(lambda a,b,c,d,e:e['exactRelations'].append({'attributes':{'BuildingCSUID':'3536012138T20160607','BuildingStructureID':6095667}}))
 def test_changed_mall_permit(self):self.negative(lambda a,b,c,d,e:e['exactStructures'][0]['attributes'].update(OPNo='OTHER'))
 def test_changed_primary_mtr_evidence(self):self.negative(lambda a,b,c,d,e:e.update(primaryMTRPageSHA256='0'*64))
 def test_changed_primary_owner_evidence(self):self.negative(lambda a,b,c,d,e:e.update(primaryOwnerPageSHA256='0'*64))
 def test_changed_station_plan(self):self.negative(lambda a,b,c,d,e:e.update(primaryStationPlanSHA256='0'*64))
 def test_no_legal_ownership_claim(self):self.negative(lambda a,b,c,d,e:e['primaryNamedRelationship'].update(legalOwnershipClaim=True))
 def test_no_common_op_claim(self):self.negative(lambda a,b,c,d,e:e['primaryNamedRelationship'].update(commonOPClaim=True))
 def test_no_all_faces_l1_claim(self):self.negative(lambda a,b,c,d,e:e['primaryNamedRelationship'].update(allFacesL1Claim=True))
 def test_no_support_claim(self):self.negative(lambda a,b,c,d,e:e['primaryNamedRelationship'].update(supportClaim=True))
 def test_source_key_substitution(self):self.negative(lambda a,b,c,d,e:e['rows'][1].update(sourceKey='other/source'))
 def test_station_source_byte_substitution(self):self.negative(lambda a,b,c,d,e:e['rows'][1]['model']['asset'].update(sha256='0'*64))
 def test_missing_related_current_actor(self):self.negative(lambda a,b,c,d,e:d.__setitem__(slice(None),[q for q in d if q['uid']!=RELATED]))
 def test_duplicate_current_actor(self):self.negative(lambda a,b,c,d,e:d.append(copy.deepcopy(d[0])))
 def test_other_same_geometry_actor_stays_foreign(self):
  def mutation(a,b,c,d,e):
   q=copy.deepcopy(next(x for x in d if x['uid']==RELATED));q['uid']='landsd/999999:0';d.append(q)
  self.negative(mutation)
 def test_missing_one_overlap_face(self):self.negative(lambda a,b,c,d,e:e['completeOverlapFaceIds'].pop())
 def test_preserve_independent_failure(self):
  f=self.fixture();f[0]['reasons'].append('independent-physical-not-identity');p=self.call(f);self.assertFalse(p['passed']);self.assertIn('independent-physical-not-identity',p['reasons'])
if __name__=='__main__':unittest.main()
