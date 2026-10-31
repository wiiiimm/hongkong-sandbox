import copy,hashlib,unittest
import numpy as np
import shapely
from approved_rendered_terrain_gap_context_v2_20261030 import check
from float32_coverage import approve_roundoff
class ApprovedInputGaps(unittest.TestCase):
 def setUp(self):
  triangles=[]
  for a,b in [(0.,.4998),(.5002,1.)]:triangles.extend([[[a,2.,0.],[b,2.,0.],[a,2.,1.]],[[b,2.,0.],[b,2.,1.],[a,2.,1.]]])
  points=np.asarray(triangles).reshape(-1).tolist();self.node=dict(w=2,h=2,meta=dict(georef=dict(bE=834500,bN=816500,aE=1.,aN=-1.)),nativeMesh=dict(position=points,index=list(range(len(points)//3)),source={}))
  approve_roundoff(self.node,[0,0,1,1]);self.outer=shapely.box(.4,.2,.6,.8);self.proof=dict(sourcePatchSHA256='exact-pin',identicalRenderedPositionBytes=True,identicalRenderedIndices=True,renderedPositionsSHA256=hashlib.sha256(np.asarray(points,dtype='<f4').tobytes()).hexdigest())
 def call(self):return check(self.node,self.outer,self.proof,'exact-pin')
 def test_existing_gap_is_explicit_and_input_unchanged(self):
  before=copy.deepcopy(self.node);r=self.call();self.assertFalse(r['missingSetEmpty']);self.assertFalse(r['legacyStrictCoverageSatisfied']);self.assertLess(r['missingAreaM2'],.001);self.assertEqual(self.node,before)
 def test_no_declaration_rejected(self):
  self.node['nativeMesh']['source'].pop('numericalCoverageGap')
  with self.assertRaises(AssertionError):self.call()
 def test_changed_declared_geometry_rejected(self):
  self.node['nativeMesh']['position'][0]=.01
  with self.assertRaises(AssertionError):self.call()
 def test_changed_policy_bound_rejected(self):
  self.node['nativeMesh']['source']['numericalCoverageGap']['maximumRoundoffDistanceM']=.1
  with self.assertRaises(AssertionError):self.call()
 def test_unbound_rendered_input_rejected(self):
  self.proof['renderedPositionsSHA256']='changed'
  with self.assertRaises(AssertionError):self.call()
 def test_return_outside_extent_rejected(self):
  self.outer=shapely.box(-.0001,.2,.6,.8)
  with self.assertRaises(AssertionError):self.call()
 def test_mismatched_patch_pin_rejected(self):
  self.proof['sourcePatchSHA256']='other'
  with self.assertRaises(AssertionError):self.call()
if __name__=='__main__':unittest.main()
