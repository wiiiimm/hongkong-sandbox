"""UNEXECUTED saved-union/provenance locator fixtures; no actual source."""
import unittest
import numpy as np
from shapely.geometry import LineString,GeometryCollection
import polyu_saved_rectangle_gap_attribution_v1_draft_20261014 as h
class LocatorFixtures(unittest.TestCase):
    half=np.asarray([[[0,2,0],[1,2,0],[0,2,1]]],dtype='<f8')
    def test_missing_distinct_from_outside(self):
        _,m,_,_=h.measure(self.half,[0,0,1,1]);self.assertEqual(m['measuredMissingAreaM2'],.5);self.assertEqual(m['measuredOutsideAreaM2'],0)
    def test_outside_and_missing_both_retained(self):
        raw=np.concatenate([self.half,np.asarray([[[1,2,0],[2,2,0],[1,2,1]]])]);_,m,_,_=h.measure(raw,[0,0,1,1])
        self.assertEqual(m['measuredMissingAreaM2'],.5);self.assertEqual(m['measuredOutsideAreaM2'],.5);self.assertEqual(m['measuredSymmetricDifferenceAreaM2'],1)
    def test_complete_two_face_rectangle_has_no_area_gap(self):
        raw=np.concatenate([self.half,np.asarray([[[1,2,0],[1,2,1],[0,2,1]]])]);_,m,missing,outside=h.measure(raw,[0,0,1,1])
        self.assertEqual(m['measuredSymmetricDifferenceAreaM2'],0);self.assertEqual(h.regions(missing)+h.regions(outside),[])
    def test_zero_face_still_counted_without_invented_index_gate(self):
        raw=np.concatenate([self.half,np.asarray([[[0,0,0],[0,2,0],[0,0,1]]])]);_,m,_,_=h.measure(raw,[0,0,1,1])
        self.assertEqual(m['completeNativeFaces'],2);self.assertEqual(m['validatorIncludedFaces'],1);self.assertEqual(m['measuredMissingAreaM2'],.5)
        self.assertEqual(h.regions(GeometryCollection([LineString([(0,0),(1,1)])])),[])
    def test_region_point_does_not_create_source_coverage(self):
        polygons,_,missing,_=h.measure(self.half,[0,0,1,1]);complete=h.CompleteGround(self.half)
        p=dict(candidateFace=0,kind='synthetic-source-plane',ancestor=dict(oldPrivateFace=5))
        row=h.attribute_component(missing,0,'missing',complete,self.half,polygons,[p])
        self.assertEqual(row['GEOSRepresentativeDiagnosticPoint']['nativeClosedMembership']['closedMembers'],[])
        self.assertTrue(row['GEOSRepresentativeDiagnosticPoint']['notClaimedExactAreaWitness'])
    def test_provenance_face_order_cannot_be_guessed(self):
        with self.assertRaises(AssertionError):h.source_descriptor(dict(candidateFace=1,kind='synthetic'),0)
        p=h.source_descriptor(dict(candidateFace=0,kind='synthetic',ancestor=dict(oldPrivateFace=99)),0)
        self.assertEqual(p['oldPrivateFace'],99);self.assertTrue(p['noArchitecturalOrPhysicalRoleClaim'])
if __name__=='__main__':unittest.main(verbosity=2)
