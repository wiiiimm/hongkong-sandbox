import unittest,numpy as np
from exact_source_planar_domain_recovery_seams_v1_20261011 import recover,source_height,overlap_interval
D=np.array([[0.,0.,0.],[2.,0.,0.],[0.,0.,2.]])
R=np.array([[[0.,0.,0.],[2.,0.,0.],[0.,0.,-2.]],[[2.,0.,0.],[0.,0.,2.],[2.,0.,2.]],[[0.,0.,2.],[0.,0.,0.],[-2.,0.,0.]]])
class Tests(unittest.TestCase):
 def test_complete_planar(self):self.assertTrue(recover([D],[D],R)['seamCompatible'])
 def test_height_crack_despite_exact_projection(self):
  src=D.copy();src[:,1]=-10;z=recover([D],[src],R);self.assertTrue(z['domainCoverage'][0]['covered']);self.assertFalse(z['seamCompatible']);self.assertTrue(any(not p['heightCompatible']for p in z['allExact3DSeamProofs']))
 def test_missing_neighbor(self):self.assertFalse(recover([D],[D],R[:2])['seamCompatible'])
 def test_point_neighbor_not_edge(self):
  q=R.copy();q[0]=[[0,0,0],[-1,0,0],[0,0,-1]];self.assertFalse(recover([D],[D],q)['seamCompatible'])
 def test_partial_neighbor(self):
  q=R.copy();q[0,1,0]=1;self.assertFalse(recover([D],[D],q)['seamCompatible'])
 def test_missing_source_area(self):
  src=D.copy();src[1,0]=1;self.assertFalse(recover([D],[src],R)['domainCoverage'][0]['covered'])
 def test_nonconstant_endpoint_crack(self):
  src=D.copy();src[1,1]=1;self.assertFalse(recover([D],[src],R)['seamCompatible'])
 def test_negative_winding_source(self):self.assertTrue(recover([D],[D[::-1]],R)['seamCompatible'])
 def test_degenerate_source_rejected(self):
  src=D.copy();src[2]=src[1];self.assertFalse(recover([D],[src],R)['seamCompatible'])
 def test_degenerate_domain(self):
  q=D.copy();q[2]=q[1]
  with self.assertRaisesRegex(AssertionError,'Degenerate domain'):recover([q],[D],R)
 def test_finite_source_height(self):self.assertEqual(source_height([[0,1,0],[2,3,0],[0,5,2]],(1,1)),4)
 def test_disjoint_intervals(self):self.assertIsNone(overlap_interval((0,0),(2,0),(3,0),(4,0)))
 def test_noncollinear_point_bridge(self):self.assertIsNone(overlap_interval((0,0),(2,0),(0,0),(0,2)))
 def test_hidden_tiny_height_crack(self):
  src=D.copy();src[:,1]=2**-40;self.assertFalse(recover([D],[src],R)['seamCompatible'])
 def test_nonmanifold_domain(self):
  with self.assertRaisesRegex(AssertionError,'Nonmanifold'):recover([D,D,D],[D],R)
 def test_no_automatic_internal_edge_credit(self):
  z=recover([D],[D],R);self.assertEqual(z['internalDomainEdges'],0);self.assertEqual(z['completeExternalDomainEdges'],3)
 def test_two_domain_internal_edge(self):
  second=np.array([[2.,0.,0.],[2.,0.,2.],[0.,0.,2.]])
  outside=np.array([R[0],[[2,0,0],[2,0,2],[4,0,0]],[[2,0,2],[0,0,2],[0,0,4]],R[2]])
  z=recover([D,second],[D,second],outside);self.assertTrue(z['seamCompatible']);self.assertEqual(z['internalDomainEdges'],1);self.assertEqual(z['completeExternalDomainEdges'],4)
 def test_internal_projected_edge_cannot_hide_height_crack(self):
  second=np.array([[2.,1.,0.],[2.,1.,2.],[0.,1.,2.]])
  with self.assertRaisesRegex(AssertionError,'shared3D height conflict'):recover([D,second],[D],R)
 def test_duplicate_domain_rejected(self):
  with self.assertRaisesRegex(AssertionError,'winding conflict'):recover([D,D],[D],R)
 def test_finite_clip_records_source_plane(self):
  source=np.array([[-1.,-1.,-1.],[4.,4.,-1.],[-1.,-1.,4.]])
  z=recover([D],[source],R)
  for p in z['exactSourcePlanarPieces']:
   for x,y,_ in p['exactPoints']:self.assertEqual(x,y)
if __name__=='__main__':unittest.main()
