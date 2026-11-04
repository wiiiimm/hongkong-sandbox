from copy import deepcopy
import unittest
import numpy as np
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from original_endpoint_root_retry_v1_20261102 import retry_paths, passed


class EndpointRetryTests(unittest.TestCase):
    def setUp(self):
        self.tri = np.array([[[0,4,0],[0,8,0],[1,5.14,0]],
                             [[0,8,0],[1,5.14,0],[1,4,0]]], dtype=float)
        self.target = dict(witness=dict(sampleIndex=0, position=[0,4.84,0]), incidentFaces=[0])
        self.low = self.anchor([1,5.03,0], 1)
        self.high = self.anchor([0,5.98,0], 0)

    def anchor(self, point, face):
        return dict(position=point, supportHeight=point[1], gap=0,
                    strictAccepted=True, incidentFaces=[face])

    def initial(self, anchors):
        return attachment_paths(self.tri, dict(targets=[self.target], proof=dict(contacts=[])),
                                [], strict_anchors=anchors)

    def test_alternative_existing_endpoint_resolves_false_search_failure(self):
        anchors = [self.low, self.high]; old = self.initial(anchors)
        self.assertFalse(passed(old[0])); self.assertGreater(old[0]['riseAboveEndpointsM'], .1)
        tri = self.tri.copy(); frozen = deepcopy(old)
        rows, attempts = retry_paths(self.tri, old, anchors)
        self.assertTrue(passed(rows[0])); self.assertEqual(rows[0]['faces'], [0])
        self.assertEqual(len(attempts), 1); self.assertEqual(old, frozen)
        np.testing.assert_array_equal(self.tri, tri)

    def test_no_valid_alternative_keeps_failure(self):
        old = self.initial([self.low]); rows, _ = retry_paths(self.tri, old, [self.low])
        self.assertFalse(passed(rows[0])); self.assertEqual(rows, old)

    def test_passing_witness_is_reused_without_extra_search(self):
        old = self.initial([self.high]); rows, attempts = retry_paths(self.tri, old, [self.high])
        self.assertEqual(rows, old); self.assertEqual(attempts, [])

    def test_off_source_root_is_rejected(self):
        old = self.initial([self.low]); forged = self.anchor([0,5.98,1], 0)
        with self.assertRaises(AssertionError): retry_paths(self.tri, old, [forged])

    def test_strict_contact_interval_is_not_widened(self):
        old = self.initial([self.low]); forged = deepcopy(self.high)
        forged.update(supportHeight=forged['position'][1]-1.25, gap=1.25)
        with self.assertRaises(AssertionError): retry_paths(self.tri, old, [forged])


if __name__ == '__main__': unittest.main()
