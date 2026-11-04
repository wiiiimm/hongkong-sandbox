"""UNEXECUTED synthetic new-schema pointer/account/source-byte fixtures."""
import copy,unittest
import numpy as np
import polyu_computed_parent_cell_enclosure_v1_draft_20261014 as packing
import polyu_saved_parent_cell_capture_binding_v3_draft_20261014 as h

class BindingFixtures(unittest.TestCase):
    def setUp(self):
        self.face=[[0,6,0],[4,6,0],[0,6,4]];self.domain=[0,0,4,4];self.hit=dict(mask=0,polygon=[[0,6,0],[1,6,0],[0,6,1]])
        self.region=dict(insidePolygon=0,**packing.inside_piece(self.hit,self.face,{},self.domain))
        k=self.region['exactComputedParentCellKernelVerbatim'];t=k['triangles'][0];n=k['sourcePlane']['normal']
        self.records=[dict(uid='synthetic-parent-mask',kind='synthetic-only')]
        self.row=dict(capturedParentFacet=0,newCandidateFaces=[8011],wholeOriginalCapturedParentTriplet=self.face,completeComputedInsideEnclosureAccount=dict(completeSavedInsideRegions=[self.region]))
        self.p=dict(candidateFace=8011,kind='capturedCurrentParentOwnPlaneFloat32CellInsideEligibleMasks',ancestor=dict(capturedParentFacet=0,wholeOriginalCapturedParentTriplet=self.face),partitionProofReference=dict(mapping='completeCapturedParentMapping',capturedParentFacet=0),mask=dict(mask=0,completeMaskLineage=self.records[0]),computedInsideCellEnclosure=dict(enclosureInsidePolygon=0,enclosureLocalTriangle=0,exactInsideExpansionAreaM2=k['exactHullExpansionAreaM2']),exactOwnPlanePoints=t['idealSourcePlanePoints'],exactPackedSourcePlaneResiduals=[v*n[1]for v in t['exactVerticalSourcePlaneResidualM']],noOtherLayerYUsed=True,packingResidualsMeasuredNotWaived=True,freshQualificationRequired=True)
        self.raw=np.asarray(t['packedPieceTriplet'],dtype='<f8')
    def test_exact_region_and_piece_pass_without_input_mutation(self):
        before=copy.deepcopy(self.p);h.validate_region(self.region,self.hit,self.face,0,self.domain);self.assertEqual((0,0),h.validate_piece(self.p,self.row,self.raw,self.records));self.assertEqual(self.p,before)
    def test_wrong_parent_pointer_rejected(self):
        self.p['partitionProofReference']['capturedParentFacet']=1
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
        self.p['partitionProofReference']['capturedParentFacet']=False
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
        self.p['partitionProofReference']['capturedParentFacet']=0
        self.p['candidateFace']=8012
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records,frozenset(self.row['newCandidateFaces']))
    def test_mask_identity_cannot_transfer_between_owners(self):
        self.p['mask']['completeMaskLineage']=dict(uid='different-actor')
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
    def test_same_count_swapped_local_triangle_rejected(self):
        self.p['computedInsideCellEnclosure']['enclosureLocalTriangle']=1
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
        self.p['computedInsideCellEnclosure']['enclosureLocalTriangle']=False
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
    def test_packed_coordinate_difference_and_signed_zero_are_not_equal(self):
        changed=self.raw.copy();changed[0,0]=np.nextafter(changed[0,0],np.inf)
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,changed,self.records)
        changed=self.raw.copy();changed[0,0]=-0.0
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,changed,self.records)
    def test_different_plane_same_projection_cannot_relabel(self):
        bad=copy.deepcopy(self.face)
        for p in bad:p[1]=7
        with self.assertRaises(AssertionError):h.validate_region(self.region,self.hit,bad,0,self.domain)
    def test_partial_enclosure_fan_is_not_complete(self):
        self.region['exactComputedParentCellKernelVerbatim']['triangles']=[]
        with self.assertRaises(AssertionError):h.validate_region(self.region,self.hit,self.face,0,self.domain)
    def test_wrong_residual_cannot_silently_pass(self):
        self.p['exactPackedSourcePlaneResiduals']=[1,1,1]
        with self.assertRaises(AssertionError):h.validate_piece(self.p,self.row,self.raw,self.records)
if __name__=='__main__':unittest.main(verbosity=2)
