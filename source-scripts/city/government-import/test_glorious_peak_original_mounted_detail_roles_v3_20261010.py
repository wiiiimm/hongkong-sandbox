import unittest,copy,hashlib
import numpy as np
from glorious_peak_original_mounted_detail_roles_v2_20261010 import component_role,SPECS,verify,SOURCES,canonical
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from run import ROOT,read
class ActualSource(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';p=base/'government-xl-terrain-recovery-glorious-peak-original-pair-current-physical-v2-20261010';cls.rows=read(p/'selection.json.gz')['rows'];cls.tri=np.concatenate([decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in cls.rows]);cls.graph=read(base/'xl-terrain-recovery-20261010-glorious-peak-wall-grade-source-v1/diagnostic.json.gz');runtime=read(ROOT/'source-scripts/city/government-import/local'/p.name/'runtime-geometry.json.gz')['rows'];cls.world=np.concatenate([np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in runtime]);cls.ground=np.unique(np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,9) for g in runtime]),axis=0).reshape(-1,3,3);cls.ctx=[]
  for r in cls.rows:
   uid=r['uid'].split('/')[1].split(':')[0];d=read(base/('xl-terrain-recovery-20261010-glorious-peak-'+uid+'-complete-context-v1')/'diagnostic.json.gz');offset=len(cls.ctx);cls.ctx.extend({**c,'sourceFace':offset+i} for i,c in enumerate(d['faces']))
  cls.role=dict(contract='glorious-peak-six-complete-original-visual-details-v1',sources=SOURCES)
 def bound(self,ctx=None,graph=None):
  ctx=self.ctx if ctx is None else ctx;graph=self.graph if graph is None else graph
  return dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(self.tri.tobytes()).hexdigest(),completeActualRenderedWorldSHA256=hashlib.sha256(self.world.tobytes()).hexdigest(),completeCurrentDrawnGroundSHA256=hashlib.sha256(self.ground.tobytes()).hexdigest(),completeContinuousContextsSHA256=canonical(ctx),completeRootedOriginalGraphSHA256=canonical(graph),frozenProviderRoleSHA256=canonical(self.role),actualProviderRootAndStreamsSHA256='a'*64,completeCurrentPhysicalSHA256='b'*64,completeCurrentForeignScopeSHA256='c'*64,currentManifestSHA256='d'*64)
 def runverify(self,ctx=None,graph=None,binding=None):
  ctx=self.ctx if ctx is None else ctx;graph=self.graph if graph is None else graph;b=self.bound(ctx,graph) if binding is None else binding
  return verify(self.tri,ctx,graph,self.ground,self.world,expected_role=self.role,expected_binding=b,current_binding=b)
 def test_actual_full_source_components_context_and_clearance(self):
  r=self.runverify();self.assertTrue(r['allComponentsAccounted']);self.assertFalse(r['visualGroundRootCredit']);self.assertFalse(r['visualStructuralBridgeCredit']);self.assertEqual(r['allOriginalFaces'],18944)
 def test_context_mutated_while_binding_retained_rejected(self):
  c=copy.deepcopy(self.ctx);c[5829]['groundProjectionCovered']=False
  with self.assertRaises(AssertionError):self.runverify(ctx=c,binding=self.bound())
 def test_missing_ground_even_with_updated_context_hash_rejected(self):
  c=copy.deepcopy(self.ctx);c[5829]['groundProjectionCovered']=False
  with self.assertRaises(AssertionError):self.runverify(ctx=c)
 def test_genuine_burial_even_with_updated_context_hash_rejected(self):
  c=copy.deepcopy(self.ctx);c[5829]['minimum']['minimumGapM']=-.501
  with self.assertRaises(AssertionError):self.runverify(ctx=c)
 def test_unrelated_host_not_rooted_rejected(self):
  g=copy.deepcopy(self.graph);g['resolvedOriginalComponents'].remove(150)
  with self.assertRaises(AssertionError):self.runverify(graph=g)
 def test_visual_component_may_not_support_another(self):
  g=copy.deepcopy(self.graph);g['groundRootedComponentParents']['150']=152
  with self.assertRaises(AssertionError):self.runverify(graph=g)
 def test_no_grade_root_rejected(self):
  g=copy.deepcopy(self.graph);g['exactExposedWallGradeRootComponents']=[]
  with self.assertRaises(AssertionError):self.runverify(graph=g)
 def test_missing_current_foreign_scope_binding_rejected(self):
  b=self.bound();del b['completeCurrentForeignScopeSHA256']
  with self.assertRaises((AssertionError,KeyError)):self.runverify(binding=b)
 def test_actual_all_six_complete_original_component_roles(self):
  for k,s in SPECS.items():
   with self.subTest(component=k):
    r=component_role(self.tri,s['faces'],self.graph['components'][s['host']]['globalOriginalFaces'],s['role']);self.assertFalse(r['structuralRootCredit']);self.assertFalse(r['structuralBridgeCredit']);self.assertEqual(r['allOriginalFaces'],s['faces']);self.assertTrue(all(v['band']['verifiedCompleteOriginalEdgeContactBand'] for v in r['completeOriginalMounts']))
 def test_actual_unrelated_host_cannot_replace_all_mounts(self):
  for k,s in SPECS.items():
   with self.subTest(component=k),self.assertRaises(AssertionError):component_role(self.tri,s['faces'],self.graph['components'][364 if s['host']!=364 else 87]['globalOriginalFaces'],s['role'])
 def test_actual_hanging_upper_loop_detached_rejected(self):
  s=SPECS[362];changed=self.tri.copy();ids=self.graph['components'][364]['globalOriginalFaces'];changed[ids,:,1]+=2
  with self.assertRaises(AssertionError):component_role(changed,s['faces'],ids,s['role'])
 def test_actual_missing_complete_detail_facet_rejected(self):
  for k,s in SPECS.items():
   with self.subTest(component=k),self.assertRaises(AssertionError):component_role(self.tri,s['faces'][:-1],self.graph['components'][s['host']]['globalOriginalFaces'],s['role'])
class NegativeGeometry(unittest.TestCase):
 def floor_fixture(self):return np.asarray([[[0,0,0],[2,0,0],[2,2,0]],[[0,0,0],[2,2,0],[0,2,0]],[[-1,0,-1],[3,0,-1],[3,0,1]],[[-1,0,-1],[3,0,1],[-1,0,1]]],float)
 def side_fixture(self):return np.asarray([[[0,0,0],[1,0,1],[1,2,1]],[[0,0,0],[1,2,1],[0,2,0]],[[0,-1,-1],[0,3,-1],[0,3,1]],[[0,-1,-1],[0,3,1],[0,-1,1]]],float)
 def test_complete_lower_edge_positive(self):component_role(self.floor_fixture(),[0,1],[2,3],'authored-lower-edge-mounted-visual-panel')
 def test_lower_endpoint_only_not_whole_edge(self):
  t=self.floor_fixture();t[2:,:,0]=np.clip(t[2:,:,0],-1,.5)
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-lower-edge-mounted-visual-panel')
 def test_detached_lower_edge_reject(self):
  t=self.floor_fixture();t[:2,:,1]+=.100001
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-lower-edge-mounted-visual-panel')
 def test_complete_vertical_side_positive(self):component_role(self.side_fixture(),[0,1],[2,3],'authored-side-edge-mounted-visual-panel')
 def test_side_partial_height_cannot_mount(self):
  t=self.side_fixture();t[2:,:,1]=np.clip(t[2:,:,1],-1,1)
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-side-edge-mounted-visual-panel')
 def test_side_point_only_cannot_mount(self):
  t=self.side_fixture();t[2:,:,1]=np.clip(t[2:,:,1],-1,0)
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-side-edge-mounted-visual-panel')
 def test_wrong_role_requires_complete_original_side(self):
  with self.assertRaises(AssertionError):component_role(self.floor_fixture(),[0,1],[2,3],'authored-side-edge-mounted-visual-panel')
 def test_winding_conflict_reject(self):
  t=self.floor_fixture();t[1]=t[1,::-1]
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-lower-edge-mounted-visual-panel')
 def test_zero_area_visual_reject(self):
  t=self.floor_fixture();t[1,2]=t[1,1]
  with self.assertRaises(AssertionError):component_role(t,[0,1],[2,3],'authored-lower-edge-mounted-visual-panel')
 def test_missing_rooted_hosts_reject(self):
  with self.assertRaises(AssertionError):component_role(self.floor_fixture(),[0,1],[],'authored-lower-edge-mounted-visual-panel')
if __name__=='__main__':unittest.main()
