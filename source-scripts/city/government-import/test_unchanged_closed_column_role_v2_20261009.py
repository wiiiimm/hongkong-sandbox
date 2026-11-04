import copy
import hashlib
import unittest
import numpy as np
from test_unchanged_closed_column_role_20261009 import fixture,evidence
from unchanged_closed_column_role_v2_20261009 import scoped_column_role,canonical_sha


def inputs(tri=None,ground=None):
    a,b=fixture();tri=a if tri is None else tri;ground=b if ground is None else ground
    contexts,binding=evidence(tri,ground);ids=list(range(12))
    role={'role':'original-vertical-column-termination','uid':'test-owned-source','sourceSHA256':binding['sourceSHA256'],
          'columnFaces':ids,'originalBounds':[tri[ids].min(axis=(0,1)).tolist(),tri[ids].max(axis=(0,1)).tolist()]}
    foreign=np.array([[[10,0,10],[11,0,10],[10,1,10]]],float)
    actor={'uid':'test-current-neighbour','worldTriangles':foreign.tolist(),'currentSourceBinding':'current-tile-sha256'}
    scope={'completeCurrentActorScope':True,'currentGroupBoundaryBinding':'source/support/neighbour-context-sha256',
           'actors':[actor],'expectedActorManifest':[{'uid':actor['uid'],'currentSourceBinding':actor['currentSourceBinding'],
               'worldTrianglesSHA256':hashlib.sha256(foreign.tobytes()).hexdigest()}]}
    binding.update(originalColumnRoleSHA256=canonical_sha(role),currentForeignScopeSHA256=canonical_sha({
        k:scope[k] for k in ['completeCurrentActorScope','currentGroupBoundaryBinding','expectedActorManifest']}))
    return tri,ground,contexts,ids,binding,role,scope


def invoke(args):
    t,g,c,i,b,r,s=args
    return scoped_column_role(t,g,c,i,expected_binding=b,current_binding=b,expected_role=r,foreign_scope=s)


def alternate_actor(actor,record):
    a=list(inputs());a[-1]['actors']=[actor];a[-1]['expectedActorManifest']=[record]
    a[4]['currentForeignScopeSHA256']=canonical_sha({k:a[-1][k] for k in
        ['completeCurrentActorScope','currentGroupBoundaryBinding','expectedActorManifest']})
    return a


class ScopedColumnTests(unittest.TestCase):
    def test_complete_narrow_source_and_foreign_scope(self):self.assertTrue(invoke(inputs())['verifiedColumnRole'])
    def test_broad_slab_cannot_be_column(self):
        t,g=fixture();t[:,:,0]*=10
        self.assertIn('original-solid-is-not-narrow-vertical-column',invoke(inputs(t,g))['reasons'])
    def test_attached_above_ground_column_has_no_burial_role(self):
        t,g=fixture();t[:,:,1]+=2
        self.assertIn('no-original-ground-crossing-column-side',invoke(inputs(t,g))['reasons'])
    def test_omitted_foreign_scope_rejects(self):
        a=list(inputs());a[-1]=None
        with self.assertRaises(AssertionError):invoke(a)
    def test_omitted_current_actor_rejects(self):
        a=list(inputs());a[-1]['actors']=[]
        with self.assertRaises(AssertionError):invoke(a)
    def test_changed_foreign_actor_rejects(self):
        a=list(inputs());a[-1]['actors'][0]['worldTriangles'][0][0][0]+=1
        with self.assertRaises(AssertionError):invoke(a)
    def test_wrong_original_column_role_rejects(self):
        a=list(inputs());a[-2]['sourceSHA256']='another-source'
        with self.assertRaises(AssertionError):invoke(a)
    def test_whole_basic_footprint_separation(self):
        rings=[[[10,10],[11,10],[11,11],[10,11],[10,10]]]
        actor={'uid':'basic','proofType':'current-basic-full-footprint','originalCurrentRings':rings,'currentSourceBinding':'actual-form-tile-sha'}
        record={k:actor[k] for k in ['uid','proofType','currentSourceBinding']};record['originalCurrentRingsSHA256']=canonical_sha(rings)
        self.assertTrue(invoke(alternate_actor(actor,record))['verifiedColumnRole'])
    def test_intersecting_basic_footprint_needs_actual_geometry(self):
        rings=[[[0,0],[1,0],[1,1],[0,1],[0,0]]]
        actor={'uid':'basic','proofType':'current-basic-full-footprint','originalCurrentRings':rings,'currentSourceBinding':'actual-form-tile-sha'}
        record={k:actor[k] for k in ['uid','proofType','currentSourceBinding']};record['originalCurrentRingsSHA256']=canonical_sha(rings)
        with self.assertRaises(AssertionError):invoke(alternate_actor(actor,record))
    def test_whole_native_source_bounds_separation(self):
        bounds=[[10.,0.,10.],[20.,30.,20.]]
        actor={'uid':'native','proofType':'complete-original-native-bounds','originalWholeSourceBounds':bounds,'currentSourceBinding':'actual-native-asset-catalogue-sha'}
        record={k:actor[k] for k in ['uid','proofType','currentSourceBinding']};record['originalWholeSourceBoundsSHA256']=canonical_sha(bounds)
        self.assertTrue(invoke(alternate_actor(actor,record))['verifiedColumnRole'])
    def test_native_bounds_touch_requires_full_export(self):
        bounds=[[1.,0.,0.],[20.,30.,20.]]
        actor={'uid':'native','proofType':'complete-original-native-bounds','originalWholeSourceBounds':bounds,'currentSourceBinding':'actual-native-asset-catalogue-sha'}
        record={k:actor[k] for k in ['uid','proofType','currentSourceBinding']};record['originalWholeSourceBoundsSHA256']=canonical_sha(bounds)
        with self.assertRaises(AssertionError):invoke(alternate_actor(actor,record))


if __name__=='__main__':unittest.main()
