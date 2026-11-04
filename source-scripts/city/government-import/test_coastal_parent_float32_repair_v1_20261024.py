import unittest
from fractions import Fraction as F
import numpy as np
from coastal_parent_float32_repair_v1_20261024 import ceil_float32,audit,repaired_positions

class CoastalRepairTests(unittest.TestCase):
    def test_rounds_up_to_exact_rational_target(self):
        old=float(np.float32(.71));delta=F(1,30000000)
        self.assertGreaterEqual(F(ceil_float32(old,delta)),F(old)+delta)
    def test_negative_increment_rejected(self):
        with self.assertRaises(AssertionError):ceil_float32(.7,F(-1,1000))
    def test_large_correction_rejected(self):
        with self.assertRaises(AssertionError):ceil_float32(.7,F(1,100))
    def test_ulp_larger_than_budget_rejected(self):
        with self.assertRaises(AssertionError):ceil_float32(100000,F(1,100000))
    def test_shared_vertices_and_xz_preserved(self):
        p=np.array([[0,.7,0],[1,.7,0],[0,.7,1],[0,.7,0],[0,.7,1],[-1,.7,0]],float)
        r=[dict(candidateFace=0,exactMinimumGapM='-1/100000',projectionCovered=True)]
        out,proof=repaired_positions(p.ravel(),list(range(6)),r)
        self.assertEqual(out[0,1],out[3,1]);self.assertEqual(out[2,1],out[4,1])
        np.testing.assert_array_equal(out[:,[0,2]],p[:,[0,2]])
        self.assertEqual(proof['changedVertexIndices'],[0,1,2,3,4])
    def test_missing_projection_cannot_be_bypassed(self):
        with self.assertRaises(AssertionError):repaired_positions([0,.7,0,1,.7,0,0,.7,1],[0,1,2],[dict(candidateFace=0,exactMinimumGapM='-1/100000',projectionCovered=False)])
    def test_exact_lp_regression_is_removed(self):
        parent=np.array([[[0,.70002,0],[1,.70005,0],[0,.70003,1]]])
        p=np.array([[0,.7,0],[1,.7,0],[0,.7,1]])
        before=audit(p.ravel(),[0,1,2],parent)
        self.assertFalse(before[0]['passed'])
        out,_=repaired_positions(p.ravel(),[0,1,2],before)
        self.assertTrue(all(r['passed']for r in audit(out.ravel(),[0,1,2],parent)))
    def test_floor_crossing_correction_remains_exact(self):
        parent=np.array([[[0,1.19999,0],[1,1.2002,0],[0,1.2001,1]]])
        p=np.array([[0,1.19998,0],[1,1.2001,0],[0,1.2001,1]])
        before=audit(p.ravel(),[0,1,2],parent)
        out,_=repaired_positions(p.ravel(),[0,1,2],before)
        self.assertTrue(all(r['passed']for r in audit(out.ravel(),[0,1,2],parent)))

if __name__=='__main__':unittest.main()
