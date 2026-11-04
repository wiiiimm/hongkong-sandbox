"""Synthetic-only exact FULL canonical output/order equivalence."""
from fractions import Fraction as F
import copy,unittest
import numpy as np
import exact_coverage_strict_bounds_cache_v1_draft_20261014 as fast

class BoundsTests(unittest.TestCase):
    def compare(self,source,ground,capacity=4096):
        source=np.asarray(source,float);ground=np.asarray(ground,float).reshape(-1,3,3)
        before=source.tobytes(),ground.tobytes();globals_before=dict(fast.canonical.__dict__)
        result,counts=fast.executor(capacity)(source,ground)
        self.assertEqual(result,fast.canonical.exact_coverage(source,ground))
        self.assertEqual(before,(source.tobytes(),ground.tobytes()))
        self.assertEqual(set(globals_before),set(fast.canonical.__dict__))
        self.assertTrue(all(fast.canonical.__dict__[k]is v for k,v in globals_before.items()))
        return result,counts
    def test_full_area_cover(self):
        self.compare([[0,2,0],[2,2,0],[0,2,2]],[[[0,0,0],[2,0,0],[0,0,2]]])
    def test_genuine_hole_area_and_piece_count(self):
        r,_=self.compare([[0,1,0],[3,1,0],[0,1,3]],[[[0,0,0],[1,0,0],[0,0,1]],[[2,0,0],[3,0,0],[2,0,1]]])
        self.assertFalse(r['exactProjectionCovered']);self.assertGreater(r['remainingPositiveAreaPieces'],0)
    def test_touching_closed_boundaries_still_canonical(self):
        sub=fast.CachedSubtractor();p=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];t=[(F(1),F(0)),(F(2),F(0)),(F(1),F(1))]
        self.assertEqual(sub(p,t),fast.canonical.subtract(p,t));self.assertEqual(sub.disjoint,0);self.assertEqual(sub.canonical_calls,1)
    def test_strict_disjoint_returns_identical_input_object(self):
        sub=fast.CachedSubtractor();p=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];t=[(F(2),F(0)),(F(3),F(0)),(F(2),F(1))]
        result=sub(p,t);self.assertEqual(result,fast.canonical.subtract(p,t));self.assertIs(result[0],p)
        sub(p,t);self.assertEqual(sub.polygon_bounds_computed,1);self.assertEqual(sub.triangle_bounds_computed,1)
    def test_non_dyadic_fragment_bounds_no_rounding(self):
        p=[(F(1,3),F(0)),(F(4,3),F(0)),(F(1,3),F(1))];t=[(F(4,3)+F(1,10**30),F(0)),(F(2),F(0)),(F(2),F(1))]
        sub=fast.CachedSubtractor();self.assertEqual(sub(p,t),fast.canonical.subtract(p,t));self.assertEqual(sub.disjoint,1)
    def test_repeated_duplicates_winding_and_order(self):
        f=[[0,2,0],[3,2,0],[0,2,3]];a=[[0,0,0],[1,0,0],[0,0,1]];b=[[1,0,0],[2,0,0],[1,0,1]]
        for g in [[a,b,a],[a,a[::-1],b],[b,a,a]]:self.compare(f,g)
    def test_interval_and_point_projection_branches(self):
        g=[[[-1,0,-1],[1,0,-1],[0,0,1]]]
        self.compare([[0,1,0],[0,2,0],[0,3,0]],g)
        self.compare([[-2,1,0],[2,1,0],[0,2,0]],g)
    def test_vertical_ground_and_zero_projection_no_credit(self):
        self.compare([[0,1,0],[2,1,0],[0,1,2]],[[[0,0,0],[0,2,0],[1,0,0]]])
    def test_eviction_changes_only_cost(self):
        f=[[0,2,0],[4,2,0],[0,2,4]];g=[[[x,0,0],[x+.25,0,0],[x,0,.25]]for x in np.arange(0,4,.25)]
        a,_=self.compare(f,g,1);b,_=self.compare(f,g,4096);self.assertEqual(a,b)
    def test_source_ground_signed_zero_and_y_kept(self):
        self.compare([[-0.,2,0],[2,3,-0.],[0,4,2]],[[[-0.,.1,0],[2,.2,-0.],[0,.3,2]]])
    def test_cache_bounded_and_no_inplace_poly_mutation(self):
        sub=fast.CachedSubtractor(2);t=[(F(100),F(0)),(F(101),F(0)),(F(100),F(1))]
        for i in range(10):
            p=[(F(i),F(0)),(F(i+1),F(0)),(F(i),F(1))];old=copy.deepcopy(p)
            sub(p,t);self.assertEqual(p,old);self.assertLessEqual(len(sub.polygons),2)
    def test_invalid_input_fails_canonical_contract(self):
        with self.assertRaises(AssertionError):fast.executor()(np.full((3,3),np.nan),np.zeros((1,3,3)))

if __name__=='__main__':unittest.main()
