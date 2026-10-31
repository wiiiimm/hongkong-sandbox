import copy,hashlib,json,unittest
import numpy as np
from original_exposed_wall_grade_root_graph_20261009 import verify,canonical
class ExposedWallGradeRoots(unittest.TestCase):
 def fixture(self):
  tri=np.asarray([[[0,-1,0],[0,1,0],[1,1,0]],[[0,1,0],[0,1,1],[1,1,0]]],float);ground=np.asarray([[[-2,0,-2],[3,0,-2],[3,0,3]],[[-2,0,-2],[3,0,3],[-2,0,3]]],float)
  actor=dict(uid='landsd/1:0',sourceSHA256='actual-original',originalStreamBindingSHA256='actual-stream',globalFaceRange=[0,2],completeOriginalFaceCount=2,originalWorldTrianglesSHA256=hashlib.sha256(tri.tobytes()).hexdigest());components=[dict(actorUID=actor['uid'],globalOriginalFaces=[0,1])];indexed=[dict(uid=actor['uid'],sourceSHA256=actor['sourceSHA256'],position=tri.reshape(-1).tolist(),index=list(range(6)))];contexts=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=m),maximumObservedGapM=1) for i,m in enumerate([-1,1])]
  return [tri,[actor],components,[],indexed,ground,contexts,[],[]]
 def binding(self,d):return dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(d[0].tobytes()).hexdigest(),currentDrawnGroundSHA256=hashlib.sha256(d[5].tobytes()).hexdigest(),groundInterfacesInputSHA256='complete-source-and-current-interface-fixture',supportScope='complete-current-drawn-ground-only',originalIndexedSourcesSHA256=canonical(d[4]),completeCurrentFacetContextsSHA256=canonical(d[6]),exactOriginalContactListSHA256=canonical(d[7]),visualOnlyComponentsSHA256=canonical(d[8]))
 def call(self,d):
  b=self.binding(d);return verify(*d,expected_binding=b,current_binding=b)
 def test_exact_grade_anchor_preserves_raw_bottom_failure(self):
  r=self.call(self.fixture());self.assertTrue(r['supportInterfaceAccepted']);self.assertEqual(r['exactExposedWallGradeRootComponents'],[0]);self.assertEqual(r['ordinaryGroundRootComponents'],[]);self.assertFalse(r['ordinaryRootGraphPreserved']['supportInterfaceAccepted']);self.assertTrue(r['rawOldRootReasons']);self.assertTrue(r['exactCurrentUpperGradeInterfaces']);self.assertFalse(r['fullAcceptance'])
 def test_visual_curb_cannot_root_or_bridge(self):
  d=self.fixture();d[8]=[0];r=self.call(d);self.assertEqual(r['allIndependentGroundRoots'],[]);self.assertEqual(r['exactCurrentUpperGradeInterfaces'],[]);self.assertFalse(r['visualOnlyGroundRootCredit']);self.assertFalse(r['visualOnlyGraphBridgeCredit']);self.assertFalse(r['supportInterfaceAccepted'])
 def test_source_binding_changed_rejects(self):
  d=self.fixture();b=self.binding(d);d[0][0,0,0]-=.1
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_context_binding_changed_rejects(self):
  d=self.fixture();b=self.binding(d);d[6][0]['maximumObservedGapM']=2
  with self.assertRaises(AssertionError):verify(*d,expected_binding=b,current_binding=b)
 def test_ground_omission_rejects(self):
  d=self.fixture();d[5][:,:,[0,2]]+=20;r=self.call(d);self.assertFalse(r['supportInterfaceAccepted']);self.assertEqual(r['exactExposedWallGradeRootComponents'],[])
 def test_higher_ground_never_credits_hidden_lower_plane(self):
  d=self.fixture();high=d[5].copy();high[:,:,1]=2;d[5]=np.concatenate([d[5],high]);r=self.call(d);self.assertFalse(r['supportInterfaceAccepted'])
 def test_no_exposure_rejects_unclassified_burial(self):
  d=self.fixture();d[6][0]['maximumObservedGapM']=-.01
  with self.assertRaisesRegex(AssertionError,'buried wall'):self.call(d)
 def test_no_roof_path_rejects(self):
  d=self.fixture();d[0][1,:,0]+=10;d[1][0]['originalWorldTrianglesSHA256']=hashlib.sha256(d[0].tobytes()).hexdigest();d[4][0]['position']=d[0].reshape(-1).tolist();d[2]=[dict(actorUID='landsd/1:0',globalOriginalFaces=[0]),dict(actorUID='landsd/1:0',globalOriginalFaces=[1])]
  with self.assertRaisesRegex(AssertionError,'roof path'):self.call(d)
 def test_buried_upward_cap_rejects(self):
  d=self.fixture();d[6][1]['minimum']['minimumGapM']=-.5001
  with self.assertRaises(AssertionError):self.call(d)
 def test_no_point_only_foreign_bridge(self):
  d=self.fixture();extra=np.asarray([[[1,1,0],[2,2,0],[2,2,1]]]);d[0]=np.concatenate([d[0],extra]);d[1][0].update(globalFaceRange=[0,3],completeOriginalFaceCount=3,originalWorldTrianglesSHA256=hashlib.sha256(d[0].tobytes()).hexdigest());d[4][0].update(position=d[0].reshape(-1).tolist(),index=list(range(9)));d[2].append(dict(actorUID='landsd/1:0',globalOriginalFaces=[2]));d[6].append(dict(sourceFace=2,groundProjectionCovered=True,minimum=dict(minimumGapM=1),maximumObservedGapM=2));d[3]=[dict(components=[0,1],globalOriginalFaces=[1,2])]
  with self.assertRaises(AssertionError):self.call(d)
 def test_visual_component_cannot_bridge_rooted_body_to_roof(self):
  d=self.fixture();d[0]=np.asarray([[[0,0,0],[1,0,0],[0,0,1]],[[0,0,0],[0,2,0],[1,0,0]],[[1,0,0],[0,2,0],[1,2,0]],[[0,2,0],[0,2,1],[1,2,0]]],float);d[1][0].update(globalFaceRange=[0,4],completeOriginalFaceCount=4,originalWorldTrianglesSHA256=hashlib.sha256(d[0].tobytes()).hexdigest());d[4][0].update(position=d[0].reshape(-1).tolist(),index=list(range(12)));d[2]=[dict(actorUID='landsd/1:0',globalOriginalFaces=ids) for ids in [[0],[1,2],[3]]];d[3]=[dict(components=[0,1],globalOriginalFaces=[0,1]),dict(components=[1,2],globalOriginalFaces=[2,3])];d[6]=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=float(t[:,1].min())),maximumObservedGapM=float(t[:,1].max())) for i,t in enumerate(d[0])];d[8]=[1];r=self.call(d);self.assertEqual(r['resolvedOriginalComponents'],[0]);self.assertEqual(r['unresolvedOriginalComponents'],[2]);self.assertFalse(r['supportInterfaceAccepted'])
 def external_roof_fixture(self,own_roof):
  d=self.fixture();faces=[d[0][0],[[.25,1,0],[.25,1,1],[.75,1,0]]]
  if own_roof:faces.extend([[[0,1,0],[1,1,0],[0,1,1]],[[0,1,1],[1,1,1],[1,1,0]]])
  d[0]=np.asarray(faces,float);n=len(faces);d[1][0].update(globalFaceRange=[0,n],completeOriginalFaceCount=n,originalWorldTrianglesSHA256=hashlib.sha256(d[0].tobytes()).hexdigest());d[4][0].update(position=d[0].reshape(-1).tolist(),index=list(range(n*3)));d[2]=[dict(actorUID='landsd/1:0',globalOriginalFaces=[0,2,3] if own_roof else [0]),dict(actorUID='landsd/1:0',globalOriginalFaces=[1])];d[3]=[dict(components=[0,1],globalOriginalFaces=[0,1])];d[7]=[[0,1]];d[6]=[dict(sourceFace=i,groundProjectionCovered=True,minimum=dict(minimumGapM=float(t[:,1].min())),maximumObservedGapM=float(t[:,1].max())) for i,t in enumerate(d[0])];return d
 def test_external_roof_shortcut_does_not_hide_real_own_roof_path(self):
  r=self.call(self.external_roof_fixture(True));self.assertTrue(r['supportInterfaceAccepted']);self.assertEqual(r['exactOriginalClearRoofPaths']['paths'][0]['originalPath'],[0,1]);self.assertEqual(r['exactCurrentUpperGradeInterfaces'][0]['exactOriginalClearRoofPath']['originalPath'],[0,2,3])
 def test_external_roof_alone_cannot_anchor_component(self):
  r=self.call(self.external_roof_fixture(False));self.assertFalse(r['supportInterfaceAccepted']);self.assertEqual(r['exactExposedWallGradeRootComponents'],[]);self.assertTrue(r['rejectedOtherComponentRoofGradeInterfaces'])
if __name__=='__main__':unittest.main()
