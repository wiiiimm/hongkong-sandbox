"""UNEXECUTED draft: full-record equivalence and unchanged negative cases."""
import gzip,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import exact_original_face_conservative_clearance_v5_20261010 as coarse
import exact_original_paired_finite_clearance_20261010 as legacy
import southside_proven_coverage_reuse_draft_v1_20261012 as draft

def previous(face,ground):
    a=coarse.verify(face,ground);b=None if a['existingOrdinaryClearanceBoundProved']else legacy.verify(face,ground)
    return dict(coarse=a,paired=b,completeFiniteOrdinaryBoundProved=bool(a['existingOrdinaryClearanceBoundProved']or(b and b['existingOrdinaryClearanceBoundProved'])))

def surface(y=0):
    return np.array([[[0,y,0],[1,y,0],[0,y,1]],[[1,y,0],[1,y,1],[0,y,1]]],float)

class Reuse(unittest.TestCase):
    def equal(self,face,ground):
        out=draft.verify(face,ground);self.assertEqual(out,previous(face,ground));return out
    def test_coarse_positive_keeps_no_paired_record(self):
        out=self.equal([[0,2,0],[1,2,0],[0,2,1]],surface());self.assertIsNone(out['paired'])
    def test_affine_pair_proves_when_vertex_bound_cannot(self):
        ground=surface();ground[:,:,1]=ground[:,:,0]*2
        face=[[0,.2,0],[1,2.2,0],[0,.2,1]]
        out=self.equal(face,ground);self.assertFalse(out['coarse']['existingOrdinaryClearanceBoundProved']);self.assertTrue(out['paired']['existingOrdinaryClearanceBoundProved'])
    def test_exact_half_metre_limit(self):
        out=self.equal([[0,-.5,0],[1,-.5,0],[0,-.5,1]],surface());self.assertTrue(out['completeFiniteOrdinaryBoundProved'])
    def test_next_double_below_limit_stays_negative(self):
        y=np.nextafter(-.5,-np.inf);out=self.equal([[0,y,0],[1,y,0],[0,y,1]],surface());self.assertFalse(out['completeFiniteOrdinaryBoundProved'])
    def test_reverse_source_and_ground_winding(self):
        face=np.array([[0,-1,0],[1,-1,0],[0,-1,1]],float)
        self.equal(face[::-1],surface()[:,::-1])
    def test_vertical_source_interval(self):
        self.equal([[.2,-1,.2],[.8,1,.2],[.2,1,.2]],surface())
    def test_point_projection(self):
        self.equal([[.2,-1,.2],[.2,1,.2],[.2,2,.2]],surface())
    def test_collapsed_ground_retains_conservative_negative(self):
        ground=np.concatenate([surface(),np.array([[[0,4,0],[0,4,1],[0,5,.5]]])])
        out=self.equal([[0,1,0],[1,1,0],[0,1,1]],ground)
        self.assertFalse(out['completeFiniteOrdinaryBoundProved']);self.assertTrue(any(q.get('collapsedProjectionConservative')for q in out['paired']['allExactFiniteSourceGroundPieces']))
    def test_exact_coverage_gap_uses_legacy_record(self):
        ground=surface()[:1];face=[[0,-1,0],[1,-1,1],[1,-1,0]]
        with patch.object(draft.legacy,'verify',wraps=legacy.verify)as called:
            out=draft.verify(face,ground);self.assertEqual(called.call_count,1)
        self.assertEqual(out,previous(face,ground));self.assertFalse(out['completeFiniteOrdinaryBoundProved'])
    def test_multiple_planes_keep_upper_envelope_gap(self):
        ground=np.concatenate([surface(),surface(3)])
        self.equal([[0,1,0],[1,1,0],[0,1,1]],ground)
    def test_positive_coverage_does_not_call_legacy_coverage(self):
        with patch.object(draft.legacy,'exact_coverage',side_effect=AssertionError('duplicate coverage')):
            out=draft.verify([[0,-1,0],[1,-1,0],[0,-1,1]],surface())
        self.assertFalse(out['completeFiniteOrdinaryBoundProved'])
    def test_missing_ground_scope_remains_contract_failure(self):
        face=[[0,0,0],[1,0,0],[0,0,1]]
        ground=surface()+[10,0,10]
        with self.assertRaises(AssertionError):draft.verify(face,ground)
    def test_actual_saved_mall_failure_all_four_views(self):
        root=Path(__file__).resolve().parents[3]
        base=root/'docs/astra-city/government-import'
        def read(path):
            with gzip.open(path,'rt')as handle:return json.load(handle)
        captured=read(base/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012/complete-two-actor-four-stream-ground-inputs.json.gz')['rows']['landsd/315025:0']
        grade=read(base/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012/diagnostic.json.gz')
        bymode={q['arithmetic']:q for q in grade['rows']if q['uid']=='landsd/315025:0'}
        ground=np.asarray(captured['completeDrawnGround'],float)
        for mode,stream in captured['completeWorldStreams'].items():
            with self.subTest(mode=mode):
                faceid=bymode[mode]['allRawFailedFaces'][0]
                self.equal(stream['completeWorldTriangles'][faceid],ground)

if __name__=='__main__':unittest.main()
