"""Actual 35,006-face provider fixture and source-bound negative roles."""
import unittest,copy,numpy as np
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from festival_original_named_visual_mount_roles_v1_20261010 import verify,canonical,WORLD
D=ROOT/'docs/astra-city/government-import'
class ActualFestivalFixture(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.g=read(D/'xl-terrain-recovery-20261010-festival-pair-finite-sampler-current-original-support-v4/diagnostic.json.gz');cls.f=read(D/'xl-terrain-recovery-20261010-festival-pair-current-finite-sampler-paired-column-v3/diagnostic.json.gz');cls.p=read(D/'xl-terrain-recovery-20261010-festival-complete-original-provider-visual-mount-roles-v1/provider-role.json.gz');rows=read(D/'government-xl-terrain-recovery-festival-pair-finite-sampler-current-v4-20261010/selection.json.gz')['rows'];cls.t=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows]);cls.b=cls.binding(cls.g,cls.f,cls.p);cls.result=verify(cls.t,cls.g,cls.f,cls.p,expected_binding=cls.b,current_binding=cls.b)
 @staticmethod
 def binding(g,f,p):return dict(completeOriginalWorldSHA256=WORLD,completeGraphSHA256=canonical(g),completeFiniteContextsSHA256=canonical(f),providerRolesSHA256=canonical(p))
 def reject(self,g=None,f=None,p=None,t=None,stale=False):
  g=self.g if g is None else g;f=self.f if f is None else f;p=self.p if p is None else p;t=self.t if t is None else t;b=self.b if stale else self.binding(g,f,p)
  with self.assertRaises((AssertionError,ValueError)):verify(t,g,f,p,expected_binding=b,current_binding=b)
 def test_actual_complete_named48_mounts(self):
  self.assertEqual(len(self.result['roles']),48);self.assertEqual(self.result['completeOriginalFaces'],35006);self.assertTrue(self.result['allComponentsAccounted']);self.assertFalse(self.result['installationApproved']);self.assertFalse(self.result['groundRootCredit']);self.assertFalse(self.result['structuralBridgeCredit'])
 def test_actual_glyph_outer_back_loop_front_opening_retained(self):
  r=next(r for r in self.result['roles'] if r['component']==219);self.assertEqual(len(r['completeOriginalMountProofs']),45);self.assertTrue(any(any(i[0]==28935 for i in e['incidences']) for e in r['completeOriginalGeometricBoundary']));self.assertFalse(r['syntheticBackOrBottomCap']);self.assertEqual(len(r['completeOriginalFaces']),173)
 def test_actual_trim_lower_edges_are_complete(self):
  r=next(r for r in self.result['roles'] if r['component']==263);self.assertEqual(len(r['completeOriginalMountProofs']),4);self.assertTrue(all(e['originalEdge'][0][1]==e['originalEdge'][1][1]==55.608001708984375 for e in r['completeOriginalMountProofs']))
 def test_original_topology_defects_are_not_solid_certification(self):
  r=next(r for r in self.result['roles'] if r['component']==205);self.assertTrue(r['originalNonmanifoldEdges']);self.assertFalse(r['closedSolidCertified'])
 def test_changed_source_position_rejects(self):
  t=self.t.copy();t[28935,0,1]+=.001;self.reject(t=t)
 def test_nan_source_rejects(self):
  t=self.t.copy();t[0,0,0]=np.nan;self.reject(t=t)
 def test_missing_named_role_rejects(self):
  p=copy.deepcopy(self.p);p['roles'].pop();self.reject(p=p)
 def test_wrong_mount_edge_rejects(self):
  p=copy.deepcopy(self.p);p['roles'][0]['completeOriginalMountEdges'][0][0][0]+=.001;self.reject(p=p)
 def test_partial_glyph_outer_back_opening_rejects(self):
  p=copy.deepcopy(self.p);next(r for r in p['roles'] if r['component']==219)['completeOriginalMountEdges'].pop();self.reject(p=p)
 def test_front_glyph_boundary_cannot_be_relabelled_back_mount(self):
  p=copy.deepcopy(self.p);r=next(r for r in p['roles'] if r['component']==219);r['completeOriginalMountEdges'][0]=r['completeOriginalGeometricBoundary'][-1];self.reject(p=p)
 def test_roof_trim_cannot_use_top_interface(self):
  p=copy.deepcopy(self.p);r=next(r for r in p['roles'] if r['component']==259);r['completeOriginalMountEdges'][0][0][1]=55.766998291015625;self.reject(p=p)
 def test_wrong_named_type_rejects(self):
  p=copy.deepcopy(self.p);p['roles'][0]['kind']='arbitrary-detail';self.reject(p=p)
 def test_visual_ground_root_credit_rejects(self):
  g=copy.deepcopy(self.g);g['resolvedOriginalComponents'].append(219);g['resolvedOriginalComponents'].sort();self.reject(g=g)
 def test_visual_bridge_rejects(self):
  g=copy.deepcopy(self.g);g['groundRootedComponentParents'][str(g['resolvedOriginalComponents'][-1])]=219;self.reject(g=g)
 def test_missing_complete_component_face_rejects(self):
  g=copy.deepcopy(self.g);g['components'][0]['globalOriginalFaces'].pop();self.reject(g=g)
 def test_unknown_source_actor_rejects(self):
  g=copy.deepcopy(self.g);g['actors'][0]['sourceSHA256']='0'*64;self.reject(g=g)
 def test_original_clearance_failure_rejects(self):
  f={**self.f,'rows':list(self.f['rows'])};row={**f['rows'][0],'allFaces':list(f['rows'][0]['allFaces'])};f['rows'][0]=row;row['allFaces'][0]={**row['allFaces'][0],'completeOriginalBoundProved':False};self.reject(f=f)
 def test_rendered_clearance_failure_rejects(self):
  f={**self.f,'rows':list(self.f['rows'])};row={**f['rows'][0],'allFaces':list(f['rows'][0]['allFaces'])};f['rows'][0]=row;row['allFaces'][0]={**row['allFaces'][0],'completeActualRenderedBoundProved':False};self.reject(f=f)
 def test_tampered_context_cannot_retain_binding(self):
  f={**self.f,'fullAcceptance':True};self.reject(f=f,stale=True)
 def test_provider_stream_change_cannot_retain_binding(self):
  p=copy.deepcopy(self.p);p['completeOriginalProviderRootAndStreams']={};self.reject(p=p,stale=True)
if __name__=='__main__':unittest.main()
