import unittest
import numpy as np
from source_triangle_windows import TriangleWindows


class WindowTests(unittest.TestCase):
    def direct(self, t, b):
        x0,z0,x1,z1=b
        return t[(t[:,:,0].max(axis=1)>=x0)&(t[:,:,0].min(axis=1)<=x1)&(t[:,:,2].max(axis=1)>=z0)&(t[:,:,2].min(axis=1)<=z1)]

    def test_exact_random_windows_and_sheet_concatenation(self):
        rng=np.random.default_rng(7);sheets=[rng.normal(size=(100,3,3))*1000 for _ in range(3)]
        combined=np.concatenate(sheets);original=combined.copy();windows=[TriangleWindows(t) for t in sheets]
        for _ in range(50):
            p=rng.normal(size=(2,2))*1000;lo=p.min(axis=0);hi=p.max(axis=0);b=[lo[0],lo[1],hi[0],hi[1]]
            np.testing.assert_array_equal(np.concatenate([w.select(b) for w in windows]),self.direct(combined,b))
        np.testing.assert_array_equal(combined,original)

    def test_touching_boundaries_and_empty(self):
        t=np.array([[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]]]);w=TriangleWindows(t)
        np.testing.assert_array_equal(w.select([1,0,2,1]),t)
        self.assertEqual(w.select([1.00001,0,2,1]).shape,(0,3,3))
        np.testing.assert_array_equal(w.select([0,1,1,2]),t)

    def test_nonfinite_and_inverted_rejected(self):
        with self.assertRaises(AssertionError):TriangleWindows(np.full((1,3,3),np.nan))
        w=TriangleWindows(np.zeros((1,3,3)))
        for b in ([1,0,0,1],[0,2,1,1],[0,0,np.inf,1]):
            with self.assertRaises(AssertionError):w.select(b)


if __name__=='__main__':unittest.main()
