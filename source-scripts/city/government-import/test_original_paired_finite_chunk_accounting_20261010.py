import copy,unittest,numpy as np
from original_paired_finite_chunk_accounting_20261010 import verify_chunk,sha
class ChunkAccounting(unittest.TestCase):
 def setUp(self):
  self.o=np.array([[[0.,1.,0.],[1.,1.,0.],[0.,1.,1.]],[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]]]);self.w=self.o.copy();self.g=self.o.copy();self.binding={'source':'independently-fenced-original','kernel':'byte-pinned'}
  self.cached=[];faces=[]
  for i,t in enumerate(self.o):
   old={'sourceFaceSHA256':sha(t),'completeCurrentGroundSHA256':sha(self.g),'existingOrdinaryClearanceBoundProved':i==0};self.cached.append({'sourceFace':i,'completeOriginal':old,'actualRendered':copy.deepcopy(old)})
   proof={'sourceFaceSHA256':sha(t),'completeCurrentGroundSHA256':sha(self.g),'contract':'exact-original-source-prism-paired-finite-clearance-v1','existingOrdinaryClearanceBoundProved':False,'rawPriorDiagnosticChanged':False,'sourceGeometryChanges':0,'rootOrContactCredit':False,'fullAcceptance':False,'installationApproved':False}
   faces.append(dict(sourceFace=i,priorCoarseBoundProofVerbatim=copy.deepcopy(self.cached[-1]),pairedExactOriginalFiniteBound=None if i==0 else proof,pairedExactActualRenderedFiniteBound=None if i==0 else copy.deepcopy(proof),completeOriginalBoundProved=i==0,completeActualRenderedBoundProved=i==0))
  self.r=dict(binding=self.binding,first=0,endExclusive=2,faces=faces,fullAcceptance=False,installationApproved=False)
 def verify(self):return verify_chunk(self.r,self.binding,self.o,self.w,self.g,self.cached,0,2)
 def reject(self):
  with self.assertRaises(AssertionError):self.verify()
 def test_good_keeps_raw_negative(self):self.assertFalse(self.verify()[1]['completeOriginalBoundProved'])
 def test_changed_binding(self):self.r['binding']={'source':'changed'};self.reject()
 def test_omitted_face(self):self.r['faces'].pop();self.reject()
 def test_reordered_faces(self):self.r['faces'].reverse();self.reject()
 def test_changed_original(self):self.o[1,0,1]+=1;self.reject()
 def test_changed_literal(self):self.w[1,0,1]+=1;self.reject()
 def test_changed_ground(self):self.g[0,0,1]+=1;self.reject()
 def test_changed_coarse(self):self.r['faces'][1]['priorCoarseBoundProofVerbatim']['sourceFace']=44;self.reject()
 def test_falsely_positive(self):self.r['faces'][1]['completeOriginalBoundProved']=True;self.reject()
 def test_structural_credit(self):self.r['faces'][1]['pairedExactOriginalFiniteBound']['rootOrContactCredit']=True;self.reject()
 def test_missing_paired(self):self.r['faces'][1]['pairedExactOriginalFiniteBound']=None;self.reject()
 def test_string_boolean(self):self.r['faces'][1]['completeOriginalBoundProved']='false';self.reject()
if __name__=='__main__':unittest.main()
