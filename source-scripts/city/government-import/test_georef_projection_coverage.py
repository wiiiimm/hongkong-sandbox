import json
import unittest
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box, Polygon
from georef_projection_coverage import whole_cell_coverage

def triangle(points): return [[x, 0, z] for x,z in points]

class ProjectionNumericalCoverage(unittest.TestCase):
    def test_actual_original_heya_mesh_union_residue(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/georef-union/184286-0.json').read_text())
        tri=np.asarray(fixture['triangles']); cell=box(*fixture['cellBounds'])
        before=tri.copy(); raw=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
        self.assertFalse(raw.covers(cell))
        proof=whole_cell_coverage(tri,cell,raw)
        self.assertTrue(proof['coversWholeCell'],proof)
        self.assertTrue(proof['numericalCorrectionApplied'])
        self.assertLess(proof['rawMissingAreaM2'],1e-14)
        np.testing.assert_array_equal(before,tri)

    def test_exact_coverage_needs_no_numerical_exception(self):
        tri=np.asarray([triangle([(0,0),(1,0),(0,1)]),triangle([(1,0),(1,1),(0,1)])])
        raw=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
        proof=whole_cell_coverage(tri,box(0,0,1,1),raw)
        self.assertTrue(proof['coversWholeCell']);self.assertFalse(proof['numericalCorrectionApplied'])

    def test_small_area_real_opening_remains_rejected(self):
        # A real micrometre square is small enough for the area bound, but must
        # still fail the independent nanometre distance/precision requirements.
        outer=box(0,0,1,1); hole=box(.5,.5,.500001,.500001)
        raw=outer.difference(hole)
        tri=np.asarray([triangle([(0,0),(1,0),(0,1)]),triangle([(1,0),(1,1),(0,1)])])
        proof=whole_cell_coverage(tri,outer,raw)
        self.assertFalse(proof['coversWholeCell']);self.assertFalse(proof['numericalCorrectionApplied'])

    def test_large_or_long_thin_missing_region_remains_rejected(self):
        cell=box(0,0,1,1);tri=np.asarray([triangle([(0,0),(1,0),(0,1)])])
        for raw in [box(0,0,.999,1), cell.difference(box(.5,.5,.50001,.500001))]:
            self.assertFalse(whole_cell_coverage(tri,cell,raw)['coversWholeCell'])

if __name__=='__main__':unittest.main()
