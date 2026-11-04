"""Closed-edge clearance regressions for the ramp return proposal."""
import unittest
import numpy as np
import shapely
from bounded_original_ramp_return_v1_20261025 import inset
from source_surface_inset import plane

def square(radius,height):
 v=np.array([[-radius,height(-radius,-radius),-radius],[radius,height(radius,-radius),-radius],[radius,height(radius,radius),radius],[-radius,height(-radius,radius),radius]])
 return v[[[0,2,1],[0,3,2]]]

def heights(tri,xz):
 q=shapely.Point(xz)
 return [float(np.r_[xz,1.]@plane(t))for t in tri if shapely.Polygon(t[:,[0,2]]).covers(q)]

class RampReturnTests(unittest.TestCase):
 def setUp(self):
  self.terrain=square(10.,lambda x,z:4.);self.ramps=square(1.,lambda x,z:3.+.1*x)
  self.out,self.proof=inset(self.terrain,self.ramps)
 def test_original_ramp_closed_edges_are_clear(self):
  # A footprint-only cut leaves the old high terrain at precisely these edges.
  for x,z in [(-1.,-1.),(-1.,0.),(1.,-1.),(1.,1.),(0.,1.)]:
   h=heights(self.out,[x,z]);self.assertTrue(h);self.assertLessEqual(max(h),3.+.1*x+1e-8)
 def test_unrelated_ground_and_inputs_are_preserved(self):
  np.testing.assert_array_equal(self.ramps,square(1.,lambda x,z:3.+.1*x))
  np.testing.assert_array_equal(self.terrain,square(10.,lambda x,z:4.))
  for xz in [[9.,0.],[-9.,0.],[0.,9.],[0.,-9.]]:self.assertAlmostEqual(max(heights(self.out,xz)),4.,places=9)
  self.assertAlmostEqual(shapely.union_all(shapely.polygons(self.out[:,:,[0,2]])).area,400.,places=6)
  self.assertLessEqual(self.out[:,:,1].max(),4.+1e-9)
 def test_return_has_no_new_closed_edge_height_steps(self):
  for point in np.unique(self.out[:,:,[0,2]].reshape(-1,2),axis=0):
   h=heights(self.out,point);self.assertTrue(h);self.assertLess(max(h)-min(h),1e-8)
  self.assertAlmostEqual(self.proof['removedProjectedAreaM2'],self.proof['insertedProjectedAreaM2'],places=6)
if __name__=='__main__':unittest.main()
