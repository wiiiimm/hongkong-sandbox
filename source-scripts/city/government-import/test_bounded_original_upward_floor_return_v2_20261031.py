"""Retain all source-floor guards and replay the actual rejected native clip."""
import json
import unittest
import shapely
from run import ROOT
from exact_affine_halfplane_clip_v1_20261024 import lower_region
from ronsdale_local_inset_v2_20261022 import lower_region as floating_clip
from bounded_original_upward_floor_return_v2_20261031 import inset
import test_bounded_original_upward_floor_return_v1_20261029 as legacy
legacy.inset=inset
SourceFloorReturn=legacy.SourceFloorReturn

class ActualNativeClip(unittest.TestCase):
    def test_exact_clip_handles_actual_rejected_polygon_without_mutation(self):
        path=ROOT/'docs/astra-city/government-import/government-xl-275446-source-floor-rejected-clip-v4-20261031/rejected-input.json'
        d=json.loads(path.read_text());region=shapely.from_wkb(bytes.fromhex(d['regionWKB']));before=region.wkb
        self.assertTrue(region.is_valid)
        with self.assertRaises(AssertionError):floating_clip(region,d['difference'])
        result=lower_region(region,d['difference'])
        self.assertTrue(result.is_valid);self.assertGreater(result.area,0)
        self.assertEqual(region.wkb,before)

if __name__=='__main__':unittest.main()
