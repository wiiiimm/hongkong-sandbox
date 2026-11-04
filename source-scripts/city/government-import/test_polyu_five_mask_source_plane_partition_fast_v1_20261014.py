"""Synthetic oracle equivalence only; never replay the active source worker."""
import copy, random, time, unittest
from fractions import Fraction as F
import polyu_five_mask_source_plane_partition_v1_20261014 as old
import polyu_five_mask_source_plane_partition_fast_v1_20261014 as fast


def records(*triangles):
    return [dict(uid='actor-' + str(i), mask=i, kind='fixture', exactClosedProjection=t)
            for i, t in enumerate(triangles)]


class ExactOutputTests(unittest.TestCase):
    def compare(self, face, rows, *, protected=False):
        before = copy.deepcopy((face, rows))
        prepared = fast.PreparedMasks(rows)
        expected = old.partition(face, prepared.masks, protected_literal=protected)
        actual = fast.partition(face, prepared, protected_literal=protected)
        self.assertEqual(expected, actual)  # Includes polygon cycles/order, ownership and every occurrence.
        self.assertEqual(old.packed_pieces(expected['outside'], face), old.packed_pieces(actual['outside'], face))
        self.assertEqual(old.packed_pieces([q['polygon'] for q in expected['inside']], face),
                         old.packed_pieces([q['polygon'] for q in actual['inside']], face))
        self.assertEqual(before, (face, rows))
        return prepared, actual

    def test_duplicate_masks_keep_all_occurrences_and_earliest_owner(self):
        t=[[0,0],[2,0],[0,2]];p,r=self.compare([[0,0,0],[4,4,0],[0,0,4]],records(t,t,t))
        self.assertEqual([0,1,2],r['completeRelevantClosedAABBMasks']);self.assertEqual([0],list(p.aliases));self.assertEqual({0},{q['mask'] for q in r['inside']})

    def test_partial_overlap_and_multiple_owners(self):
        self.compare([[0,7,0],[5,12,0],[0,7,5]],records([[0,0],[3,0],[0,3]],[[1,0],[4,0],[1,3]],[[0,2],[2,2],[0,4]]))

    def test_nested_interior_hole_outside_pieces(self):
        self.compare([[0,0,0],[6,0,0],[0,0,6]],records([[1,1],[2,1],[1,2]],[[3,1],[4,1],[3,2]]))

    def test_closed_point_and_edge_touch(self):
        self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[2,0],[3,0],[2,1]],[[0,2],[2,0],[3,3]]))

    def test_one_sided_plane_keeps_boundary_vertices_in_outside_order(self):
        self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[2,0],[4,0],[2,4]]))

    def test_disjoint_masks_with_overlapping_boxes_keep_incidental_subdivisions(self):
        self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[2,2],[2,-1],[3,2]],[[1,2],[2,1],[3,3]]))

    def test_reversed_and_rotated_masks_are_not_merged(self):
        a=[[0,0],[2,0],[0,2]];rows=records(a,a[::-1],a[1:]+a[:1]);p,_=self.compare([[0,0,0],[4,0,0],[0,0,4]],rows)
        self.assertEqual(3,len(p.first_ids))

    def test_duplicate_after_different_owner_keeps_original_output(self):
        a=[[0,0],[2,0],[0,2]];b=[[1,0],[4,0],[1,3]]
        self.compare([[0,0,0],[5,0,0],[0,0,5]],records(a,b,a,b,a))

    def test_other_height_layer_uses_its_own_plane(self):
        for y in [0,100]:self.compare([[0,y,0],[4,y+4,0],[0,y,4]],records([[1,0],[3,0],[1,3]]))

    def test_vertical_and_zero_are_retained_whole(self):
        for face in [[[0,0,0],[0,2,0],[0,0,2]],[[1,2,3]]*3]:self.compare(face,records([[0,0],[2,0],[0,2]]))

    def test_protected_literal_rejection_is_unchanged(self):
        rows=records([[0,0],[2,0],[0,2]]);face=[[0,0,0],[4,0,0],[0,0,4]];p=fast.PreparedMasks(rows)
        for call in [lambda:old.partition(face,p.masks,protected_literal=True),lambda:fast.partition(face,p,protected_literal=True)]:
            with self.assertRaisesRegex(AssertionError,'protected literal'):call()

    def test_degenerate_mask_rejection_is_unchanged(self):
        with self.assertRaises(AssertionError):fast.PreparedMasks(records([[0,0],[0,0],[1,1]]))

    def test_non_dyadic_and_signed_zero_output_is_exact(self):
        self.compare([[0.,-0.,0.],[3.,1.,0.],[0.,0.,3.]],records([[0,0],['1/3',0],[0,'2/3']]))

    def test_exact_spatial_index_matches_full_closed_scan(self):
        rows=records(*([[(i,0),(i+1,0),(i,1)] for i in range(-20,21)] * 2));p=fast.PreparedMasks(rows)
        for x in range(-22,23):
            bound=[F(x),F(0),F(x+1),F(1)]
            _,actual=p.relevant(bound)
            expected=[i for i,m in enumerate(p.masks) if not fast._disjoint(bound,m['bounds'])]
            self.assertEqual(expected,actual)

    def test_deterministic_fraction_oracle_equivalence(self):
        rng=random.Random(274206)
        for case in range(80):
            a,b,c,d=[F(rng.randint(-4,8),rng.choice([1,2,3])) for _ in range(4)]
            face=[[F(0),F(1),F(0)],[F(5),F(6),F(0)],[F(0),F(1),F(5)]]
            m1=[[a,b],[a+F(2),b],[a,b+F(2)]];m2=[[c,d],[c+F(3),d],[c,d+F(1)]]
            with self.subTest(case=case):self.compare(face,records(m1,m2,m1,m2))


if __name__=='__main__':unittest.main(verbosity=2)
