import copy,unittest,numpy as np
from retained_original_nonheight_terrain_facets_20261010 import inventory,append_omitted
from run import ROOT,read
from native_parent_child_flat_composition_20261010 import faces
def patch(tri):return {'nativeMesh':{'position':np.asarray(tri,float).reshape(-1).tolist(),'index':list(range(np.asarray(tri).size//3))}}
class LiteralTests(unittest.TestCase):
 def test_actual_complete_man_oi_inventory(self):
  p=read(ROOT/'3d-viewer/city/data/government-native-75697-0.json');r=inventory(p);self.assertEqual(r['completeOriginalParentFaces'],602);self.assertEqual(r['allHeightSamplerExcludedFaceIds'],[536]);self.assertFalse(r['allOriginalFaceRecords'][536]['exactDegenerate3D'])
 def test_actual_literal_face_copy(self):
  p=read(ROOT/'3d-viewer/city/data/government-native-75697-0.json');c=patch([[[0,0,0],[1,0,0],[0,0,1]]]);out,r=append_omitted(c,p,inventory(p)['completeRenderedWorldSHA256']);self.assertTrue(np.array_equal(faces(out)[-1],faces(p)[536]));self.assertEqual(c['nativeMesh']['index'],[0,1,2])
 def test_vertical_nonzero_retained(self):
  p=patch([[[0,0,0],[0,1,0],[0,0,1]]]);out,r=append_omitted(patch([]),p,inventory(p)['completeRenderedWorldSHA256']);self.assertEqual(out['nativeMesh']['position'],p['nativeMesh']['position'])
 def test_tiny_nonzero_projection_record_retained(self):
  p=patch([[[0,0,0],[2**-40,0,0],[0,0,2**-40]]]);r=inventory(p);self.assertFalse(r['allOriginalFaceRecords'][0]['exactZeroProjectedArea']);out,_=append_omitted(patch([]),p,r['completeRenderedWorldSHA256']);self.assertEqual(out['nativeMesh']['position'],p['nativeMesh']['position'])
 def test_true_degenerate_record_retained(self):
  p=patch([[[0,0,0],[1,1,1],[2,2,2]]]);out,r=append_omitted(patch([]),p,inventory(p)['completeRenderedWorldSHA256']);self.assertTrue(r['allOriginalFaceRecords'][0]['exactDegenerate3D']);self.assertEqual(out['nativeMesh']['index'],[0,1,2])
 def test_already_literal_no_duplicate(self):
  p=patch([[[0,0,0],[0,1,0],[0,0,1]]]);out,r=append_omitted(p,p,inventory(p)['completeRenderedWorldSHA256']);self.assertEqual(out,p);self.assertTrue(r['literalRetainedFaceDispositions'][0]['alreadyLiteralInCandidate'])
 def test_changed_parent_world_rejected(self):
  p=patch([[[0,0,0],[0,1,0],[0,0,1]]]);sha=inventory(p)['completeRenderedWorldSHA256'];p['nativeMesh']['position'][1]=2
  with self.assertRaises(AssertionError):append_omitted(patch([]),p,sha)
 def test_budget_increase_rejected(self):
  p=patch([[[0,0,0],[0,1,0],[0,0,1]]])
  with self.assertRaises(AssertionError):append_omitted(p,p,inventory(p)['completeRenderedWorldSHA256'],terrain_budget=100001)
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):inventory(patch([[[0,0,0],[0,float('inf'),0],[0,0,1]]]))
 def test_existing_index_and_positions_unchanged(self):
  c=patch([[[1,1,1],[2,1,1],[1,1,2]]]);p=patch([[[0,0,0],[0,1,0],[0,0,1]]]);out,r=append_omitted(c,p,inventory(p)['completeRenderedWorldSHA256']);self.assertEqual(out['nativeMesh']['position'][:9],c['nativeMesh']['position']);self.assertEqual(out['nativeMesh']['index'][:3],c['nativeMesh']['index'])
if __name__=='__main__':unittest.main()
