from copy import deepcopy
import unittest
import numpy as np
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from original_endpoint_root_retry_grouped_v1_20261103 import retry_paths
from original_endpoint_root_retry_v1_20261102 import passed


class GroupedEndpointRetryTests(unittest.TestCase):
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


class BatchWorkTests(GroupedEndpointRetryTests):
    def test_many_targets_share_one_complete_original_graph(self):
        from unittest.mock import patch
        import original_endpoint_root_retry_grouped_v1_20261103 as tool
        anchors = [self.low, self.high]
        targets = [dict(self.target, witness=dict(self.target['witness'], sampleIndex=i)) for i in range(25)]
        old = attachment_paths(self.tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=anchors)
        with patch.object(tool, 'attachment_paths', wraps=attachment_paths) as kernel:
            rows, attempts = retry_paths(self.tri, old, anchors)
        self.assertTrue(all(passed(r) for r in rows))
        self.assertEqual(kernel.call_count, 1)
        self.assertEqual(len(attempts), 25)

    def test_disconnected_original_warning_remains_without_root_credit(self):
        tri = np.concatenate([self.tri, self.tri[:1] + [10, 0, 0]])
        targets = [self.target, dict(witness=dict(sampleIndex=1, position=[10,4.84,0]), incidentFaces=[2])]
        old = attachment_paths(tri, dict(targets=targets, proof=dict(contacts=[])), [], strict_anchors=[self.low, self.high])
        self.assertFalse(old[1]['hasUnrestrictedFiniteAttachment'])
        rows, attempts = retry_paths(tri, old, [self.low, self.high])
        self.assertTrue(passed(rows[0]))
        self.assertEqual(rows[1], old[1])
        self.assertFalse(passed(rows[1]))
        self.assertEqual({r['sampleIndex'] for r in attempts}, {0})


if __name__ == '__main__': unittest.main()
