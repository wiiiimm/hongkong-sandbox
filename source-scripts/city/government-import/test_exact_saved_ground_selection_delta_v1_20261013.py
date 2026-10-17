"""Synthetic equivalence/adversarial tests only; no production saved arrays."""
import copy
from collections import Counter
import math
import unittest
from fractions import Fraction as F
import numpy as np
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround, sha
from exact_saved_ground_selection_delta_v1_20261013 import SavedGroundSelectionDelta, selection_sha


def tri(x=0., z=0., y=0.):
    return [[x,y,z],[x+1,y,z],[x,y,z+1]]


def query(x=0., z=0.):
    return [[str(F(x)), '1', str(F(z))], [str(F(x+1)), '2', str(F(z+1))]]


class Tests(unittest.TestCase):
    def check_equivalent(self, old, new, queries):
        delta = SavedGroundSelectionDelta(old, new)
        for points in queries:
            old_ids, saved = CompleteGround(old).select(points)
            expected_ids, expected_binding = CompleteGround(new).select(points)
            old_saved = copy.deepcopy(saved)
            actual_ids, binding, proof = delta.select(points, saved,
                authenticated_selection_sha=selection_sha(saved),
                authenticated_selected_ground_sha=sha(delta.old.ground[old_ids]))
            self.assertEqual(actual_ids.tolist(), expected_ids.tolist())
            self.assertEqual(binding, expected_binding)
            self.assertEqual(proof['oldSelectionVerbatim'], old_saved)
            self.assertEqual(saved, old_saved)
            self.assertEqual(proof['unchangedFacetAABBTests'], 0)
            old_multiset = Counter(f.tobytes() for f in delta.old.ground[old_ids])
            new_multiset = Counter(f.tobytes() for f in delta.new.ground[expected_ids])
            self.assertEqual(proof['completeSelectedTripletMultisetExactlyEqual'], old_multiset == new_multiset)
            if proof['completeSelectedTripletMultisetExactlyEqual']:
                mapped = proof['newFaceByOldSelectedFace']
                self.assertEqual(delta.new.ground[mapped].tobytes(), delta.old.ground[old_ids].tobytes())
        delta.verify_binding()
        return delta

    def test_reordering_duplicate_occurrences_and_identity(self):
        a,b = tri(),tri(10)
        d=self.check_equivalent(np.array([a,a,b]),np.array([a,b,a]),[query(),query(10),query(100)])
        self.assertEqual(d.old_to_new.tolist(),[0,2,1]);self.assertEqual(len(d.added),0)

    def test_removed_and_added_duplicate_preserve_multiplicity(self):
        a,b=tri(),tri(10)
        self.check_equivalent(np.array([a,a,b]),np.array([b,a]),[query(),query(10)])
        self.check_equivalent(np.array([a,b]),np.array([a,b,a]),[query(),query(10)])

    def test_split_parent_touching_each_child_and_outside(self):
        left=[[0,0,0],[.5,0,0],[0,0,1]];right=[[.5,0,0],[1,0,0],[0,0,1]]
        self.check_equivalent(np.array([tri(20),tri()]),np.array([right,tri(20),left]),
            [query(),query(20),[['1','1','0']],[['.5','2','0']],query(50)])

    def test_vertical_line_point_and_boundary_remain_selected(self):
        extras=[[[1,0,0],[1,3,0],[1,5,1]],[[0,2,0]]*3,[[0,0,0],[.5,0,0],[1,0,0]]]
        self.check_equivalent(np.array([tri(30)]),np.array(extras+[tri(30)]),
            [[['0','4','0'],['1','5','0']],query(30)])

    def test_rational_rounding_halo_is_not_exact_clipped(self):
        x=F(1)-F(1,2**55)
        d=self.check_equivalent(np.array([tri(20)]),np.array([[[1,2,0]]*3,tri(20)]),
            [[[str(x),'1','0'],[str(x),'2','0']]])
        self.assertEqual(d.added.tolist(),[0])

    def test_same_projection_changed_height_is_not_unchanged(self):
        d=self.check_equivalent(np.array([tri()]),np.array([tri(y=100)]),[query()])
        self.assertEqual(d.removed.tolist(),[0]);self.assertEqual(d.added.tolist(),[0])

    def test_signed_zero_and_vertex_order_are_byte_changes(self):
        old=np.array([tri()]);new=old.copy();new[0,0,1]=-0.
        d=self.check_equivalent(old,new,[query()]);self.assertEqual(d.added.tolist(),[0])
        d=self.check_equivalent(old,old[:,[1,2,0],:],[query()]);self.assertEqual(d.added.tolist(),[0])

    def test_empty_selection_and_complete_replacement(self):
        self.check_equivalent(np.array([tri()]),np.array([tri(30)]),[query(),query(30),query(100)])

    def test_nonintersection_inside_aabb_still_nominated(self):
        self.check_equivalent(np.array([tri(30)]),np.array([tri(),tri(30)]),[[['.9','1','.9']]])

    def test_wrong_ground_query_hash_order_or_omission_rejected(self):
        d=SavedGroundSelectionDelta(np.array([tri(),tri()]),np.array([tri(),tri()]))
        ids,s=d.old.select(query());digest=selection_sha(s);relevant=sha(d.old.ground[ids])
        def attempt(selection=s,points=None,digest=digest,relevant=relevant):
            return d.select(points or query(),selection,authenticated_selection_sha=digest,authenticated_selected_ground_sha=relevant)
        for mutate in ['omit','order','ground','flags']:
            bad=copy.deepcopy(s)
            if mutate=='omit':bad['selectedOriginalGroundFaces']=[0];bad['selectedFacetCount']=1;bad['strictlyDisjointNoncandidateCount']=1
            if mutate=='order':bad['selectedOriginalGroundFaces']=[1,0]
            if mutate=='ground':bad['completeGroundSHA256']='0'*64
            if mutate=='flags':bad['touchingAndCollapsedProjectionsRetained']=False
            with self.assertRaises(AssertionError):attempt(bad)
        with self.assertRaises(AssertionError):attempt(points=query(10))
        with self.assertRaises(AssertionError):attempt(digest='0'*64)
        with self.assertRaises(AssertionError):attempt(relevant='0'*64)
        self.assertEqual(attempt()[0].tolist(),[0,1])

    def test_corruption_rejected_even_if_attacker_rehashes_mapping(self):
        d=SavedGroundSelectionDelta(np.array([tri(),tri(10)]),np.array([tri(10),tri()]))
        d.old_to_new.flags.writeable=True;d.old_to_new[:]=[0,1];d.bijection_sha=sha(d.old_to_new)
        with self.assertRaises(AssertionError):d.verify_binding()

    def test_input_mutation_cannot_change_copy_and_corrupt_mapping_rejected(self):
        old=np.array([tri(),tri(10)]);new=old[::-1].copy();d=SavedGroundSelectionDelta(old,new)
        old[:]=99;new[:]=99;d.verify_binding()
        d.old_to_new.flags.writeable=True;d.old_to_new[:]=0
        with self.assertRaises(AssertionError):d.verify_binding()

    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError):SavedGroundSelectionDelta(np.array([tri(y=math.inf)]),np.array([tri()]))

    def test_seeded_random_deltas_match_oracle_for_every_query(self):
        rng=np.random.default_rng(20261013)
        for _ in range(12):
            old=rng.integers(-4,5,size=(25,3,3)).astype(float)
            old[2]=old[1];old[4,:,:]=old[4,0,:]
            kept=rng.choice(len(old),size=19,replace=False)
            new=np.concatenate([old[kept],rng.integers(-4,5,size=(4,3,3))]).astype(float)
            rng.shuffle(new)
            queries=[[[str(F(int(v),3)) for v in p] for p in rng.integers(-15,16,size=(3,3))]for _ in range(35)]
            self.check_equivalent(old,new,queries)

    def test_many_unchanged_faces_only_delta_bounds_tested(self):
        old=np.array([tri(float(i*3)) for i in range(1200)])
        new=np.concatenate([old[::-1],np.array([tri(4000),tri(4003)])])
        d=SavedGroundSelectionDelta(old,new)
        for i in [0,500,1199]:
            ids,s=d.old.select(query(float(i*3)))
            newids,b,p=d.select(query(float(i*3)),s,authenticated_selection_sha=selection_sha(s),authenticated_selected_ground_sha=sha(d.old.ground[ids]))
            self.assertEqual(p['addedFacetAABBTests'],2);self.assertEqual(p['unchangedFacetAABBTests'],0)
            self.assertEqual(b,d.new.select(query(float(i*3)))[1])
        d.verify_binding()

    def test_exact_negative_kernel_context_remains_outside_continuation(self):
        old=np.array([tri()]);d=SavedGroundSelectionDelta(old,old)
        ids,s=d.old.select(query());negative={'ordinaryBoundProved':False,'projectionCovered':False,'exactLowerM':'-9','oldKernelGroundHash':'historical','crossings':[23]}
        row={'selection':s,'findings':negative,'roles':['held-foreign']};before=copy.deepcopy(row)
        ids,b,p=d.select(query(),row['selection'],authenticated_selection_sha=selection_sha(s),authenticated_selected_ground_sha=sha(d.old.ground[ids]))
        self.assertEqual(row,before);self.assertTrue(p['completeSelectedTripletMultisetExactlyEqual']);self.assertNotIn('findings',p)

if __name__=='__main__':unittest.main()
