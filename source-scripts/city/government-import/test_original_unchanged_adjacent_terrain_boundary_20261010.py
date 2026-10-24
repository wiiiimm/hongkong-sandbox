import unittest,numpy as np
from original_unchanged_adjacent_terrain_boundary_20261010 import verify,sha
class SeamTests(unittest.TestCase):
 def setUp(self):
  self.p=np.array([[[0,0,0],[1,1,0],[1,1,1]],[[0,0,0],[1,1,1],[0,0,1]]],float);self.a=self.p+np.array([1,0,0]);self.b=dict(completeOriginalParentTrianglesSHA256=sha(self.p),completeProposalTrianglesSHA256=sha(self.p),completeUnchangedAdjacentTrianglesSHA256=sha(self.a))
 def runproof(self,p=None,q=None,a=None,b=None,adjacent_bounds=None):return verify(self.p if p is None else p,self.p if q is None else q,self.a if a is None else a,parent_bounds=[0,0,1,1],proposal_bounds=[0,0,1,1],adjacent_bounds=[1,0,2,1] if adjacent_bounds is None else adjacent_bounds,expected_binding=self.b if b is None else b,current_binding=self.b if b is None else b)
 def test_exact_affine_seam(self):self.assertFalse(self.runproof()['positiveAreaOverlap'])
 def test_real_area_overlap(self):
  with self.assertRaises(AssertionError):self.runproof(adjacent_bounds=[.9,0,2,1])
 def test_corner_only(self):
  with self.assertRaises(AssertionError):self.runproof(adjacent_bounds=[1,1,2,2])
 def test_changed_seam(self):
  q=self.p.copy();q[0,1,1]=2;b={**self.b,'completeProposalTrianglesSHA256':sha(q)}
  with self.assertRaises(AssertionError):self.runproof(q=q,b=b)
 def test_missing_seam(self):
  q=self.p.copy();q[:,:,0]*=.9;b={**self.b,'completeProposalTrianglesSHA256':sha(q)}
  with self.assertRaises(AssertionError):self.runproof(q=q,b=b)
 def test_unbound_adjacent_change(self):
  a=self.a.copy();a[0,0,1]=3
  with self.assertRaises(AssertionError):self.runproof(a=a)
 def test_face_outside_declared_bounds(self):
  q=self.p.copy();q[0,1,0]=1.1;b={**self.b,'completeProposalTrianglesSHA256':sha(q)}
  with self.assertRaises(AssertionError):self.runproof(q=q,b=b)
 def test_new_intermediate_seam_kink(self):
  q=np.concatenate([self.p,np.array([[[1,1,0],[1,1.5,.5],[1,1,1]]])]);b={**self.b,'completeProposalTrianglesSHA256':sha(q)}
  with self.assertRaises(AssertionError):self.runproof(q=q,b=b)
if __name__=='__main__':unittest.main()
