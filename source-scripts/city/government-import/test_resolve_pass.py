"""Native-surface acceptance must catch geometry missed by vertex-only diagnostics."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
spec=importlib.util.spec_from_file_location('resolve_pass',Path(__file__).with_name('resolve-pass.py'));resolve=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolve)

class CompleteNativeTests(unittest.TestCase):
    def test_triangle_centre_catches_native_spike(self):
        geometry={'position':[0,.05,0,6,.05,0,0,.05,6],'index':[0,1,2]}
        points,bottom=resolve.sample_points(geometry)
        peak=[2,3,2];a=[0,0,0];b=[6,0,0];c=[0,0,6]
        native=np.array([[a,b,peak],[b,c,peak],[c,a,peak]],dtype=float)
        corners=resolve.audit_native(np.array(geometry['position']).reshape(-1,3),bottom,native)
        complete=resolve.audit_native(points,bottom,native)
        self.assertTrue(corners['passed'])
        self.assertFalse(complete['passed'])
        self.assertIn('native-source-below-grade',complete['reasons'])
        self.assertLess(complete['gapRange'][0],-2)

    def test_missing_ground_is_not_accepted(self):
        result=resolve.audit_native(np.array([[20,.05,20],[1,.05,1]]),.05,np.array([[[0,0,0],[6,0,0],[0,0,6]]],dtype=float))
        self.assertFalse(result['passed']);self.assertEqual(result['covered'],1)
        self.assertIn('native-terrain-coverage',result['reasons'])

    def test_surveyed_model_elevations_are_not_changed(self):
        geometry={'position':[0,5,0,6,5,0,0,5,6],'index':[0,1,2]}
        points,bottom=resolve.sample_points(geometry)
        self.assertTrue(np.all(points[:,1]==5));self.assertEqual(bottom,5)
        self.assertTrue(any(np.allclose(p,[3,5,0]) for p in points))
        result=resolve.audit_native(points,bottom,np.array([[[0,0,0],[6,0,0],[0,0,6]]],dtype=float))
        self.assertFalse(result['passed']);self.assertIn('native-ground-contact',result['reasons'])

if __name__=='__main__':unittest.main()
