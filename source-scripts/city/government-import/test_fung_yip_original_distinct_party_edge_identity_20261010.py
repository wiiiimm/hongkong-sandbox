"""Actual complete three-source fixtures and adverse identity-only cases."""
import copy
import unittest
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from fung_yip_original_distinct_party_edge_identity_20261010 import named_proof,UID,FOREIGN,EXPECTED,RAW_REASONS

BASE=ROOT/'docs/astra-city/government-import'

def fixture():
    x=read(BASE/'government-xl-fung-yip-distinct-original-shared-boundary-diagnostic-v2-20261010/diagnostic.json.gz')
    primary=read(BASE/'government-xl-fung-yip-three-podium-primary-relationships-20261010/diagnostic.json')
    selection={r['uid']:r for p in ['government-xl-terrain-recovery-fung-yip-original-pair-current-recovery-v2-20261010','government-xl-terrain-recovery-fung-yip-foreign-original-recovery-v1-20261010']for r in read(BASE/p/'selection.json.gz')['rows']}
    row=selection[UID];worlds={u:decode_original_world_triangles((ROOT/selection[u]['candidate']['path']).read_bytes())for u in EXPECTED}
    previous=next(p for p in read(BASE/'xl-terrain-recovery-20261010-fung-yip-current-identity-guard-checkpoint-v1/diagnostic.json.gz')['completeCurrentIdentityProofs']if p['uid']==UID)
    return [previous,row,worlds,x['allCurrentForms'],primary['primary'],primary['relations'],primary['structures']]

class Identity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual=fixture()
        cls.positive=named_proof(*cls.actual)
    def f(self):return copy.deepcopy(self.actual)
    def reject(self,args):
        with self.assertRaises((AssertionError,KeyError,ValueError)):named_proof(*args)
    def test_actual_complete_three_originals(self):
        p=self.positive;self.assertTrue(p['passed']);self.assertEqual(p['reasons'],[])
        self.assertEqual(set(p['rawUnrelatedOverlapReasonsRetained']),RAW_REASONS)
        self.assertEqual(len(p['allOriginalPartFaceIds'][0]),398)
    def test_actual_all17actors_retained(self):self.assertEqual(len(self.positive['completeCurrentForeignActorsRetained']),17)
    def test_actual_distinct_permits_no_physics(self):
        p=self.positive;self.assertTrue(p['allDistinctPrimaryPermitRolesRetained']);self.assertTrue(p['noCommonOwnershipOrSupportClaim'])
        for k in ['physicalAccepted','installationApproved','foreignRemoval','foreignCollisionExemption','foreignTerrainExemption']:self.assertIs(p[k],False)
    def test_all_direct_and_non_direct_interfaces_retained(self):
        p=self.positive;self.assertEqual(len(p['completeOriginalMutualInterfaces'][FOREIGN[0]]['contacts']),39);self.assertEqual(len(p['completeOriginalMutualInterfaces'][FOREIGN[1]]['contacts']),76)
        self.assertEqual(p['independentFullSourceSpatialChecks']['current']['namedForeignBoundaryRoles'][FOREIGN[0]]['originalFacesWithoutDirectForeignContactRetained'],[378])
    def test_complete_current_and_primary_finite_portions(self):
        for c in self.positive['independentFullSourceSpatialChecks'].values():
            self.assertGreater(c['namedForeignBoundaryRoles'][FOREIGN[0]]['rawNamedForeignExcessM2'],1)
            for r in c['namedForeignBoundaryRoles'].values():
                self.assertTrue(all(f['finiteSharedSegmentCertificates']for f in r['completeFinitePortionCertificates']))
    def test_unknown_raw_reason_preserved(self):
        a=self.f();a[0]['reasons'].append('independent-unresolved-foreign-actor');p=named_proof(*a);self.assertFalse(p['passed']);self.assertIn('independent-unresolved-foreign-actor',p['reasons'])
    def test_wrong_source_sha(self):a=self.f();a[1]['sourceSHA256']='0'*64;self.reject(a)
    def test_wrong_source_model(self):a=self.f();a[1]['modelId']=EXPECTED[FOREIGN[0]][2];self.reject(a)
    def test_wrong_source_uid(self):a=self.f();a[1]['uid']=FOREIGN[0];self.reject(a)
    def test_original_ownership_missing(self):a=self.f();a[0]['originalOwnership']['sourceGraphVerified']=False;self.reject(a)
    def test_missing_raw_failure(self):a=self.f();a[0]['reasons']=[];self.reject(a)
    def test_deleted_own_face(self):a=self.f();a[2][UID]=a[2][UID][:-1];self.reject(a)
    def test_deleted_foreign_face(self):a=self.f();a[2][FOREIGN[0]]=a[2][FOREIGN[0]][:-1];self.reject(a)
    def test_reordered_source(self):a=self.f();a[2][UID]=a[2][UID][::-1];self.reject(a)
    def test_y_only_own_geometry_change(self):a=self.f();a[2][UID][378,0,1]+=.0001;self.reject(a)
    def test_x_own_geometry_change(self):a=self.f();a[2][UID][0,0,0]+=.0001;self.reject(a)
    def test_foreign_geometry_change(self):a=self.f();a[2][FOREIGN[0]][0,0,1]+=.0001;self.reject(a)
    def test_nonfinite_source(self):a=self.f();a[2][UID][0,0,0]=np.nan;self.reject(a)
    def test_missing_original_foreign(self):a=self.f();del a[2][FOREIGN[1]];self.reject(a)
    def test_missing_current_foreign(self):a=self.f();a[3]=[b for b in a[3]if b['uid']!=FOREIGN[1]];self.reject(a)
    def test_duplicate_current_uid(self):a=self.f();a[3].append(copy.deepcopy(a[3][0]));self.reject(a)
    def test_changed_current_own_source(self):a=self.f();next(b for b in a[3]if b['uid']==UID)['name']='Other';self.reject(a)
    def test_changed_current_foreign_identity(self):a=self.f();next(b for b in a[3]if b['uid']==FOREIGN[0])['buildingId']+=1;self.reject(a)
    def test_missing_provider(self):a=self.f();a[4]=a[4][:-1];self.reject(a)
    def test_duplicate_provider(self):a=self.f();a[4][0]=copy.deepcopy(a[4][1]);self.reject(a)
    def test_inactive_provider(self):a=self.f();a[4][0]['attributes']['Status']='Inactive';self.reject(a)
    def test_changed_provider_date(self):a=self.f();a[4][0]['attributes']['DateCreate']+=86400000;self.reject(a)
    def test_changed_provider_height(self):a=self.f();a[4][0]['attributes']['TopHeight']+=1;self.reject(a)
    def test_changed_provider_type(self):a=self.f();a[4][0]['attributes']['BuildingBlockType']='Tower';self.reject(a)
    def test_shared_permit_invented(self):a=self.f();a[6][0]['attributes']['OPNo']='H234/75';self.reject(a)
    def test_wrong_explicit_structure_relation(self):a=self.f();a[5][0]['attributes']['BuildingStructureID']=1492454;self.reject(a)
    def test_missing_structure_role(self):a=self.f();a[6]=a[6][:-1];self.reject(a)
    def test_primary_shared_boundary_moved(self):
        a=self.f();p=next(p for p in a[4]if p['attributes']['BuildingCSUID']==EXPECTED[FOREIGN[0]][0]);p['geometry']['rings']=[[[v[0]+1,v[1]]for v in r]for r in p['geometry']['rings']];self.reject(a)
    def test_current_shared_boundary_moved(self):
        a=self.f();b=next(b for b in a[3]if b['uid']==FOREIGN[0]);b['rings']=[[[v[0]+1,v[1]]for v in r]for r in b['rings']];self.reject(a)

if __name__=='__main__':unittest.main()
