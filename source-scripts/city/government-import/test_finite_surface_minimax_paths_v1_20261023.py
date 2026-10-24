import unittest
import numpy as np
from finite_surface_minimax_paths_v1_20261023 import adjacency,minimum_barrier

class Minimax(unittest.TestCase):
    def test_higher_attachment_recorded_not_approved(self):
        t=np.array([[[0.,0.,0.],[1.,2.,0.],[0.,2.,0.]],[[1.,2.,0.],[0.,2.,0.],[1.,0.,0.]]]);a,v=adjacency(t,[]);r=minimum_barrier(t,a,v,[0,0,0],[0],[dict(sourceFace=1,point=[1.,0.,0.])]);self.assertEqual(r['minimumExcessOverOwnEndpointsM'],2);self.assertFalse(r['strictOwnEndpointHeightPassed']);self.assertFalse(r['installationApproved'])
    def test_point_contact_cannot_connect(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[2.,0.,0.],[2.,1.,0.]]]);a,v=adjacency(t,[]);self.assertIsNone(minimum_barrier(t,a,v,[0,0,0],[0],[dict(sourceFace=1,point=[2.,0.,0.])]))
    def test_nonrendering_bridge_cannot_connect(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[3.,0.,0.],[3.,1.,0.]],[[0.,0.,0.],[1.,0.,0.],[3.,0.,0.]]]);a,v=adjacency(t,[]);self.assertFalse(v[2]);self.assertIsNone(minimum_barrier(t,a,v,[0,0,0],[0],[dict(sourceFace=1,point=[2.,0.,0.])]))
    def test_positive_join_requires_actual_surface(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[2.,0.,0.],[2.,1.,0.]]]);j=dict(dimension=1,primitiveDimensions=[2,2],sourceFaceA=0,sourceFaceB=1,points=[[100.,0.,0.]])
        with self.assertRaises(AssertionError):adjacency(t,[j])

if __name__=='__main__':unittest.main()
