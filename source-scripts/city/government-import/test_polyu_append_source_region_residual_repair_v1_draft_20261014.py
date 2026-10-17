"""UNEXECUTED complete source-region append fixtures, synthetic only."""
from fractions import Fraction as F
import copy,unittest
import numpy as np
import polyu_append_source_region_residual_repair_v1_draft_20261014 as h
class AppendFixtures(unittest.TestCase):
    def setUp(self):
        self.plane=[[0,2,0],[4,2,0],[0,2,4]];self.poly=[[F(1,3),2,F(1,3)],[1,2,F(1,3)],[F(1,3),2,1]]
        self.target=dict(oldPrivateFace=0,outsidePolygon=0,completeIdealOutsidePolygon=self.poly,ownProposedPlane=self.plane,previousLineageVerbatim={},locatorRegions=[1],sourcePointer=dict(oldPrivateFace=0,outsidePolygon=0))
        row=dict(oldPrivateFace=0,newCandidateFaces=[0],previousLineageVerbatim=dict(exactProposedPoints=self.plane),completeExactMaskPartition=dict(completeOwnPlanePartition=True,outside=[self.poly]))
        self.nom=dict(completeOldPrivateMapping=[row],candidateFaceProvenance=[dict(candidateFace=0,kind='unchangedPreviousPrivateDraw',oldPrivateFace=0)])
        self.region=dict(region=1,kind='missing',absoluteXZBounds=[0,0,2,2],completeClosedBBoxNominations=[dict(candidateFace=0)],GEOSRepresentativeDiagnosticPoint=dict(nativeClosedMembership=dict(closedMembers=[])))
    def test_source_coordinates_not_gap_locator_vertices_construct_geometry(self):
        targets,_=h.select_targets(dict(regions=[self.region]),self.nom);self.assertEqual(targets[0]['completeIdealOutsidePolygon'],self.poly)
        altered=copy.deepcopy(self.region);altered['GEOSRepresentativeDiagnosticPoint']['x']=999
        other,_=h.select_targets(dict(regions=[altered]),self.nom);self.assertEqual(targets,other)
    def test_duplicate_regions_deduplicate_source_key_without_losing_lineage(self):
        other=copy.deepcopy(self.region);other['region']=2
        targets,_=h.select_targets(dict(regions=[self.region,other]),self.nom);self.assertEqual(len(targets),1);self.assertEqual(targets[0]['locatorRegions'],[1,2])
    def test_covered_contradiction_and_existing_enclosure_do_not_trigger_blind_replay(self):
        self.region['GEOSRepresentativeDiagnosticPoint']['nativeClosedMembership']['closedMembers']=[dict(face=0)]
        targets,meta=h.select_targets(dict(regions=[self.region]),self.nom);self.assertEqual(targets,[]);self.assertEqual(meta['contradictoryCoveredRepresentativeRegions'],[1])
        self.region['GEOSRepresentativeDiagnosticPoint']['nativeClosedMembership']['closedMembers']=[];self.nom['completeOldPrivateMapping'][0]['computedOutsideEnclosureAccount']={'already':True}
        self.assertEqual(h.select_targets(dict(regions=[self.region]),self.nom)[0],[])
    def test_exact_rectangle_clip_stays_on_same_source_plane(self):
        target=copy.deepcopy(self.target);target['completeIdealOutsidePolygon']=[[-1,2,0],[1,2,0],[0,2,1]]
        account=h.enclose_target(target,[0,0,4,4],{});k=account['exactOwnPlaneCellEnclosure']
        self.assertTrue(all(x>=0 and z>=0 for x,z in k['exactFloat32CellEnclosingHull']));self.assertTrue(all(y==2 for t in k['triangles']for x,y,z in t['idealSourcePlanePoints']))
    def test_append_preserves_all_old_slots_indices_and_signed_zero(self):
        mesh=dict(position=[-0.0,2,0,1,2,0,0,2,1,99,99,99],index=[0,1,2]);before=copy.deepcopy(mesh)
        out,meta=h.append_pieces(mesh,[h.enclose_target(self.target,[0,0,4,4],{})]);self.assertEqual(mesh,before)
        self.assertEqual(np.asarray(out['position'][:12],dtype='<f8').tobytes(),np.asarray(mesh['position'],dtype='<f8').tobytes());self.assertEqual(out['index'][:3],mesh['index']);self.assertTrue(meta['appendedFaces'])
    def test_byte_identical_existing_geometry_not_appended_again(self):
        account=h.enclose_target(self.target,[0,0,4,4],{});mesh=dict(position=[],index=[])
        # Seed every exact enclosure triangle, preserving its source geometry.
        for t in account['exactOwnPlaneCellEnclosure']['triangles']:
            start=len(mesh['position'])//3;mesh['position'].extend(v for p in t['packedPieceTriplet']for v in p);mesh['index'].extend(range(start,start+3))
        out,meta=h.append_pieces(mesh,[account]);self.assertEqual(out,mesh);self.assertEqual(meta['appendedFaces'],[]);self.assertTrue(meta['exactExistingRepresentations'])
    def test_other_plane_height_never_supplies_lift(self):
        shared={};a=h.enclose_target(self.target,[0,0,4,4],shared);other=copy.deepcopy(self.target)
        other['completeIdealOutsidePolygon']=[[x,9,z]for x,y,z in self.poly];other['ownProposedPlane']=[[x,9,z]for x,y,z in self.plane]
        b=h.enclose_target(other,[0,0,4,4],shared);self.assertEqual(a['exactOwnPlaneCellEnclosure']['exactFloat32CellEnclosingHull'],b['exactOwnPlaneCellEnclosure']['exactFloat32CellEnclosingHull']);self.assertNotEqual(a['exactOwnPlaneCellEnclosure']['triangles'],b['exactOwnPlaneCellEnclosure']['triangles'])
    def test_closed_disjoint_source_and_zero_projection_get_no_infill(self):
        r=copy.deepcopy(self.region);r['absoluteXZBounds']=[3,3,4,4]
        self.assertEqual(h.select_targets(dict(regions=[r]),self.nom)[0],[])
        t=copy.deepcopy(self.target);t['completeIdealOutsidePolygon']=[[0,2,0],[1,2,0],[2,2,0]]
        self.assertTrue(h.enclose_target(t,[0,0,4,4],{})['noPositiveRestrictedSourceRegion'])
if __name__=='__main__':unittest.main(verbosity=2)
