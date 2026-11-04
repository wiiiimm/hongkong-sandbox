import copy,unittest,numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from festival_original_mounted_sign_roles_20261010 import verify,canonical
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.graph=read(b/'xl-terrain-recovery-20261010-festival-podium-independent-original-support-v1/diagnostic.json.gz');cls.role=read(b/'xl-terrain-recovery-20261010-festival-original-three-provider-sign-role-v1/provider-role.json.gz');rows=read(b/'government-xl-festival-two-originals-full-physical-20261007/selection.json.gz')['rows'];r=next(r for r in rows if r['uid']=='landsd/91827:0');cls.tri=decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes());runtime=read(ROOT/'source-scripts/city/government-import/local/government-xl-terrain-recovery-festival-podium-original-terrain-current-v1-20261010/runtime-geometry.json.gz')['rows'][0];cls.world=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];cls.ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
 def check(self,tri=None,world=None,ground=None,graph=None,role=None):
  tri=self.tri if tri is None else tri;world=self.world if world is None else world;ground=self.ground if ground is None else ground;graph=self.graph if graph is None else graph;role=self.role if role is None else role;b=dict(completeOriginalWorldSHA256=digest(tri.tobytes()),completeActualRenderedWorldSHA256=digest(world.tobytes()),completeCurrentGroundSHA256=digest(ground.tobytes()),completeStrictGraphSHA256=canonical(graph),frozenProviderRoleSHA256=canonical(role));return verify(tri,world,ground,graph,role,expected_binding=b,current_binding=b)
 def test_complete_actual_three_visual_glyphs_no_roots(self):
  r=self.check();self.assertEqual(r['visualSignComponents'],[46,53,58]);self.assertEqual(len(r['independentlyStructuralComponents']),89);self.assertFalse(r['visualGroundRootCredit']);self.assertFalse(r['upperActorOtherDetailsAccepted']);self.assertFalse(r['installationApproved'])
 def test_source_face_changed_rejects(self):
  t=self.tri.copy();t[5057,0,0]+=.0001
  with self.assertRaises(AssertionError):self.check(tri=t)
 def test_actual_rendered_stream_changed_rejects(self):
  t=self.world.copy();t[5057,0,0]+=.00001
  with self.assertRaises(AssertionError):self.check(world=t)
 def test_partial_role_faces_rejects(self):
  r=copy.deepcopy(self.role);r['completeOriginalSignFaces']['53'].pop()
  with self.assertRaises(AssertionError):self.check(role=r)
 def test_unrelated_source_role_rejects(self):
  r=copy.deepcopy(self.role);r['sourceSHA256']='0'*64
  with self.assertRaises(AssertionError):self.check(role=r)
 def test_visual_structural_parent_rejects(self):
  g=copy.deepcopy(self.graph);g['groundRootedComponentParents']['0']=46
  with self.assertRaises(AssertionError):self.check(graph=g)
 def test_visual_cannot_be_root_rejects(self):
  g=copy.deepcopy(self.graph);g['resolvedOriginalComponents']=sorted(g['resolvedOriginalComponents']+[46]);g['ordinaryGroundRootComponents'].append(46)
  with self.assertRaises(AssertionError):self.check(graph=g)
 def test_unaccounted_body_component_rejects(self):
  g=copy.deepcopy(self.graph);g['resolvedOriginalComponents'].remove(0)
  with self.assertRaises(AssertionError):self.check(graph=g)
 def test_ordinary_burial_rejects(self):
  ground=self.ground.copy();ground[:,:,1]+=50
  with self.assertRaises(AssertionError):self.check(ground=ground)
 def test_missing_finite_ground_rejects(self):
  with self.assertRaises(AssertionError):self.check(ground=self.ground[:1])
 def test_stale_binding_rejects(self):
  b=dict(completeOriginalWorldSHA256=digest(self.tri.tobytes()),completeActualRenderedWorldSHA256=digest(self.world.tobytes()),completeCurrentGroundSHA256=digest(self.ground.tobytes()),completeStrictGraphSHA256=canonical(self.graph),frozenProviderRoleSHA256=canonical(self.role));r=copy.deepcopy(self.role);r['interpretation']='different'
  with self.assertRaises(AssertionError):verify(self.tri,self.world,self.ground,self.graph,r,expected_binding=b,current_binding=b)
if __name__=='__main__':unittest.main()
