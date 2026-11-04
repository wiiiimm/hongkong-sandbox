import unittest
import numpy as np
from fractions import Fraction
from finite_height_clearance_bound_v1_20261023 import verify

class FiniteHeightBoundTests(unittest.TestCase):
    def test_finite_mesh_cannot_have_unbounded_negative_column_gap(self):
        s=[[0,17.4,0],[1e-12,100,0],[0,18,1]];g=[[0,9,0],[1,4,0],[0,6,1]]
        r=verify(s,g);self.assertTrue(r['ordinaryClearanceBoundProved']);self.assertGreater(r['clearanceLowerBoundM'],8)
    def test_exact_half_metre_boundary(self):
        self.assertTrue(verify([[0,.5,0]],[[0,1,0]])['ordinaryClearanceBoundProved'])
        self.assertFalse(verify([[0,np.nextafter(.5,-np.inf),0]],[[0,1,0]])['ordinaryClearanceBoundProved'])
    def test_high_ground_vertex_cannot_be_omitted(self):
        r=verify([[0,17,0]],[[0,3,0],[100,18,100]]);self.assertFalse(r['ordinaryClearanceBoundProved'])
    def test_every_source_vertex_is_accounted(self):
        r=verify([[0,17,0],[1,1,1]],[[0,3,0]]);self.assertFalse(r['ordinaryClearanceBoundProved'])
    def test_nonfinite_or_empty_inputs_reject(self):
        for s,g in [([],[[0,1,0]]),([[0,float('nan'),0]],[[0,1,0]]),([[0,2,0]],[[0,float('inf'),0]])]:
            with self.assertRaises(AssertionError):verify(s,g)

if __name__=='__main__':unittest.main()
