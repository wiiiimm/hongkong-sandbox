import copy,unittest,numpy as np
from fractions import Fraction as F
from original_bound_facet_wall_context_20261010 import contexts,canonical,sha,down
from exact_original_face_conservative_clearance_v5_20261010 import verify as coarse
from exact_original_paired_finite_clearance_20261010 import verify as paired
class ContextTests(unittest.TestCase):
 def setUp(self):
  self.t=np.array([[[0,-1,0],[1,2,0],[0,2,1]]],float);self.g=np.array([[[-2,0,-2],[4,0,-2],[-2,0,4]]],float)
  c=coarse(self.t[0],self.g);p=paired(self.t[0],self.g);self.rows=[dict(sourceFace=0,priorCoarseBoundProofVerbatim=dict(sourceFace=0,completeOriginal=c),pairedExactOriginalFiniteBound=p,completeOriginalBoundProved=False)]
  self.b=dict(completeOriginalWorldTrianglesSHA256=sha(self.t),completeDrawnGroundSHA256=sha(self.g),completeFiniteFacetProofRowsSHA256=canonical(self.rows))
 def runproof(self,rows=None,t=None,g=None,b=None):return contexts(self.t if t is None else t,self.g if g is None else g,self.rows if rows is None else rows,expected_binding=self.b,current_binding=self.b if b is None else b)
 def test_real_bound_and_exposure(self):
  c=self.runproof()[0];self.assertEqual(c['minimum']['minimumGapM'],-1);self.assertEqual(c['maximumObservedGapM'],2);self.assertFalse(c['rootOrContactCredit'])
 def test_source_changed(self):
  t=self.t.copy();t[0,0,1]=0
  with self.assertRaises(AssertionError):self.runproof(t=t)
 def test_ground_changed(self):
  g=self.g.copy();g[0,0,1]=10
  with self.assertRaises(AssertionError):self.runproof(g=g)
 def test_context_mutation_stale_binding(self):
  r=copy.deepcopy(self.rows);r[0]['pairedExactOriginalFiniteBound']['exactCertifiedLowerClearanceM']='0'
  with self.assertRaises(AssertionError):self.runproof(rows=r)
 def test_missing_projection(self):
  r=copy.deepcopy(self.rows);r[0]['pairedExactOriginalFiniteBound']['groundProjectionCovered']=False;b={**self.b,'completeFiniteFacetProofRowsSHA256':canonical(r)}
  with self.assertRaises(AssertionError):contexts(self.t,self.g,r,expected_binding=b,current_binding=b)
 def test_false_pass_bool(self):
  r=copy.deepcopy(self.rows);r[0]['completeOriginalBoundProved']=True;b={**self.b,'completeFiniteFacetProofRowsSHA256':canonical(r)}
  with self.assertRaises(AssertionError):contexts(self.t,self.g,r,expected_binding=b,current_binding=b)
 def test_omitted_facet(self):
  r=copy.deepcopy(self.rows);r[0]['pairedExactOriginalFiniteBound']['allProjectedBoundingCandidateOriginalGroundFacets']=[];b={**self.b,'completeFiniteFacetProofRowsSHA256':canonical(r)}
  with self.assertRaises(AssertionError):contexts(self.t,self.g,r,expected_binding=b,current_binding=b)
 def test_invented_face_sha(self):
  r=copy.deepcopy(self.rows);r[0]['pairedExactOriginalFiniteBound']['sourceFaceSHA256']='0'*64;b={**self.b,'completeFiniteFacetProofRowsSHA256':canonical(r)}
  with self.assertRaises(AssertionError):contexts(self.t,self.g,r,expected_binding=b,current_binding=b)
 def test_rounding_never_raises_bound(self):
  for q in [F(-1,2)-F(1,10**18),F(1,3),F(-1,3)]:self.assertLessEqual(F.from_float(down(q)),q)
 def test_wrong_binding(self):
  with self.assertRaises(AssertionError):self.runproof(b={**self.b,'other':'changed'})
if __name__=='__main__':unittest.main()
