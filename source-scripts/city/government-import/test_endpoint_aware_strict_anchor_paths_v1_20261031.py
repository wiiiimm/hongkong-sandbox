import copy
import unittest

import numpy as np

from endpoint_aware_strict_anchor_paths_v1_20261031 import choose_paths


class EndpointAwareAnchors(unittest.TestCase):
    def fixture(self, bottom=0., ridge=2., upper_root=None):
        tri = np.array([[[0., bottom, 0.], [1., ridge, 0.], [0., ridge, 1.]],
                        [[1., ridge, 0.], [0., ridge, 1.], [1., bottom, 1.]]])
        target = dict(witness=dict(position=tri[0, 0].tolist()), incidentFaces=[0])
        def anchor(point):
            return dict(position=point, supportHeight=point[1], gap=0.,
                        incidentFaces=[1], strictAccepted=True)
        upper = tri[1, 0].tolist() if upper_root is None else upper_root
        return tri, [target], [anchor(tri[1, 2].tolist()), anchor(upper)]

    def test_higher_verified_terminal_can_pass_exact_ceiling(self):
        tri, targets, anchors = self.fixture()
        result = choose_paths(tri, targets, anchors)
        self.assertFalse(result['baseline'][0]['passesExistingEndpointHeight'])
        self.assertTrue(result['selected'][0]['passesExistingEndpointHeight'])
        self.assertEqual(result['selected'][0]['riseAboveEndpointsM'], 0.)
        self.assertEqual(result['selected'][0]['terminal']['strictRoot'], anchors[1])

    def test_one_ulp_rise_is_not_forgiven_but_alternate_endpoint_is_real(self):
        bottom = 28.5
        tri, targets, anchors = self.fixture(bottom, np.nextafter(bottom, np.inf))
        result = choose_paths(tri, targets, anchors)
        self.assertGreater(result['baseline'][0]['riseAboveEndpointsM'], 0.)
        self.assertEqual(result['selected'][0]['riseAboveEndpointsM'], 0.)
        self.assertFalse(result['endpointToleranceChanged'])

    def test_genuine_bridge_above_all_endpoints_still_fails(self):
        tri, targets, anchors = self.fixture(0., 3., [1., 2., 1./3.])
        result = choose_paths(tri, targets, anchors)
        self.assertFalse(result['selected'][0]['passesExistingEndpointHeight'])
        self.assertEqual(result['remainingIndices'], [0])

    def test_no_anchor_does_not_create_support(self):
        tri, targets, _ = self.fixture()
        result = choose_paths(tri, targets, [])
        self.assertFalse(result['selected'][0]['hasUnrestrictedFiniteAttachment'])
        self.assertFalse(result['supportApproved'])

    def test_bad_anchor_is_rejected_even_when_another_can_pass(self):
        tri, targets, anchors = self.fixture()
        anchors.append(dict(anchors[1], gap=2., supportHeight=0.))
        with self.assertRaises(AssertionError):
            choose_paths(tri, targets, anchors)

    def test_inputs_unchanged(self):
        tri, targets, anchors = self.fixture()
        before = tri.copy(), copy.deepcopy(targets), copy.deepcopy(anchors)
        choose_paths(tri, targets, anchors)
        np.testing.assert_array_equal(tri, before[0])
        self.assertEqual(targets, before[1])
        self.assertEqual(anchors, before[2])


if __name__ == '__main__':
    unittest.main()
