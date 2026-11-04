import copy,hashlib,json,unittest
import numpy as np
from original_ordinary_ground_root_graph_20261009 import verify
class OrdinaryRootGraphTests(unittest.TestCase):
 def fixture(self,tri=None,components=None,ground=None,contacts=None):
  tri=np.asarray(tri if tri is not None else [[[0,0,0],[1,0,0],[0,0,1]]],float)
  ground=np.asarray(ground if ground is not None else [[[0,.45,0],[2,-.45,0],[0,-.45,2]]],float)
  a={'uid':'landsd/1:0','sourceSHA256':'original-source','originalStreamBindingSHA256':'original-stream','globalFaceRange':[0,len(tri)],'completeOriginalFaceCount':len(tri),'originalWorldTrianglesSHA256':hashlib.sha256(tri.tobytes()).hexdigest()}
  c=components or [{'actorUID':a['uid'],'globalOriginalFaces':list(range(len(tri)))}]
  sources=[{'uid':a['uid'],'sourceSHA256':a['sourceSHA256'],'position':tri.reshape(-1).tolist(),'index':list(range(len(tri)*3))}]
  b={'completeOriginalWorldTrianglesSHA256':a['originalWorldTrianglesSHA256'],'currentDrawnGroundSHA256':hashlib.sha256(ground.tobytes()).hexdigest(),'groundInterfacesInputSHA256':'complete-original-input','supportScope':'complete-current-drawn-ground-only','originalIndexedSourcesSHA256':hashlib.sha256(json.dumps(sources,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
  return [tri,[a],c,contacts or [],sources,ground,b]
 def runproof(self,d):return verify(*d[:6],expected_binding=d[6],current_binding=d[6])
 def test_real_ordinary_root_retains_old_strict_failure(self):
  r=self.runproof(self.fixture());self.assertTrue(r['supportInterfaceAccepted']);self.assertEqual(r['ordinaryGroundRootComponents'],[0]);self.assertFalse(r['strictOriginalGraphWithoutNewRoots']['supportInterfaceAccepted']);self.assertFalse(r['wallRoleCredit']);self.assertFalse(r['fullAcceptance'])
 def test_burial_beyond_existing_floor_rejects(self):
  r=self.runproof(self.fixture(ground=[[[0,.51,0],[2,-.49,0],[0,-.49,2]]]));self.assertFalse(r['supportInterfaceAccepted'])
 def test_no_genuine_anchor_rejects(self):
  r=self.runproof(self.fixture(ground=[[[0,.4,0],[2,.4,0],[0,.4,2]]]));self.assertFalse(r['supportInterfaceAccepted'])
 def test_detached_floating_component_rejects(self):
  t=[[[0,0,0],[1,0,0],[0,0,1]],[[0,2,0],[1,2,0],[0,2,1]]];c=[{'actorUID':'landsd/1:0','globalOriginalFaces':[0]},{'actorUID':'landsd/1:0','globalOriginalFaces':[1]}]
  r=self.runproof(self.fixture(t,c));self.assertEqual(r['resolvedOriginalComponents'],[0]);self.assertIn('unresolved-original-component:1',r['reasons'])
 def test_exact_attachment_roots_upper_original_component(self):
  t=[[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[0,2,0],[1,0,0]],[[1,0,0],[0,2,0],[1,2,0]],[[0,2,0],[1,2,0],[0,2,1]]]
  c=[{'actorUID':'landsd/1:0','globalOriginalFaces':[0,1,2]},{'actorUID':'landsd/1:0','globalOriginalFaces':[3]}]
  r=self.runproof(self.fixture(t,c,contacts=[{'components':[0,1],'globalOriginalFaces':[2,3]}]));self.assertTrue(r['supportInterfaceAccepted']);self.assertEqual(r['ordinaryGroundRootComponents'],[0]);self.assertEqual(r['resolvedOriginalComponents'],[0,1])
 def test_fake_contact_rejects(self):
  t=[[[0,0,0],[1,0,0],[0,0,1]],[[0,2,0],[1,2,0],[0,2,1]]];c=[{'actorUID':'landsd/1:0','globalOriginalFaces':[0]},{'actorUID':'landsd/1:0','globalOriginalFaces':[1]}]
  with self.assertRaises(AssertionError):self.runproof(self.fixture(t,c,contacts=[{'components':[0,1],'globalOriginalFaces':[0,1]}]))
 def test_missing_ground_rejects_root(self):
  r=self.runproof(self.fixture(ground=[[[4,0,4],[5,0,4],[4,0,5]]]));self.assertFalse(r['supportInterfaceAccepted'])
 def test_source_index_change_rejects(self):
  d=self.fixture();d[4][0]['index']=[0,2,1];d[6]['originalIndexedSourcesSHA256']=hashlib.sha256(json.dumps(d[4],sort_keys=True,separators=(',',':')).encode()).hexdigest()
  with self.assertRaises(AssertionError):self.runproof(d)
 def test_ground_binding_change_rejects(self):
  d=self.fixture();d[5][0][0][1]+=.01
  with self.assertRaises(AssertionError):self.runproof(d)
 def test_omitted_original_face_rejects(self):
  d=self.fixture();d[2][0]['globalOriginalFaces']=[]
  with self.assertRaises(AssertionError):self.runproof(d)
 def test_detached_faces_in_one_component_reject(self):
  d=self.fixture([[[0,0,0],[1,0,0],[0,0,1]],[[0,2,0],[1,2,0],[0,2,1]]])
  with self.assertRaises(AssertionError):self.runproof(d)
if __name__=='__main__':unittest.main()
