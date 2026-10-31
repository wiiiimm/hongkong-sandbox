"""Actual paired source/current/provider evidence and binding counterexamples."""
import gzip,json,unittest,numpy as np
from copy import deepcopy
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lei_tung_lower_platform_current_bound_identity_20261010 import DOC,MODELS,UID,PLATFORM,stream_pin,verify_native_rows,verify_receipt,checked_provider,current_binding,module
class BoundActualInputs(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=read(DOC/'selection.json.gz')['rows'];cls.contexts=read(DOC/'context.json.gz')['rows'];cls.capture=read(DOC/'current-inputs.json.gz');cls.native=read(DOC/'source-lookup.json.gz')['rows'];cls.pins=read(DOC/'complete-original-stream-pins.json.gz');cls.raw={r['uid']:(ROOT/r['candidate']['path']).read_bytes() for r in cls.rows};cls.world=np.concatenate([decode_original_world_triangles(cls.raw[r['uid']]) for r in cls.rows]);cls.final=module('lei_tung_complete_adapter_fixtures','xl-final-script-pass.py')
 def reject_binding(self,mutate):
  rows,contexts,capture=deepcopy(self.rows),deepcopy(self.contexts),deepcopy(self.capture);mutate(rows,contexts,capture)
  with self.assertRaises(AssertionError):current_binding(rows,contexts,self.world,capture,self.final.load_forms)
 def reject_native(self,mutate):
  n=deepcopy(self.native);mutate(n)
  with self.assertRaises(AssertionError):verify_native_rows(n)
 def test_actual_both_complete_streams(self):
  for u,(mid,_,count) in MODELS.items():self.assertEqual(stream_pin(self.raw[u],mid,count),self.pins[u])
 def test_wrong_root_rejected(self):
  with self.assertRaises(AssertionError):stream_pin(self.raw[UID],'wrong',874)
 def test_face_omission_rejected(self):
  with self.assertRaises(AssertionError):stream_pin(self.raw[PLATFORM],MODELS[PLATFORM][0],431)
 def test_literal_binary_mutation_changes_pin(self):
  v=bytearray(gzip.decompress(self.raw[PLATFORM]));v[-1]^=1;self.assertNotEqual(stream_pin(gzip.compress(v),MODELS[PLATFORM][0],432),self.pins[PLATFORM])
 def test_actual_pair_current_actor_inventory(self):self.assertEqual(current_binding(self.rows,self.contexts,self.world,self.capture,self.final.load_forms),self.capture['forms'])
 def test_missing_required_original_row(self):self.reject_binding(lambda r,c,p:r.pop())
 def test_missing_required_original_context(self):self.reject_binding(lambda r,c,p:c.pop())
 def test_duplicate_original_row(self):self.reject_binding(lambda r,c,p:r.__setitem__(1,deepcopy(r[0])))
 def test_stale_manifest(self):self.reject_binding(lambda r,c,p:p.__setitem__('manifestSHA256','0'*64))
 def test_missing_actor(self):self.reject_binding(lambda r,c,p:p['forms'].pop())
 def test_missing_context_tile(self):self.reject_binding(lambda r,c,p:c[0]['neighbourTileHashes'].pop(next(iter(c[0]['neighbourTileHashes']))))
 def test_current_tile_changed(self):
  target=ROOT/'3d-viewer'/next(iter(self.capture['tileHashes']))
  with self.assertRaises(AssertionError):current_binding(self.rows,self.contexts,self.world,self.capture,self.final.load_forms,lambda p:p.read_bytes()+b' ' if p==target else p.read_bytes())
 def test_actual_unique_native_versions(self):self.assertTrue(verify_native_rows(self.native))
 def test_duplicate_native_version(self):self.reject_native(lambda n:n.append(deepcopy(n[0])))
 def test_missing_native_version(self):self.reject_native(lambda n:n.pop())
 def test_duplicate_native_model(self):self.reject_native(lambda n:n[1]['model'].__setitem__('modelId',n[0]['model']['modelId']))
 def test_duplicate_native_key(self):self.reject_native(lambda n:n[1].__setitem__('sourceKey',n[0]['sourceKey']))
 def test_other_native_bytes(self):self.reject_native(lambda n:n[0]['model']['asset'].__setitem__('sha256','0'*64))
 def test_actual_exact_provider(self):self.assertEqual(len(checked_provider('exact-current-primary',0,True)),3);self.assertEqual(checked_provider('exact-current-structure-relations',1002,False),[])
 def reject_provider(self,key,value):
  def load(p):
   v=read(p)
   if p.name.endswith('.request.json'):v[key]=value
   return v
  with self.assertRaises(AssertionError):checked_provider('exact-current-primary',0,True,load=load)
 def test_provider_url(self):self.reject_provider('url','https://example.org')
 def test_provider_geometry(self):self.reject_provider('parameters',{'returnGeometry':'false'})
 def test_provider_response(self):self.reject_provider('decodedSHA256','0'*64)
 def test_actual_frozen_refs(self):self.assertTrue(verify_receipt(read(DOC/'result.json')))
 def test_any_frozen_ref_mutation(self):
  receipt=read(DOC/'result.json');target=ROOT/receipt['evidenceRefs'][0]['path']
  with self.assertRaises(AssertionError):verify_receipt(receipt,lambda p:p.read_bytes()+b' ' if p==target else p.read_bytes())
 def test_duplicate_ref(self):
  r=read(DOC/'result.json');r['evidenceRefs'].append(deepcopy(r['evidenceRefs'][0]))
  with self.assertRaises(AssertionError):verify_receipt(r)
 def test_input_cannot_approve_identity(self):
  r=read(DOC/'result.json');r['identityAccepted']=True
  with self.assertRaises(AssertionError):verify_receipt(r)
if __name__=='__main__':unittest.main()
