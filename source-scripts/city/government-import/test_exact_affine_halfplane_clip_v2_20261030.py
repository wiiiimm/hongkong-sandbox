import json,unittest
from fractions import Fraction as F
import shapely
from run import ROOT
from exact_affine_halfplane_clip_v1_20261024 import lower_region as old
from exact_affine_halfplane_clip_v2_20261030 import lower_region,cross,signed_area
import test_exact_affine_halfplane_clip_v1_20261024 as legacy
legacy.lower_region=lower_region
ExactAffineClipTests=legacy.ExactAffineClipTests
class ActualRejectedClip(unittest.TestCase):
 def test_actual_native_cliff_operand_keeps_all_old_bounds(self):
  d=json.loads((ROOT/'docs/astra-city/government-import/government-xl-after-disneyland-piers-academic309823-clip-probe-v1-20261030/rejected-clip-input.json').read_text());p=shapely.from_wkb(bytes.fromhex(d['regionWKB']));before=p.wkb
  with self.assertRaises(AssertionError):old(p,d['difference'])
  r=lower_region(p,d['difference']);self.assertTrue(r.is_valid);self.assertGreater(r.area,0);self.assertEqual(p.wkb,before)
  rounded=shapely.Polygon([(10655.37109375,-5348.056640625),(10655.371093777376,-5348.056640624986),(10674.507812499362,-5348.046875),(10674.5078125,-5348.046875)])
  self.assertLessEqual(abs(r.area-rounded.area),1e-12);self.assertLessEqual(shapely.hausdorff_distance(rounded,r),1e-12)
  self.assertLessEqual(abs(r.area-1.9237625776625306e-12),1e-12)
  coeff=list(map(F,d['difference']));source=[tuple(map(F,v[:2]))for v in p.exterior.coords[:-1]];orientation=1 if signed_area(source)>0 else -1
  for v in r.exterior.coords[:-1]:
   q=tuple(map(F,v[:2]));self.assertGreaterEqual(sum(coeff[i]*q[i]for i in range(2))+coeff[2],0)
   for a,b in zip(source,source[1:]+source[:1]):self.assertGreaterEqual(orientation*cross(a,b,q),0)
 def test_ordinary_results_are_identical(self):
  p=shapely.box(10600,-5600,10800,-5400)
  for c in [[1,0,-10700],[1,1,-5200],[0,0,1],[0,0,-1]]:self.assertEqual(lower_region(p,c).wkb,old(p,c).wkb)
if __name__=='__main__':unittest.main()
