import gzip,json
from pathlib import Path
import unittest
import numpy as np
import shapely
from conditioned_planar_partition_v1_20261026 import qualify

class ConditionedPartitionTests(unittest.TestCase):
    def test_real_tung_on_union_false_overlap_regression(self):
        root=Path(__file__).resolve().parents[3];p=root/'docs/astra-city/government-import/government-xl-after-tuen-mun-tung-on-upper-overlap-v1-20261026/upper-fragments.json.gz'
        tri=np.asarray(json.loads(gzip.decompress(p.read_bytes()))['triangles']);parts=shapely.polygons(tri[:,:,[0,2]]);before=shapely.get_coordinates(parts).copy();proof=qualify(parts,parts)
        self.assertGreater(proof['rawWorldUnionOverlapAreaM2'],.2);self.assertLess(proof['conditionedOverlapAreaM2'],1e-6);self.assertTrue(np.array_equal(before,shapely.get_coordinates(parts)))
    def test_true_overlap_is_rejected(self):
        parts=[shapely.box(5000,5000,5002,5002),shapely.box(5001,5001,5003,5003)]
        with self.assertRaisesRegex(AssertionError,'overlap'):qualify(parts,parts)
    def test_missing_coverage_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'coverage'):qualify([shapely.box(5000,5000,5001,5001)],[shapely.box(5000,5000,5002,5002)])
    def test_extra_coverage_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'coverage'):qualify([shapely.box(5000,5000,5002,5002)],[shapely.box(5000,5000,5001,5001)])
    def test_adjacent_faces_pass(self):
        proof=qualify([shapely.box(5000,5000,5001,5001),shapely.box(5001,5000,5002,5001)],[shapely.box(5000,5000,5002,5001)]);self.assertEqual(proof['conditionedCoverageDifferenceAreaM2'],0)
    def test_cross_origin_uses_exact_zero_anchor(self):
        proof=qualify([shapely.box(-1,-1,1,1)],[shapely.box(-1,-1,1,1)]);self.assertEqual(proof['coordinateAnchor'],[0,0])

if __name__=='__main__':unittest.main()
