import unittest
import numpy as np
from exact_local_floor_representation_v1_20261102 import recover

def context(vegetation=None):
 return dict(w=2,h=2,vegetation=vegetation or [0,0,0,0],meta=dict(georef=dict(bE=834500,aE=2,bN=816500,aN=-2)),nativeMesh={})
def split(t):
 a,b,c=np.asarray(t,float);ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
 return np.asarray([[a,ab,ca],[ab,b,bc],[ca,bc,c],[ab,bc,ca]])
class ExactLocalRepresentation(unittest.TestCase):
 def setUp(self):
  self.parent=np.asarray([[[0,10,0],[0,10,4],[4,10,0]],[[8,7,0],[8,7,4],[12,7,0]]],float)
 def test_reduces_changed_fragments_keeps_untouched_literal(self):
  f=np.concatenate([split(self.parent[0]),self.parent[1:]]);l=[dict(parentFace=0,kind='ramp-plane-core',fieldFace=i%2)for i in range(4)]+[dict(parentFace=1,kind='unchanged')]
  out,rows,p=recover(f,l,self.parent,context());self.assertLess(len(out),len(f));self.assertTrue(np.array_equal(out[0],self.parent[1]));self.assertEqual(p['unchangedParentFaceIds'],[1]);self.assertTrue(p['productionFloat32SurfacesNormalsAndColoursPreserved'])
 def test_never_merges_across_original_parents(self):
  f=np.concatenate([split(t)for t in self.parent]);l=[dict(parentFace=i//4,kind='parent-fragment')for i in range(8)]
  out,rows,p=recover(f,l,self.parent,context());self.assertEqual({r['parentFace']for r in rows},{0,1});self.assertEqual(len(p['groups']),2)
 def test_mixed_colour_fragments_remain_literal(self):
  f=split(self.parent[0]);l=[dict(parentFace=0,kind='ramp-derived-return')for _ in f];out,rows,p=recover(f,l,self.parent,context([0,1,0,1]));mixed=p['groups'][0]['certificate']['mixedColourOriginalFaceIds'];self.assertTrue(mixed)
  for i in mixed:self.assertTrue(any(np.array_equal(t,f[i])for t in out))
 def test_changed_face_cannot_claim_untouched_credit(self):
  f=self.parent.copy();f[0,0,1]+=.125
  with self.assertRaises(AssertionError):recover(f,[dict(parentFace=i,kind='unchanged')for i in range(2)],self.parent,context())
if __name__=='__main__':unittest.main()
