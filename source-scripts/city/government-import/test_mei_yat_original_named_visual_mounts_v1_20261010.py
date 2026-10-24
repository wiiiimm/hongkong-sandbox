import copy,unittest
import numpy as np
from run import ROOT,HERE,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import mei_yat_original_named_visual_mounts_v1_20261010 as m

class ActualSourceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';phys=base/'government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010'
  row=read(phys/'selection.json.gz')['rows'][0];cls.t=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes())
  r=read(HERE/'local'/phys.name/'runtime-geometry.json.gz')['rows'][0];cls.w=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
  cls.g=read(base/'xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1/diagnostic.json.gz');cls.f=read(base/'xl-terrain-recovery-20261010-mei-yat-complete-paired-column-v1/diagnostic.json.gz')
  cls.p=read(base/'xl-terrain-recovery-20261010-mei-yat-all-named-original-visual-mounts-v1/conditional-provider-roles.json')
  cls.b=dict(completeOriginalWorldSHA256=m.WORLD,completeLiteralWorldSHA256=m.ACTUAL,completeGraphSHA256=m.canonical(cls.g),completeFiniteContextsSHA256=m.canonical(cls.f),providerRolesSHA256=m.canonical(cls.p))
 def invoke(self,t=None,w=None,g=None,f=None,p=None,b=None):
  return m.verify(self.t if t is None else t,self.w if w is None else w,self.g if g is None else g,self.f if f is None else f,self.p if p is None else p,expected_binding=self.b,current_binding=self.b if b is None else b)
 def test_actual10209_all121_mounts_no_structural_credit(self):
  q=self.invoke();self.assertEqual(len(q['namedVisualOnlyComponents']),121);self.assertEqual(len(q['independentlyStructuralComponents']),757);self.assertFalse(q['fullAcceptance']);self.assertTrue(q['visualDetailsSupplyNoStructuralRootsOrBridges'])
 def test_original_geometry_mutation(self):
  t=self.t.copy();t[610,0,0]+=.001
  with self.assertRaises(AssertionError):self.invoke(t=t)
 def test_literal_geometry_mutation(self):
  w=self.w.copy();w[610,0,0]+=.001
  with self.assertRaises(AssertionError):self.invoke(w=w)
 def test_original_clearance_failure_even_ordinary(self):
  f=copy.deepcopy(self.f);f['rows'][0]['allFaces'][9000]['completeOriginalBoundProved']=False
  with self.assertRaises(AssertionError):self.invoke(f=f)
 def test_literal_clearance_failure(self):
  f=copy.deepcopy(self.f);f['rows'][0]['allFaces'][610]['completeActualRenderedBoundProved']=False
  with self.assertRaises(AssertionError):self.invoke(f=f)
 def test_stale_context_binding(self):
  b=dict(self.b);b['completeFiniteContextsSHA256']='0'*64
  with self.assertRaises(AssertionError):self.invoke(b=b)
 def test_missing_provider_component(self):
  p=copy.deepcopy(self.p);p['roles'].pop()
  with self.assertRaises(AssertionError):self.invoke(p=p)
 def test_provider_source_changed(self):
  p=copy.deepcopy(self.p);p['sourceSHA256']='0'*64
  with self.assertRaises(AssertionError):self.invoke(p=p)
 def test_component_face_omitted(self):
  g=copy.deepcopy(self.g);g['components'][722]['globalOriginalFaces'].pop()
  with self.assertRaises(AssertionError):self.invoke(g=g)
 def test_visual_component_illegally_used_as_root(self):
  g=copy.deepcopy(self.g);g['ordinaryGroundRootComponents']=[76]
  with self.assertRaises(AssertionError):self.invoke(g=g)
 def test_visual_component_illegally_used_as_bridge(self):
  g=copy.deepcopy(self.g);g['groundRootedComponentParents']['fixture']=722
  with self.assertRaises(AssertionError):self.invoke(g=g)
 def test_unrelated_host_cannot_mount_actual_complete_boundary(self):
  t=self.t.copy();w=self.w.copy();hosts=sorted(i for k in self.g['resolvedOriginalComponents'] for i in self.g['components'][k]['globalOriginalFaces']);t[hosts]+=np.array([10,0,10]);w[hosts]+=np.array([10,0,10])
  with self.assertRaises(AssertionError):m.complete_boundary_mounts(t,w,self.g['components'][0]['globalOriginalFaces'],hosts,[4,4])
 def test_omitted_actual_whole_front_host_rejects(self):
  from exact_original_facet_orthogonal_finite_facade_band_20261010 import verify
  self.assertFalse(verify(self.t[610],self.t[[9000]])['verifiedWholeOriginalFacetFiniteFacadeBand'])
 def test_missing_ledge_mount_face_rejects(self):
  hosts=sorted(i for k in self.g['resolvedOriginalComponents'] for i in self.g['components'][k]['globalOriginalFaces'])
  with self.assertRaises(AssertionError):m.ledge(self.t,self.w,m.TRIM_PARTS['lowerLedge'][:-1],hosts,expected_original_sha256=m.WORLD,expected_rendered_sha256=m.ACTUAL)

if __name__=='__main__':unittest.main()
