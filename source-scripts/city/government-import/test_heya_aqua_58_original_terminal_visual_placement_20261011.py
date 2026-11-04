"""Actual-source provenance, exact role scope and no-support adverse cases."""
import copy,unittest
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from heya_aqua_58_original_terminal_visual_placement_20261011 import verify,UID,IMAGES,NAMED
class ActualSourceCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b=ROOT/'docs/astra-city/government-import'
        cls.c=read(b/'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011/diagnostic.json.gz')
        cls.x=read(b/'government-xl-heya-aqua-terminal-parts-orthographic-context-v2-20261011/context.json')
        rows=read(b/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json')['sources']
        cls.w=decode_original_world_triangles((ROOT/next(r for r in rows if r['uid']==UID)['candidate']['path']).read_bytes())
    def run_case(self,c=None,w=None,x=None,images=None):
        return verify(census=self.c if c is None else c,world=self.w if w is None else w,
            context=self.x if x is None else x,image_refs=IMAGES if images is None else images)
    def changed(self,edit):
        c=copy.deepcopy(self.c);edit(c)
        with self.assertRaises(AssertionError):self.run_case(c=c)
    def test_complete_actual58(self):
        r=self.run_case();self.assertEqual(r['completeNamedTerminalComponents'],NAMED)
        self.assertEqual(len(r['completeNamedTerminalFaces']),1312)
        self.assertTrue(all(not p['structuralRootCredit']and not p['structuralBridgeCredit']and not p['loadBearingClaim']and not p['functionCertified']and not p['mountCertified']for p in r['complete58PlacementRecords']))
    def test_wrong_uid(self):self.changed(lambda c:c.update(uids=['landsd/184287:0','landsd/184285:0']))
    def test_wrong_native_source(self):self.changed(lambda c:c['actors'][UID]['sourceTuple'].update(sourceSHA256='0'*64))
    def test_wrong_primary_csuid(self):self.changed(lambda c:c['actors'][UID]['sourceTuple'].update(csuid='3396822186P20151008'))
    def test_changed_actual_pose(self):
        w=self.w.copy();w[0,0,0]=np.nextafter(w[0,0,0],np.inf)
        with self.assertRaises(AssertionError):self.run_case(w=w)
    def test_reversed_original_facet(self):
        w=self.w.copy();w[0]=w[0,[0,2,1]]
        with self.assertRaises(AssertionError):self.run_case(w=w)
    def test_fake_mainbody_as_visual(self):self.changed(lambda c:c['actors'][UID]['completeOriginalTopology']['sharedEdgeConnectedComponents'].__setitem__(93,c['actors'][UID]['completeOriginalTopology']['sharedEdgeConnectedComponents'][4]))
    def test_erased_raw_gap(self):self.changed(lambda c:c['rawTwoResidualRimFailuresRetained']['samples'][1].update(gap=0))
    def test_point_root_claim(self):self.changed(lambda c:c['residualSourceIncidences'][0].update(pointSupportCredit=True))
    def test_source_root_claim(self):self.changed(lambda c:c.update(groundRootsAccepted=True))
    def test_installed_claim(self):self.changed(lambda c:c.update(installationApproved=True))
    def test_relabelled_image(self):
        bad=list(IMAGES);bad[0]=(bad[0][0],'0'*64)
        with self.assertRaises(AssertionError):self.run_case(images=bad)
    def test_missing_terminal_face(self):
        x=copy.deepcopy(self.x);x['complete58TerminalFaceIds'].pop()
        with self.assertRaises(AssertionError):self.run_case(x=x)
    def test_missing_actual_boundaries(self):self.changed(lambda c:c['actors'][UID]['completeBodyBoundaryCensus'][93].update(completeOriginalFaceIds=[]))
if __name__=='__main__':unittest.main()
