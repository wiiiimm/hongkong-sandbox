import unittest,numpy as np
from whole_source_disjoint_literal_parent_facets_20261010 import propose,finite_projection
from native_parent_child_flat_composition_20261010 import faces
from run import digest
def patch(t):return {'nativeMesh':{'position':np.array(t,float).reshape(-1).tolist(),'index':list(range(np.array(t).size//3))}}
P=patch([[[0,3,0],[2,3,0],[0,3,2]]]);S=np.array([[[10,0,10],[11,0,10],[10,0,11]]],float);B={'uid':'outside','rings':[[[.1,.1],[.2,.1],[.1,.2],[.1,.1]]]}
class ExactWholeSource(unittest.TestCase):
 def test_literal_source_prefix(self):
  c=patch([[[0,1,0],[2,1,0],[0,1,2]]]);o,r=propose(c,P,{'source':S},[B],digest(faces(P).astype('<f8').tobytes()));self.assertEqual(o['nativeMesh']['position'][:9],c['nativeMesh']['position']);self.assertTrue(np.array_equal(faces(o)[-1],faces(P)[0]));self.assertFalse(r['physicalAccepted'])
 def test_whole_parent_facet_crosses_source_rejected(self):
  s=np.array([[[1,0,0],[1.1,0,0],[1,0,.1]]])
  with self.assertRaises(AssertionError):propose(P,P,{'source':s},[B],digest(faces(P).astype('<f8').tobytes()))
 def test_collinear_source_line_not_omitted(self):
  s=np.array([[[1,0,0],[1,1,.5],[1,2,1]]])
  with self.assertRaises(AssertionError):propose(P,P,{'source':s},[B],digest(faces(P).astype('<f8').tobytes()))
 def test_source_isolated_point_not_omitted(self):
  s=np.array([[[1,0,.1],[1,1,.1],[1,2,.1]]])
  with self.assertRaises(AssertionError):propose(P,P,{'source':s},[B],digest(faces(P).astype('<f8').tobytes()))
 def test_tiny_real_source_triangle_not_omitted(self):
  d=2**-80;s=np.array([[[0,0,0],[d,0,0],[0,0,d]]]);self.assertGreater(finite_projection(s).area,0)
 def test_intersecting_form_rejected(self):
  b={'uid':'bad','rings':[[[10,10],[11,10],[10,11],[10,10]]]}
  with self.assertRaises(AssertionError):propose(P,P,{'source':S},[b],digest(faces(P).astype('<f8').tobytes()))
 def test_changed_parent_rejected(self):
  with self.assertRaises(AssertionError):propose(P,P,{'source':S},[B],'0'*64)
 def test_budget_increase_rejected(self):
  with self.assertRaises(AssertionError):propose(P,P,{'source':S},[B],digest(faces(P).astype('<f8').tobytes()),budget=100001)
 def test_nonfinite_source_rejected(self):
  with self.assertRaises(AssertionError):finite_projection(np.array([[[0,0,0],[1,float('nan'),0],[0,0,1]]]))
 def test_duplicate_actor_rejected(self):
  with self.assertRaises(AssertionError):propose(P,P,{'source':S},[B,B],digest(faces(P).astype('<f8').tobytes()))
if __name__=='__main__':unittest.main()
