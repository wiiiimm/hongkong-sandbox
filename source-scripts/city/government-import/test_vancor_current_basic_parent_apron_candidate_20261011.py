import copy,unittest
import numpy as np
from vancor_current_basic_parent_apron_candidate_20261011 import propose
from native_parent_child_flat_composition_20261010 import faces
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def patch(y):
 p=[[-2,y,-2],[3,y,-2],[-2,y,3],[3,y,-2],[3,y,3],[-2,y,3]]
 return {'nativeMesh':{'position':np.asarray(p,float).reshape(-1).tolist(),'index':list(range(6))}}
def fixtures():
 basic=np.asarray([[[0,10,0],[1,10,0],[0,10,1]]],float);streams={k:np.asarray([[[10,0,10],[11,0,10],[10,0,11]]],float)for k in MODES}
 return patch(0),patch(1),streams,basic,[[[0,0],[1,0],[0,1],[0,0]]]
class ApronTests(unittest.TestCase):
 def test_candidate_prefix_exact(self):
  a,p,s,b,r=fixtures();old=copy.deepcopy(a);out,q=propose(a,p,s,b,r);self.assertEqual(out['nativeMesh']['position'][:len(a['nativeMesh']['position'])],a['nativeMesh']['position']);self.assertEqual(out['nativeMesh']['index'][:len(a['nativeMesh']['index'])],a['nativeMesh']['index']);self.assertEqual(a,old);self.assertFalse(q['physicalAccepted'])
 def test_core_and_outer_boundaries_are_explicit(self):
  out,q=propose(*fixtures());vertices=[v for rec in q['completeOriginalParentFacetDispositions']for c in rec['completeFiniteClipDispositions']if c['output']for v in c['output']['completePrepackVertices']];self.assertTrue(any(v['blendAlpha']==0 for v in vertices));self.assertTrue(any(v['blendAlpha']==1 for v in vertices));self.assertTrue(all(0<=v['blendAlpha']<=1 for v in vertices))
 def test_all_parent_inventory(self):
  out,q=propose(*fixtures());self.assertEqual([r['originalParentFace']for r in q['completeOriginalParentFacetDispositions']],[0,1]);self.assertFalse(q['exactParentPlanePreservationClaimed'])
 def test_foreign_source_intersection_rejected(self):
  a,p,s,b,r=fixtures();s['actualLiteral']=b
  with self.assertRaises(AssertionError):propose(a,p,s,b,r)
 def test_missing_f32_stream_rejected(self):
  a,p,s,b,r=fixtures();del s['explicitBalancedF32ModelMatrix']
  with self.assertRaises(AssertionError):propose(a,p,s,b,r)
 def test_increased_margin_rejected(self):
  with self.assertRaises(AssertionError):propose(*fixtures(),margin=.02)
 def test_increased_budget_rejected(self):
  with self.assertRaises(AssertionError):propose(*fixtures(),budget=100001)
 def test_nonfinite_parent_rejected(self):
  a,p,s,b,r=fixtures();p['nativeMesh']['position'][1]=float('nan')
  with self.assertRaises(AssertionError):propose(a,p,s,b,r)
 def test_nonfinite_basic_rejected(self):
  a,p,s,b,r=fixtures();b[0,0,1]=float('inf')
  with self.assertRaises(AssertionError):propose(a,p,s,b,r)
 def test_actual_final_budget(self):
  a,p,s,b,r=fixtures();a['nativeMesh']['index']=[0,1,2]*100000
  with self.assertRaises(AssertionError):propose(a,p,s,b,r)
 def test_parent_vertical_record_not_height_credited(self):
  a,p,s,b,r=fixtures();p['nativeMesh']['position'].extend([0,0,0,0,1,0,0,0,1]);p['nativeMesh']['index'].extend([6,7,8]);out,q=propose(a,p,s,b,r);self.assertIn(2,q['allParentNonheightClipFaceIds']);self.assertTrue(q['completeOriginalParentFacetDispositions'][2]['exactZeroProjectedArea'])
 def test_parent_zeroarea_record_preserved_inventory(self):
  a,p,s,b,r=fixtures();p['nativeMesh']['position'].extend([0,0,0]*3);p['nativeMesh']['index'].extend([6,7,8]);out,q=propose(a,p,s,b,r);self.assertTrue(q['completeOriginalParentFacetDispositions'][2]['exactDegenerate3D'])
if __name__=='__main__':unittest.main()
