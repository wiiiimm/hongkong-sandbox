"""Reject missing roots, fabricated floors and altered warning sets."""
import copy
import unittest
import numpy as np
from run import ROOT, read
from ying_hoi_native_wall_admission_v1_20261026 import verify_paths


class NativeFloorAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = ROOT / 'docs/astra-city/government-import'
        x = read(base / 'government-xl-after-ferry-ying-hoi-support-binding-v1-20261026/original/input.json.gz')
        r = x['rows'][0]
        cls.tri = np.asarray(r['position'], dtype='<f8').reshape(-1, 3)[np.asarray(r['index']).reshape(-1, 3)]
        cls.parent = np.asarray(x['podium'], dtype='<f8')
        cls.rim = read(base / 'government-xl-after-ferry-ying-hoi-strict-root-paths-v1-20261026/original.json.gz')
        cls.wall = read(base / 'government-xl-after-ferry-ying-hoi-wall-root-paths-v1-20261026/original.json.gz')

    def test_complete_original_floor_paths_replay(self):
        self.assertEqual(verify_paths(self.tri, self.parent, self.rim, self.wall)['replayedVerticalWallPaths'], 15)

    def test_missing_native_floor_anchor_rejected(self):
        changed = copy.deepcopy(self.rim)
        changed['canonicalStrictRoots'].pop()
        with self.assertRaises(AssertionError):
            verify_paths(self.tri, self.parent, changed, self.wall)

    def test_fabricated_provider_floor_rejected(self):
        changed = copy.deepcopy(self.rim)
        changed['canonicalStrictRoots'][0]['provider']['vertices'][0][1] += .01
        with self.assertRaises(AssertionError):
            verify_paths(self.tri, self.parent, changed, self.wall)

    def test_extra_unreviewed_negative_face_rejected(self):
        changed = copy.deepcopy(self.wall)
        changed['rawCapProof']['negativeSourceFaces'].append(100)
        with self.assertRaises(AssertionError):
            verify_paths(self.tri, self.parent, self.rim, changed)

    def test_claimed_path_above_height_limit_rejected(self):
        changed = copy.deepcopy(self.wall)
        changed['rows'][0]['riseAboveEndpointsM'] = .001
        with self.assertRaises(AssertionError):
            verify_paths(self.tri, self.parent, self.rim, changed)


if __name__ == '__main__':
    unittest.main()
