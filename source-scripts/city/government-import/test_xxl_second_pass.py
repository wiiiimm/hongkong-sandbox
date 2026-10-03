"""Meaningful geometry/identity regression checks for source-only diagnostics."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
from shapely.geometry import Polygon
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ProjectionTests(unittest.TestCase):
    def test_concave_projection_does_not_fill_missing_corner(self):
        # An L shape has a different centroid from its convex hull.
        points=np.array([[0,0,0],[3,0,0],[3,0,1],[1,0,1],[1,0,3],[0,0,3]],float)
        triangles=points[np.array([[0,1,3],[1,2,3],[0,3,5],[3,4,5]])]
        foot=Polygon(points[:,[0,2]])
        fit=m.projection_metrics(triangles,foot)
        self.assertAlmostEqual(fit['projectionArea'],5)
        self.assertAlmostEqual(fit['centroidDistance'],0)
        self.assertAlmostEqual(fit['footprintCovered'],1)
        self.assertAlmostEqual(fit['projectionInsideFootprint'],1)
        self.assertGreater(foot.convex_hull.centroid.distance(foot.centroid),0)
    def test_partial_overlap_does_not_imply_full_coverage(self):
        tri=np.array([[[0,0,0],[1,0,0],[0,0,1]]],float)
        fit=m.projection_metrics(tri,Polygon([(0,0),(2,0),(2,2),(0,2)]))
        self.assertAlmostEqual(fit['overlapOfSmaller'],1)
        self.assertLess(fit['footprintCovered'],.2)
    def test_exact_identity_rejects_nearby_and_retains_ambiguity(self):
        n={'modelId':'B123456789001063C0','matching':{'officialCandidates':[{'objectId':42,'buildingCSUID':'1234567890P20200101'}]}}
        def form(uid,csuid,obj=42):return {'building':{'uid':uid,'objectId':obj,'buildingCSUID':csuid}}
        a=form('landsd/42:0','1234567890P20200101');b=form('landsd/42:1','1234567890P20200101')
        self.assertEqual(m.exact_forms(n,[a,b,form('landsd/43:0','1234567890P20200101',43),form('landsd/44:0','1234567891P20200101')]),[a,b])

if __name__=='__main__':unittest.main()
