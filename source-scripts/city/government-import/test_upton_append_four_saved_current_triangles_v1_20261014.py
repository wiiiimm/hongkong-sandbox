import unittest
from copy import deepcopy
from upton_append_four_saved_current_triangles_v1_20261014 import append_saved_current,digest
class SavedCurrent(unittest.TestCase):
 def setUp(self):
  self.raw=[[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]]];self.pv=[{'old':True}];self.mesh={'position':[v for p in self.raw[0]for v in p]+[10.,11.,12.],'index':[0,1,2]};f=[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]]
  self.records=[{'originalCurrentFace':7,'wholeOriginalCurrentTriplet':f,'wholeOriginalCurrentTripletSHA256':digest(f),'completeCurrentAttribution':{'globalCurrentFace':7,'globalOrderedSavedFaceSHA256':digest(f)}}];self.protected=[{'newCandidate':0,'rawTripletSHA256':digest(self.raw[0])}]
 def call(self):return append_saved_current(self.raw,self.pv,self.mesh,self.records,self.protected)
 def test_whole_byte_prefix_unused_and_original_no_mutation(self):
  prior=deepcopy((self.raw,self.pv,self.mesh,self.records,self.protected));n=self.call();self.assertEqual(prior,(self.raw,self.pv,self.mesh,self.records,self.protected));self.assertEqual(n['newNativeMesh']['index'],[0,1,2,4,5,6]);self.assertEqual(n['candidateRawPositionTriplets'][1],self.records[0]['wholeOriginalCurrentTriplet']);self.assertEqual(n['protectedWholeCurrentTripletsUnchanged'],self.protected)
 def test_no_unpacked_current_snap(self):
  self.records[0]['wholeOriginalCurrentTriplet'][0][0]=1/3;self.records[0]['wholeOriginalCurrentTripletSHA256']=digest(self.records[0]['wholeOriginalCurrentTriplet']);self.records[0]['completeCurrentAttribution']['globalOrderedSavedFaceSHA256']=self.records[0]['wholeOriginalCurrentTripletSHA256']
  with self.assertRaises(AssertionError):self.call()
 def test_wrong_source_sha(self):
  self.records[0]['wholeOriginalCurrentTripletSHA256']='0'*64
  with self.assertRaises(AssertionError):self.call()
 def test_duplicate_current_ancestor(self):
  self.records.append(deepcopy(self.records[0]))
  with self.assertRaises(AssertionError):self.call()
 def test_wrong_current_source_attribution(self):
  self.records[0]['completeCurrentAttribution']['globalCurrentFace']=8
  with self.assertRaises(AssertionError):self.call()
 def test_changed_protected_literal(self):
  self.protected[0]['rawTripletSHA256']='0'*64
  with self.assertRaises(AssertionError):self.call()
if __name__=='__main__':unittest.main()
