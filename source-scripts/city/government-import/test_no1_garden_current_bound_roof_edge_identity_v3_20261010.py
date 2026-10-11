"""Actual current/source/provider inputs with adapter counterexamples."""
import gzip,importlib.util,json,unittest
from copy import deepcopy
from run import ROOT,HERE,read,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from no1_garden_current_bound_roof_edge_identity_v3_20261010 import DOC,stream_pin,primary_records,verify_receipt,current_binding,verify_native_rows
ROW=read(DOC/'selection.json.gz')['rows'][0];CTX=read(DOC/'context.json.gz')['rows'][0];CAPTURE=read(DOC/'current-inputs.json.gz');RAW=(ROOT/ROW['candidate']['path']).read_bytes();TRI=decode_original_world_triangles(RAW)
s=importlib.util.spec_from_file_location('tung_sing_adapter_fixture_forms',HERE/'xl-final-script-pass.py');FINAL=importlib.util.module_from_spec(s);s.loader.exec_module(FINAL)
class BoundActualInputs(unittest.TestCase):
 def test_actual_all_streams(self):self.assertEqual(stream_pin(RAW,ROW['modelId'],821),read(DOC/'complete-original-stream-pins.json.gz')['own'])
 def test_original_root_renamed(self):
  with self.assertRaises(AssertionError):stream_pin(RAW,'wrong-model-root',821)
 def test_original_faces_removed(self):
  with self.assertRaises(AssertionError):stream_pin(RAW,ROW['modelId'],820)
 def test_complete_binary_mutation_detected(self):
  raw=bytearray(gzip.decompress(RAW));raw[-1]^=1;changed=stream_pin(gzip.compress(bytes(raw)),ROW['modelId'],821);self.assertNotEqual(changed,read(DOC/'complete-original-stream-pins.json.gz')['own']);self.assertNotEqual(changed['completeBinarySHA256'],read(DOC/'complete-original-stream-pins.json.gz')['own']['completeBinarySHA256'])
 def test_actual_current_complete_inventory(self):self.assertEqual(current_binding(ROW,CTX,TRI,CAPTURE,FINAL.load_forms),CAPTURE['forms'])
 def test_missing_foreign_actor_rejected(self):
  def incomplete(bounds):return FINAL.load_forms(bounds)[:-1]
  with self.assertRaises(AssertionError):current_binding(ROW,CTX,TRI,CAPTURE,incomplete)
 def test_duplicate_actor_rejected(self):
  def duplicated(bounds):
   r=FINAL.load_forms(bounds);return r+[r[0]]
  with self.assertRaises(AssertionError):current_binding(ROW,CTX,TRI,CAPTURE,duplicated)
 def test_missing_tile_binding_rejected(self):
  ctx=deepcopy(CTX);ctx['neighbourTileHashes'].pop(next(iter(ctx['neighbourTileHashes'])))
  with self.assertRaises(AssertionError):current_binding(ROW,ctx,TRI,CAPTURE,FINAL.load_forms)
 def test_manifest_revision_rejected(self):
  cap=deepcopy(CAPTURE);cap['manifestSHA256']='0'*64
  with self.assertRaises(AssertionError):current_binding(ROW,CTX,TRI,cap,FINAL.load_forms)
 def test_tile_revision_rejected(self):
  tile=next(iter(CTX['neighbourTileHashes']));target=ROOT/'3d-viewer'/tile
  with self.assertRaises(AssertionError):current_binding(ROW,CTX,TRI,CAPTURE,FINAL.load_forms,lambda p:p.read_bytes()+b' ' if p==target else p.read_bytes())
 def test_actual_two_exact_provider_queries(self):
  self.assertEqual(len(primary_records()),2)
 def provider_reject(self,key,value):
  def load(p):
   x=read(p)
   if p.name.endswith('.request.json'):x[key]=value
   return x
  with self.assertRaises(AssertionError):primary_records(load=load)
 def test_provider_url_change_rejected(self):self.provider_reject('url','https://example.org/query')
 def test_provider_query_change_rejected(self):self.provider_reject('parameters',{'where':'1=1'})
 def test_provider_decoded_bytes_change_rejected(self):self.provider_reject('decodedSHA256','0'*64)
 def test_provider_original_response_change_rejected(self):self.provider_reject('sha256','0'*64)
 def test_actual_all_frozen_evidence_refs(self):self.assertTrue(verify_receipt(read(DOC/'result.json')))
 def test_any_frozen_dependency_mutation_rejected(self):
  receipt=read(DOC/'result.json');target=ROOT/receipt['evidenceRefs'][0]['path']
  with self.assertRaises(AssertionError):verify_receipt(receipt,lambda p:p.read_bytes()+b' ' if p==target else p.read_bytes())
 def test_duplicate_frozen_ref_rejected(self):
  r=read(DOC/'result.json');r['evidenceRefs'].append(deepcopy(r['evidenceRefs'][0]))
  with self.assertRaises(AssertionError):verify_receipt(r)
 def test_install_credit_rejected_from_input_receipt(self):
  r=read(DOC/'result.json');r['identityAccepted']=True
  with self.assertRaises(AssertionError):verify_receipt(r)
class UniqueNativeVersions(unittest.TestCase):
 def native(self):return read(DOC/'source-lookup.json.gz')['rows']
 def reject(self,mutate):
  x=self.native();mutate(x)
  with self.assertRaises(AssertionError):verify_native_rows(x)
 def test_actual_exact_two_current_source_versions(self):self.assertTrue(verify_native_rows(self.native()))
 def test_duplicate_current_native_version_rejected(self):self.reject(lambda x:x.append(deepcopy(x[0])))
 def test_missing_other_original_rejected(self):self.reject(lambda x:x.pop())
 def test_duplicate_model_id_rejected(self):self.reject(lambda x:x[1]['model'].__setitem__('modelId',x[0]['model']['modelId']))
 def test_duplicate_source_key_rejected(self):self.reject(lambda x:x[1].__setitem__('sourceKey',x[0]['sourceKey']))
 def test_changed_native_byte_version_rejected(self):self.reject(lambda x:x[0]['model']['asset'].__setitem__('sha256','0'*64))
 def test_mismatched_source_key_model_rejected(self):self.reject(lambda x:x[0].__setitem__('sourceKey',x[0]['sourceKey'].rsplit('/',1)[0]+'/wrongModel'))
if __name__=='__main__':unittest.main()
