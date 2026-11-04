import unittest
from fractions import Fraction as F
from exact_source_core_ten_metre_transition_domain_v1_20261011 import domain
from exact_compute_transition_mesh_v1_20261011 import nominate,faces,project,outer_segments,interpolated,edge_intersections,fan,mesh_edges,positive_overlap_inventory
class Tests(unittest.TestCase):
 def setUp(self):self.core=[[(0,1,0),(1,1,0),(0,1,1)],[(1,1,0),(1,1,1),(0,1,1)]];self.current=[[(-50,0,-50),(50,0,-50),(-50,0,50)],[(50,0,-50),(50,0,50),(-50,0,50)]]
 def test_complete_nomination_flat_outer(self):
  d=domain([project(f)for f in faces(self.core)]);r=nominate(self.core,self.current,d);self.assertFalse(r['terrainCandidateApproved']);self.assertFalse(r['fullProtectedActorRegressionsDischarged']);self.assertFalse(r['actualFloat32InternalSeams']['allInvalidInternalIncidences'])
 def test_missing_outer_finite_ground(self):
  d=domain([project(f)for f in faces(self.core)])
  with self.assertRaises(AssertionError):nominate(self.core,[[(-1,0,-1),(2,0,-1),(-1,0,2)]],d)
 def test_multiple_outer_current_heights(self):
  d=domain([project(f)for f in faces(self.core)]);high=[[(x,2,z)for x,y,z in f]for f in self.current]
  with self.assertRaises(AssertionError):nominate(self.core,self.current+high,d)
 def test_source_core_height_crack(self):
  core=[self.core[0],[(x,2,z)for x,y,z in self.core[1]]];d=domain([project(f)for f in faces(core)])
  with self.assertRaises(AssertionError):nominate(core,self.current,d)
 def test_tiny_wrong_outer_height_reject(self):
  d=domain([project(f)for f in faces(self.core)]);cur=[self.current[0],[(x,1e-20,z)for x,y,z in self.current[1]]]
  with self.assertRaises(AssertionError):nominate(self.core,cur,d)
 def test_crossing_exact(self):self.assertEqual(edge_intersections((F(0),F(0)),(F(3),F(0)),(F(1),F(-1)),(F(1),F(1))),[(F(1),F(0))])
 def test_collinear_partial(self):self.assertEqual(set(edge_intersections((F(0),F(0)),(F(3),F(0)),(F(1),F(0)),(F(2),F(0)))),{(F(1),F(0)),(F(2),F(0))})
 def test_shared_anchor_conflict(self):
  e=dict(start=(F(0),F(0)),end=(F(1),F(0)),exactEndpointY=[F(1),F(1)]);q=dict(e,exactEndpointY=[F(0),F(0)])
  with self.assertRaises(AssertionError):interpolated((F(0),F(0)),[e],[q])
 def test_generated_interior_bounded(self):
  a=dict(start=(F(0),F(0)),end=(F(0),F(2)),exactEndpointY=[F(3),F(3)]);b=dict(start=(F(2),F(0)),end=(F(2),F(2)),exactEndpointY=[F(7),F(7)]);self.assertEqual(interpolated((F(1),F(1)),[a],[b]),5)
 def test_positive_fan(self):
  r=fan([(F(0),F(0)),(F(1),F(0)),(F(0),F(1))],lambda p:F(0));self.assertEqual(len(r),3);self.assertFalse(mesh_edges(r)['allInvalidInternalIncidences'])
 def test_nonfinite_faces(self):
  with self.assertRaises(AssertionError):faces([[(0,float('nan'),0),(1,0,0),(0,0,1)]])
 def test_duplicate_positive_overlap(self):
  self.assertEqual(len(positive_overlap_inventory(faces([self.core[0],self.core[0]]))),1)
 def test_actual_float32_collapse_reject(self):
  core=[[(x+10**10,y,z+10**10)for x,y,z in f]for f in self.core];current=[[(x+10**10,y,z+10**10)for x,y,z in f]for f in self.current];d=domain([project(f)for f in faces(core)])
  with self.assertRaises(AssertionError):nominate(core,current,d)
if __name__=='__main__':unittest.main()
