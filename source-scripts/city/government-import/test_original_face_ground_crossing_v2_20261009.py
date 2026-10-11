import unittest
import numpy as np
import original_face_ground_crossing_v2_20261009 as module
from run import ROOT,read


class CoverageV2Tests(unittest.TestCase):
    def test_original_ground_union_avoids_fragment_seam(self):
        fixture=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context/coverage-fixture.json')
        r=module.face_ground_context(fixture['face'],fixture['ground'])
        self.assertFalse(r['clippedUnionCoverageDiagnostic'])
        self.assertTrue(r['groundProjectionCovered'])
        self.assertEqual(r['uncoveredProjectionLengthM'],0)
        self.assertEqual(r['uncoveredProjectionAreaM2'],0)
        self.assertAlmostEqual(r['minimum']['minimumGapM'],-2.682003974915725)

    def test_real_ground_hole_stays_uncovered(self):
        ground=np.array([[[0,0,-2],[3,0,-2],[0,0,2]]],float)
        r=module.face_ground_context([[-1,-1,0],[1,-1,0],[0,3,0]],ground)
        self.assertFalse(r['groundProjectionCovered'])
        self.assertGreater(r['uncoveredProjectionLengthM'],0)
        self.assertFalse(r['installationApproved'])


if __name__=='__main__':unittest.main()
