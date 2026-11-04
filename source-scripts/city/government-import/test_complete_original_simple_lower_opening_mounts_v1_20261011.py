"""Adverse opening/source/finite-host guards, including genuine six-edge loop."""
import unittest
import numpy as np
from complete_original_simple_lower_opening_mounts_v1_20261011 import verify,binding,complete_lower_cycle

def prism(n=6,low=None):
 low=np.array([[np.cos(2*np.pi*i/n),0,np.sin(2*np.pi*i/n)]for i in range(n)])if low is None else np.asarray(low,float);n=len(low);high=low+[0,1,0];faces=[]
 for i in range(n):
  j=(i+1)%n;faces.extend([[low[i],low[j],high[i]],[low[j],high[j],high[i]]])
 faces.extend([[high[0],high[i],high[i+1]]for i in range(1,n-1)]);return np.array(faces)
def hosts():return np.array([[[-2,0,-2],[2,0,-2],[2,0,2]],[[-2,0,-2],[2,0,2],[-2,0,2]]],float)
def run(body,host=None):
 host=hosts()if host is None else host;t=np.concatenate([body,host]);b=list(range(len(body)));h=list(range(len(body),len(t)));return verify(t,b,h,expected_binding=binding(t,b,h))
class Guards(unittest.TestCase):
 def test_complete_six_edge(self):
  p=run(prism());self.assertTrue(p['completeLowerOpeningAssociated']);self.assertEqual(len(p['completeDirectedLowerOpening']),6);self.assertFalse(p['structuralRootCredit'])
 def test_existing_four_edge(self):self.assertTrue(run(prism(4))['completeLowerOpeningAssociated'])
 def test_missing_body_edge_face(self):
  with self.assertRaises(AssertionError):run(prism()[1:])
 def test_reversed_face(self):
  b=prism();b[0]=b[0,::-1]
  with self.assertRaises(AssertionError):run(b)
 def test_disjoint_complete_body(self):
  with self.assertRaises(AssertionError):run(np.concatenate([prism(),prism()+[10,0,0]]))
 def test_point_only_host_inadequate(self):self.assertFalse(run(prism(),np.array([[[1,0,0],[1.01,0,0],[1,0,.01]]]))['completeLowerOpeningAssociated'])
 def test_partial_host_inadequate(self):self.assertFalse(run(prism(),np.array([[[-2,0,-2],[0,0,-2],[0,0,2]],[[-2,0,-2],[0,0,2],[-2,0,2]]]))['completeLowerOpeningAssociated'])
 def test_stray_lower_connected_face(self):
  b=prism();b=np.concatenate([b,[[b[0,1],b[0,0],[0,-1,0]]]])
  with self.assertRaises(AssertionError):run(b)
 def test_hidden_closed_tetrahedron(self):
  a,b,c,d=np.array([[5,-1,0],[6,-1,0],[5,-1,1],[5,0,0]],float);tetra=np.array([[a,b,c],[a,d,b],[b,d,c],[c,d,a]])
  with self.assertRaises(AssertionError):run(np.concatenate([prism(),tetra]))
 def test_degenerate_host(self):
  h=np.concatenate([hosts(),[[[0,0,0],[0,0,0],[0,0,0]]]])
  with self.assertRaises(AssertionError):run(prism(),h)
 def test_point_glued_body_not_single_genuine_body(self):
  body=prism();a=body[0,0];b=a+[4,0,0];c=a+[0,0,4];d=a+[0,4,0];tetra=np.array([[a,b,c],[a,d,b],[b,d,c],[c,d,a]])
  with self.assertRaises(AssertionError):run(np.concatenate([body,tetra]))
 def test_crossing_boundary(self):
  low=[[0,0,0],[3,0,2],[0,0,3],[2,0,0]]
  with self.assertRaises(AssertionError):run(prism(low=low))
 def test_stale_binding(self):
  t=np.concatenate([prism(),hosts()]);b=list(range(len(t)-2));h=list(range(len(t)-2,len(t)));expected=binding(t,b,h);t[0,0,0]+=.001
  with self.assertRaises(AssertionError):verify(t,b,h,expected_binding=expected)
 def test_disconnected_cycles(self):
  # Single connected annular vertical sheet: lower and higher boundarycycles.
  low=np.array([[0,0,0],[2,0,0],[2,0,2],[0,0,2]],float);high=low+[0,1,0];faces=[]
  for i in range(4):j=(i+1)%4;faces.extend([[low[i],low[j],high[i]],[low[j],high[j],high[i]]])
  with self.assertRaises(AssertionError):run(np.array(faces))
if __name__=='__main__':unittest.main()
