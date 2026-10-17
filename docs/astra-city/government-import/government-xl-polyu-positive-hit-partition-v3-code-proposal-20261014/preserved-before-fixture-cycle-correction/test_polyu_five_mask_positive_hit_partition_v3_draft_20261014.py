"""UNEXECUTED synthetic exact continuous-surface/ownership fixtures, not rendering."""
import copy, random, unittest
from fractions import Fraction as F
import polyu_five_mask_source_plane_partition_fast_v1_20261014 as v2
import polyu_five_mask_positive_hit_partition_v3_draft_20261014 as v3


def records(*triangles):
    return [dict(uid=str(i), mask=i, exactClosedProjection=t) for i,t in enumerate(triangles)]


def polygon_planes(poly):
    p=[(q[0],q[2])for q in poly]
    twice=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(p,p[1:]+p[:1]))
    assert twice
    if twice<0:p.reverse()
    return [(-(b[1]-a[1]), b[0]-a[0], (b[1]-a[1])*a[0]-(b[0]-a[0])*a[1])
            for a,b in zip(p,p[1:]+p[:1]) if a!=b]


def difference_area(left,right,axis):
    pending=left
    for poly in right:
        following=[]
        for piece in pending:
            _,rest=v2._split_positive(piece,polygon_planes(poly),axis)
            following.extend(rest)
        pending=following
    return sum((v2.oracle.old.intrinsic_area(p,axis)for p in pending),F(0))


def closed_segment_covered(a,b,polygons):
    intervals=[]
    for poly in polygons:
        lo,hi=F(0),F(1)
        for x,z,c in polygon_planes(poly):
            p=x*a[0]+z*a[2]+c;q=x*b[0]+z*b[2]+c
            if p<0 and q<0:lo,hi=F(1),F(0);break
            if p<0:lo=max(lo,p/(p-q))
            if q<0:hi=min(hi,p/(p-q))
        if lo<=hi:intervals.append((lo,hi))
    end=F(0)
    for lo,hi in sorted(intervals):
        if lo>end:return False
        end=max(end,hi)
    return bool(intervals)and end==1


class ContinuousSurfaceTests(unittest.TestCase):
    def compare(self,face,rows):
        snapshot=copy.deepcopy((face,rows));prepared=v2.PreparedMasks(rows)
        old=v2.partition(face,prepared);new=v3.partition(face,prepared)
        self.assertEqual(snapshot,(face,rows));self.assertFalse(new['packedOutputEquivalenceClaimed'])
        if old.get('projectedVerticalOrZeroPreservedWhole'):
            self.assertEqual(old['inside'],new['inside']);self.assertEqual(old['outside'],new['outside']);return old,new
        self.assertEqual(old['completeRelevantClosedAABBMasks'],new['completeRelevantClosedAABBMasks'])
        axis=max(range(3),key=lambda k:abs(v2.oracle.normal(v2.oracle.points(face))[k]))
        for key in ['exactWholeIntrinsicArea','exactInsideMaskUnionIntrinsicArea','exactOutsideMaskUnionIntrinsicArea']:self.assertEqual(old[key],new[key])
        for name in ['outside','inside']:
            a=old[name]if name=='outside'else [x['polygon']for x in old[name]]
            b=new[name]if name=='outside'else [x['polygon']for x in new[name]]
            self.assertEqual(0,difference_area(a,b,axis));self.assertEqual(0,difference_area(b,a,axis))
        for mi in prepared.first_ids:
            a=[x['polygon']for x in old['inside']if x['mask']==mi];b=[x['polygon']for x in new['inside']if x['mask']==mi]
            self.assertEqual(0,difference_area(a,b,axis));self.assertEqual(0,difference_area(b,a,axis))
        polygons=new['outside']+[x['polygon']for x in new['inside']]
        points=v2.oracle.points(face)
        self.assertTrue(all(closed_segment_covered(a,b,polygons)for a,b in zip(points,points[1:]+points[:1])))
        return old,new

    def test_strict_fragment_disjointness_retains_whole_polygon(self):
        self.compare([[0,0,0],[3,0,0],[0,0,3]],records([[5,5],[6,5],[5,6]]))

    def test_zero_hit_removes_incidental_outside_cuts_without_surface_loss(self):
        old,new=self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[2,2],[2,-1],[3,2]]))
        self.assertGreater(len(old['outside']),len(new['outside']));self.assertEqual(1,len(new['outside']))

    def test_closed_point_touch_stays_in_retained_surface(self):
        self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[2,0],[4,0],[2,2]]))

    def test_closed_full_edge_touch_stays_in_retained_surface(self):
        self.compare([[0,0,0],[2,0,0],[0,0,2]],records([[0,2],[2,0],[2,2]]))

    def test_partial_overlap_and_first_ownership_are_exact(self):
        self.compare([[0,3,0],[5,8,0],[0,3,5]],records([[0,0],[3,0],[0,3]],[[1,0],[4,0],[1,3]]))

    def test_duplicates_keep_all_occurrences(self):
        _,new=self.compare([[0,0,0],[4,0,0],[0,0,4]],records([[0,0],[2,0],[0,2]],[[0,0],[2,0],[0,2]]))
        self.assertEqual([0,1],new['completeRelevantClosedAABBMasks']);self.assertEqual({0:[0,1]},new['allOriginalMaskOccurrenceAliases'])

    def test_nested_masks_and_separate_interior_regions(self):
        self.compare([[0,1,0],[8,9,0],[0,1,8]],records([[1,1],[3,1],[1,3]],[[1,1],[2,1],[1,2]],[[4,1],[5,1],[4,2]]))

    def test_whole_containment_has_no_outside(self):
        _,new=self.compare([[0,0,0],[1,0,0],[0,0,1]],records([[-1,-1],[4,-1],[-1,4]]));self.assertEqual([],new['outside'])

    def test_vertical_and_zero_are_uncredited_whole(self):
        for face in [[[0,0,0],[0,2,0],[0,0,2]],[[0,0,0]]*3]:self.compare(face,records([[0,0],[2,0],[0,2]]))

    def test_other_height_layer_never_donates_y(self):
        for y in [0,100]:self.compare([[0,y,0],[4,y+4,0],[0,y,4]],records([[1,0],[3,0],[1,3]]))

    def test_protected_literal_rejection_unchanged(self):
        prepared=v2.PreparedMasks(records([[0,0],[2,0],[0,2]]))
        with self.assertRaisesRegex(AssertionError,'protected literal'):v3.partition([[0,0,0],[4,0,0],[0,0,4]],prepared,protected_literal=True)

    def test_non_dyadic_packing_remains_a_separate_obligation(self):
        _,new=self.compare([[0,0,0],[3,1,0],[0,0,3]],records([[0,0],['1/3',0],[0,'2/3']]))
        pieces=v2.oracle.packed_pieces([x['polygon']for x in new['inside']],[[0,0,0],[3,1,0],[0,0,3]])
        self.assertTrue(any(x for p in pieces for x in p['exactPackedSourcePlaneResiduals']));self.assertTrue(new['freshPackedQualificationRequired'])

    def test_flat_float32_plane_still_cannot_certify_closed_packed_coverage(self):
        _,new=self.compare([[0,8,0],[3,8,0],[0,8,3]],records([[0,0],['1/3',0],[0,'2/3']]))
        pieces=v2.oracle.packed_pieces([x['polygon']for x in new['inside']],[[0,8,0],[3,8,0],[0,8,3]])
        self.assertFalse(any(x for p in pieces for x in p['exactPackedSourcePlaneResiduals']))
        self.assertFalse(new['packedOutputEquivalenceClaimed']);self.assertTrue(new['freshPackedQualificationRequired'])

    def test_bounded_progress_reports_count_only(self):
        prepared=v2.PreparedMasks(records([[0,0],[1,0],[0,1]],[[2,0],[3,0],[2,1]]));seen=[]
        v3.partition([[0,0,0],[4,0,0],[0,0,4]],prepared,progress=seen.append)
        self.assertEqual(2,len(seen));self.assertTrue(all(x['diagnosticOnly']for x in seen));self.assertTrue(all('pending'not in x for x in seen))

    def test_deterministic_exact_union_oracle_cases(self):
        rng=random.Random(891)
        for i in range(30):
            x,z=F(rng.randint(-2,8),3),F(rng.randint(-2,8),2)
            with self.subTest(i=i):self.compare([[0,0,0],[5,5,0],[0,0,5]],records([[x,z],[x+2,z],[x,z+2]],[[1,1],[3,1],[1,3]]))


if __name__=='__main__':unittest.main(verbosity=2)
