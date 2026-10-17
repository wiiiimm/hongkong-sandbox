import unittest
from unittest.mock import patch as mock_patch
import numpy as np
import shapely
from rendered_patch_sampler import RenderedPatchSampler, clip_native_against_retained_facets, remove_coplanar_duplicates
import native_patch_resolution as patches


class Flat:
    def __init__(self, y): self.y = y
    def ground(self, x, z): return self.y


class RenderedPatchSamplerTest(unittest.TestCase):
    def sampler(self):
        patch = {'w': 2, 'h': 2, 'meta': {'georef':
            {'bE': 834500, 'bN': 816500, 'aE': 4, 'aN': -4}},
            'nativeMesh': {'position': [0, 2, 0, 4, 4, 0, 0, 2, 4], 'index': [0, 1, 2]}}
        return RenderedPatchSampler(patch, Flat(9), Flat(7))

    def test_vertical_retaining_face_does_not_block_height_sampling(self):
        value = {'w': 2, 'h': 2, 'meta': {'georef':
            {'bE': 834500, 'bN': 816500, 'aE': 4, 'aN': -4}},
            'nativeMesh': {'position': [0, 2, 0, 4, 4, 0, 0, 2, 4,
                                       1, 1, 0, 1, 8, 0, 1, 1, 4],
                           'index': list(range(6))}}
        s = RenderedPatchSampler(value, Flat(9), Flat(7))
        self.assertEqual(s.ground(1, 1), 2.5)
        self.assertEqual(s.ground(1, 3.5), 7)
        self.assertEqual(len(s.faces), 1)
        self.assertEqual(len(value['nativeMesh']['index']), 6)

    def test_original_plane_not_coarse_grid_is_sampled(self):
        s = self.sampler()
        self.assertEqual(s.ground(1, 1), 2.5)
        self.assertEqual(s.ground(3, 3), 7)  # Original TIN hole.
        self.assertEqual(s.ground(5, 5), 9)  # Outside the replaced patch.

    def test_preserved_faces_keep_native_slope_and_grid_hole(self):
        s = self.sampler()
        def grid(sampler, region):
            return [[[x, sampler.ground(x, z), z] for x, z in list(t.exterior.coords)[:3]]
                    for t in patches._triangles(region)]
        with mock_patch.object(patches, 'grid_surface_faces', side_effect=grid):
            faces = np.asarray(s.surface_faces(shapely.box(0, 0, 4, 4)))
        polygons = shapely.polygons(faces[:, :, [0, 2]])
        self.assertAlmostEqual(shapely.union_all(polygons).area, 16)
        for face, polygon in zip(faces, polygons):
            p = polygon.centroid
            expected = 2 + p.x / 2 if p.x + p.y < 4 else 7
            self.assertAlmostEqual(s.height(face, p.x, p.y), expected)

    def test_highest_existing_facet_wins(self):
        s = self.sampler()
        upper = s.faces[0].copy(); upper[:, 1] += 3
        s.faces = np.concatenate((s.faces, [upper]))
        s.polygons = shapely.polygons(s.faces[:, :, [0, 2]])
        s.tree = shapely.STRtree(s.polygons)
        self.assertEqual(s.ground(1, 1), 5.5)

    def test_mixed_overlap_clipped_without_changing_retained_plane(self):
        # A 2m2 duplicate must be removed by clipping, not accepted by a larger cap.
        old = np.array([[0, 3, 0], [2, 4, 0], [0, 3, 2]], dtype=float)
        new = np.array([[0, 1, 0], [4, 3, 0], [0, 1, 4]], dtype=float)
        value = {'nativeMesh': {'position': np.concatenate((new, old)).reshape(-1).tolist(),
                                'index': list(range(6))}}
        proof = clip_native_against_retained_facets(value, 1)
        self.assertLessEqual(proof['mixedOverlapAfterM2'], .25)
        faces = patches._faces(value)
        np.testing.assert_array_equal(faces[-1], old)
        for face in faces[:-1]:
            np.testing.assert_allclose(face[:, 1], 1 + face[:, 0] / 2)

    def test_disjoint_retained_projection_does_not_rewrite_source(self):
        value = {'nativeMesh': {'position': [0, 1, 0, 1, 1, 0, 0, 1, 1,
                                             2, 2, 2, 3, 2, 2, 2, 2, 3], 'index': list(range(6))}}
        before = repr(value)
        proof = clip_native_against_retained_facets(value, 1)
        self.assertEqual(proof['passes'], []); self.assertEqual(repr(value), before)

    def test_duplicate_coplanar_surface_removed_with_height_and_coverage_preserved(self):
        face = [0, 3, 0, 4, 5, 0, 0, 3, 4]
        value = {'nativeMesh': {'position': face + face, 'index': list(range(6))}}
        proof = remove_coplanar_duplicates(value)
        self.assertEqual(len(proof['passes']), 1)
        faces = patches._faces(value)
        self.assertEqual(len(faces), 1)
        np.testing.assert_array_equal(faces[0], np.asarray(face).reshape(3, 3))

    def test_crossing_or_different_height_surfaces_remain_untouched(self):
        for upper in ([0, 5, 0, 4, 5, 0, 0, 5, 4],
                      [0, 2, 0, 4, 6, 0, 0, 4, 4]):
            value = {'nativeMesh': {'position': [0, 4, 0, 4, 4, 0, 0, 4, 4] + upper,
                                    'index': list(range(6))}}
            before = repr(value)
            self.assertEqual(remove_coplanar_duplicates(value)['passes'], [])
            self.assertEqual(repr(value), before)


if __name__ == '__main__': unittest.main()
