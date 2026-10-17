import copy
import hashlib
import unittest
import numpy as np
from exact_original_wall_contact_paths_20261009 import contact_paths
from unchanged_closed_column_role_v2_20261009 import canonical_sha
from verified_original_graph_cache_20261009 import envelope, replay


def packet(tri=None):
    t = np.asarray([[[0, -1, 0], [1, 1, 0], [0, 1, 0]],
                    [[0, 1, 0], [2, 1, 2], [2, 1, 0]]] if tri is None else tri, float)
    c = [{'sourceFace': i, 'groundProjectionCovered': True,
          'minimum': {'minimumGapM': -1 if i == 0 else 1}} for i in range(2)]
    b = {'sourceSHA256': 'source', 'positionTriangleStreamSHA256': 'position',
         'normalTriangleStreamSHA256': 'normal', 'colourTriangleStreamSHA256': 'colour',
         'rootMatrix': [1], 'drawnGroundSHA256': 'ground',
         'decodedWorldTrianglesSHA256': hashlib.sha256(t.tobytes()).hexdigest(),
         'continuousFaceContextsSHA256': canonical_sha(c), 'currentForeignScopeSHA256': 'old'}
    g = contact_paths(t, c, [0], expected_source_binding=b, current_source_binding=b)
    e = envelope(t, c, [0], b, g)
    r = {'stage': 'immutable-original-contact-graph-cache-v1', 'jobId': 'verified-job',
         'graphArtifact': {'sha256': 'bytes'}, 'sourceOnlyKeySHA256': e['sourceOnlyKeySHA256'],
         'sourceGeometryChanges': 0, 'installationApproved': False}
    return t, c, b, e, r


def check(p, actual=None):
    t, c, b, e, r = p
    return replay(t, c, [0], b, e, immutable_complete_result=('complete', r) if actual is None else actual,
                  expected_result=r, artifact_sha256='bytes')


class CacheReplayTests(unittest.TestCase):
    def test_exact_original_contact_recomputed_and_current_scope_not_reused(self):
        p = packet(); p[2]['currentForeignScopeSHA256'] = 'fresh'
        r = check(p)
        self.assertTrue(r['allAffectedHaveExactContactRoofPaths'])
        self.assertEqual(r['sourceBinding']['currentForeignScopeSHA256'], 'fresh')
        self.assertEqual(r['verifiedSourceOnlyCacheReplay']['creditedOriginalPathContactsRecomputed'], [[0, 1]])
        self.assertFalse(r['verifiedSourceOnlyCacheReplay']['currentPhysicalAcceptanceReused'])
    def test_unfenced_or_failed_job_rejects(self):
        p = packet()
        for actual in [None, ('failed', p[4]), ('running', p[4]), ('complete', {**p[4], 'jobId': 'other'})]:
            with self.assertRaises(AssertionError): check(p, actual=actual if actual is not None else ('complete', None))
    def test_source_attributes_root_and_ground_changes_reject(self):
        for key in ['sourceSHA256', 'positionTriangleStreamSHA256', 'normalTriangleStreamSHA256',
                    'colourTriangleStreamSHA256', 'rootMatrix', 'drawnGroundSHA256']:
            p = packet(); p[2][key] = ['changed'] if key == 'rootMatrix' else 'changed'
            with self.assertRaises(AssertionError): check(p)
    def test_changed_world_even_with_updated_hash_rejects(self):
        p = packet(); p[0][:, :, 0] += 1; p[2]['decodedWorldTrianglesSHA256'] = hashlib.sha256(p[0].tobytes()).hexdigest()
        with self.assertRaises(AssertionError): check(p)
    def test_changed_complete_context_even_with_updated_hash_rejects(self):
        p = packet(); p[1][1]['minimum']['minimumGapM'] = .2; p[2]['continuousFaceContextsSHA256'] = canonical_sha(p[1])
        with self.assertRaises(AssertionError): check(p)
    def test_missing_ground_or_original_face_rejects(self):
        for mutate in [lambda p: p[1][0].update(groundProjectionCovered=False), lambda p: p[1].pop()]:
            p = packet(); mutate(p); p[2]['continuousFaceContextsSHA256'] = canonical_sha(p[1])
            with self.assertRaises(AssertionError): check(p)
    def test_changed_affected_face_set_rejects(self):
        p = packet(); p[1][1]['minimum']['minimumGapM'] = -1; p[2]['continuousFaceContextsSHA256'] = canonical_sha(p[1])
        with self.assertRaises(AssertionError): check(p)
    def test_changed_kernel_or_artifact_receipt_rejects(self):
        p = packet(); p[3]['sourceOnlyKey']['exactGraphKernelSHA256'] = 'changed'
        with self.assertRaises(AssertionError): check(p)
        p = packet(); p[4]['graphArtifact']['sha256'] = 'changed'
        with self.assertRaises(AssertionError): check(p)
    def test_omitted_inventory_or_changed_eligible_roof_rejects(self):
        for key, value in [('completeOriginalFaceInventory', [0]), ('clearOriginalRoofFaces', []), ('eligibleWallFaces', [])]:
            p = packet(); p[3]['computedOriginalGraph'][key] = value
            with self.assertRaises(AssertionError): check(p)
    def test_fabricated_cycle_or_incomplete_path_rejects(self):
        for path in [[0, 0, 1], [1], [0]]:
            p = packet(); p[3]['computedOriginalGraph']['paths'][0]['originalWallContactRoofPath'] = path
            with self.assertRaises(AssertionError): check(p)
    def test_vertex_only_claimed_contact_recomputed_and_rejected(self):
        p = packet([[[0, -1, 0], [1, 1, 0], [0, 1, 0]],
                    [[1, 1, 0], [2, 1, 2], [2, 1, 0]]])
        g = p[3]['computedOriginalGraph']; g['paths'][0].update(originalWallContactRoofPath=[0, 1], hasExactPositiveDimensionPathToClearRoof=True)
        g['allAffectedHaveExactContactRoofPaths'] = True
        with self.assertRaisesRegex(AssertionError, 'vertex-only'): check(p)
    def test_tiny_real_gap_claimed_contact_recomputed_and_rejected(self):
        p = packet([[[0, -1, 0], [1, 1, 0], [0, 1, 0]],
                    [[0, 1+1e-10, 0], [2, 1+1e-10, 2], [2, 1+1e-10, 0]]])
        g = p[3]['computedOriginalGraph']; g['paths'][0].update(originalWallContactRoofPath=[0, 1], hasExactPositiveDimensionPathToClearRoof=True)
        g['allAffectedHaveExactContactRoofPaths'] = True
        with self.assertRaisesRegex(AssertionError, 'detached'): check(p)


if __name__ == '__main__': unittest.main()
