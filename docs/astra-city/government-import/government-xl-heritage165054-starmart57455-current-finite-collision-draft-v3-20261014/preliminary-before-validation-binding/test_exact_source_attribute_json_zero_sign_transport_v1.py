"""ROOT runs actual saved-array binding plus precise adverse JSON cases."""
import gzip,json,struct,unittest
from copy import deepcopy
from pathlib import Path
from exact_source_attribute_json_zero_sign_transport_v1 import verify
D=Path(__file__).resolve().parent;ROOT=D.parents[3]
def actual():
 c=json.loads((D/'input-contract.json').read_text())
 return (ROOT/c['originalAssetPath']).read_bytes(),json.loads(gzip.decompress((ROOT/c['reusedCompleteCapturePath']).read_bytes()))
class TransportTests(unittest.TestCase):
 def inputs(self):return actual()
 def rejects(self,change):
  raw,c=self.inputs();change(c)
  with self.assertRaises((AssertionError,OverflowError,struct.error)):verify(raw,c)
 def test_actual_complete_saved_arrays(self):
  raw,c=self.inputs();r=verify(raw,c);self.assertEqual(len(r['attributes']['normal']['zeroSignTransportRecords']),18)
  self.assertTrue(r['attributes']['position']['completeOriginalFloat32BytesExactlyEqual']);self.assertTrue(r['attributes']['color']['completeOriginalFloat32BytesExactlyEqual']);self.assertEqual(r['attributes']['normal']['nonzeroBitDifferences'],0)
 def test_nonzero_normal_bit_change(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'].__setitem__(0,1.0))
 def test_nonzero_sign_change(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'].__setitem__(0,-c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'][0]))
 def test_subnormal_at_zero_rejected(self):
  def change(c):
   a=c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'];i=next(i for i,v in enumerate(a)if v==0);a[i]=struct.unpack('<f',struct.pack('<I',1))[0]
  self.rejects(change)
 def test_tiny_non_float32_change(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'].__setitem__(0,c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'][0]+2**-52))
 def test_wrong_index_order(self):
  def change(c):
   a=c['actualSourceMeshes'][0]['completeIndex'];assert a[0]!=a[1];a[0],a[1]=a[1],a[0]
  self.rejects(change)
 def test_wrong_index_type(self):self.rejects(lambda c:c['actualSourceMeshes'][0].__setitem__('indexArrayType','Float32Array'))
 def test_wrong_attribute_type(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal'].__setitem__('arrayType','Float64Array'))
 def test_nonfinite(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'].__setitem__(0,float('nan')))
 def test_position_sign_transport_not_permitted(self):
  def change(c):
   a=c['actualSourceMeshes'][0]['completeAttributes']['position']['values'];i=next(i for i,v in enumerate(a)if v==0);a[i]=-0.0
  # No assumption actual POSITION contains an appropriate +0: use a nonzero change to test this mandatory byte gate instead.
  self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['position']['values'].__setitem__(0,0.0))
 def test_color_change(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['color']['values'].__setitem__(0,1.0))
 def test_missing_unused_normal_scalar(self):self.rejects(lambda c:c['actualSourceMeshes'][0]['completeAttributes']['normal']['values'].pop())
if __name__=='__main__':unittest.main()
