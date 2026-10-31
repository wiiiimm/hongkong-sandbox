"""UNEXECUTED focused parent-packing fixtures, no actual source evaluation."""
from fractions import Fraction as F
import copy,unittest
import polyu_computed_parent_cell_enclosure_v1_draft_20261014 as h

class ParentCellFixtures(unittest.TestCase):
    domain=[0,0,4,4]
    flat=[[0,6,0],[4,6,0],[0,6,4]]
    def hit(self,poly,mask=0):return dict(mask=mask,polygon=poly)
    def test_nondyadic_closed_region_has_drawn_and_admitted_enclosure(self):
        r=h.inside_piece(self.hit([[F(1,3),6,F(1,3)],[F(2,3),6,F(1,3)],[F(1,3),6,F(2,3)]]),self.flat,{},self.domain)['exactComputedParentCellKernelVerbatim']
        self.assertTrue(r['exactDrawnOutsideProjection']['completeClosedXZCovered']);self.assertTrue(r['exactHeightAdmittedOutsideProjection']['completeClosedXZCovered'])
    def test_dyadic_parent_rectangle_boundary_never_expands_beyond_domain(self):
        r=h.inside_piece(self.hit([[0,6,0],[F(1,3),6,0],[0,6,F(1,3)]]),self.flat,{},self.domain)['exactComputedParentCellKernelVerbatim']
        self.assertTrue(all(x>=0 and z>=0 for x,z in r['exactFloat32CellEnclosingHull']))
    def test_different_parent_planes_keep_own_height_and_shared_xz_cells(self):
        shared={};poly=[[F(1,3),6,F(1,3)],[1,6,F(1,3)],[F(1,3),6,1]]
        a=h.inside_piece(self.hit(poly),self.flat,shared,self.domain)['exactComputedParentCellKernelVerbatim']
        b=h.inside_piece(self.hit([[x,9,z]for x,y,z in poly]),[[0,9,0],[4,9,0],[0,9,4]],shared,self.domain)['exactComputedParentCellKernelVerbatim']
        self.assertEqual(a['exactFloat32CellEnclosingHull'],b['exactFloat32CellEnclosingHull']);self.assertNotEqual(a['triangles'],b['triangles'])
    def test_slope_lifts_on_source_plane_before_f32_storage(self):
        face=[[0,2,0],[4,6,0],[0,2,4]];poly=[[F(1,3),F(7,3),F(1,3)],[1,3,F(1,3)],[F(1,3),F(7,3),1]]
        r=h.inside_piece(self.hit(poly),face,{},self.domain)['exactComputedParentCellKernelVerbatim']
        self.assertTrue(all(y==2+x for t in r['triangles']for x,y,z in t['idealSourcePlanePoints']))
    def test_saved_first_ownership_and_all_regions_preserved_no_input_mutation(self):
        proof=dict(completeOwnPlanePartition=True,inside=[self.hit([[0,6,0],[1,6,0],[0,6,1]],9),self.hit([[1,6,0],[1,6,1],[0,6,1]],3)]);before=copy.deepcopy(proof)
        p,a=h.parent_pieces(proof,self.flat,{},self.domain,lambda *_:None)
        self.assertEqual([r['mask']for r in a['completeSavedInsideRegions']],[9,3]);self.assertEqual(proof,before);self.assertTrue(p)
    def test_vertical_parent_cannot_supply_invented_affine_height(self):
        with self.assertRaises(AssertionError):h.inside_piece(self.hit([[0,0,0],[1,0,0],[0,0,1]]),[[0,0,0],[0,1,0],[0,0,1]],{},self.domain)
    def test_out_of_parent_target_rejected_instead_of_clipped(self):
        with self.assertRaises(AssertionError):h.inside_piece(self.hit([[-1,6,0],[1,6,0],[0,6,1]]),self.flat,{},self.domain)
    def test_nonf32_extent_and_zero_target_rejected_without_infill(self):
        with self.assertRaises(AssertionError):h.inside_piece(self.hit([[0,6,0],[1,6,0],[0,6,1]]),self.flat,{},[0,0,F(10,3),4])
        with self.assertRaises(AssertionError):h.inside_piece(self.hit([[0,6,0],[1,6,0],[2,6,0]]),self.flat,{},self.domain)
        with self.assertRaises(AssertionError):h.inside_piece(self.hit([[0,7,0],[1,7,0],[0,7,1]]),self.flat,{},self.domain)
if __name__=='__main__':unittest.main(verbosity=2)
