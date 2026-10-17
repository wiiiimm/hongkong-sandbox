import unittest
from fractions import Fraction as F
from polyu_five_mask_source_plane_partition_v1_20261014 import partition,masks_from_records,packed_pieces,verify_saved_packing,protected_literal_declaration


class Tests(unittest.TestCase):
    def masks(self,*ts):return masks_from_records([dict(uid=str(i),mask=i,exactClosedProjection=t)for i,t in enumerate(ts)])
    def test_overlapping_masks_union_has_no_duplicate_area(self):
        face=[[0,2,0],[4,6,0],[0,2,4]];m=self.masks([[0,0],[3,0],[0,3]],[[0,0],[2,0],[0,2]])
        r=partition(face,m);self.assertEqual(r['exactWholeIntrinsicArea'],r['exactInsideMaskUnionIntrinsicArea']+r['exactOutsideMaskUnionIntrinsicArea'])
        self.assertEqual(r['exactInsideMaskUnionIntrinsicArea'],F(9,2));self.assertEqual(len(r['inside']),1)
    def test_sloped_source_and_other_height_layer_keep_own_y(self):
        m=self.masks([[0,0],[1,0],[0,1]])
        for y in [0,100]:
            face=[[0,y,0],[2,y+2,0],[0,y,2]];r=partition(face,m)
            for q in packed_pieces(r['outside'],face):
                for x,h,z in q['exactOwnPlanePoints']:self.assertEqual(h,F(y)+x)
    def test_current_parent_cut_uses_parent_plane_not_source_plane(self):
        m=self.masks([[0,0],[1,0],[0,1]]);parent=[[0,7,0],[2,9,0],[0,7,2]]
        r=partition(parent,m);pieces=packed_pieces([q['polygon']for q in r['inside']],parent)
        self.assertTrue(pieces)
        for q in pieces:
            for x,y,z in q['exactOwnPlanePoints']:self.assertEqual(y,F(7)+x)
    def test_disjoint_face_and_closed_touch_have_no_removed_area(self):
        face=[[0,0,0],[1,0,0],[0,0,1]]
        for t in [[[2,2],[3,2],[2,3]],[[1,0],[2,0],[1,1]]]:
            r=partition(face,self.masks(t));self.assertEqual(r['exactInsideMaskUnionIntrinsicArea'],0)
    def test_projected_vertical_and_point_retained_whole(self):
        for face in [[[0,0,0],[0,2,0],[0,0,1]],[[0,2,0]]*3]:
            r=partition(face,self.masks([[0,0],[1,0],[0,1]]));self.assertTrue(r['projectedVerticalOrZeroPreservedWhole']);self.assertEqual(r['inside'],[])
    def test_protected_literal_cannot_be_split(self):
        with self.assertRaises(AssertionError):partition([[0,0,0],[2,0,0],[0,0,2]],self.masks([[0,0],[1,0],[0,1]]),protected_literal=True)
    def test_non_dyadic_new_node_packing_residual_is_explicit(self):
        face=[[0,0,0],[3,1,0],[0,0,3]];m=self.masks([[0,0],['1/3',0],[0,'1/3']]);r=partition(face,m)
        ps=packed_pieces([q['polygon']for q in r['inside']],face);self.assertTrue(any(v for q in ps for v in q['exactPackedSourcePlaneResiduals']))
    def test_degenerate_mask_rejected_not_dropped(self):
        with self.assertRaises(AssertionError):self.masks([[0,0],[0,0],[0,0]])
    def test_real_saved_facet0_rational_strings_reproduce_exact_packed_bytes(self):
        ideal=[['1043081/512','200950823/31447040','-18598132187/9434112'],['1045641/512','40089995/8388608','-2016439/1024'],['1043081/512','6401943927/990402560','-27916530943/14148608']]
        raw=[[2037.267578125,6.390134811401367,-1971.3707275390625],[2042.267578125,4.779099941253662,-1969.1787109375],[2037.267578125,6.463981628417969,-1973.0938720703125]]
        self.assertTrue(verify_saved_packing(ideal,raw))
        changed=[p[:]for p in raw];changed[0][1]+=1
        with self.assertRaises(AssertionError):verify_saved_packing(ideal,changed)
    def test_absent_prior_protection_declaration_is_explicit_no_credit(self):
        ids,q=protected_literal_declaration({'outputFacets':3214},3214)
        self.assertEqual(ids,[]);self.assertFalse(q['declarationPresent']);self.assertTrue(q['noPriorLiteralProtectionCredit']);self.assertTrue(q['fullSourceAndPhysicalObligationsPending'])
    def test_explicit_protection_declaration_must_bind_exact_existing_ids(self):
        ids,q=protected_literal_declaration({'protectedLiteralOutputFacetIDs':[0,3]},4)
        self.assertEqual(ids,[0,3]);self.assertTrue(q['declarationPresent'])
        for ids in [[0,0],[3,0],[4],[-1],[True],None]:
            with self.assertRaises(AssertionError):protected_literal_declaration({'protectedLiteralOutputFacetIDs':ids},4)

if __name__=='__main__':unittest.main()
