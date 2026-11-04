import unittest
from exact_terrain_contact_20261009 import continuous_contact


class ExactTerrainContactTests(unittest.TestCase):
    def test_interior_ridge_contact_is_not_vertex_contact(self):
        source = [[[0, 1, 0], [10, 1, 0], [0, 1, 10]]]
        terrain = [[[0, 0, 0], [10, 0, 0], [2, 1, 2]],
                   [[10, 0, 0], [0, 0, 10], [2, 1, 2]],
                   [[0, 0, 10], [0, 0, 0], [2, 1, 2]]]
        result = continuous_contact(source, terrain, bottom=1)
        self.assertEqual(result['minimum']['gapM'], 0)
        self.assertEqual(result['minimum']['position'], [2, 1, 2])
        self.assertEqual(result['maximumAtIntersectionVertices']['gapM'], 1)
        self.assertFalse(result['completeLowRimProof'])

    def test_floating_source_does_not_gain_contact(self):
        source = [[[0, 1, 0], [10, 1, 0], [0, 1, 10]]]
        ground = [[[0, 0, 0], [10, 0, 0], [0, 0, 10]]]
        self.assertEqual(continuous_contact(source, ground, bottom=1)['minimum']['gapM'], 1)

    def test_lower_layer_cannot_hide_upper_burial(self):
        source = [[[0, 1, 0], [10, 1, 0], [0, 1, 10]]]
        ground = [[[0, 1, 0], [10, 1, 0], [0, 1, 10]],
                  [[0, 2, 0], [10, 2, 0], [0, 2, 10]]]
        self.assertEqual(continuous_contact(source, ground, bottom=1)['minimum']['gapM'], -1)

    def test_band_clip_keeps_original_plane(self):
        source = [[[0, 0, 0], [10, 10, 0], [0, 0, 10]]]
        ground = [[[0, 0, 0], [10, 0, 0], [0, 0, 10]]]
        result = continuous_contact(source, ground, bottom=0, band=.35)
        self.assertAlmostEqual(result['maximumAtIntersectionVertices']['gapM'], .35)

    def test_crossing_planes_maximum_not_falsely_certified(self):
        source = [[[0,1,0], [2,1,0], [0,1,2]]]
        ground = [[[0,0,0], [2,2,0], [0,0,2]],
                  [[0,2,0], [2,0,0], [0,2,2]]]
        result = continuous_contact(source, ground, bottom=1)
        self.assertEqual(result['minimum']['gapM'], -1)
        self.assertEqual(result['maximumAtIntersectionVertices']['gapM'], -1)
        # True maximum is 0 on x=1; this diagnostic does not partition it.
        self.assertFalse(result['continuousMaximumCertified'])

    def test_infinite_band_rejected(self):
        with self.assertRaises(AssertionError):
            continuous_contact([[[0,0,0],[1,0,0],[0,0,1]]],
                               [[[0,0,0],[1,0,0],[0,0,1]]], bottom=0, band=float('inf'))

    def test_nonfinite_rejected(self):
        with self.assertRaises(AssertionError):
            continuous_contact([[[0,float('nan'),0],[1,0,0],[0,0,1]]],
                               [[[0,0,0],[1,0,0],[0,0,1]]], bottom=0)


if __name__ == '__main__':
    unittest.main()
