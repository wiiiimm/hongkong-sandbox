"""Actual-source binding tests; no full production/current acceptance claim."""
from copy import deepcopy
import json,unittest
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import one_peking_current_bound_installed_foreign_identity_v3_20261010 as adapter
from one_peking_current_installed_foreign_inventory_20261010 import verify_native_rows,installed_inventory
from one_peking_installed_hullett_finite_silhouette_identity_20261010 import OWN,FOREIGN
BASE=ROOT/'docs/astra-city/government-import'
class ActualSourceBindings(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  context=read(BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010/diagnostic.json.gz');cls.context=context
  cls.rows={r['uid']:r for r in context['sources']};cls.row=cls.rows[OWN]['metadata'];cls.forms=[r['building'] for r in context['completeCurrentForms']]
  cls.own=decode_original_world_triangles((ROOT/cls.rows[OWN]['source']['path']).read_bytes());cls.foreign=decode_original_world_triangles((ROOT/cls.rows[FOREIGN]['source']['path']).read_bytes())
  cls.literal=read(BASE/'government-xl-one-peking-hullett-literal-production-geometry-v1-20261010/diagnostic.json.gz');cls.literal['rows']=[r for r in cls.literal['rows'] if r['uid'] in [OWN,FOREIGN]]
  cls.bindings=read(BASE/'government-xl-one-peking-hullett-complete-literal-silhouette-check-v1-20261010/diagnostic.json.gz')['completeGeometryBindings']
  cls.primary=read(BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010/exact-three-source-primary.json')['features']
  cls.native=[dict(sourceKey=cls.row['native']['cacheKey']+'/'+cls.row['modelId'],model=cls.row['native']['model'],resultSHA256=cls.row['native']['resultSha'])]
  cls.entry=cls.rows[FOREIGN]['entry'];cls.catalogue=ROOT/cls.rows[FOREIGN]['catalogue']['path'];cls.catalogue_raw=cls.catalogue.read_bytes()
  cls.manifest=json.dumps({'officialModelCatalogues':[str(cls.catalogue.relative_to(ROOT/'3d-viewer'))]}).encode()
  cls.current_manifest=(BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010/captured-manifest.json').read_bytes()
  cls.loaded=[(r['building'],None,r['tile']) for r in context['completeCurrentForms']]
  cls.hashes={r['tile']:r['tileSHA256'] for r in context['completeCurrentForms']}
  route={}
  for t in json.loads(cls.current_manifest)['tiles']:
   raw=(ROOT/'3d-viewer'/t['url']).read_bytes()
   if any(str(b.get('buildingCSUID') or '')[:10]=='3551217446' for b in json.loads(raw)['buildings']):route[t['url']]=digest(raw)
  cls.capture=dict(manifestSHA256=digest(cls.current_manifest),forms=cls.forms,tileHashes=cls.hashes,exactRouteTileHashes=route,installedInventory=installed_inventory(cls.current_manifest))
 def test_actual_unique_current_source(self):self.assertTrue(verify_native_rows(self.native))
 def test_duplicate_native_source(self):
  with self.assertRaises(AssertionError):verify_native_rows(self.native+self.native)
 def test_missing_native_source(self):
  with self.assertRaises(AssertionError):verify_native_rows([])
 def test_changed_native_original(self):
  rows=deepcopy(self.native);rows[0]['model']['asset']['sha256']='0'*64
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_wrong_native_model_revision(self):
  rows=deepcopy(self.native);rows[0]['model']['modelId']='B355121744602062G0'
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_changed_source_face_count(self):
  rows=deepcopy(self.native);rows[0]['model']['triangles']-=1
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_actual_complete_installed_foreign(self):
  inv=installed_inventory(self.manifest);self.assertEqual(inv['installedForeign']['entry'],self.entry);self.assertEqual(len(inv['completeCatalogueHashes']),1)
 def reader(self,cat):
  raw=json.dumps(cat).encode();return lambda p:raw if p==self.catalogue else p.read_bytes()
 def test_duplicate_installed_entry(self):
  cat=json.loads(self.catalogue_raw);cat['models'].append(deepcopy(next(e for e in cat['models'] if e['uid']==FOREIGN)))
  with self.assertRaises(AssertionError):installed_inventory(self.manifest,self.reader(cat))
 def test_missing_installed_foreign(self):
  cat=json.loads(self.catalogue_raw);cat['models']=[e for e in cat['models'] if e['uid']!=FOREIGN]
  with self.assertRaises(AssertionError):installed_inventory(self.manifest,self.reader(cat))
 def test_duplicate_catalogue_route(self):
  m=json.loads(self.manifest);m['officialModelCatalogues']*=2
  with self.assertRaises(AssertionError):installed_inventory(json.dumps(m).encode())
 def test_catalogue_path_escape(self):
  with self.assertRaises(AssertionError):installed_inventory(json.dumps({'officialModelCatalogues':['../../AGENTS.md']}).encode())
 def test_asset_path_escape(self):
  cat=json.loads(self.catalogue_raw);next(e for e in cat['models'] if e['uid']==FOREIGN)['asset']='../../../../../../../AGENTS.md'
  with self.assertRaises(AssertionError):installed_inventory(self.manifest,self.reader(cat))
 def test_wrong_installed_asset_sha(self):
  cat=json.loads(self.catalogue_raw);next(e for e in cat['models'] if e['uid']==FOREIGN)['sha256']='0'*64
  with self.assertRaises(AssertionError):installed_inventory(self.manifest,self.reader(cat))
 def test_changed_actual_asset_bytes(self):
  path=ROOT/self.rows[FOREIGN]['source']['path']
  with self.assertRaises(AssertionError):installed_inventory(self.manifest,lambda p:p.read_bytes()+b'x' if p==path else p.read_bytes())
 def measurements(self,literal=None,bindings=None):return adapter.literal_measurements(self.own,self.foreign,self.forms,self.primary,literal or self.literal,bindings or self.bindings)
 def test_all_eight_actual_mesh_target_combinations(self):
  rows=self.measurements();self.assertEqual(len(rows),8);self.assertLess(max(r['allForeignEffectiveExcessM2'] for r in rows),1)
 def test_literal_face_omission(self):
  a=deepcopy(self.literal);a['rows'][0]['index']=a['rows'][0]['index'][:-3]
  with self.assertRaises(AssertionError):self.measurements(a)
 def test_literal_vertex_mutation(self):
  a=deepcopy(self.literal);a['rows'][0]['position'][0]+=.001
  with self.assertRaises(AssertionError):self.measurements(a)
 def test_literal_wrong_world_binding(self):
  a=deepcopy(self.bindings);a[FOREIGN]['literal']['worldTrianglesSHA256']='0'*64
  with self.assertRaises(AssertionError):self.measurements(bindings=a)
 def test_literal_missing_foreign(self):
  a=deepcopy(self.literal);a['rows']=a['rows'][:1]
  with self.assertRaises(AssertionError):self.measurements(a)
 def test_literal_duplicate_source(self):
  a=deepcopy(self.literal);a['rows'][1]=deepcopy(a['rows'][0])
  with self.assertRaises(AssertionError):self.measurements(a)
 def current(self,capture=None,loaded=None,read_bytes=None):
  return adapter.current_binding(self.row,dict(neighbourTileHashes=self.hashes),self.own,capture or self.capture,lambda bounds:self.loaded if loaded is None else loaded,read_bytes or (lambda p:self.current_manifest if p==ROOT/'3d-viewer/city/data/manifest.json' else p.read_bytes()))
 def test_actual_complete_current_catalogue_form_route(self):
  forms,sources,inventory=self.current();self.assertEqual(forms,self.forms);self.assertTrue(sources);self.assertEqual(inventory,self.capture['installedInventory'])
 def test_stale_current_manifest(self):
  with self.assertRaises(AssertionError):self.current(read_bytes=lambda p:self.current_manifest+b' ' if p==ROOT/'3d-viewer/city/data/manifest.json' else p.read_bytes())
 def test_missing_current_foreign_actor(self):
  with self.assertRaises(AssertionError):self.current(loaded=[r for r in self.loaded if r[0]['uid']!=FOREIGN])
 def test_changed_current_form(self):
  loaded=deepcopy(self.loaded);loaded[0][0]['rings'][0][0][0]+=.001
  with self.assertRaises(AssertionError):self.current(loaded=loaded)
 def test_incomplete_territory_source_route(self):
  capture=deepcopy(self.capture);capture['exactRouteTileHashes']={}
  with self.assertRaises(AssertionError):self.current(capture=capture)
 def test_catalogue_changed_without_source_change(self):
  def reader(p):
   if p==ROOT/'3d-viewer/city/data/manifest.json':return self.current_manifest
   return p.read_bytes()+b' ' if p==self.catalogue else p.read_bytes()
  with self.assertRaises(AssertionError):self.current(read_bytes=reader)
 def test_actual_plain_primary_request(self):
  base=BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010';raw=(base/'exact-three-source-primary.json').read_bytes();req=read(base/'exact-three-source-primary.request.json')
  self.assertEqual(len(adapter.primary_records(lambda p:req,lambda p:raw)),3)
 def test_changed_primary_bytes(self):
  base=BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010';raw=(base/'exact-three-source-primary.json').read_bytes();req=read(base/'exact-three-source-primary.request.json')
  with self.assertRaises(AssertionError):adapter.primary_records(lambda p:req,lambda p:raw+b' ')
 def test_wrong_primary_query(self):
  base=BASE/'government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010';raw=(base/'exact-three-source-primary.json').read_bytes();req=read(base/'exact-three-source-primary.request.json');req['parameters']['where']='1=1'
  with self.assertRaises(AssertionError):adapter.primary_records(lambda p:req,lambda p:raw)
class ActualRawRouteReplay(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  d=adapter.DOC;cls.row=read(d/'selection.json.gz')['rows'][0];cls.context=read(d/'context.json.gz')['rows'][0];cls.capture=read(d/'current-inputs.json.gz');cls.raw=(ROOT/cls.row['candidate']['path']).read_bytes();cls.tri=decode_original_world_triangles(cls.raw);cls.expected=read(d/'raw-identity.json')
  final=adapter.module('peking_test_actual_routes','xl-final-script-pass.py');cls.forms,cls.sources,_=adapter.current_binding(cls.row,cls.context,cls.tri,cls.capture,final.load_forms)
 def replay(self,expected=None):return adapter.replay_raw(self.row,self.context,self.tri,self.raw,self.forms,self.sources,self.capture,self.expected if expected is None else expected)
 def test_actual_complete_raw_route_fields_inside_exact_wrapper(self):
  proof=self.replay();self.assertEqual(proof,self.expected);self.assertEqual(proof['rawFloatingIdentity']['exactRouteTileHashes'],self.capture['exactRouteTileHashes']);self.assertEqual(proof['rawFloatingIdentity']['exactRouteManifestSHA256'],self.capture['manifestSHA256'])
 def test_missing_nested_route_binding_rejected(self):
  expected=deepcopy(self.expected);expected['rawFloatingIdentity'].pop('exactRouteManifestSHA256')
  with self.assertRaises(AssertionError):self.replay(expected)
 def test_unknown_raw_failure_rejected(self):
  expected=deepcopy(self.expected);expected['reasons'].append('unknown-source-hold')
  with self.assertRaises(AssertionError):self.replay(expected)
if __name__=='__main__':unittest.main()
