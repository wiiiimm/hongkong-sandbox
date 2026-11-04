"""UNEXECUTED synthetic fixtures; no saved actual geometry calculations."""
import copy, hashlib, unittest
from fractions import Fraction as F
import numpy as np
import polyu_face891_saved_packed_closed_coverage_v1_draft_20261014 as h


def row(i, points, role='outside-retained-source', admitted=True, collapsed=False):
    p=[tuple(F(v) for v in x) for x in points]
    return dict(id=i,points=p,bound=h.bounds(p),role=role,heightAdmitted=admitted,
                collapsed=collapsed,projectedPositive=bool(h.coverage.signed_area(p)))


class CoverageFixtures(unittest.TestCase):
    def setUp(self):self.t=[(F(0),F(0)),(F(2),F(0)),(F(0),F(2))]

    def test_complete_triangle_and_all_closed_edges(self):
        result=h.closed_coverage(self.t,[row(0,self.t)])
        self.assertTrue(result['completeClosedXZCovered'])
        self.assertEqual(3,len(result['completeBoundaryEdges']))

    def test_internal_hole_with_all_outer_edges_retained(self):
        # Triangulated outer square ring: boundary success cannot certify area.
        outer=[(0,0),(3,0),(3,3),(0,3)]; inner=[(1,1),(2,1),(2,2),(1,2)]
        triangles=[]
        for i in range(4):
            j=(i+1)%4;triangles.extend([[outer[i],outer[j],inner[j]],[outer[i],inner[j],inner[i]]])
        result=h.closed_coverage([tuple(map(F,p)) for p in outer],[row(i,t) for i,t in enumerate(triangles)])
        self.assertTrue(all(e['covered'] for e in result['completeBoundaryEdges']))
        self.assertEqual(F(1),result['exactUncoveredAreaM2'])
        self.assertFalse(result['completeClosedXZCovered'])

    def test_positive_area_near_boundary_is_not_tolerated(self):
        tiny=F(1,2**100);smaller=[(tiny,0),(2,0),(tiny,2-tiny)]
        result=h.closed_coverage(self.t,[row(0,smaller)])
        self.assertGreater(result['exactUncoveredAreaM2'],0)
        self.assertFalse(result['completeClosedXZCovered'])

    def test_rational_target_not_rounded_to_binary64(self):
        target=[(F(1,3),F(0)),(F(1),F(0)),(F(1,3),F(1))]
        shifted=[(F(float(F(1,3))),0),(1,0),(F(float(F(1,3))),1)]
        result=h.closed_coverage(target,[row(0,shifted)])
        # Here float(1/3) rounds left, extending coverage; exact bound retained.
        self.assertEqual(target[0][0],F(1,3));self.assertTrue(result['completeClosedXZCovered'])
        shifted[0]=(F(1,3)+F(1,2**100),0);shifted[2]=(F(1,3)+F(1,2**100),1)
        self.assertFalse(h.closed_coverage(target,[row(0,shifted)])['completeClosedXZCovered'])

    def test_height_excluded_redundant_face_is_not_global_failure(self):
        rows=[row(0,self.t,admitted=False),row(1,self.t)]
        admitted=[r for r in rows if r['heightAdmitted']]
        self.assertTrue(h.closed_coverage(self.t,admitted)['completeClosedXZCovered'])

    def test_height_excluded_only_face_has_drawn_but_not_index_coverage(self):
        rows=[row(0,self.t,admitted=False)]
        self.assertTrue(h.closed_coverage(self.t,rows)['completeClosedXZCovered'])
        self.assertFalse(h.closed_coverage(self.t,[])['completeClosedXZCovered'])

    def test_collapsed_or_vertical_projection_gets_no_surface_credit(self):
        for r in [row(0,self.t,collapsed=True),row(0,[(0,0),(1,0),(2,0)])]:
            self.assertFalse(h.closed_coverage(self.t,[r])['completeClosedXZCovered'])

    def test_other_role_cannot_certify_retained_outside(self):
        rows=[row(0,self.t,role='inside-source-shadow-not-restored-parent')]
        self.assertTrue(h.closed_coverage(self.t,rows)['completeClosedXZCovered'])
        self.assertFalse(h.closed_coverage(self.t,[r for r in rows if r['role']=='outside-retained-source'])['completeClosedXZCovered'])

    def test_closed_line_and_point_contacts_preserve_exact_endpoints(self):
        rows=[self.t]
        self.assertTrue(h.edge_coverage((F(0),F(0)),(F(2),F(0)),rows)['covered'])
        self.assertTrue(h.edge_coverage((F(0),F(0)),(F(0),F(0)),rows)['covered'])
        self.assertFalse(h.edge_coverage((F(-1),F(0)),(F(2),F(0)),rows)['covered'])

    def test_exact_3d_zero_is_not_projected_zero(self):
        self.assertFalse(h.exact_zero_3d([(F(0),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(0),F(1))]))
        self.assertTrue(h.exact_zero_3d([(F(0),)*3,(F(1),)*3,(F(2),)*3]))

    def packet(self):
        t=[[0.,0.,0.],[2.,0.,0.],[0.,0.,2.]]
        return dict(complete=True,face=891,exactIdealPartition=dict(outside=[copy.deepcopy(t)],inside=[]),
            exactOwnPlanePackedPieces=[dict(exactOwnPlanePoints=copy.deepcopy(t),packedPieceTriplet=copy.deepcopy(t))],
            packedFacetCount=1,orderedOneFacePackedSHA256=hashlib.sha256(np.asarray(t,dtype='<f8').tobytes()).hexdigest(),
            exact3DAreaZeroPackedFacets=0,rendererExcludedProjectedFacetsAtExistingAbsDetLessThan1eMinus10=0)

    def test_saved_fan_order_and_inputs_immutable(self):
        packet=self.packet();before=copy.deepcopy(packet);regions,rows=h.map_saved_packet(packet)
        self.assertEqual(before,packet);self.assertEqual([0],regions[0]['packedPieceIDs'])
        packet['exactOwnPlanePackedPieces'][0]['exactOwnPlanePoints'].reverse()
        with self.assertRaises(AssertionError):h.map_saved_packet(packet)

    def test_non_float32_saved_value_fails_before_coverage(self):
        packet=self.packet();packet['exactOwnPlanePackedPieces'][0]['packedPieceTriplet'][0][0]=1/3
        with self.assertRaises(AssertionError):h.map_saved_packet(packet)

    def test_signed_zero_ordered_bytes_must_match_saved_digest(self):
        packet=self.packet();packet['exactOwnPlanePackedPieces'][0]['packedPieceTriplet'][0][0]=-0.0
        with self.assertRaises(AssertionError):h.map_saved_packet(packet)


if __name__=='__main__':unittest.main(verbosity=2)
