import unittest
from fractions import Fraction
import numpy as np
import shapely
from exact_gap_float32_caps_v1_20261023 import bracket,enclosing_hull,lower_cap

class Caps(unittest.TestCase):
    def test_exact_value_needs_no_expansion(self):self.assertEqual(bracket('1.5'),[1.5])
    def test_signed_fraction_is_conservatively_bracketed(self):
        for q in [Fraction(1,3),Fraction(-40001,10),Fraction(100001,3)]:
            a,b=bracket(q);self.assertLessEqual(Fraction(a),q);self.assertGreaterEqual(Fraction(b),q)
    def test_rational_polygon_inside_exact_hull(self):
        hull=enclosing_hull([['1/3','2/3'],['4/3','2/3'],['4/3','5/3']]);self.assertGreater(hull.area,0)
    def test_floor_cannot_raise_existing_surface(self):
        t=np.asarray([[[0.,2.,0.],[2.,2.,0.],[0.,2.,2.]]]);p=shapely.polygons(t[:,:,[0,2]]);h=shapely.box(.25,.25,.5,.5)
        f,r=lower_cap(h,t,p,shapely.STRtree(p));self.assertTrue((f[:,:,1]<2).all());self.assertEqual(r['addedFaces'],2)
    def test_no_adjacent_surface_fails(self):
        t=np.asarray([[[0.,2.,0.],[2.,2.,0.],[0.,2.,2.]]]);p=shapely.polygons(t[:,:,[0,2]])
        with self.assertRaises(AssertionError):lower_cap(shapely.box(10,10,11,11),t,p,shapely.STRtree(p))
    def test_clamp_is_preserved(self):
        t=np.asarray([[[0.,1.2,0.],[2.,1.2,0.],[0.,1.2,2.]]]);p=shapely.polygons(t[:,:,[0,2]])
        with self.assertRaises(AssertionError):lower_cap(shapely.box(.25,.25,.5,.5),t,p,shapely.STRtree(p))

if __name__=='__main__':unittest.main()
