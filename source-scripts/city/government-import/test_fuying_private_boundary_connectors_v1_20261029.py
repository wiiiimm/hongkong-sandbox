import unittest,copy,struct
from fuying_private_boundary_connectors_v1_20261029 import add_connectors
class ConnectorTests(unittest.TestCase):
 def fixture(self,x=1):
  x=struct.unpack("f",struct.pack("f",x))[0]
  node=dict(nativeMesh=dict(position=[0,0,0,1,0,0,1,0,1,0,0,1,x,0,.5],index=[0,1,2,0,2,3],source={}))
  row=dict(point=[x,0,.5],hasLocalPlaneWithin1cm=True,hasFiniteMateWithin1cm=True,closestPlaneCandidates=[dict(faceIndex=0,sourcePlaneDeltaY=0,distanceXZ=0)],mateCurves=[dict(axis=0,coordinate=1,expectedMateY=0,pointDeltaM=0)])
  return node,row
 def test_prior_arrays_and_input_immutable(self):
  node,row=self.fixture();before=copy.deepcopy(node);out=add_connectors(node,[row]);self.assertEqual(node,before);self.assertEqual(out['nativeMesh']['position'],before['nativeMesh']['position']);self.assertEqual(out['nativeMesh']['index'][:6],before['nativeMesh']['index']);self.assertEqual(len(out['nativeMesh']['index']),15)
 def test_finite_mate_adds_only_one_vertex(self):
  node,row=self.fixture(.999);out=add_connectors(node,[row]);self.assertEqual(out['nativeMesh']['position'][:15],node['nativeMesh']['position']);self.assertEqual(len(out['nativeMesh']['position']),18);self.assertEqual(out['nativeMesh']['position'][-3:],[1,0,.5])
 def test_missing_plane_nomination(self):
  n,r=self.fixture();r['hasLocalPlaneWithin1cm']=False;self.assertRaises(AssertionError,add_connectors,n,[r])
 def test_plane_limit_not_widened(self):
  n,r=self.fixture();r['closestPlaneCandidates'][0]['sourcePlaneDeltaY']=.02;self.assertRaises(AssertionError,add_connectors,n,[r])
 def test_mate_limit_not_widened(self):
  n,r=self.fixture();r['mateCurves'][0]['pointDeltaM']=.02
  with self.assertRaises((AssertionError,ValueError)):add_connectors(n,[r])
 def test_two_millimetre_band_not_widened(self):
  n,r=self.fixture(.997);self.assertRaises(AssertionError,add_connectors,n,[r])
 def test_point_must_exist_exactly(self):
  n,r=self.fixture();r['point'][1]=.0001;self.assertRaises(AssertionError,add_connectors,n,[r])
if __name__=='__main__':unittest.main()
