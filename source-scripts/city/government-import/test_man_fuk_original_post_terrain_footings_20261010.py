"""Actual prior mesh and source mutations for a terrain-only proposal."""
import copy
import unittest
import numpy as np
from run import ROOT, HERE, read
from man_fuk_original_post_terrain_footings_20261010 import propose

OLD = 'government-xl-man-fuk-complete-retained-original-physical-v5-20261010'
PATCH = read(HERE / 'local' / OLD / 'government-native-266062-0.json')
ROW = read(ROOT / 'docs/astra-city/government-import' / OLD / 'selection.json.gz')['rows'][0]
RAW = (ROOT / ROW['candidate']['path']).read_bytes()


class TerrainOnlyActualInputs(unittest.TestCase):
    def test_actual_source_pins_and_local_changes(self):
        out, proof = propose(PATCH, RAW)
        self.assertEqual(out['nativeMesh']['index'], PATCH['nativeMesh']['index'])
        old = np.asarray(PATCH['nativeMesh']['position']).reshape(-1, 3)
        new = np.asarray(out['nativeMesh']['position']).reshape(-1, 3)
        self.assertTrue(np.array_equal(old[:, [0, 2]], new[:, [0, 2]]))
        self.assertTrue(np.array_equal(old[old[:, 0] >= 1950], new[old[:, 0] >= 1950]))
        self.assertEqual(proof['sourceGeometryChanges'], 0)
        self.assertFalse(proof['physicalAccepted'])
        self.assertFalse(proof['exactSameSurfaceClaim'])
        self.assertFalse(proof['rootCredit'])

    def test_caller_prior_terrain_not_mutated(self):
        old = copy.deepcopy(PATCH)
        propose(PATCH, RAW)
        self.assertEqual(old, PATCH)

    def test_changed_source_rejected(self):
        with self.assertRaises(AssertionError):
            propose(PATCH, RAW + b' ')

    def test_changed_unrelated_terrain_height_rejected(self):
        patch = copy.deepcopy(PATCH)
        patch['nativeMesh']['position'][1] += .001
        with self.assertRaises(AssertionError):
            propose(patch, RAW)

    def test_changed_horizontal_geometry_rejected(self):
        patch = copy.deepcopy(PATCH)
        patch['nativeMesh']['position'][0] += .001
        with self.assertRaises(AssertionError):
            propose(patch, RAW)

    def test_changed_terrain_connectivity_rejected(self):
        patch = copy.deepcopy(PATCH)
        patch['nativeMesh']['index'][0] = patch['nativeMesh']['index'][1]
        with self.assertRaises(AssertionError):
            propose(patch, RAW)


if __name__ == '__main__':
    unittest.main()
