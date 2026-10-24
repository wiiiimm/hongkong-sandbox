"""Exact finite diagnostic clipping adverse cases; no support/role acceptance."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,unittest
s=importlib.util.spec_from_file_location('lippo_lower_partition_v2',Path(__file__).with_name('xl-lippo-tower-current-basic-complete-lower-interface-partition-v2-20261011.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ExactLowerClip(unittest.TestCase):
 def poly(self):return [(F(0),F(0),F(0)),(F(2),F(2),F(0)),(F(0),F(2),F(2))]
 def test_all_inside(self):self.assertEqual(m.clip(self.poly(),lambda p:p[1]+1),self.poly())
 def test_all_outside(self):self.assertEqual(m.clip(self.poly(),lambda p:p[1]-3),[])
 def test_plane_closed_boundary(self):self.assertEqual(m.clip(self.poly(),lambda p:-p[0]),[self.poly()[0],self.poly()[2]])
 def test_real_polygon_clipped_exactly(self):
  p=m.clip(self.poly(),lambda p:F(1)-p[1]);self.assertEqual(p,[(F(0),F(0),F(0)),(F(1),F(1),F(0)),(F(0),F(1),F(1))]);self.assertEqual(m.polygon_dimension(p),2)
 def test_tiny_real_facet_retained(self):
  e=F(1,2**500);p=[(F(0),F(0),F(0)),(e,F(0),F(0)),(F(0),F(0),e)];self.assertEqual(m.polygon_dimension(p),2);self.assertEqual(m.clip(p,lambda v:F(1)),p)
 def test_collapsed_line_not_area(self):self.assertEqual(m.polygon_dimension([(F(0),)*3,(F(1),)*3,(F(2),)*3]),1)
 def test_collapsed_point_not_area(self):self.assertEqual(m.polygon_dimension([(F(1),)*3]*3),0)
 def test_empty_dimension(self):self.assertEqual(m.polygon_dimension([]),-1)
 def test_no_epsilon_outside(self):
  e=F(1,2**500);self.assertEqual(m.clip([(e,F(0),F(0)),(e,F(1),F(0)),(e,F(0),F(1))],lambda p:-p[0]),[])
 def test_fractional_intersection_never_float(self):
  p=m.clip(self.poly(),lambda v:F(1,3)-v[1]);self.assertTrue(all(isinstance(v,F) for q in p for v in q));self.assertEqual(p[1],(F(1,3),F(1,3),F(0)))
 def test_two_height_planes(self):
  p=m.clip(m.clip(self.poly(),lambda v:v[1]-F(1,2)),lambda v:F(3,2)-v[1]);self.assertEqual(m.polygon_dimension(p),2);self.assertTrue(all(F(1,2)<=v[1]<=F(3,2) for v in p))
 def test_nonzero_3d_vertical_facet(self):self.assertEqual(m.polygon_dimension([(F(0),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(0),F(1))]),2)
if __name__=='__main__':unittest.main()
