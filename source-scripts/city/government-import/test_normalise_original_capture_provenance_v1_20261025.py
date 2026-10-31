"""Reject forged compatibility claims without changing acceptance policy."""
from copy import deepcopy
import unittest
from normalise_original_capture_provenance_v1_20261025 import check_entry


class OriginalCaptureProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.canonical = dict(uid='landsd/1:0', sha256='source', triangles=7,
                              rootTranslation=[-834500, 0, 816500], asset='canonical.glb.gz')
        self.row = dict(uid='landsd/1:0', sourceSHA256='source', triangles=7,
                        candidate=dict(entry={**deepcopy(self.canonical), 'asset': 'cached.glb.gz'}),
                        native=dict(model=dict(asset=dict(sha256='source'), triangles=7)))

    def test_missing_flag_requires_canonical_entry(self):
        check_entry(self.row, self.canonical)

    def test_explicit_false_is_not_repaired(self):
        self.row['originalGeometryOnly'] = False
        with self.assertRaises(AssertionError):
            check_entry(self.row, self.canonical)

    def test_added_transform_or_approval_is_rejected(self):
        for key, value in [('scale', 2), ('rotation', [0, 1, 0]),
                           ('publicationApproved', True), ('placementReviewed', True)]:
            with self.subTest(key=key):
                row = deepcopy(self.row)
                row['candidate']['entry'][key] = value
                with self.assertRaises(AssertionError):
                    check_entry(row, self.canonical)

    def test_source_pose_change_is_rejected(self):
        self.row['candidate']['entry']['rootTranslation'][1] = 1
        with self.assertRaises(AssertionError):
            check_entry(self.row, self.canonical)

    def test_geometry_bindings_must_agree(self):
        for key, value in [('uid', 'landsd/2:0'), ('sourceSHA256', 'derived'), ('triangles', 8)]:
            with self.subTest(key=key):
                row = deepcopy(self.row)
                row[key] = value
                with self.assertRaises(AssertionError):
                    check_entry(row, self.canonical)

    def test_native_digest_cannot_be_substituted(self):
        self.row['native']['model']['asset']['sha256'] = 'derived'
        with self.assertRaises(AssertionError):
            check_entry(self.row, self.canonical)


if __name__ == '__main__':
    unittest.main()
