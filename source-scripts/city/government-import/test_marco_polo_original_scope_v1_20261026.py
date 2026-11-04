import copy
import json
from pathlib import Path
import unittest
from marco_polo_original_scope_v1_20261026 import SOURCES, verify_entry, verify_review

BASE = Path(__file__).resolve().parents[3] / 'docs/astra-city/government-import'


class MarcoPoloScope(unittest.TestCase):
    def setUp(self):
        local = Path(__file__).parent / 'local/government-xl-after-dragon-next-five-marco-polo-private-native-preview-v1-20261026/catalogue.json'
        self.entry = json.loads(local.read_text())['models'][0]
        self.review = json.loads((BASE / 'government-xl-after-dragon-next-five-marco-polo-source-review-v1-20261026/ROOT-SOURCE-REVIEW.json').read_text())

    def test_exact_original_and_complete_review(self):
        self.assertTrue(verify_entry(self.entry, SOURCES))
        self.assertTrue(verify_review(self.review))

    def test_other_sources_cannot_reuse_admission(self):
        for change in [{'uid': 'landsd/93417:0'}, {'sha256': '0'*64}, {'triangles': 10431}, {'verticalPlacementOffsetHKPD': 1}]:
            with self.subTest(change=change), self.assertRaises(AssertionError):
                verify_entry({**self.entry, **change}, SOURCES)

    def test_no_dependencies_suppression_or_partial_geometry(self):
        for key in ['supportDependencies', 'retainedBasicSupportDependencies', 'suppressesBuildingUids', 'partialSource', 'renderGroups']:
            with self.subTest(key=key), self.assertRaises(AssertionError):
                verify_entry({**self.entry, key: ['landsd/123:0']}, SOURCES)

    def test_missing_native_mode_is_rejected(self):
        bad = copy.deepcopy(self.review); bad['rawNativeContacts'][0]['modes'].pop()
        with self.assertRaises(AssertionError): verify_review(bad)

    def test_raw_crossings_cannot_be_zeroed(self):
        bad = copy.deepcopy(self.review)
        row = next(r for r in bad['rawNativeContacts'] if r['nativeUid'] == 'landsd/205767:0')
        row['modes'][0]['finiteContactPairs'] = 0
        with self.assertRaises(AssertionError): verify_review(bad)

    def test_native_metadata_cannot_be_relabelled(self):
        bad = copy.deepcopy(self.review); bad['rawNativeContacts'][0]['rawCurrentNativeEntry']['publicationApproved'] = False
        with self.assertRaises(AssertionError): verify_review(bad)

    def test_missing_retained_image_or_form_is_rejected(self):
        for key in ['retainedImagesActuallyViewed', 'leaseResources']:
            bad = copy.deepcopy(self.review); bad[key].pop()
            with self.subTest(key=key), self.assertRaises(AssertionError): verify_review(bad)


if __name__ == '__main__':
    unittest.main()
