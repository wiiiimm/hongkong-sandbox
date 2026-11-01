"""Exact source-plane regression cases: real cancellation, heights and bounds."""
import unittest
from fractions import Fraction as F
import numpy as np
import shapely
from shapely.affinity import translate
from exact_affine_halfplane_clip_v2_20261030 import lower_region as old_clip
from original_source_plane_clipping_v1_20261101 import from_original_facet, lower_region

class ExactPlanes(unittest.TestCase):
    def test_shared_corner(self):
        faces=np.asarray([[[10626.41015625,99.28227996826172,-5673.755859375],[10626.3984375,106.61861419677734,-5670.755859375],[10626.390625,99.28227996826172,-5645.0859375]],[[10626.390625,99.28227996826172,-5645.0859375],[10626.3984375,111.78750610351562,-5659.005859375],[10626.3984375,110.6527099609375,-5662.005859375]]])
        original=faces.copy();region=shapely.Polygon([(10626.3984375,-5659.005859375),(10626.3984375,-5662.005859375),(10626.390625,-5645.0859375)])
        with self.assertRaises(AssertionError):old_clip(region,[3032.9196260787344,.8948375849741259,-32223937.245874286])
        a,b=map(from_original_facet,faces);diff=tuple(y-x for x,y in zip(a,b));x,_,z=map(F,map(float,faces[0,2]));self.assertEqual(diff[0]*x+diff[1]*z+diff[2],0)
        result=lower_region(region,diff);self.assertTrue(result.is_valid);self.assertTrue(result.equals(region));np.testing.assert_array_equal(faces,original)
        for face in faces:
            a,b,c=from_original_facet(face)
            for x,y,z in face:self.assertEqual(a*F(x)+b*F(z)+c,F(y))
    def test_translation(self):
        region=shapely.box(0,0,1,1);result=lower_region(region,(F(1),F(0),-F(1,2)));self.assertEqual(result.area,.5)
        shifted=lower_region(translate(region,xoff=10000000,yoff=-10000000),(F(1),F(0),-F(20000001,2)))
        self.assertTrue(translate(shifted,xoff=-10000000,yoff=10000000).equals(result))
    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError):lower_region(shapely.box(0,0,1,1),(float('nan'),0,0))

if __name__=='__main__':unittest.main()
