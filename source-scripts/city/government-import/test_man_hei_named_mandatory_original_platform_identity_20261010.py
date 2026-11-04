"""Actual original Man Hei/platform fixtures and scoped adverse cases.

The source contact algorithm is separately replayed without mocking by the
production diagnostic. Unit tests reuse its complete immutable 209-interface
fixture after checking both full world hashes; geometry mutations fail before
that mocked call. This avoids re-running identical 24k-facet contact searches.
"""
import copy
import unittest
from unittest.mock import patch
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import man_hei_named_mandatory_original_platform_identity_20261010 as k

BASE=ROOT/'docs/astra-city/government-import'
UPPER=BASE/'government-xl-man-fuk-nine-current-identity-75694-0-20261010'
LOWER=BASE/'government-xl-man-fuk-complete-retained-original-physical-v7-20261010'
UR=read(UPPER/'selection.json.gz')['rows'][0];PR=read(LOWER/'selection.json.gz')['rows'][0]
FORMS=read(BASE/'government-xl-man-fuk-current-bound-envelope-inputs-v3-20261010/current-inputs.json.gz')['forms']
for row in [UR,PR]:row['source']['building']=next(f for f in FORMS if f['uid']==row['uid'])
A=decode_original_world_triangles((ROOT/UR['candidate']['path']).read_bytes());B=decode_original_world_triangles((ROOT/PR['candidate']['path']).read_bytes())
PREVIOUS=read(UPPER/'identity.json');PIDENTITY=read(LOWER/'owned-source-identity.json')['rows'][0]
PRIMARY=read(BASE/'government-xl-man-hei-man-fuk-primary-platform-context-20261010/exact-current-primary.json')['features']
PLAN=dict(url=k.PLAN_URL,sha256=k.PLAN_SHA,namedEstate='Chun Man Court',namedBlock='H',namedBuilding='Man Hei House',role='reference-typical-floor-plan-1F-15F')
CONTACT=next(r for r in read(BASE/'government-xl-man-fuk-nine-original-platform-interfaces-20261010/diagnostic.json.gz')['rows'] if r['uid']==k.UID)
assert CONTACT['sourceSHA256']==k.SOURCE_SHA and CONTACT['completeOriginalWorldSHA256']==digest(A.tobytes())==k.WORLD_SHA
assert digest(B.tobytes())==k.PLATFORM_WORLD_SHA and CONTACT['positiveDimensionalContacts']==209

def fixture():return [copy.deepcopy(PREVIOUS),copy.deepcopy(PIDENTITY),copy.deepcopy(UR),copy.deepcopy(PR),A.copy(),B.copy(),copy.deepcopy(FORMS),copy.deepcopy(PRIMARY),copy.deepcopy(PLAN)]
def prove(x):
    with patch.object(k,'exact_component_contacts',return_value=copy.deepcopy(CONTACT['completeOriginalPlatformContacts'])):return k.named_proof(*x)

class ManHeiIdentityTests(unittest.TestCase):
    def reject(self,mutate):
        x=fixture();mutate(x)
        with self.assertRaises((AssertionError,KeyError,ValueError)):prove(x)
    def test_actual_complete_original_assembly(self):
        p=prove(fixture());self.assertTrue(p['passed'],p['reasons']);self.assertEqual(p['mandatoryOriginalRuntimeUIDs'],[k.UID,k.PLATFORM]);self.assertFalse(p['standaloneOriginalImportAccepted']);self.assertFalse(p['physicalAccepted'])
    def test_genuine_partial_gaps_and_raw_standalone_failure_retained(self):
        p=prove(fixture());self.assertEqual(len(p['rawStandaloneUpperCoverageReasonsRetained']),2);self.assertFalse(p['completeMissingFloorClaim'])
        for m in p['independentCurrentProviderAssemblyChecks'].values():
            self.assertLess(m['rawStandaloneUpperCoverage'],.95);self.assertGreater(m['upperPlusOriginalMainBodyLowerFloorCoverage'],.95);self.assertGreater(m['genuineRemainingLowerFloorGapM2'],.18);self.assertEqual(len(m['completeOriginalSupplyingLowerFloorFaceIds']),45);self.assertGreater(m['allCurrentForeignPairExcessM2Retained'],1)
    def test_unknown_previous_failure_preserved(self):
        x=fixture();x[0]['reasons'].append('independent-other-failure');self.assertFalse(prove(x)['passed'])
    def test_other_actors_and_physics_retained(self):
        x=fixture();p=prove(x);self.assertEqual(p['completeOriginalPartCounts'],[6,93]);self.assertEqual(p['completeCurrentForeignActorsRetained'],x[6]);self.assertFalse(p['foreignCollisionExemption']);self.assertFalse(p['foreignTerrainExemption']);self.assertFalse(p['foreignRemoval']);self.assertFalse(p['installationApproved'])
    def test_tower_y_mutation(self):self.reject(lambda x:x[4].__setitem__((0,0,1),x[4][0,0,1]+.001))
    def test_platform_y_mutation(self):self.reject(lambda x:x[5].__setitem__((0,0,1),x[5][0,0,1]+.001))
    def test_missing_tower_face(self):self.reject(lambda x:x.__setitem__(4,x[4][:-1]))
    def test_missing_platform_face(self):self.reject(lambda x:x.__setitem__(5,x[5][:-1]))
    def test_nonfinite_vertex(self):self.reject(lambda x:x[5].__setitem__((0,0,0),float('nan')))
    def test_wrong_tower_source(self):self.reject(lambda x:x[2].__setitem__('sourceSHA256','0'*64))
    def test_wrong_platform_source(self):self.reject(lambda x:x[3].__setitem__('sourceSHA256','0'*64))
    def test_wrong_model_identifier(self):self.reject(lambda x:x[2].__setitem__('modelId','different-original'))
    def test_source_graph_not_verified(self):self.reject(lambda x:x[0]['originalOwnership'].__setitem__('sourceGraphVerified',False))
    def test_unaccepted_platform_not_borrowed(self):self.reject(lambda x:x[1].__setitem__('passed',False))
    def test_platform_unknown_reason_not_waived(self):self.reject(lambda x:x[1]['reasons'].append('other-platform-failure'))
    def test_platform_source_version_changed(self):self.reject(lambda x:x[1].__setitem__('sourceSHA256','0'*64))
    def test_platform_world_changed(self):self.reject(lambda x:x[1].__setitem__('worldTrianglesSHA256','0'*64))
    def test_other_related_actor_not_exempted(self):self.reject(lambda x:x[1].__setitem__('explicitRelatedUID',k.UID))
    def test_platform_collision_exemption_rejected(self):self.reject(lambda x:x[1].__setitem__('currentRelatedActorCollisionExemption',True))
    def test_platform_terrain_exemption_rejected(self):self.reject(lambda x:x[1].__setitem__('currentRelatedActorTerrainExemption',True))
    def test_missing_current_platform(self):self.reject(lambda x:x.__setitem__(6,[f for f in x[6] if f['uid']!=k.PLATFORM]))
    def test_omitted_foreign_actor(self):self.reject(lambda x:x[6].pop(0))
    def test_duplicate_current_actor(self):self.reject(lambda x:x[6].append(copy.deepcopy(x[6][0])))
    def test_duplicate_primary_actor(self):self.reject(lambda x:x[7].append(copy.deepcopy(x[7][0])))
    def test_primary_inactive(self):self.reject(lambda x:x[7][0]['attributes'].__setitem__('Status','Inactive'))
    def test_primary_creation_date(self):self.reject(lambda x:x[7][0]['attributes'].__setitem__('DateCreate',0))
    def test_primary_wrong_role(self):self.reject(lambda x:x[7][1]['attributes'].__setitem__('BuildingBlockType','Tower'))
    def test_primary_wrong_building_id(self):self.reject(lambda x:x[7][0]['attributes'].__setitem__('BuildingID',1))
    def test_primary_wrong_georef(self):self.reject(lambda x:x[7][0]['attributes'].__setitem__('GeoRefNo','different'))
    def test_wrong_named_block(self):self.reject(lambda x:x[8].__setitem__('namedBlock','K'))
    def test_unpinned_plan(self):self.reject(lambda x:x[8].__setitem__('sha256','0'*64))
    def test_new_unrelated_actor_stays_foreign(self):
        x=fixture();f=copy.deepcopy(x[6][0]);lo=np.concatenate([A,B]).min((0,1));hi=np.concatenate([A,B]).max((0,1));f['uid']='unrelated-new-actor';f['rings']=[[[lo[0]-1,lo[2]-1],[hi[0]+1,lo[2]-1],[hi[0]+1,hi[2]+1],[lo[0]-1,hi[2]+1],[lo[0]-1,lo[2]-1]]];x[6].append(f);x[1]['allOtherCurrentFormsRetained'].append(copy.deepcopy(f));p=prove(x);self.assertFalse(p['passed']);self.assertGreater(p['independentCurrentProviderAssemblyChecks']['current']['allOtherForeignPairExcessM2'],1)
    def test_incomplete_contacts_not_positive(self):
        with patch.object(k,'exact_component_contacts',return_value={'contacts':[]}):
            with self.assertRaises(AssertionError):k.named_proof(*fixture())

if __name__=='__main__':unittest.main()
