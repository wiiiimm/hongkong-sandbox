import unittest
import numpy as np
from original_assembly_four_world_pair_context_v3_20261101 import require_same_worlds


class ExactPairReuse(unittest.TestCase):
    def worlds(self):
        face = np.asarray([[[0., 1., 2.], [3., 4., 5.], [6., 7., 8.]],
                           [[9., 10., 11.], [12., 13., 14.], [15., 16., 17.]]], dtype='<f8')
        return {m: face.copy() for m in ['original', 'literal', 'leftF32', 'balancedF32']}

    def test_equal_full_inputs(self):
        require_same_worlds(self.worlds(), self.worlds())

    def test_one_ulp_change_in_one_stream_rejected(self):
        left, right = self.worlds(), self.worlds()
        right['balancedF32'][1, 2, 2] = np.nextafter(right['balancedF32'][1, 2, 2], np.inf)
        with self.assertRaises(AssertionError):
            require_same_worlds(left, right)

    def test_face_reordering_rejected(self):
        left, right = self.worlds(), self.worlds()
        right['literal'] = right['literal'][::-1].copy()
        with self.assertRaises(AssertionError):
            require_same_worlds(left, right)

    def test_dtype_change_rejected(self):
        left, right = self.worlds(), self.worlds()
        right['leftF32'] = right['leftF32'].astype('<f4')
        with self.assertRaises(AssertionError):
            require_same_worlds(left, right)

    def test_missing_representation_rejected(self):
        left, right = self.worlds(), self.worlds()
        del right['original']
        with self.assertRaises(AssertionError):
            require_same_worlds(left, right)

    def test_signed_zero_not_silently_canonicalized(self):
        left, right = self.worlds(), self.worlds()
        right['original'][0, 0, 0] = -0.
        with self.assertRaises(AssertionError):
            require_same_worlds(left, right)


if __name__ == '__main__':
    unittest.main()
