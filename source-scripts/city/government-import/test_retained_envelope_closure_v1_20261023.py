import unittest
from retained_envelope_closure_v1_20261023 import closure


def node(url, box, packed=()):
    return dict(url=url, coarseBounds=box, packedBounds=list(packed))


class ClosureTests(unittest.TestCase):
    def test_transitive_dependency_and_order(self):
        nodes = [node('a', [0, 0, 2, 2]), node('b', [1, 1, 3, 3]), node('c', [2.5, 2.5, 4, 4])]
        expected = closure([0, 0, 1, 1], nodes)
        self.assertEqual(expected['requiredUrls'], ['a', 'b', 'c'])
        self.assertEqual(expected, closure([0, 0, 1, 1], list(reversed(nodes))))
        self.assertEqual(expected['bounds'], [0, 0, 4, 4])

    def test_shared_edge_and_point_are_not_positive_overlap(self):
        self.assertEqual(closure([0, 0, 1, 1], [node('edge', [1, 0, 2, 1]), node('point', [1, 1, 2, 2])])['requiredUrls'], [])

    def test_packed_child_can_add_dependency(self):
        result = closure([0, 0, 1, 1], [node('packed', [3, 3, 4, 4], [[.5, .5, 3, 3]])])
        self.assertEqual(result['requiredUrls'], ['packed'])
        self.assertEqual(result['bounds'], [0, 0, 4, 4])

    def test_ambiguous_duplicate_url_fails(self):
        with self.assertRaises(AssertionError):
            closure([0, 0, 1, 1], [node('a', [0, 0, 2, 2]), node('a', [3, 3, 4, 4])])


if __name__ == '__main__':
    unittest.main()
