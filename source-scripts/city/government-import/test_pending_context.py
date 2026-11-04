"""Analytic terrain cases distinguish viewer error from source-context holds."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import shapely

spec=importlib.util.spec_from_file_location('pending_context',Path(__file__).with_name('pending-context.py'))
context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)

class NativeContextTests(unittest.TestCase):
    def measure(self,positions,current,triangles=None):
        tri=np.array(triangles if triangles is not None else [[[0,0,0],[10,0,0],[0,0,10]]],dtype=float)
        tree=shapely.STRtree(shapely.polygons(tri[:,:,[0,2]]))
        return context.terrain_diagnostic({'position':np.array(positions).ravel().tolist(),'drawnGround':current},tri,tree)

    def test_false_burial_from_coarse_viewer_ground(self):
        r=self.measure([[1,0,1],[2,0,1],[1,3,2]],[2,2,2])
        self.assertTrue(r['currentBurialAbsentAgainstNativeVertices'])
        self.assertEqual(r['belowCurrentTerrainBy05m'],2)
        self.assertEqual(r['belowNativeTerrainBy05m'],0)

    def test_burial_in_both_sources_is_not_viewer_only(self):
        r=self.measure([[1,-2,1],[2,0,1],[1,3,2]],[2,2,2])
        self.assertFalse(r['currentBurialAbsentAgainstNativeVertices'])
        self.assertEqual(r['belowNativeTerrainBy05m'],1)

    def test_missing_native_coverage_never_resolves_burial(self):
        r=self.measure([[1,0,1],[20,0,20]],[2,2])
        self.assertEqual(r['nativeCoveredVertices'],1)
        self.assertFalse(r['currentBurialAbsentAgainstNativeVertices'])

    def test_native_slope_uses_interpolated_triangle_heights(self):
        r=self.measure([[2,5,2],[1,4,2]],[0,0],[[[0,0,0],[10,10,0],[0,0,10]]])
        self.assertEqual(r['nativeSurfaceGapRange'],[3.0,3.0])
        self.assertEqual(r['nativeLowRimGapRange'],[3.0,3.0])
        self.assertEqual(r['currentMinusNativeTerrainRange'],[-2.0,-1.0])

if __name__=='__main__':unittest.main()
