import unittest
import numpy as np
from source_closed_components import components, winding


def tetrahedron():
    vertices = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=float)
    return vertices[np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])]


class ExactClosedComponentDiagnostics(unittest.TestCase):
    def test_exact_closed_body_is_diagnostic_only(self):
        result = components(tetrahedron()); self.assertEqual(result['triangles'], 4)
        self.assertTrue(result['components'][0]['closedConsistentlyWound'])
        self.assertAlmostEqual(result['components'][0]['signedVolumeM3'], 1/6)
        self.assertFalse(result['components'][0]['selfIntersectionCertified'])
        self.assertFalse(result['supportApproved'])

    def test_missing_face_and_reversed_face_are_not_closed_solids(self):
        tri = tetrahedron()
        self.assertFalse(components(tri[:3])['components'][0]['closedConsistentlyWound'])
        tri[0] = tri[0, ::-1]
        result = components(tri)['components'][0]
        self.assertFalse(result['closedConsistentlyWound'])
        self.assertGreater(result['inconsistentWindingEdges'], 0)

    def test_original_open_and_degenerate_geometry_is_accounted_for(self):
        tri = np.concatenate([tetrahedron(), [[[10,0,0],[11,0,0],[10,1,0]]],
                              [[[20,0,0],[20,0,0],[20,0,0]]]])
        result = components(tri)
        self.assertEqual(sum(x['triangles'] for x in result['components']), 6)
        self.assertEqual(sum(x['closedConsistentlyWound'] for x in result['components']), 1)
        self.assertEqual(sum(x['degenerateTriangles'] for x in result['components']), 1)

    def test_duplicate_faces_make_nonmanifold_components(self):
        tri = tetrahedron(); result = components(np.concatenate([tri, tri[:1]]))
        self.assertFalse(result['components'][0]['closedConsistentlyWound'])
        self.assertGreater(result['components'][0]['nonManifoldEdges'], 0)

    def test_small_open_edges_are_never_snapped_closed(self):
        tri = tetrahedron(); tri[0, 0, 0] += 1e-9
        self.assertFalse(components(tri)['components'][0]['closedConsistentlyWound'])

    def test_winding_distinguishes_inside_outside_and_undefined_boundary(self):
        inside, outside, boundary = winding(tetrahedron(), [[.1,.1,.1],[2,2,2],[0,0,0]])
        self.assertAlmostEqual(inside, 1)
        self.assertAlmostEqual(outside, 0)
        self.assertIsNone(boundary)

    def test_nested_reverse_winding_preserves_cavity(self):
        tri = tetrahedron(); inner = (tri * .2 + .1)[:, ::-1]
        total = winding(np.concatenate([tri, inner]), [[.12,.12,.12]])[0]
        self.assertAlmostEqual(total, 0)

    def test_translation_preserves_volume_and_inputs(self):
        tri = tetrahedron() + [834500, 22, -816500]; before = tri.tobytes()
        self.assertAlmostEqual(components(tri)['components'][0]['signedVolumeM3'], 1/6)
        self.assertAlmostEqual(winding(tri, [[834500.1,22.1,-816499.9]])[0], 1)
        self.assertEqual(tri.tobytes(), before)

    def test_nonfinite_source_rejected(self):
        tri = tetrahedron(); tri[0,0,0] = np.nan
        with self.assertRaises(ValueError): components(tri)
        with self.assertRaises(ValueError): winding(tri, [[0,0,0]])


if __name__ == '__main__': unittest.main()
