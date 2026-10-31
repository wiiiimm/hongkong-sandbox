import unittest
from fractions import Fraction
import numpy as np
from original_native_contact_lineage_v2_20261027 import coordinate_deltas,original_role_counts

class CoordinateDeltas(unittest.TestCase):
    def test_all_vertices_match_exact_oracle(self):
        a=np.array([[[1.,2.,3.],[1.,2.,3.],[4.,5.,6.]],[[7.,8.,9.],[4.,5.,6.],[1.,2.,3.]]]);b=a.copy();b[1,0,0]=np.nextafter(7.,8.);b[0,2,1]-=.125
        r=coordinate_deltas(a,b)
        expected=[str(max(abs(Fraction(float(x))-Fraction(float(y)))for x,y in zip(a.reshape(-1,3)[:,i],b.reshape(-1,3)[:,i])))for i in range(3)]
        self.assertEqual(r['exactMaximumAbsoluteCoordinateDeltaM'],expected);self.assertEqual(r['completeIndexedVerticesCompared'],6)
    def test_changed_repeated_occurrence_is_not_dropped(self):
        a=np.zeros((2,3,3));b=a.copy();b[1,2,2]=1
        self.assertEqual(coordinate_deltas(a,b)['exactMaximumAbsoluteCoordinateDeltaM'],['0','0','1'])
    def test_mismatched_shapes_reject(self):
        with self.assertRaises(AssertionError):coordinate_deltas(np.zeros((2,3,3)),np.zeros((1,3,3)))
    def test_nonfinite_reject(self):
        a=np.zeros((1,3,3));b=a.copy();b[0,0,0]=np.nan
        with self.assertRaises(AssertionError):coordinate_deltas(a,b)
    def test_missing_original_pair_remains_explicit_and_json_stable(self):
        import json
        r=original_role_counts([{'originalPairRole':None},{'originalPairRole':'surface-point-contact'}])
        self.assertEqual(r,{'no-original-facet-pair-contact':1,'surface-point-contact':1});self.assertEqual(r,json.loads(json.dumps(r)))
    def test_empty_reject(self):
        with self.assertRaises(AssertionError):coordinate_deltas(np.zeros((0,3,3)),np.zeros((0,3,3)))
if __name__=='__main__':unittest.main()
