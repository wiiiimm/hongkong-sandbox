"""Actual captured hospital input mutations; no synthetic building fixtures."""
import copy,json,unittest
from unittest.mock import patch
from run import ROOT,read,digest
import tuen_mun_current_bound_identity_20261010 as adapter
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import/government-xl-tuen-mun-current-full-cell-preflight-20261009'
PAIR=BASE.parent/'government-xl-tuen-mun-special-primary-counterpart-20261009'
class HospitalCurrentBoundInputs(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.row=read(BASE/'selection.json.gz')['rows'][0];cls.ctx=read(BASE/'context.json.gz')['rows'][0];cls.capture=read(BASE/'all-current-forms.json.gz');cls.capture['manifestSHA256']=read(BASE/'selection.json.gz')['manifestSHA256'];cls.tri=decode_original_world_triangles((ROOT/cls.row['candidate']['path']).read_bytes())
 def check_forms(self,capture=None,loaded=None,row=None,raw=None):
  capture=copy.deepcopy(capture or self.capture);byuid={f['uid']:f for f in capture['forms']}
  if loaded is None:
   final=__import__('importlib').util.spec_from_file_location('hospital_test_forms',ROOT/'source-scripts/city/government-import/xl-final-script-pass.py');m=__import__('importlib').util.module_from_spec(final);final.loader.exec_module(m);lo,hi=self.tri.min(axis=(0,1)),self.tri.max(axis=(0,1));loaded=m.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
  return adapter.current_binding(row or self.row,self.ctx,self.tri,capture,lambda bounds:loaded,read_bytes=raw or (lambda p:p.read_bytes()))
 def provider(self,change=None):
  values={adapter.DOC/'exact-current-primary.json':(PAIR/'exact-primary.json').read_bytes(),adapter.DOC/'exact-current-primary.request.json':(PAIR/'exact-primary.request.json').read_bytes()}
  zipped=PAIR/'exact-primary.provider-original.gz'
  if zipped.exists():values[adapter.DOC/'exact-current-primary.provider-original.gz']=zipped.read_bytes()
  if change:change(values)
  return adapter.checked_provider(load=lambda p:json.loads(values[p]),read_bytes=lambda p:values[p])
 def test_actual_complete_current_forms(self):self.assertEqual(self.check_forms(),self.capture['forms'])
 def test_changed_manifest_rejected(self):
  c=copy.deepcopy(self.capture);c['manifestSHA256']='0'*64
  with self.assertRaises(AssertionError):self.check_forms(c)
 def test_changed_current_actor_rejected(self):
  c=copy.deepcopy(self.capture);c['forms'][0]['height']+=1
  with self.assertRaises(AssertionError):self.check_forms(c)
 def test_missing_current_actor_rejected(self):
  c=copy.deepcopy(self.capture);c['forms']=c['forms'][1:]
  with self.assertRaises(AssertionError):self.check_forms(c)
 def test_changed_tile_inventory_rejected(self):
  c=copy.deepcopy(self.capture);c['tileHashes'].pop(next(iter(c['tileHashes'])))
  with self.assertRaises(AssertionError):self.check_forms(c)
 def test_changed_tile_bytes_rejected(self):
  tile=ROOT/'3d-viewer'/next(iter(self.capture['tileHashes']))
  with self.assertRaises(AssertionError):self.check_forms(raw=lambda p:b'changed' if p==tile else p.read_bytes())
 def test_actual_exact_primary_response(self):self.assertEqual(len(self.provider()),2)
 def mutate_request(self,key,value):
  def mutate(values):
   p=adapter.DOC/'exact-current-primary.request.json';d=json.loads(values[p]);d[key]=value;values[p]=json.dumps(d).encode()
  with self.assertRaises(AssertionError):self.provider(mutate)
 def test_changed_provider_url_rejected(self):self.mutate_request('url',adapter.BASE+'/1002/query')
 def test_changed_provider_where_rejected(self):self.mutate_request('parameters',{**adapter.PARAMS,'where':'1=1'})
 def test_changed_decoded_primary_sha_rejected(self):self.mutate_request('decodedSHA256','0'*64)
 def test_changed_primary_bytes_rejected(self):
  def mutate(values):values[adapter.DOC/'exact-current-primary.json']+=b' '
  with self.assertRaises(AssertionError):self.provider(mutate)
 def test_frozen_reference_hash_rejects_change(self):
  receipt=dict(batch=adapter.DOC.name,identityAccepted=False,newlyInstalled=0,evidenceRefs=[dict(path='3d-viewer/city/data/manifest.json',sha256=digest(b'original'))])
  with self.assertRaises(AssertionError):adapter.verify_receipt(receipt,read_bytes=lambda p:b'changed')
 def test_frozen_reference_cannot_escape_workspace(self):
  receipt=dict(batch=adapter.DOC.name,identityAccepted=False,newlyInstalled=0,evidenceRefs=[dict(path='../outside',sha256=digest(b'original'))])
  with self.assertRaises(AssertionError):adapter.verify_receipt(receipt,read_bytes=lambda p:b'original')
 def test_identity_input_cannot_claim_installation(self):
  with self.assertRaises(AssertionError):adapter.verify_receipt(dict(batch=adapter.DOC.name,identityAccepted=False,newlyInstalled=1,evidenceRefs=[]))
if __name__=='__main__':unittest.main()
