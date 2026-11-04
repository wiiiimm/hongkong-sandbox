"""UNEXECUTED constructor integration fixtures, synthetic geometry only."""
import copy,unittest
from fractions import Fraction as F
import numpy as np
import polyu_five_mask_source_plane_partition_v1_20261014 as old
import polyu_five_mask_positive_hit_partition_v3_draft_20261014 as positive
from polyu_five_mask_source_plane_partition_fast_v1_20261014 import PreparedMasks
from polyu_v3_computed_outside_enclosure_adapter_draft_20261014 import affected_outside


def masks(*triangles):
    return PreparedMasks([dict(uid=str(i),mask=i,exactClosedProjection=t)for i,t in enumerate(triangles)])


class IntegrationFixtures(unittest.TestCase):
    def test_affected_outside_own_plane_and_source_inputs_immutable(self):
        face=[[0,0,0],[4,2,0],[0,0,4]];proof=positive.partition(face,masks([[0,0],[F(1,3),0],[0,F(2,3)]]))
        before=copy.deepcopy((face,proof));pieces,account=affected_outside(proof,face,{})
        self.assertEqual(before,(face,proof));self.assertTrue(pieces)
        n=old.normal(old.points(face));a=old.points(face)[0]
        self.assertTrue(all(sum(n[k]*(p[k]-a[k])for k in range(3))==0 for t in pieces for p in t['exactOwnPlanePoints']))
        self.assertTrue(account['freshExpandedRegionLayerCompatibilityOrdinaryAndRuntimePending'])
    def test_protected_literal_rejected_even_with_synthetic_positive_proof(self):
        proof=positive.partition([[0,0,0],[4,0,0],[0,0,4]],masks([[0,0],[1,0],[0,1]]))
        with self.assertRaisesRegex(AssertionError,'protected literal'):affected_outside(proof,[[0,0,0],[4,0,0],[0,0,4]],{},protected_literal=True)
    def test_unaffected_and_vertical_source_do_not_take_enclosure(self):
        face=[[0,0,0],[4,0,0],[0,0,4]]
        proof=positive.partition(face,masks([[10,10],[11,10],[10,11]]))
        with self.assertRaisesRegex(AssertionError,'unaffected'):affected_outside(proof,face,{})
        vertical=[[0,0,0],[0,2,0],[0,0,2]]
        with self.assertRaises(AssertionError):affected_outside(positive.partition(vertical,masks([[0,0],[1,0],[0,1]])),vertical,{})
    def test_full_mask_has_no_computed_outside_to_emit(self):
        face=[[0,1,0],[1,1,0],[0,1,1]];proof=positive.partition(face,masks([[-1,-1],[4,-1],[-1,4]]))
        pieces,account=affected_outside(proof,face,{})
        self.assertEqual([],pieces);self.assertEqual([],account['completeComputedOutsidePolygonAccounting'])
    def test_parent_inside_uses_original_packer_and_parent_height(self):
        face=[[0,100,0],[4,100,0],[0,100,4]];proof=positive.partition(face,masks([[0,0],[F(1,3),0],[0,F(2,3)]]))
        before=copy.deepcopy(proof['inside'])
        pieces=old.packed_pieces([r['polygon']for r in proof['inside']],face)
        self.assertEqual(before,proof['inside']);self.assertTrue(all(p[1]==100 for t in pieces for p in t['packedPieceTriplet']))
    def test_duplicate_masks_preserve_occurrences_and_first_owner(self):
        face=[[0,1,0],[4,1,0],[0,1,4]];t=[[0,0],[1,0],[0,1]];proof=positive.partition(face,masks(t,t))
        self.assertEqual([0,1],proof['completeRelevantClosedAABBMasks']);self.assertTrue(all(r['mask']==0 for r in proof['inside']))
        pieces,account=affected_outside(proof,face,{})
        self.assertTrue(pieces);self.assertEqual({0:[0,1]},proof['allOriginalMaskOccurrenceAliases'])
    def test_legacy_dot_residual_equals_new_vertical_residual_times_ny(self):
        face=[[0,0,0],[3,1,0],[0,0,3]];proof=positive.partition(face,masks([[0,0],[F(1,3),0],[0,F(2,3)]]))
        pieces,_=affected_outside(proof,face,{})
        a=old.points(face)[0];n=old.normal(old.points(face))
        for t in pieces:
            expected=[sum(n[k]*(F(float(p[k]))-a[k])for k in range(3))for p in t['packedPieceTriplet']]
            self.assertEqual(expected,t['exactPackedSourcePlaneResiduals'])
    def test_original_prefix_packing_function_and_bytes_remain_unchanged(self):
        ideal=[[0,2,0],[3,2,0],[0,2,3]];poly=[[F(0),F(2),F(0)],[F(1,3),F(2),F(0)],[F(0),F(2),F(2,3)]]
        before=old.packed_pieces([poly],ideal)
        proof=positive.partition(ideal,masks([[0,0],[1,0],[0,1]]));affected_outside(proof,ideal,{})
        after=old.packed_pieces([poly],ideal)
        self.assertEqual(before,after)
        self.assertEqual(np.asarray([t['packedPieceTriplet']for t in before],dtype='<f8').tobytes(),np.asarray([t['packedPieceTriplet']for t in after],dtype='<f8').tobytes())


if __name__=='__main__':unittest.main(verbosity=2)
