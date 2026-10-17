"""Vectorized original-parent diagnostics must match the rendered triangle sampler."""
import importlib.util
import unittest
from pathlib import Path
import numpy as np
from run import ROOT

s = importlib.util.spec_from_file_location('preview_three',Path(__file__).with_name('xl-three-original-surfaces-preview.py'))
preview = importlib.util.module_from_spec(s);s.loader.exec_module(preview)
s = importlib.util.spec_from_file_location('fine_parent',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py')
fine = importlib.util.module_from_spec(s);s.loader.exec_module(fine)


class ParentTriangleSamplerTests(unittest.TestCase):
    def test_triangle_diagonals_and_water_match_runtime_parent(self):
        data={'w':3,'h':3,'elev':[0,2,10,4,8,-2,3,1,6],
              'meta':{'georef':{'aE':5,'bE':834500,'aN':-5,'bN':816500}}}
        points=np.array([[1,0,1],[4,0,4],[5,0,7],[7,0,5],[8,0,9]])
        sampler=fine.DemSampler(data,rendered=True)
        expected=np.array([sampler.ground(p[0],p[2]) for p in points])
        np.testing.assert_allclose(preview.parent_heights(points,data),expected,rtol=0,atol=1e-12)

    def test_recorded_rendered_override_matches_original_sampler(self):
        data={'w':2,'h':2,'elev':[0,2,10,-2],'renderedElev':[1,None,None,3],
              'meta':{'georef':{'aE':5,'bE':834500,'aN':-5,'bN':816500}}}
        points=np.array([[1,0,2],[4,0,3],[3,0,4]])
        sampler=fine.DemSampler(data,rendered=True)
        np.testing.assert_allclose(preview.parent_heights(points,data),[sampler.ground(p[0],p[2]) for p in points],rtol=0,atol=1e-12)

if __name__=='__main__':unittest.main()
