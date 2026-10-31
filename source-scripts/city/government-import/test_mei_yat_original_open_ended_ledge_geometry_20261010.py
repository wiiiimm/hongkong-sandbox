import hashlib,unittest
import numpy as np
from mei_yat_original_open_ended_ledge_geometry_20261010 import verify
class Tests(unittest.TestCase):
 def setUp(self):
  a,b,c,d=[(0,0),(2,0),(2,1),(0,1)];lo,hi=1.,1.2
  def v(p,y):return [p[0],y,p[1]]
  self.t=np.array([[v(a,hi),v(d,hi),v(b,hi)],[v(b,hi),v(d,hi),v(c,hi)],[v(a,lo),v(b,lo),v(d,lo)],[v(b,lo),v(c,lo),v(d,lo)],[v(a,lo),v(d,lo),v(d,hi)],[v(d,hi),v(a,hi),v(a,lo)],[v(d,lo),v(c,lo),v(c,hi)],[v(c,hi),v(d,hi),v(d,lo)],[[-1,0,-.05],[3,0,-.05],[3,2,-.05]],[[-1,0,-.05],[3,2,-.05],[-1,2,-.05]]],float);self.ids=list(range(8));self.host=[8,9]
 def proof(self):return verify(self.t,self.ids,self.host,expected_world_sha256=hashlib.sha256(self.t.tobytes()).hexdigest())
 def test_complete_open_end(self):
  x=self.proof();self.assertEqual(len(x['completeMountedBackUEdges']),3);self.assertEqual(len(x['actualOriginalFreeEndEdges']),3);self.assertFalse(x['installationApproved']);self.assertFalse(x['visualRoleAccepted'])
 def test_missing_face(self):
  self.ids.pop()
  with self.assertRaises(AssertionError):self.proof()
 def test_reversed_face(self):
  self.t[0]=self.t[0,::-1]
  with self.assertRaises(AssertionError):self.proof()
 def test_detached(self):
  self.t[:8,:,2]+=1
  with self.assertRaises(AssertionError):self.proof()
 def test_partial_host(self):
  self.host=[8]
  with self.assertRaises(AssertionError):self.proof()
 def test_changed_hash(self):
  with self.assertRaises(AssertionError):verify(self.t,self.ids,self.host,expected_world_sha256='0'*64)
 def test_missing_host(self):
  self.host=[]
  with self.assertRaises(AssertionError):self.proof()
 def test_self_host(self):
  self.host=[0,8,9]
  with self.assertRaises(AssertionError):self.proof()
 def test_degenerate_cap(self):
  self.t[0,0]=self.t[0,1]
  with self.assertRaises(AssertionError):self.proof()
 def test_fabricated_cap(self):
  self.ids.append(8)
  with self.assertRaises(AssertionError):self.proof()
 def test_actual_original_721(self):
  from run import ROOT,read
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  row=read(ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-mei-yat-original-physical-v3-20261010/selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),'ca03730a32beed8bd41aea1ef631517746bf20861dc83000364b39040abfcb82');t=decode_original_world_triangles(raw);g=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-mei-yat-complete-original-support-v1/diagnostic.json.gz');hosts=sorted(i for k in g['resolvedOriginalComponents'] for i in g['components'][k]['globalOriginalFaces']);self.assertTrue(verify(t,g['components'][721]['globalOriginalFaces'],hosts,expected_world_sha256=g['binding']['completeOriginalWorldTrianglesSHA256'])['verifiedOriginalLedgeGeometry'])
if __name__=='__main__':unittest.main()
