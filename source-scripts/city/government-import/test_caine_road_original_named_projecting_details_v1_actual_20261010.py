"""Real complete source fixture and adverse role/source/context/mount tests."""
import copy,unittest
import numpy as np
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from caine_road_original_named_projecting_details_v1_20261010 import verify,canonical,WORLD,SOURCES,DETAILS
from mei_yat_original_named_visual_mounts_v1_20261010 import topology
from exact_original_perpendicular_edge_facet_band_20261010 import verify as edge_band
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v5-20261010'
GRAPH=BASE/'xl-terrain-recovery-20261010-unnamed-268032-v5-complete-original-support-v1';FINITE=BASE/'xl-terrain-recovery-20261010-unnamed-268032-v5-complete-paired-finite-clearance-v1'
class ActualFixture(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  selected=read(PHYSICAL/'selection.json.gz');cls.t=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in selected['rows']]);cls.w=cls.t.copy();cls.g=read(GRAPH/'diagnostic.json.gz');cls.f=read(FINITE/'diagnostic.json.gz');cls.roles=dict(contract='caine-road-pinned-open-back-cantilever-and-one-end-slanted-strip-visual-only-v1',sourceSHA256s=SOURCES,completeOriginalWorldSHA256=WORLD,roles=[dict(component=70,kind='original-ten-face-open-back-cantilever',completeOriginalFaces=DETAILS[70]),dict(component=202,kind='original-two-face-one-end-mounted-slanted-strip',completeOriginalFaces=DETAILS[202])]);cls.binding=cls.bind(cls.g,cls.f,cls.roles);cls.hosts=sorted(i for k in cls.g['resolvedOriginalComponents'] for i in cls.g['components'][k]['globalOriginalFaces'])
 @staticmethod
 def bind(g,f,roles):return dict(completeOriginalWorldSHA256=WORLD,completeLiteralWorldSHA256=WORLD,completeGraphSHA256=canonical(g),completeFiniteContextsSHA256=canonical(f),providerRolesSHA256=canonical(roles))
 def call(self,t=None,w=None,g=None,f=None,roles=None,binding=None):return verify(self.t if t is None else t,self.w if w is None else w,self.g if g is None else g,self.f if f is None else f,self.roles if roles is None else roles,expected_binding=self.binding if binding is None else binding,current_binding=self.binding if binding is None else binding)
 def rejects(self,**kw):
  with self.assertRaises(AssertionError):self.call(**kw)
 def test_complete_real_source_passes(self):
  r=self.call();self.assertEqual(r['namedVisualOnlyComponents'],[70,202]);self.assertTrue(r['allComponentsAccounted']);self.assertFalse(r['fullAcceptance']);self.assertTrue(r['visualDetailsSupplyNoStructuralRootsOrBridges'])
 def test_changed_original_pose_rejects(self):
  t=self.t.copy();t[7983,0,0]+=.01;self.rejects(t=t)
 def test_changed_literal_pose_rejects(self):
  w=self.w.copy();w[10943,0,1]+=.01;self.rejects(w=w)
 def test_removed_original_face_rejects(self):self.rejects(t=np.delete(self.t,7983,axis=0))
 def test_reversed_original_face_rejects(self):
  t=self.t.copy();t[7983]=t[7983,::-1];self.rejects(t=t)
 def test_removed_component_face_rejects(self):
  g=copy.deepcopy(self.g);g['components'][70]['globalOriginalFaces'].pop();self.rejects(g=g,binding=self.bind(g,self.f,self.roles))
 def test_wrong_actor_source_rejects(self):
  g=copy.deepcopy(self.g);g['actors'][1]['sourceSHA256']='0'*64;self.rejects(g=g,binding=self.bind(g,self.f,self.roles))
 def test_missing_body_root_rejects(self):
  g=copy.deepcopy(self.g);g['resolvedOriginalComponents'].remove(0);self.rejects(g=g,binding=self.bind(g,self.f,self.roles))
 def test_visual_component_as_root_rejects(self):
  g=copy.deepcopy(self.g);g['resolvedOriginalComponents']=sorted(g['resolvedOriginalComponents']+[70]);self.rejects(g=g,binding=self.bind(g,self.f,self.roles))
 def test_visual_bridge_rejects(self):
  g=copy.deepcopy(self.g);g['groundRootedComponentParents']['1']=202;self.rejects(g=g,binding=self.bind(g,self.f,self.roles))
 def test_changed_provider_role_rejects(self):
  r=copy.deepcopy(self.roles);r['roles'][1]['kind']='closed-support-solid';self.rejects(roles=r,binding=self.bind(self.g,self.f,r))
 def test_unproved_original_clearance_rejects(self):
  f=copy.deepcopy(self.f);f['rows'][1]['allFaces'][100]['completeOriginalBoundProved']=False;self.rejects(f=f,binding=self.bind(self.g,f,self.roles))
 def test_unproved_literal_clearance_rejects(self):
  f=copy.deepcopy(self.f);f['rows'][1]['allFaces'][100]['completeActualRenderedBoundProved']=False;self.rejects(f=f,binding=self.bind(self.g,f,self.roles))
 def test_stale_current_ground_context_rejects(self):
  f=copy.deepcopy(self.f);f['rows'][0]['completeGroundSHA256']='0'*64;self.rejects(f=f)
 def test_stale_mount_graph_rejects(self):
  g=copy.deepcopy(self.g);g['ordinaryGroundRootComponents']=[4];self.rejects(g=g)
 def test_authored_free_edges_and_negative_whole_mount_remain(self):
  r=self.call();q=r['completeOriginalAndLiteralVisualMounts'][1]['mountGeometry'];self.assertTrue(q['everyFreeOriginalEdgeRetained']);self.assertTrue(q['rawWholeFacetAndWholeBoundaryMountFailuresPreserved']);p=q['wholeOriginalAndLiteralMountedEndAndSeparateCorner'];self.assertTrue(p[0]['originalMount']['verifiedCompleteOriginalEdgePerpendicularBand']);self.assertFalse(p[1]['originalMount']['verifiedCompleteOriginalEdgePerpendicularBand']);self.assertIn(['0','0'],p[1]['originalMount']['exactCertifiedMergedIntervals'])
 def test_actual_back_host_detachment_rejects_band(self):
  _,boundary,_,_=topology(self.t,DETAILS[70]);i,a,b=boundary[0];host=self.t[self.hosts].copy();host[:,:,0]+=1;self.assertFalse(edge_band(np.array([a,b]),host)['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_actual_partial_end_host_omission_rejects_band(self):
  _,boundary,_,_=topology(self.t,DETAILS[202]);end=next(e for e in boundary if e[1][2]==e[2][2]==729.5068359375);i,a,b=end;host=self.t[self.hosts];proof=edge_band(np.array([a,b]),host);positive={r['originalSurfaceFace'] for r in proof['allFiniteOriginalFacetIntervals'] if r['entireIntervalWithinFixedBand']};self.assertTrue(positive);kept=[j for j in range(len(host)) if j not in positive];self.assertFalse(edge_band(np.array([a,b]),host[kept])['verifiedCompleteOriginalEdgePerpendicularBand'])
if __name__=='__main__':unittest.main()
