import copy,unittest
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import ko_fung_original_mounted_facade_roles_v3_20261010 as tested
from ko_fung_original_mounted_facade_roles_v3_20261010 import canonical,SOURCES
_ACTUAL=None
def surfaces(tri):
 global _ACTUAL
 if len(tri)==15561:
  if _ACTUAL is None:
   r=read(ROOT/'source-scripts/city/government-import/local/government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010/runtime-geometry.json.gz')['rows']
   _ACTUAL=(np.unique(np.concatenate([np.asarray(x['drawnGroundGeometry']).reshape(-1,9) for x in r]),axis=0).reshape(-1,3,3),np.concatenate([np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)] for x in r]))
  return _ACTUAL
 return np.array([[[-10.,-1.,-10.],[10.,-1.,-10.],[10.,-1.,10.]],[[-10.,-1.,-10.],[10.,-1.,10.],[-10.,-1.,10.]]]),tri
def open_back_role(tri,faces,hosts,ctx):
 ground,world=surfaces(tri);return tested.open_back_role(tri,faces,hosts,ctx,ground,world)
def slanted_triangle_seam_role(tri,faces,hosts,ctx):
 ground,world=surfaces(tri);return tested.slanted_triangle_seam_role(tri,faces,hosts,ctx,ground,world)
def verify(tri,ctx,graph,**kwargs):
 ground,world=surfaces(tri);return tested.verify(tri,ctx,graph,ground,world,**kwargs)

def contexts(tri):return [dict(sourceFace=i,groundProjectionCovered=True,minimum={'minimumGapM':1.}) for i in range(len(tri))]
def box_fixture():
 lo=np.array([0.,0.,-.3]);hi=np.array([1.,1.,0.]);faces=[]
 for axis in range(3):
  others=[a for a in range(3) if a!=axis]
  for side in [0,1]:
   if axis==2 and side==1:continue
   quad=[]
   for bits in [(0,0),(1,0),(1,1),(0,1)]:
    v=lo.copy();v[axis]=hi[axis] if side else lo[axis]
    for a,b in zip(others,bits):v[a]=hi[a] if b else lo[a]
    quad.append(v)
   normal=np.cross(quad[1]-quad[0],quad[2]-quad[0])
   if normal[axis]*(1 if side else -1)<0:quad.reverse()
   faces.extend([[quad[0],quad[1],quad[2]],[quad[0],quad[2],quad[3]]])
 walls=[[[ -1.,-1.,0.],[2.,-1.,0.],[2.,2.,0.]],[[-1.,-1.,0.],[2.,2.,0.],[-1.,2.,0.]]]
 return np.asarray(faces+walls,float),list(range(10)),[10,11]
def seam_fixture():
 a=[0.,2.,0.];b=[1.,2.01,0.];c=[.5,1.,0.]
 return np.array([[a,b,c],[a,[-1.,2.,0.],[0.,3.,1.]],[b,[2.,2.01,0.],[1.,3.,1.]]]),[0],[1,2]

class Synthetic(unittest.TestCase):
 def test_whole_original_opening_passes_without_root_credit(self):
  t,f,h=box_fixture();p=open_back_role(t,f,h,[contexts(t)[i] for i in f]);self.assertFalse(p['structuralRootCredit']);self.assertFalse(p['syntheticBackCapCreated'])
 def test_outside_fixed_band_rejects(self):
  t,f,h=box_fixture();t[h,:,2]=.101
  with self.assertRaises(AssertionError):open_back_role(t,f,h,[contexts(t)[i] for i in f])
 def test_missing_host_facet_leaves_real_edge_gap(self):
  t,f,h=box_fixture()
  with self.assertRaises(AssertionError):open_back_role(t,f,[10],[contexts(t)[i] for i in f])
 def test_reversed_face_rejects(self):
  t,f,h=box_fixture();t[0]=t[0][::-1]
  with self.assertRaises(AssertionError):open_back_role(t,f,h,[contexts(t)[i] for i in f])
 def test_multiple_openings_reject(self):
  t,f,h=box_fixture()
  with self.assertRaises(AssertionError):open_back_role(t,f[2:],h,[contexts(t)[i] for i in f[2:]])
 def test_missing_ground_context_rejects(self):
  t,f,h=box_fixture();cs=[contexts(t)[i] for i in f];cs[0]['groundProjectionCovered']=False
  with self.assertRaises(AssertionError):open_back_role(t,f,h,cs)
 def test_ordinary_burial_rejects(self):
  t,f,h=box_fixture();cs=[contexts(t)[i] for i in f];cs[0]['minimum']['minimumGapM']=-.501
  with self.assertRaises(AssertionError):open_back_role(t,f,h,cs)
 def test_genuine_slanted_edge_two_exact_mounts(self):
  t,f,h=seam_fixture();p=slanted_triangle_seam_role(t,f,h,[contexts(t)[0]]);self.assertEqual({r['corner'] for r in p['exactOriginalTopEdgeMounts']},{0,1});self.assertFalse(p['structuralBridgeCredit'])
 def test_near_endpoint_is_not_exact_attachment(self):
  t,f,h=seam_fixture();t[2,:,2]+=.000000000001
  with self.assertRaises(AssertionError):slanted_triangle_seam_role(t,f,h,[contexts(t)[0]])
 def test_one_mount_rejects(self):
  t,f,h=seam_fixture()
  with self.assertRaises(AssertionError):slanted_triangle_seam_role(t,f,[1],[contexts(t)[0]])
 def test_coplanar_contact_is_not_point_only_seam(self):
  t,f,h=seam_fixture();t[1]=[[-2,0,0],[3,0,0],[.5,5,0]]
  with self.assertRaises(AssertionError):slanted_triangle_seam_role(t,f,h,[contexts(t)[0]])

class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';physical=base/'government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010';rows=read(physical/'selection.json.gz')['rows'];cls.tri=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows]);cls.graph=read(base/'xl-terrain-recovery-20261010-ko-fung-original-current-support-v1/diagnostic.json.gz');cls.ctx=[];cursor=0
  for number in [79097,110480]:
   cs=read(base/f'xl-terrain-recovery-20261010-ko-fung-{number}-complete-context-v1/diagnostic.json.gz')['faces'];cls.ctx.extend({**c,'sourceFace':cursor+i} for i,c in enumerate(cs));cursor+=len(cs)
  wanted=sorted(set(range(len(cls.graph['components'])))-set(cls.graph['resolvedOriginalComponents']));cls.role=dict(contract='ko-fung-complete-original-mounted-facade-role-v3',sources=SOURCES,allVisualComponents=wanted,openBackComponents=[k for k in wanted if k!=598],slantedSeamComponent=598,seamRootedBodyComponent=0)
  ground,world=surfaces(cls.tri)
  cls.binding=dict(completeActualRenderedWorldSHA256=digest(world.tobytes()),completeCurrentDrawnGroundSHA256=digest(ground.tobytes()),completeOriginalWorldTrianglesSHA256=digest(cls.tri.tobytes()),completeContinuousContextsSHA256=canonical(cls.ctx),completeStrictOriginalGraphSHA256=canonical(cls.graph),frozenProviderRoleSHA256=canonical(cls.role),actualProviderRootAndStreamsSHA256='1'*64,completeCurrentPhysicalSHA256='2'*64,completeCurrentForeignScopeSHA256='3'*64,currentManifestSHA256='4'*64)
 def test_actual_four_different_authored_openings(self):
  rooted=set(self.graph['resolvedOriginalComponents'])
  for k in [77,197,271,646]:
   c=self.graph['components'][k];host=[i for j in rooted if self.graph['components'][j]['actorUID']==c['actorUID'] for i in self.graph['components'][j]['globalOriginalFaces']];p=open_back_role(self.tri,c['globalOriginalFaces'],host,[self.ctx[i] for i in c['globalOriginalFaces']]);self.assertGreater(p['actualOutwardFrontProtrusionM'],0)
 def test_actual_single_original_slanted_seam(self):
  p=slanted_triangle_seam_role(self.tri,[13402],self.graph['components'][0]['globalOriginalFaces'],[self.ctx[13402]]);self.assertGreater(len(p['exactOriginalTopEdgeMounts']),1)
 def test_actual_all_119_visual_components_no_structural_credit(self):
  p=verify(self.tri,self.ctx,self.graph,expected_role=self.role,expected_binding=self.binding,current_binding=self.binding);self.assertEqual(len(p['accountedVisualComponents']),119);self.assertEqual(len(p['independentlyStructuralComponents']),547);self.assertFalse(p['visualGroundRootCredit'])
 def test_changed_context_with_same_binding_rejects(self):
  cs=copy.deepcopy(self.ctx);cs[1414]['minimum']['minimumGapM']=-2
  with self.assertRaises(AssertionError):verify(self.tri,cs,self.graph,expected_role=self.role,expected_binding=self.binding,current_binding=self.binding)
 def test_missing_visual_component_rejects(self):
  role=copy.deepcopy(self.role);role['allVisualComponents'].pop();binding={**self.binding,'frozenProviderRoleSHA256':canonical(role)}
  with self.assertRaises(AssertionError):verify(self.tri,self.ctx,self.graph,expected_role=role,expected_binding=binding,current_binding=binding)
 def test_visual_component_cannot_be_structural_bridge(self):
  graph=copy.deepcopy(self.graph);graph['groundRootedComponentParents']['0']=77;binding={**self.binding,'completeStrictOriginalGraphSHA256':canonical(graph)}
  with self.assertRaises(AssertionError):verify(self.tri,self.ctx,graph,expected_role=self.role,expected_binding=binding,current_binding=binding)
 def test_source_substitution_rejects(self):
  role=copy.deepcopy(self.role);role['sources']['landsd/110480:0']='0'*64;binding={**self.binding,'frozenProviderRoleSHA256':canonical(role)}
  with self.assertRaises(AssertionError):verify(self.tri,self.ctx,self.graph,expected_role=role,expected_binding=binding,current_binding=binding)
if __name__=='__main__':unittest.main()
