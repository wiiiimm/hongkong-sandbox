"""Full cycle counterexamples plus fresh roundoff-cache semantics."""
import copy,unittest
from unittest.mock import patch
import one_peking_nested_cycle_boundary_v3_20261101 as b
import test_one_peking_nested_cycle_boundary_v2_20261101 as previous
class FreshCycleTests(previous.CycleTests):
 def setUp(self):
  scope=patch.object(previous,'b',b);scope.start();self.addCleanup(scope.stop);super().setUp()
class RoundoffTests(unittest.TestCase):
 def node(self,right):
  return dict(w=2,h=2,meta=dict(georef=dict(bE=834500,bN=816500,aE=1,aN=-1)),nativeMesh=dict(position=[0.,5.,0.,right,5.,0.,right,5.,1.,0.,5.,1.],index=[0,1,2,0,2,3],source={}))
 def test_real_float32_sliver_metadata_only(self):
  n=self.node(.9999);old=copy.deepcopy(n['nativeMesh']);p=b.declare_roundoff(n);self.assertGreater(p['measuredAreaM2'],0);self.assertEqual(p['maximumAreaM2'],.25);self.assertEqual(p['maximumRoundoffDistanceM'],.002);self.assertEqual(n['nativeMesh']['position'],old['position']);self.assertEqual(n['nativeMesh']['index'],old['index'])
 def test_cached_proof_cannot_be_mutated_by_caller(self):
  n=self.node(.9999);p=b.declare_roundoff(n);p['maximumAreaM2']=999;n['nativeMesh']['source']['numericalCoverageGap']['maximumAreaM2']=999;self.assertEqual(b.declare_roundoff(n)['maximumAreaM2'],.25)
 def test_new_geometry_cannot_reuse_small_gap_approval(self):
  n=self.node(.9999);b.declare_roundoff(n);n['nativeMesh']['position'][3]=.99;n['nativeMesh']['position'][6]=.99;self.assertRaises(AssertionError,b.declare_roundoff,n)
 def test_exact_surface_needs_no_fallback_declaration(self):
  n=self.node(1.);self.assertIsNone(b.declare_roundoff(n));self.assertNotIn('numericalCoverageGap',n['nativeMesh']['source'])
if __name__=='__main__':unittest.main()
