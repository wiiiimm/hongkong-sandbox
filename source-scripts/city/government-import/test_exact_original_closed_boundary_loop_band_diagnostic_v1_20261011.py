import unittest,numpy as np
from exact_original_closed_boundary_loop_band_diagnostic_v1_20261011 import verify

def edges(points):return np.asarray(list(zip(points,points[1:]+points[:1])),float)
T=edges([[0,0,0],[1,0,0],[0,1,0]])
class Tests(unittest.TestCase):
 def test_exact_loop(self):self.assertTrue(verify(T,T)['completeReciprocalBoundaryBandProved'])
 def test_offset(self):self.assertTrue(verify(T,T+[0,0,.05])['completeReciprocalBoundaryBandProved'])
 def test_fixed_boundary(self):self.assertTrue(verify(T,T+[0,0,.1])['completeReciprocalBoundaryBandProved'])
 def test_outside(self):self.assertFalse(verify(T,T+[0,0,np.nextafter(.1,np.inf)])['completeReciprocalBoundaryBandProved'])
 def test_only_point_near(self):self.assertFalse(verify(T,edges([[0,0,0],[3,0,0],[0,3,0]]))['completeReciprocalBoundaryBandProved'])
 def test_open(self):
  with self.assertRaises(AssertionError):verify(T,T[:2])
 def test_two_loops(self):
  with self.assertRaises(AssertionError):verify(T,np.concatenate([T,T+[5,0,0]]))
 def test_duplicate(self):
  with self.assertRaises(AssertionError):verify(T,np.concatenate([T,T[:1]]))
 def test_zero_edge(self):
  t=T.copy();t[0,1]=t[0,0]
  with self.assertRaises(AssertionError):verify(T,t)
 def test_mutation(self):
  old=verify(T,T)['binding']
  with self.assertRaises(AssertionError):verify(T,T+[0,0,.01],expected_binding=old)
 def test_no_interior_or_role_credit(self):
  r=verify(T,T);self.assertFalse(r['wholeInteriorProximityCertified']);self.assertFalse(r['authoredMountCertified']);self.assertFalse(r['simpleGeometricHoleCertified']);self.assertFalse(r['structuralRootCredit'])
if __name__=='__main__':unittest.main()
