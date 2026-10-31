"""Byte-bound actual-source/literal/current binding adversarial tests."""
from copy import deepcopy
import json,unittest
import numpy as np
from run import ROOT,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import lippo_current_bound_six_roof_identity_v2_20261010 as adapter
from lippo_three_original_current_inventory_20261010 import EXPECTED,verify_native_rows,catalogue_inventory
from lippo_original_six_roof_current_scope_proposal_v2_20261010 import OWN,FOREIGN,TOWER,source_proof,ROLE_FACES
BASE=ROOT/'docs/astra-city/government-import'
class ActualCurrentBindings(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  d=adapter.DOC;cls.rows={r['uid']:r for r in read(d/'selection.json.gz')['rows']};cls.row=cls.rows[OWN];cls.context=read(d/'context.json.gz')['rows'][0];cls.capture=read(d/'current-inputs.json.gz');cls.forms=cls.capture['forms'];cls.lookup=read(d/'source-lookup.json.gz')['rows']
  cls.raws={u:(ROOT/r['candidate']['path']).read_bytes() for u,r in cls.rows.items()};cls.originals={u:decode_original_world_triangles(raw) for u,raw in cls.raws.items()}
  cls.literal=read(d/'literal-production-geometry.json.gz');cls.bindings=read(d/'literal-complete-geometry-bindings.json.gz');cls.primary=read(d/'exact-current-primary.json')['features']
  cls.fixture=read(BASE/'government-xl-lippo-current-binding-hermetic-fixtures-v2-20261010/manifest-and-catalogue-bytes.json.gz');assert all(digest(v.encode())==cls.fixture['hashes'][k] for k,v in cls.fixture['rawStrings'].items())
  assert {k.removeprefix('3d-viewer/'):h for k,h in cls.fixture['hashes'].items() if k!='3d-viewer/city/data/manifest.json'}==cls.capture['catalogueInventory']['completeCatalogueHashes']
  cls.manifest=cls.fixture['rawStrings']['3d-viewer/city/data/manifest.json'].encode();assert digest(cls.manifest)==cls.capture['manifestSHA256']
  cls.loaded=[(f,None,'city/data/tiles/'+f['tile']+'.json') for f in cls.forms]
 def reader(self,p):
  key=str(p.relative_to(ROOT));return self.fixture['rawStrings'][key].encode() if key in self.fixture['rawStrings'] else p.read_bytes()
 def source(self,forms=None,primary=None):return source_proof(self.raws[OWN],self.raws[FOREIGN],self.forms if forms is None else forms,self.primary if primary is None else primary)
 def literal_check(self,literal=None,bindings=None,forms=None):return adapter.literal_measurements(self.originals,self.forms if forms is None else forms,self.primary,self.literal if literal is None else literal,self.bindings if bindings is None else bindings)
 def current(self,capture=None,loaded=None,reader=None):return adapter.current_binding(self.row,self.context,self.originals[OWN],self.capture if capture is None else capture,lambda bounds:self.loaded if loaded is None else loaded,self.reader if reader is None else reader)
 def test_three_unique_actual_native_sources(self):self.assertTrue(verify_native_rows(self.lookup))
 def test_missing_native_version(self):
  with self.assertRaises(AssertionError):verify_native_rows(self.lookup[:-1])
 def test_duplicate_native_version(self):
  with self.assertRaises(AssertionError):verify_native_rows(self.lookup+[deepcopy(self.lookup[0])])
 def test_same_model_duplicate_source_keys(self):
  rows=deepcopy(self.lookup);rows[1]=deepcopy(rows[0])
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_changed_native_bytes(self):
  rows=deepcopy(self.lookup);rows[0]['model']['asset']['sha256']='0'*64
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_changed_native_count(self):
  rows=deepcopy(self.lookup);rows[0]['model']['triangles']-=1
  with self.assertRaises(AssertionError):verify_native_rows(rows)
 def test_actual_complete_catalogue_census(self):self.assertEqual(catalogue_inventory(self.manifest,self.reader),self.capture['catalogueInventory'])
 def test_duplicate_catalogue_route(self):
  obj=json.loads(self.manifest);obj['officialModelCatalogues'].append(obj['officialModelCatalogues'][0])
  with self.assertRaises(AssertionError):catalogue_inventory(json.dumps(obj).encode(),self.reader)
 def test_catalogue_path_escape(self):
  with self.assertRaises(AssertionError):catalogue_inventory(json.dumps(dict(officialModelCatalogues=['../../AGENTS.md'])).encode(),self.reader)
 def test_unexpected_installed_silvercord(self):
  url=json.loads(self.manifest)['officialModelCatalogues'][0];path=ROOT/'3d-viewer'/url;cat=json.loads(self.reader(path));cat['models'].append(dict(uid=FOREIGN))
  with self.assertRaises(AssertionError):catalogue_inventory(self.manifest,lambda p:json.dumps(cat).encode() if p==path else self.reader(p))
 def test_current_complete_twelve_foreign_scope(self):
  forms,sources,inventory=self.current();self.assertEqual(len(forms),12);self.assertTrue(sources);self.assertEqual(inventory,self.capture['catalogueInventory'])
 def test_missing_additional_ocean_actor(self):
  with self.assertRaises(AssertionError):self.current(loaded=[v for v in self.loaded if v[0]['uid']!='landsd/156599:0'])
 def test_changed_current_foreign_ring(self):
  loaded=deepcopy(self.loaded);loaded[0][0]['rings'][0][0][0]+=.001
  with self.assertRaises(AssertionError):self.current(loaded=loaded)
 def test_stale_manifest(self):
  with self.assertRaises(AssertionError):self.current(reader=lambda p:self.reader(p)+b' ' if p==ROOT/'3d-viewer/city/data/manifest.json' else self.reader(p))
 def test_changed_catalogue_metadata(self):
  path=ROOT/'3d-viewer'/json.loads(self.manifest)['officialModelCatalogues'][0]
  with self.assertRaises(AssertionError):self.current(reader=lambda p:self.reader(p)+b' ' if p==path else self.reader(p))
 def test_missing_georef_route(self):
  c=deepcopy(self.capture);c['exactRouteTileHashes']={}
  with self.assertRaises(AssertionError):self.current(capture=c)
 def test_actual_twelve_scope_source_role_only(self):
  proof=self.source();self.assertTrue(proof['sourceOnlyRoleProposalSupported']);self.assertFalse(proof['identityAccepted']);self.assertFalse(proof['physicalAccepted']);self.assertEqual(len(proof['allCurrentForeignActorsRetained']),12)
 def test_missing_extended_source_actor_rejected(self):
  with self.assertRaises(AssertionError):self.source(forms=[f for f in self.forms if f['uid']!='landsd/239032:0'])
 def test_nonrole_foreign_current_penetration_is_not_exempt(self):
  forms=deepcopy(self.forms);next(f for f in forms if f['uid']=='landsd/208070:0')['rings']=deepcopy(next(f for f in forms if f['uid']==FOREIGN)['rings'])
  with self.assertRaises(AssertionError):self.source(forms=forms)
 def test_all_four_actual_source_literal_roof_associations(self):
  p=self.literal_check();self.assertEqual(len(p['completeAllFourSourceLiteralExactRoleContacts']),4);self.assertEqual(len(p['completeAllFourSpatialMeasurements']),4)
  for v in p['completeAllFourSpatialMeasurements']:self.assertLess(v['effectiveAllForeignExcessM2'],1)
 def test_literal_role_face_omission(self):
  lit=deepcopy(self.literal);lit['rows'][0]['index']=lit['rows'][0]['index'][:-3]
  with self.assertRaises(AssertionError):self.literal_check(literal=lit)
 def test_literal_world_y_mutation(self):
  lit=deepcopy(self.literal);lit['rows'][0]['position'][1]+=.001
  with self.assertRaises(AssertionError):self.literal_check(literal=lit)
 def test_literal_duplicate_source_actor(self):
  lit=deepcopy(self.literal);lit['rows'][1]=deepcopy(lit['rows'][0])
  with self.assertRaises(AssertionError):self.literal_check(literal=lit)
 def test_literal_missing_tower(self):
  lit=deepcopy(self.literal);lit['rows']=[r for r in lit['rows'] if r['uid']!=TOWER]
  with self.assertRaises(AssertionError):self.literal_check(literal=lit)
 def test_changed_original_world_pin(self):
  pins=deepcopy(self.bindings);pins[OWN]['original']['worldTrianglesSHA256']='0'*64
  with self.assertRaises(AssertionError):self.literal_check(bindings=pins)
 def test_changed_literal_world_pin(self):
  pins=deepcopy(self.bindings);pins[FOREIGN]['literal']['worldTrianglesSHA256']='0'*64
  with self.assertRaises(AssertionError):self.literal_check(bindings=pins)
 def primary_reader(self,p):return (adapter.DOC/'exact-current-primary.json').read_bytes()
 def test_exact_primary_actual_request(self):self.assertEqual(len(adapter.primary_records()),3)
 def test_changed_primary_response(self):
  with self.assertRaises(AssertionError):adapter.primary_records(read,lambda p:self.primary_reader(p)+b' ')
 def test_wrong_primary_query(self):
  req=read(adapter.DOC/'exact-current-primary.request.json');req['parameters']['where']='1=1'
  with self.assertRaises(AssertionError):adapter.primary_records(lambda p:req,self.primary_reader)
if __name__=='__main__':unittest.main()
