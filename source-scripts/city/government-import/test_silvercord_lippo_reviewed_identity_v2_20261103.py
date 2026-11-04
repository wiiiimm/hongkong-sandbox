import json
import unittest
from copy import deepcopy
from pathlib import Path
from silvercord_lippo_reviewed_identity_v2_20261103 import REVIEW, reviewed_proof

ROOT = Path(__file__).resolve().parents[3]
DECISIONS = json.loads((ROOT / 'docs/astra-city/government-import' / REVIEW / 'decisions.json').read_text())['decisions']


class ExactReviewedIdentityTests(unittest.TestCase):
    def test_both_authentic_reviews_accept_identity_only(self):
        for decision in DECISIONS:
            proof = reviewed_proof(decision['rawIdentityVerbatim'], decision)
            self.assertTrue(proof['identityAccepted'])
            self.assertEqual(proof['rawCurrentIdentity'], decision['rawIdentityVerbatim'])
            for key in ['physicalAccepted', 'placementApproved', 'collisionExemption', 'installationApproved', 'publication', 'providerObjectIdExact']:
                self.assertFalse(proof[key])

    def test_changed_current_source_route_cell_or_foreign_context_rejected(self):
        for key in ['sourceSHA256', 'worldTrianglesSHA256', 'originalOwnership', 'exactRouteTileHashes', 'geographicCell', 'exactCurrentComponentRoute', 'freshCurrentIdentity']:
            current = deepcopy(DECISIONS[0]['rawIdentityVerbatim']); current[key] = None
            with self.subTest(key=key), self.assertRaises(AssertionError):
                reviewed_proof(current, DECISIONS[0])

    def test_any_new_raw_failure_rejected(self):
        current = deepcopy(DECISIONS[0]['rawIdentityVerbatim']); current['reasons'].append('new-current-source-failure')
        with self.assertRaises(AssertionError): reviewed_proof(current, DECISIONS[0])

    def test_provider_revision_and_review_scope_cannot_be_relabelled(self):
        for key, value in [('providerObjectIdExact', True), ('foreignBoundaryUid', 'landsd/1:0'), ('currentProviderObjectId', 233997), ('physicalAccepted', True), ('sourceGeometryChanges', 1)]:
            decision = deepcopy(DECISIONS[0]); decision[key] = value
            with self.subTest(key=key), self.assertRaises(AssertionError):
                reviewed_proof(decision['rawIdentityVerbatim'], decision)

    def test_new_manifest_needs_fresh_ordinary_binding_without_transferring_review(self):
        decision = DECISIONS[0]; current = deepcopy(decision['rawIdentityVerbatim'])
        current['exactRouteManifestSHA256'] = 'a' * 64
        proof = reviewed_proof(current, decision)
        self.assertEqual(proof['exactRouteManifestSHA256'], 'a' * 64)
        self.assertFalse(proof['installationApproved'])


if __name__ == '__main__': unittest.main()
