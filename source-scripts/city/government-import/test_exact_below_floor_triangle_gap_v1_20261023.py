from fractions import Fraction
import unittest
import numpy as np
from exact_below_floor_triangle_gap_v1_20261023 import verify
from exact_original_triangle_pair_column_gap_20261010 import verify as whole


class ExactBelowFloorGapTests(unittest.TestCase):
    def test_negative_above_floor_is_not_inherited_depth_regression(self):
        source=np.array([[0.,0.,0.],[1.,2.,0.],[0.,0.,1.]])
        ground=np.array([[0.,-1.5,0.],[1.,2.5,0.],[0.,-1.5,1.]])
        self.assertLess(Fraction(whole(source,ground)['exactMinimumFiniteColumnGapM']),0)
        self.assertGreater(Fraction(verify(source,ground)['exactMinimumFiniteColumnGapM']),0)

    def test_hidden_subfloor_regression_is_rejected(self):
        s=np.array([[0.,.5,0.],[1.,.5,0.],[0.,.5,1.]])
        g=s.copy();g[:,1]=.6
        self.assertLess(Fraction(verify(s,g)['exactMinimumFiniteColumnGapM']),0)

    def test_identical_and_collapsed_faces(self):
        for s in [np.array([[0.,-4.,0.],[1.,-4.,0.],[0.,-4.,1.]]),np.array([[0.,.5,0.]]*3)]:
            self.assertEqual(Fraction(verify(s,s)['exactMinimumFiniteColumnGapM']),0)

    def test_no_qualifying_source_or_disjoint_ground(self):
        s=np.array([[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]])
        self.assertFalse(verify(s,s)['exactClosedHorizontalProjectionsMeet'])
        s[:,1]=0;g=s.copy();g[:,0]+=10
        self.assertFalse(verify(s,g)['exactClosedHorizontalProjectionsMeet'])

    def test_witnesses_obey_exact_height_halfspace(self):
        s=np.array([[0.,0.,0.],[1.,2.,0.],[0.,0.,1.]])
        r=verify(s,s)
        for point in r['allExactBasicFeasibleColumnVertices']:
            self.assertLessEqual(Fraction(point['exactSourcePoint'][1]),Fraction(r['exactSourceHeightCeilingM']))
            self.assertEqual(Fraction(point['exactHeightSlackM']),Fraction(r['exactSourceHeightCeilingM'])-Fraction(point['exactSourcePoint'][1]))


if __name__=='__main__':unittest.main()
