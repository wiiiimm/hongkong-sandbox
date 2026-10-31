import unittest
import numpy as np
from source_sections import horizontal_section


def walls(x0=0, x1=2, z0=0, z1=3, base=0, top=10):
    ring = [(x0,z0), (x1,z0), (x1,z1), (x0,z1)]
    faces = []
    for a, b in zip(ring, ring[1:]+ring[:1]):
        aa, ab = [a[0],base,a[1]], [a[0],top,a[1]]
        ba, bb = [b[0],base,b[1]], [b[0],top,b[1]]
        faces += [[aa,ba,bb], [aa,bb,ab]]
    return np.array(faces,dtype=float)


class Sections(unittest.TestCase):
    def test_closed_walls_and_reversed_winding(self):
        for tri in [walls(), walls()[:,::-1]]:
            p, r = horizontal_section(tri, 4.123456789)
            self.assertAlmostEqual(p.area, 6)
            self.assertTrue(r['completeClosedLinework'])

    def test_open_wall_is_not_closed(self):
        p, r = horizontal_section(walls()[:-2], 5)
        self.assertEqual(p.area, 0)
        self.assertFalse(r['completeClosedLinework'])
        self.assertGreater(r['danglingEdges'], 0)

    def test_disconnected_and_nested_parts_are_explicit(self):
        p, r = horizontal_section(np.concatenate([walls(), walls(10,12,0,3), walls(.5,1.5,1,2)]), 5)
        self.assertAlmostEqual(p.area,12)
        self.assertEqual(r['closedPolygonFaces'],3)

    def test_duplicate_faces_do_not_duplicate_area(self):
        p,r=horizontal_section(np.concatenate([walls(),walls()]),5)
        self.assertAlmostEqual(p.area,6)
        self.assertEqual(r['uniqueSegments'],8)

    def test_coplanar_and_outside_levels(self):
        tri = np.concatenate([walls(), [[[0,5,0],[2,5,0],[0,5,3]]]])
        _,r=horizontal_section(tri,5)
        self.assertEqual(r['coplanarTriangles'],1)
        self.assertFalse(r['completeClosedLinework'])
        p,r=horizontal_section(walls(),11)
        self.assertTrue(p.is_empty)
        self.assertFalse(r['completeClosedLinework'])

    def test_nearby_unconnected_edges_are_not_snapped(self):
        tri=walls();tri[-2:,:,0] += 1e-8
        _,r=horizontal_section(tri,5)
        self.assertFalse(r['completeClosedLinework'])

    def test_invalid_input(self):
        for tri,h in [(np.full((1,3,3),np.nan),5),(walls(),float('nan'))]:
            with self.assertRaises(ValueError):horizontal_section(tri,h)


if __name__=='__main__':unittest.main()
