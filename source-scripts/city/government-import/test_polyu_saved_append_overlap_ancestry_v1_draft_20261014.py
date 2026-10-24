"""UNEXECUTED five synthetic measurement/ancestry/actual-edge fixtures."""
import unittest
import numpy as np
from shapely.geometry import Polygon
import polyu_saved_append_overlap_ancestry_v1_draft_20261014 as h
class OverlapFixtures(unittest.TestCase):
    def test_complete_adjacent_rectangle_zero_excess(self):
        raw=np.asarray([[[0,0,0],[1,0,0],[0,0,1]],[[1,0,0],[1,0,1],[0,0,1]]]);_,ids,m=h.measurement(raw,[0,0,1,1])
        self.assertEqual(ids,[0,1]);self.assertEqual(m['nativeProjectedExcessM2'],0);self.assertEqual(m['measuredSymmetricCoverageDifferenceM2'],0)
    def test_duplicate_source_layers_are_counted_not_deduplicated(self):
        face=[[0,0,0],[1,0,0],[0,0,1]];_,ids,m=h.measurement([face,face],[0,0,1,1])
        self.assertEqual(ids,[0,1]);self.assertEqual(m['nativeProjectedExcessM2'],.5);self.assertEqual(m['measuredMissingInsideM2'],.5)
    def test_distinct_heights_and_packing_difference_remain_explicit(self):
        raw=np.asarray([[[0,1,0],[1,1,0],[0,1,1]],[[0,3,0],[1,3,0],[0,3,1]]]);d=[dict(sourcePlaneKey='a'),dict(sourcePlaneKey='b')]
        sources=dict(a=dict(kind='legacy',exactOwnPlane=h.rational_plane(raw[0])),b=dict(kind='parent',exactOwnPlane=h.rational_plane(raw[1])))
        q=h.pair_record(0,1,Polygon([[0,0],[1,0],[0,1]]),raw,d,sources)
        self.assertEqual(q['exactPackedSignedLeftMinusRightAtMeasuredVertices'],['-2','-2']);self.assertFalse(q['sameAuthenticatedIdealPlane']);self.assertTrue(q['differentSourceKinds'])
        sources['b']['exactOwnPlane']=sources['a']['exactOwnPlane'];q=h.pair_record(0,1,Polygon([[0,0],[1,0],[0,1]]),raw,d,sources)
        self.assertTrue(q['sameAuthenticatedIdealPlane']);self.assertEqual(q['exactPackedSignedLeftMinusRightAtMeasuredVertices'],['-2','-2'])
    def test_projected_zero_retained_but_excluded_and_boundary_not_area(self):
        raw=[[[0,0,0],[1,0,0],[0,0,1]],[[1,0,0],[2,0,0],[1,0,1]],[[0,0,0],[0,1,0],[0,2,0]]]
        p,ids,m=h.measurement(raw,[0,0,2,1]);self.assertEqual(ids,[0,1]);self.assertEqual(m['allOtherDrawnFaceIDs'],[2]);self.assertEqual(p[0].intersection(p[1]).area,0)
    def test_actual_unused_position_boundary_is_in_existing_edge_inventory(self):
        parent=dict(w=2,h=2,elev=[0]*4,renderedElev=[0]*4,meta=dict(georef=dict(aE=1,aN=-1,bE=834500,bN=816500)))
        patch=dict(nativeMesh=dict(position=[0,0,0,1,0,0,0,0,1,0,2,1],index=[0,1,2]))
        q=h.parent_edge_rows(patch,parent,[0,0,1,1]);self.assertEqual(q['completePositionSlotsIncludingUnused'],4);self.assertEqual(q['maxGapM'],2);self.assertEqual(q['allActualValidatorEdgeVertices'][-1]['positionSlot'],3)
if __name__=='__main__':unittest.main(verbosity=2)
