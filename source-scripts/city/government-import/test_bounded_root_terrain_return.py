import unittest,numpy as np
from bounded_root_terrain_return_v1 import transition
from primrose_compound_foundation_v2_20261015 import module
from run import HERE
b=module('return_test_clipper',HERE/'resolve_pass_indexed_parent_clipping_v2.py')
class ReturnTests(unittest.TestCase):
 def test_preserves_interior_and_vertical(self):
  faces=np.array([[[3,7,3],[4,8,3],[3,9,4]],[[4,2,4],[4,8,4],[4,2,5]]],float)
  np.testing.assert_array_equal(transition(faces,[0,0,10,10],[[[0,0],[10,0],[0,10]],[[10,0],[10,10],[0,10]]],lambda x,z:0,2,b.exact),faces)
 def test_exact_boundary_and_unchanged_core(self):
  faces=np.array([[[0,10,0],[10,10,0],[0,10,10]],[[10,10,0],[10,10,10],[0,10,10]]],float);cells=np.array([[[0,0],[10,0],[0,10]],[[10,0],[10,10],[0,10]]],float)
  out=transition(faces,[0,0,10,10],cells,lambda x,z:1+x*.1+z*.2,2,b.exact);v=out.reshape(-1,3)
  edge=np.minimum.reduce([v[:,0],10-v[:,0],v[:,2],10-v[:,2]])<1e-8
  np.testing.assert_allclose(v[edge,1],1+v[edge,0]*.1+v[edge,2]*.2,atol=1e-10)
  inner=np.minimum.reduce([v[:,0],10-v[:,0],v[:,2],10-v[:,2]])>=2-1e-8
  np.testing.assert_allclose(v[inner,1],10,atol=1e-10)
 def test_rejects_invalid_strip(self):
  for width in [0,-1,5,float('nan')]:
   with self.assertRaises(AssertionError):transition([], [0,0,10,10],[],lambda x,z:0,width,b.exact)
if __name__=='__main__':unittest.main()
