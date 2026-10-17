"""UNEXECUTED synthetic V3 pointer/multiset fixtures; no source calculations."""
import copy,unittest
import polyu_five_saved_nomination_binding_v2_20261014 as h


def fixture():
    old=[[0.,2.,0.],[2.,2.,0.],[0.,2.,2.]];parent=[[0.,5.,0.],[2.,5.,0.],[0.,5.,2.]]
    lineage=[{'original':0}];proof={'completeOwnPlanePartition':True}
    patch={'nativeMesh':{'position':[v for p in old for v in p],'index':[0,1,2]}}
    nom={'schema':'private-source-plane-preserving-five-current-parent-mask-nomination-v3','oldPositionBufferRetainedIncludingUnusedVertices':True,
        'newNativeMesh':{'position':patch['nativeMesh']['position']+[v for p in parent for v in p],'index':[0,1,2,3,4,5]},
        'completeOldPrivateMapping':[{'oldPrivateFace':0,'wholeOldRawTriplet':old,'previousLineageVerbatim':lineage[0],'removedFragmentsRemainInSourceInventory':True,'completeExactMaskPartition':proof,'newCandidateFaces':[0]}],
        'completeCapturedParentMapping':[{'capturedParentFacet':0,'wholeOriginalCapturedParentTriplet':parent,'completeExactMaskPartition':proof,'newCandidateFaces':[1]}],
        'candidateFaceProvenance':[{'candidateFace':0,'kind':'unchangedPreviousPrivateDraw','oldPrivateFace':0,'previousLineageVerbatim':lineage[0]},
            {'candidateFace':1,'kind':'capturedCurrentParentInsideEligibleMasks','ancestor':{'capturedParentFacet':0,'wholeOriginalCapturedParentTriplet':parent},'partitionProofReference':{'mapping':'completeCapturedParentMapping','capturedParentFacet':0},'exactOwnPlanePoints':parent,'noOtherLayerYUsed':True,'packingResidualsMeasuredNotWaived':True}]}
    return nom,patch,lineage,[parent]


class BindingFixtures(unittest.TestCase):
    def test_complete_slots_and_inputs_immutable(self):
        values=fixture();before=copy.deepcopy(values);raw=h.validate_binding(*values)
        self.assertEqual((2,3,3),raw.shape);self.assertEqual(before,values)
    def test_dangling_pointer_rejected(self):
        values=fixture();values[0]['candidateFaceProvenance'][1]['partitionProofReference']['capturedParentFacet']=1
        with self.assertRaises(AssertionError):h.validate_binding(*values)
    def test_wrong_ancestor_or_ambiguous_inline_proof_rejected(self):
        for field in ['ancestor','partitionProof']:
            values=fixture();p=values[0]['candidateFaceProvenance'][1]
            if field=='ancestor':p['ancestor']['capturedParentFacet']=1
            else:p['partitionProof']={'completeOwnPlanePartition':True}
            with self.assertRaises(AssertionError):h.validate_binding(*values)
    def test_cross_mapping_namespace_and_extra_keys_rejected(self):
        for pointer in [{'mapping':'not-a-map','capturedParentFacet':0},{'mapping':'completeCapturedParentMapping','capturedParentFacet':0,'oldPrivateFace':0}]:
            values=fixture();values[0]['candidateFaceProvenance'][1]['partitionProofReference']=pointer
            with self.assertRaises(AssertionError):h.validate_binding(*values)
    def test_face_assignment_not_aggregate_count_match(self):
        values=fixture();values[0]['completeCapturedParentMapping'][0]['newCandidateFaces']=[0]
        with self.assertRaises(AssertionError):h.validate_binding(*values)
    def test_changed_parent_layer_and_position_prefix_rejected(self):
        for target in ['parent','prefix']:
            values=fixture()
            if target=='parent':values[0]['candidateFaceProvenance'][1]['ancestor']['wholeOriginalCapturedParentTriplet'][0][1]=6
            else:values[0]['newNativeMesh']['position'][1]=3
            with self.assertRaises(AssertionError):h.validate_binding(*values)
    def test_enclosed_outside_resolves_full_account_exactly(self):
        nom,patch,lineage,parents=fixture();old=nom['completeOldPrivateMapping'][0]['wholeOldRawTriplet']
        nom['completeOldPrivateMapping'][0]['computedOutsideEnclosureAccount']={'completeComputedOutsidePolygonAccounting':[{'outsidePolygon':0,'exactHullExpansionAreaM2':'0','triangles':[{'idealSourcePlanePoints':old,'packedPieceTriplet':old}]}]}
        nom['candidateFaceProvenance'][0]={'candidateFace':0,'kind':'previousPrivateOwnPlaneFloat32CellOutsideEligibleMasks','ancestor':{'oldPrivateFace':0,'previousLineageVerbatim':lineage[0]},'partitionProofReference':{'mapping':'completeOldPrivateMapping','oldPrivateFace':0},'exactOwnPlanePoints':old,'noOtherLayerYUsed':True,'packingResidualsMeasuredNotWaived':True,'computedOutsideCellEnclosure':{'enclosureOutsidePolygon':0,'enclosureLocalTriangle':0,'exactOutsideExpansionAreaM2':'0','packedGeometryChangedFreshQualificationRequired':True}}
        h.validate_binding(nom,patch,lineage,parents)
        nom['candidateFaceProvenance'][0]['computedOutsideCellEnclosure']['enclosureLocalTriangle']=1
        with self.assertRaises(AssertionError):h.validate_binding(nom,patch,lineage,parents)
    def test_boolean_face_index_not_accepted_as_integer(self):
        values=fixture();values[0]['completeCapturedParentMapping'][0]['newCandidateFaces']=[True]
        with self.assertRaises(AssertionError):h.validate_binding(*values)


if __name__=='__main__':unittest.main(verbosity=2)
