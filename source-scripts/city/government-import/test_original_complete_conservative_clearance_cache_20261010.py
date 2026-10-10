import copy,unittest,numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_complete_conservative_clearance_cache_20261010 import reuse,canonical
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  b=ROOT/'docs/astra-city/government-import';cls.cached=read(b/'xl-terrain-recovery-20261010-festival-podium-current-finite-clearance-v1/diagnostic.json.gz')['rows'][0];r=next(r for r in read(b/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010/selection.json.gz')['rows'] if r['uid']==cls.cached['uid']);cls.source=r['sourceSHA256'];cls.tri=decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes());g=next(r for r in read(ROOT/'source-scripts/city/government-import/local/government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010/runtime-geometry.json.gz')['rows'] if r['uid']==cls.cached['uid']);cls.world=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];cls.ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);cls.pin=canonical(cls.cached)
 def replay(self,cached=None,tri=None,world=None,ground=None,source=None):return reuse(self.cached if cached is None else cached,self.source if source is None else source,self.tri if tri is None else tri,self.world if world is None else world,self.ground if ground is None else ground,expected_cached_sha=self.pin)
 def test_actual_complete_row_preserves_all1379_failures(self):self.assertEqual(self.replay(),self.cached);self.assertEqual(len(self.cached['unprovedOriginalFaceBounds']),1379)
 def test_changed_current_world_rejects(self):
  w=self.world.copy();w[0,0,0]+=.00001
  with self.assertRaises(AssertionError):self.replay(world=w)
 def test_changed_ground_rejects(self):
  g=self.ground.copy();g[0,0,1]+=.00001
  with self.assertRaises(AssertionError):self.replay(ground=g)
 def test_face_omission_rejects(self):
  with self.assertRaises(AssertionError):self.replay(tri=self.tri[:-1],world=self.world[:-1])
 def test_failure_tampering_rejects(self):
  c=copy.deepcopy(self.cached);c['unprovedOriginalFaceBounds']=[]
  with self.assertRaises(AssertionError):self.replay(cached=c)
 def test_row_order_tampering_rejects(self):
  c=copy.deepcopy(self.cached);c['allFaces'][0],c['allFaces'][1]=c['allFaces'][1],c['allFaces'][0]
  with self.assertRaises(AssertionError):self.replay(cached=c)
 def test_source_substitution_rejects(self):
  with self.assertRaises(AssertionError):self.replay(source='0'*64)
if __name__=='__main__':unittest.main()
