"""Meaningful lineage/coverage/height adversaries; not run before ROOT review."""
import copy,unittest
from upton_v6_saved_overlap_source_classification_v1_20261013 import classify,verify_complete
def fixture():
    row=dict(leftFace=1,rightFace=2,leftProvenance=dict(candidateFace=1,kind='capturedCurrentRing',originalFace=10),rightProvenance=dict(candidateFace=2,kind='capturedCurrentRing',originalFace=11),proof=dict(exactProjectedDimension='area',exactDoubledAreaM2='2',exactLeftHeightRangeM=['0','1'],exactRightHeightRangeM=['2','3'],exactSignedLeftMinusRightRangeM=['-2','-2']))
    ancestor=dict(exactCandidateProjectionDimension='area',exactCandidatePairAreaM2='1',exactOriginalPairAreaM2='1',projectionInherited=True,heightInherited=True,exactPerLineageHeightDifferenceRangesM=[['0','0'],['0','0']])
    return row,ancestor
class Tests(unittest.TestCase):
    def test_distinct_actual_current_layers(self):
        r,a=fixture();q=classify(r,a);self.assertEqual(q['classification'],'positive-area intersection contained in two ancestral surfaces');self.assertFalse(q['physicalAccepted'])
    def test_mixed_layers_never_current_inheritance(self):
        r,a=fixture();r['leftProvenance']['kind']='originalTIN';self.assertEqual(classify(r,a)['classification'],'introduced original-TIN/current coexistence')
    def test_same_ancestor_does_not_invent_original_multilayer(self):
        r,a=fixture();r['rightProvenance']['originalFace']=10;self.assertEqual(classify(r,a)['classification'],'introduced packed fragments of one source facet')
    def test_packing_area_from_original_edge(self):
        r,a=fixture();a['exactOriginalPairAreaM2']='0';a['projectionInherited']=False;a['heightInherited']=False;self.assertIn('formerly non-area',classify(r,a)['classification'])
    def test_expanded_original_overlap_remains_new_region(self):
        r,a=fixture();a['projectionInherited']=False;a['heightInherited']=False;self.assertIn('expanded',classify(r,a)['classification'])
    def test_real_height_change_preserved_without_threshold(self):
        r,a=fixture();a['heightInherited']=False;a['exactPerLineageHeightDifferenceRangesM'][0]=['1/1099511627776','1/1099511627776'];q=classify(r,a);self.assertFalse(q['exactIdealAffineHeightsInherited']);self.assertEqual(q['completeAncestorComparison'],a)
    def test_height_order_crossing_not_one_witness(self):
        r,a=fixture();r['proof']['exactSignedLeftMinusRightRangeM']=['-2','2'];self.assertEqual(classify(r,a)['heightOrdering'],'height order crosses')
    def test_point_cannot_enter_area_policy(self):
        r,a=fixture();r['proof']['exactProjectedDimension']='point'
        with self.assertRaises(AssertionError):classify(r,a)
    def test_source_id_wrong_candidate_rejected(self):
        r,a=fixture();r['leftProvenance']['candidateFace']=99
        with self.assertRaises(AssertionError):classify(r,a)
    def test_unknown_join_origin_not_silently_inherited(self):
        r,a=fixture();r['leftProvenance']['kind']='computedVerticalRuledJoin'
        with self.assertRaises(AssertionError):classify(r,a)
    def test_missing_saved_area_pair_rejected(self):
        r,a=fixture()
        with self.assertRaises(AssertionError):verify_complete([r],[])
    def test_changed_saved_witness_rejected(self):
        r,a=fixture();q=classify(r,a);q=copy.deepcopy(q);q['fullSavedCandidatePairProof']['proof']['exactSignedLeftMinusRightRangeM']=['0','0']
        with self.assertRaises(AssertionError):verify_complete([r],[q])
if __name__=='__main__':unittest.main()
