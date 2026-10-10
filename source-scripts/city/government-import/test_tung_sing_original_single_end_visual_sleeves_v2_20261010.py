import copy,json,unittest,numpy as np
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from tung_sing_original_single_end_visual_sleeves_v2_20261010 import verify_current_visual_roles
class CompleteLiteralActualFixture(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=ROOT/'docs/astra-city/government-import';physical=base/'government-xl-tung-sing-three-original-literal-parent-physical-20261010';s=read(physical/'selection.json.gz');row=next(r for r in s['rows'] if r['uid']=='landsd/53800:0');raw=(ROOT/row['candidate']['path']).read_bytes();cls.a=decode_original_world_triangles(raw);cls.streams=source_stream_binding(raw)
  runtime=next(r for r in read(HERE/'local'/physical.name/'runtime-geometry.json.gz')['rows'] if r['uid']==row['uid']);cls.world=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];cls.ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);cls.graph=read(base/'government-xl-tung-sing-three-original-captured-root-graph-20261010/diagnostic.json.gz')['completeCurrentOriginalGraph']
  canonical=lambda v:digest(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
  cls.binding={'currentManifestSHA256':s['manifestSHA256'],'completeCurrentPhysicalSHA256':digest((physical/'result.json').read_bytes()),'completeCurrentForeignActorScopeSHA256':digest((physical/'neighbour-inputs.json.gz').read_bytes()),'completeProviderRootAndStreamsSHA256':canonical(cls.streams),'completeOriginalWorldSHA256':digest(cls.a.astype('<f8').tobytes()),'completeActualRenderedWorldSHA256':digest(cls.world.astype('<f8').tobytes()),'completeActualDrawnGroundSHA256':digest(cls.ground.astype('<f8').tobytes()),'completeCurrentRootedGraphSHA256':canonical(cls.graph)}
 def altered_graph(self,g):
  b=copy.deepcopy(self.binding);b['completeCurrentRootedGraphSHA256']=digest(json.dumps(g,sort_keys=True,separators=(',',':'),allow_nan=False).encode());return b
 def verify(self,**kw):
  args={'triangles':self.a,'rendered':self.world,'drawn_ground':self.ground,'graph':self.graph,'source_streams':self.streams,'expected_binding':self.binding,'current_binding':self.binding};args.update(kw);return verify_current_visual_roles(**args)
 def test_literal_actual_streams_independently_check_all16_facets_and_mounts(self):
  r=self.verify();self.assertFalse(r['priorExactOriginalRenderedEqualityPassed']);self.assertEqual(len(r['completeIndependentCurrentOriginalFacetClearance']),16);self.assertEqual(len(r['completeActualRenderedVisualMounts']),2);self.assertFalse(r['physicalAccepted']);self.assertFalse(r['installationApproved']);self.assertEqual(r['rawCurrentGraphReasonsVerbatim'],['unresolved-original-component:343','unresolved-original-component:344'])
 def test_rendered_mutation_even_if_caller_supplies_own_hash_rejected(self):
  a=self.world.copy();a[0,0,1]=np.nextafter(a[0,0,1],np.inf);b=copy.deepcopy(self.binding);b['completeActualRenderedWorldSHA256']=digest(a.astype('<f8').tobytes())
  with self.assertRaises(AssertionError):self.verify(rendered=a,expected_binding=b,current_binding=b)
 def test_original_mutation_rejected(self):
  a=self.a.copy();a[0,0,1]=np.nextafter(a[0,0,1],np.inf)
  with self.assertRaises(AssertionError):self.verify(triangles=a)
 def test_provider_normal_mutation_rejected(self):
  s=copy.deepcopy(self.streams);s['normalTriangleStreamSHA256']='0'*64
  with self.assertRaises(AssertionError):self.verify(source_streams=s)
 def test_provider_root_mutation_rejected(self):
  s=copy.deepcopy(self.streams);s['rootMatrix']='changed'
  with self.assertRaises(AssertionError):self.verify(source_streams=s)
 def test_missing_ground_rejected(self):
  with self.assertRaises(AssertionError):self.verify(drawn_ground=self.ground[:0])
 def test_changed_ground_rejected(self):
  g=self.ground.copy();g[0,0,1]+=1
  with self.assertRaises(AssertionError):self.verify(drawn_ground=g)
 def test_nan_rendered_rejected(self):
  a=self.world.copy();a[0,0,1]=np.nan
  with self.assertRaises(AssertionError):self.verify(rendered=a)
 def test_changed_manifest_expected_pin_rejected(self):
  b=copy.deepcopy(self.binding);b['currentManifestSHA256']='0'*64
  with self.assertRaises(AssertionError):self.verify(current_binding=b)
 def test_visual_detail_cannot_be_new_root(self):
  g=copy.deepcopy(self.graph);g['genuineGroundAnchorComponents'].append(343)
  b=self.altered_graph(g)
  with self.assertRaises(AssertionError):self.verify(graph=g,expected_binding=b,current_binding=b)
 def test_visual_detail_cannot_be_new_bridge(self):
  g=copy.deepcopy(self.graph);g['exactOriginalContacts'].append({'components':[343,1]})
  b=self.altered_graph(g)
  with self.assertRaises(AssertionError):self.verify(graph=g,expected_binding=b,current_binding=b)
 def test_missing_whole_component_accounting_rejected(self):
  g=copy.deepcopy(self.graph);g['completeOriginalComponentCount']=386
  b=self.altered_graph(g)
  with self.assertRaises(AssertionError):self.verify(graph=g,expected_binding=b,current_binding=b)
 def test_unrooted_host_rejected(self):
  g=copy.deepcopy(self.graph);g['resolvedOriginalComponents'].remove(1)
  b=self.altered_graph(g)
  with self.assertRaises(AssertionError):self.verify(graph=g,expected_binding=b,current_binding=b)
 def test_caller_cannot_claim_cleared_raw_graph_failure(self):
  g=copy.deepcopy(self.graph);g['reasons']=[]
  b=self.altered_graph(g)
  with self.assertRaises(AssertionError):self.verify(graph=g,expected_binding=b,current_binding=b)
if __name__=='__main__':unittest.main()
