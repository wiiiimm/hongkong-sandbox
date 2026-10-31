import unittest,copy,gzip,json
from pathlib import Path
import numpy as np
from run import ROOT
from exact_complete_owned_bounds_runtime_ground_binding_20261011 import verify,sha_array,bounds_sha,MODES
class Tests(unittest.TestCase):
 def fixture(self):
  a=np.asarray([[[0,0,0],[1,0,0],[0,0,1]],[[4,0,4],[5,0,4],[4,0,5]],[[1,0,0],[1,1,0],[1,0,1]],[[1,2,0],[1,2,0],[1,2,0]]],dtype='<f8')
  boxes={m:[[0,-10,0],[1,10,1]]for m in MODES};return a,a[[0,2,3]].copy(),boxes
 def check(self,a,b,boxes,**kw):
  return verify(a,b,boxes,regional_sha=kw.get('regional_sha',sha_array(a)),runtime_sha=kw.get('runtime_sha',sha_array(b)),owned_bounds_sha=kw.get('owned_bounds_sha',bounds_sha(boxes)))
 def test_complete_exact_census(self):
  a,b,c=self.fixture();r=self.check(a,b,c);self.assertEqual(r['completeRelevantRegionalFacetIds'],[0,2,3])
 def test_reordered_records(self):
  a,b,c=self.fixture();self.check(a,b[::-1].copy(),c)
 def test_missing_relevant(self):
  a,b,c=self.fixture()
  with self.assertRaises(AssertionError):self.check(a,b[:-1],c)
 def test_missing_vertical(self):
  a,b,c=self.fixture()
  with self.assertRaises(AssertionError):self.check(a,b[[0,2]],c)
 def test_reversed_orientation(self):
  a,b,c=self.fixture();b[0]=b[0,::-1]
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_duplicate_multiplicity(self):
  a,b,c=self.fixture();b=np.concatenate([b,b[:1]])
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_real_duplicate_source_multiplicity(self):
  a,b,c=self.fixture();a=np.concatenate([a,a[:1]]);b=np.concatenate([b,b[:1]]);self.check(a,b,c)
 def test_vertex_one_ulp_changed(self):
  a,b,c=self.fixture();b[0,0,1]=np.nextafter(b[0,0,1],1)
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_irrelevant_extra_rejected(self):
  a,b,c=self.fixture();b=np.concatenate([b,a[1:2]])
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_signed_zero_bytes_not_silently_normalized(self):
  a,b,c=self.fixture();b[0,0,1]=-0.
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_stale_regional_sha(self):
  a,b,c=self.fixture()
  with self.assertRaises(AssertionError):self.check(a,b,c,regional_sha='0'*64)
 def test_stale_runtime_sha(self):
  a,b,c=self.fixture()
  with self.assertRaises(AssertionError):self.check(a,b,c,runtime_sha='0'*64)
 def test_stale_bounds_sha(self):
  a,b,c=self.fixture()
  with self.assertRaises(AssertionError):self.check(a,b,c,owned_bounds_sha='0'*64)
 def test_missing_owned_mode(self):
  a,b,c=self.fixture();del c['providerOriginal']
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_nonfinite_rejected(self):
  a,b,c=self.fixture();a[1,0,1]=np.nan
  with self.assertRaises(AssertionError):self.check(a,b,c)
 def test_bounds_touch_closed_boundary(self):
  a,b,c=self.fixture();c={m:[[1,99,0],[1,99,0]]for m in MODES};self.check(a,b,c)
 def test_actual_complete_1713_and_320(self):
  def read(p):return json.loads(gzip.decompress(p.read_bytes()))
  base=ROOT/'docs/astra-city/government-import';geo=read(base/'government-xl-lippo-tower-only-current-complete-inputs-v5-20261011/complete-current-geometry.json.gz');run=read(ROOT/'source-scripts/city/government-import/local/government-xl-lippo-tower-only-unchanged-current-ordinary-physical-v3-20261011/runtime-geometry.json.gz')['rows'][0]
  d=geo['completeCurrentDrawnTerrain'];a=np.asarray(d['position']).reshape(-1,3)[np.asarray(d['index']).reshape(-1,3)];b=np.asarray(run['drawnGroundGeometry']).reshape(-1,3,3);boxes=read(base/'government-xl-lippo-tower-all-current-native-actual-position-separation-v2-20261011/diagnostic.json.gz')['completeOwnedWorldBounds']
  result=self.check(a,b,boxes);self.assertEqual(result['completeRegionalGroundFacets'],1713);self.assertEqual(result['completeRuntimeGroundFacets'],320)
if __name__=='__main__':unittest.main()
