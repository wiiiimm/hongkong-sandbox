import copy
import unittest
import numpy as np
from unchanged_low_parent_lineage_v1_20261029 import qualify


class LowLineageTests(unittest.TestCase):
    def setUp(self):
        self.before = np.array([[[0, -4, 0], [1, 3, 0], [0, 3, 1]],
                                [[1, 4, 0], [2, 4, 0], [1, 4, 1]]], dtype=float)
        self.after = self.before.copy()
        self.after[1, :, 1] = 3
        self.lineage = dict(changedParentFaces=[1], outputLineage=[
            dict(kind='unchanged', parentFace=0), dict(kind='original-inset-or-return', parentFace=1)])

    def test_unchanged_low_and_edited_high(self):
        self.assertTrue(qualify(self.before, self.after, self.lineage)['everyLowParentRetainedWholeExactlyOnce'])

    def test_low_coordinate_change_rejected(self):
        self.after[0, 0, 1] += 1e-9
        with self.assertRaises(AssertionError): qualify(self.before, self.after, self.lineage)

    def test_low_removal_rejected(self):
        with self.assertRaises(AssertionError): qualify(self.before, self.after[1:], dict(changedParentFaces=[1], outputLineage=self.lineage['outputLineage'][1:]))

    def test_low_duplication_rejected(self):
        rows = self.lineage['outputLineage'] + [self.lineage['outputLineage'][0]]
        with self.assertRaises(AssertionError): qualify(self.before, np.concatenate([self.after, self.after[:1]]), dict(changedParentFaces=[1], outputLineage=rows))

    def test_changed_low_parent_rejected(self):
        self.lineage['changedParentFaces'].append(0)
        with self.assertRaises(AssertionError): qualify(self.before, self.after, self.lineage)

    def test_new_below_clamp_rejected(self):
        self.after[1, 0, 1] = 1.1
        with self.assertRaises(AssertionError): qualify(self.before, self.after, self.lineage)

    def test_low_fragment_rejected(self):
        self.lineage['outputLineage'][0]['kind'] = 'parent-fragment'
        with self.assertRaises(AssertionError): qualify(self.before, self.after, self.lineage)

    def test_invalid_parent_rejected(self):
        self.lineage['outputLineage'][1]['parentFace'] = -1
        with self.assertRaises(AssertionError): qualify(self.before, self.after, self.lineage)


if __name__ == '__main__': unittest.main()
