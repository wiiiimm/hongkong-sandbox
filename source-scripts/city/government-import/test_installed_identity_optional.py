import unittest
from installed_identity_optional import supports_single_source_reuse


class LegacyReceiptShape(unittest.TestCase):
    def test_disneyland_batch_receipt_cannot_become_individual_approval(self):
        self.assertFalse(supports_single_source_reuse({
            'installedUids': ['landsd/169147:0', 'landsd/169148:0'],
            'evidenceHashes': {'catalogueSHA256': 'legacy'}, 'sourceGeometryPreserved': True}))

    def test_elements_assembly_receipt_cannot_become_individual_approval(self):
        self.assertFalse(supports_single_source_reuse({
            'primaryUid': 'landsd/273061:0', 'catalogueSHA256': 'legacy',
            'sourceModels': [{'uid': 'landsd/273061:0', 'sha256': 'source'}]}))

    def test_missing_binding_field_declines_reuse(self):
        complete = {'uid': 'landsd/1:0', 'sourceSHA256': 'source', 'catalogueSHA256': 'catalogue'}
        for key in complete:
            self.assertFalse(supports_single_source_reuse({k: v for k, v in complete.items() if k != key}))

    def test_supported_shape_still_requires_existing_strict_verifier(self):
        self.assertTrue(supports_single_source_reuse({
            'uid': 'landsd/1:0', 'sourceSHA256': 'source', 'catalogueSHA256': 'catalogue'}))
        for other in [None, [], 'legacy']:
            self.assertFalse(supports_single_source_reuse(other))


if __name__ == '__main__':
    unittest.main()
