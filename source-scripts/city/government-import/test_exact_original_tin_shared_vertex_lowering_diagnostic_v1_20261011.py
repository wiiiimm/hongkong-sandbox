import copy,unittest
import numpy as np
from exact_original_tin_shared_vertex_lowering_diagnostic_v1_20261011 import verify,sha
class WholeTINLoweringTests(unittest.TestCase):
 def setUp(self):
  # Two changed incident triangles meet two untouched neighbours along exact
  # unmodified edges; the central edited point occurs in both authored records.
  self.old=np.array([[[0,1,0],[1,1,0],[0,1,1]],[[0,1,0],[0,1,1],[-1,1,0]],[[1,1,0],[1,1,1],[0,1,1]],[[0,1,1],[-1,1,1],[-1,1,0]]],float);self.new=self.old.copy();self.new[np.all(self.old==[0,1,0],axis=2),1]=.5
 def runproof(self,old=None,new=None,expected=None,current=None,cap=.65):
  old=self.old if old is None else old;new=self.new if new is None else new;binding=dict(completeOriginalGroundSHA256=sha(old),completeDerivedGroundSHA256=sha(new),providerSource='fixed-original-fixture')
  return verify(old,new,expected_binding=binding if expected is None else expected,current_binding=binding if current is None else current,maximum_downward_delta=cap)
 def test_complete_incidence_and_affine_seams(self):
  r=self.runproof();self.assertEqual(r['completeChangedOriginalFaceIDs'],[0,1]);self.assertEqual(r['completeUnchangedExteriorFaceIDs'],[2,3]);self.assertEqual(len(r['completeSourceBoundaryAffineSeams']),2);self.assertEqual(r['completeOriginalVertexCorrections'][0]['allOriginalDuplicateRecords'],2);self.assertFalse(r['fullAcceptance'])
 def test_duplicate_omission_rejects(self):
  bad=self.new.copy();bad[1,0,1]=1
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_duplicate_inconsistent_rejects(self):
  bad=self.new.copy();bad[1,0,1]=.6
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_upward_edit_rejects(self):
  bad=self.old.copy();bad[np.all(self.old==[0,1,0],axis=2),1]=1.01
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_excessive_lowering_rejects(self):
  bad=self.old.copy();bad[np.all(self.old==[0,1,0],axis=2),1]=.3
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_xy_change_rejects(self):
  bad=self.new.copy();bad[2,0,0]+=.001
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_face_order_change_rejects(self):
  with self.assertRaises(AssertionError):self.runproof(new=self.new[[1,0,2,3]])
 def test_missing_face_rejects(self):
  with self.assertRaises(AssertionError):self.runproof(new=self.new[:-1])
 def test_no_change_rejects(self):
  with self.assertRaises(AssertionError):self.runproof(new=self.old)
 def test_bound_tamper_rejects(self):
  with self.assertRaises(AssertionError):self.runproof(current={'completeOriginalGroundSHA256':'0'*64})
 def test_cap_change_rejects(self):
  with self.assertRaises(AssertionError):self.runproof(cap=.7)
 def test_nonfinite_rejects(self):
  bad=self.new.copy();bad[0,0,1]=np.nan
  with self.assertRaises(AssertionError):self.runproof(new=bad)
 def test_original_nonmanifold_not_repaired_or_hidden(self):
  old=np.concatenate([self.old,self.old[:1]]);new=np.concatenate([self.new,self.new[:1]]);r=self.runproof(old,new);self.assertTrue(r['rawOriginalNonmanifoldEdges']);self.assertFalse(r['closedOrManifoldTINClaim'])
if __name__=='__main__':unittest.main()
