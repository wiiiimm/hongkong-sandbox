import unittest
import numpy as np
from exact_mesh_components import face_components


class ExactComponents(unittest.TestCase):
    def test_transitive_shared_vertices_and_disconnected_face(self):
        faces = np.array([[[0,0,0],[1,0,0],[0,1,0]],
                          [[1,0,0],[2,0,0],[2,1,0]],
                          [[2,1,0],[3,1,0],[3,2,0]],
                          [[10,0,0],[11,0,0],[10,1,0]]], dtype=float)
        self.assertEqual([g.tolist() for g in face_components(faces)], [[0,1,2],[3]])

    def test_close_vertices_are_not_snapped(self):
        faces = np.array([[[0,0,0],[1,0,0],[0,1,0]],
                          [[0,0,.000001],[1,0,.000001],[0,1,.000001]]])
        self.assertEqual([g.tolist() for g in face_components(faces)], [[0],[1]])

    def test_nonfinite_geometry_rejected(self):
        with self.assertRaises(ValueError):
            face_components(np.full((1,3,3), np.nan))

    def test_empty_input(self):
        self.assertEqual(face_components(np.empty((0,3,3))), [])


if __name__ == '__main__': unittest.main()
