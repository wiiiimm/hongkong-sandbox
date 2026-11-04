"""Counterexamples against exact immutable terrain evidence; no DB or publication."""
import copy,unittest
from run import ROOT,read,digest
import one_peking_cycle_retained_contract_v1_20261101 as c
class RetentionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.patch=read(ROOT/'docs/astra-city/government-import/government-xl-one-peking-after-twin-cycle-preparation-v2-20261101/summary.json');cls.candidate=read(ROOT/cls.patch['candidate']['path']);cls.parentpath=ROOT/'3d-viewer'/cls.patch['replacedNativeTerrain'][0]['url'];cls.parent=read(cls.parentpath)
 def setUp(self):self.p=copy.deepcopy(self.patch);self.n=copy.deepcopy(self.candidate)
 def verify(self):return c.verify_terrain(self.parent,self.n,self.p,digest(self.parentpath.read_bytes()),self.patch['candidate']['sha256'],self.patch['currentManifestSHA256'])
 def test_exact_current_cycle(self):self.assertTrue(self.verify()['allThreeFiniteEdgesRequired'])
 def test_changed_manifest(self):self.p['currentManifestSHA256']='x'*64;self.assertRaises(AssertionError,self.verify)
 def test_unvalidated_surface(self):self.p['terrainValidatorPassed']=False;self.assertRaises(AssertionError,self.verify)
 def test_missing_retained_target(self):self.p['replacedNativeTerrain'][0]['retainedUids'].pop();self.assertRaises(AssertionError,self.verify)
 def test_lost_cycle_member(self):self.n['patches'].pop();self.assertRaises(AssertionError,self.verify)
 def test_changed_retained_root_grid(self):self.n['elev'][0]+=1;self.assertRaises(AssertionError,self.verify)
 def test_changed_approval_only_child_geometry(self):self.n['patches'][16]['nativeMesh']['position'][1]+=1;self.assertRaises(AssertionError,self.verify)
 def test_unrelated_source_cannot_use_publisher(self):self.assertRaises(AssertionError,c.publisher,'test',self.parentpath,ROOT/self.p['candidate']['path'],{},c.SUPPORTS,self.p)
if __name__=='__main__':unittest.main()
