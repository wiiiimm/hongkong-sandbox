"""Adverse raw GLTF decoder schema tests; synthetic inputs only, no model output."""
import copy,json,tempfile,unittest
from pathlib import Path
import numpy as np
from science_museum_open_sided_original_gltf_identity_comparison_v3_20261011 import decode_original
class Decoder(unittest.TestCase):
 def fixture(self):
  positions=np.array([[0,0,0],[1,0,0],[0,1,0]],dtype='<f4');raw=positions.tobytes()+bytes([0,1,2]);d=dict(asset={'version':'2.0'},scenes=[{'nodes':[0]}],nodes=[{'mesh':0}],meshes=[{'primitives':[{'attributes':{'POSITION':0},'indices':1,'mode':4}]}],buffers=[{'uri':'source.bin','byteLength':len(raw)}],bufferViews=[{'buffer':0,'byteOffset':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':3}],accessors=[{'bufferView':0,'componentType':5126,'count':3,'type':'VEC3'},{'bufferView':1,'componentType':5121,'count':3,'type':'SCALAR'}]);return d,raw,positions
 def run_source(self,d,raw):
  with tempfile.TemporaryDirectory()as folder:
   p=Path(folder)/'source.gltf';p.write_text(json.dumps(d));(p.parent/'source.bin').write_bytes(raw);return decode_original(p)
 def test_unsigned_byte_exact_indices_and_authored_matrix(self):
  d,raw,p=self.fixture();d['nodes'][0]['matrix']=[1,0,0,0,0,1,0,0,0,0,1,0,834500,7,-816500,1];tri,pos,account=self.run_source(d,raw);np.testing.assert_array_equal(tri[0],p.astype(float)+[0,7,0]);self.assertEqual(account['sourcePrimitives'][0]['unreferencedPositionIds'],[])
 def test_duplicate_scene_node_cannot_hide_unvisited_node(self):
  d,raw,_=self.fixture();d['scenes'][0]['nodes']=[0,0];d['nodes'].append({});
  with self.assertRaises(AssertionError):self.run_source(d,raw)
 def test_index_accessor_overrun_rejected(self):
  d,raw,_=self.fixture();d['accessors'][1]['count']=4
  with self.assertRaises(AssertionError):self.run_source(d,raw)
 def test_out_of_range_unsigned_index_rejected(self):
  d,raw,_=self.fixture();raw=raw[:-1]+bytes([3])
  with self.assertRaises(AssertionError):self.run_source(d,raw)
 def test_normalized_index_rejected(self):
  d,raw,_=self.fixture();d['accessors'][1]['normalized']=True
  with self.assertRaises(AssertionError):self.run_source(d,raw)
if __name__=='__main__':unittest.main()
