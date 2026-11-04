import unittest
import numpy as np
from source_grade_parent_return_v1_20261023 import blend


class SourceGradeParentReturnTests(unittest.TestCase):
    def test_land_and_existing_water_return(self):
        result=blend([3.,3.,3.],[-4.,-4.,4.],[0.,.8,1.])
        np.testing.assert_array_equal(result[[0,2]],[3.,4.])
        self.assertGreaterEqual(result[1],-4.)
        self.assertLess(result[1],1.2)

    def test_new_below_floor_source_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'source terrain'):blend([1.19],[-4.],[0.])

    def test_land_cannot_become_subclamp(self):
        for source in [1.2,3.,10.]:
            for parent in [1.2,2.,8.]:
                self.assertTrue(np.all(blend([source]*3,[parent]*3,[0.,.5,1.])>=1.2))

    def test_invalid_weights_or_nonfinite_rejected(self):
        for weights in [[-.1],[1.1],[np.nan]]:
            with self.assertRaises(AssertionError):blend([3.],[-4.],weights)


if __name__=='__main__':unittest.main()
