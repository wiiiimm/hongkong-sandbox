import copy
import unittest
import numpy as np
from government_georef_cell_identity import verify
from test_government_owned_identity import fixture as old_fixture


def fixture():
    raw, row, context, tri = old_fixture()
    context['identity']['target'] = {'uid': row['uid'], 'objectId': 1}
    context['identity']['targetIntersectionAreaM2'] = 64
    return raw, row, context, tri, copy.deepcopy(context['identity'])


def check(raw, row, context, tri, current):
    return verify(raw, row, context, tri, current_identity=current)


class CompleteGeorefIdentity(unittest.TestCase):
    def test_cached_shape_proxies_are_explicit_diagnostics_only(self):
        args = fixture(); row = args[1]
        for values in row['native']['model']['matching'].values():
            values[0]['footprintCentroidDistanceMetres'] = 4
            values[0]['overlapOfSmallerFootprint'] = .96
        result = check(*args)
        self.assertTrue(result['passed'], result['reasons'])
        self.assertEqual(len(result['cachedShapeProxyReasonsReplaced']), 3)
        self.assertFalse(result['originalOwnership']['provenanceAndSpatialDiagnosticPassed'])
        self.assertFalse(result['installationApproved'])

    def test_unique_identifier_is_still_mandatory(self):
        args = fixture(); args[1]['native']['model']['matching']['viewerMatches'] *= 2
        self.assertIn('unique-viewerMatches', check(*args)['reasons'])

    def test_wrong_exact_object_and_csuid_still_fail(self):
        for field, value in [('objectId', 2), ('buildingCSUID', '3450016501T20250101')]:
            args = fixture(); args[1]['native']['model']['matching']['viewerMatches'][0][field] = value
            self.assertIn('exact-viewerMatches', check(*args)['reasons'])

    def test_corrupt_cached_values_cannot_be_replaced(self):
        for field, value in [('footprintCentroidDistanceMetres', float('nan')),
                             ('footprintCentroidDistanceMetres', -1),
                             ('overlapOfSmallerFootprint', 1.2),
                             ('overlapOfSmallerFootprint', None)]:
            args = fixture(); args[1]['native']['model']['matching']['viewerMatches'][0][field] = value
            self.assertIn('malformed-cached-spatial-viewerMatches', check(*args)['reasons'])

    def test_current_geometry_cannot_borrow_stale_context(self):
        args = fixture(); args[4]['sourceProjectionAreaM2'] = 101
        self.assertIn('fresh-current-identity-differs:sourceProjectionAreaM2', check(*args)['reasons'])

    def test_every_fresh_projection_bound_remains(self):
        for field, value in [('targetCoveredBySourceProjection', .94),
                             ('sourceExcessMaximumDistanceFromTargetM', 10.01),
                             ('sourceExcessCoveredByUnrelatedFormsM2', 1.01)]:
            args = fixture(); args[2]['identity'][field] = args[4][field] = value
            self.assertIn('fresh-current-spatial-bound:'+field, check(*args)['reasons'])

    def test_geo_cell_cannot_be_replaced_with_centroid_or_point(self):
        args = fixture(); args[1]['source']['building']['rings'][0] = [[.1,-4],[4,-4],[4,4],[.1,4],[.1,-4]]
        self.assertIn('current-target-does-not-cover-whole-georef-cell', check(*args)['reasons'])

    def test_wrong_world_pose_and_nonfinite_geometry_still_fail(self):
        args = fixture(); args[3][:,:,0] += 100
        self.assertIn('original-world-pose-or-bounds', check(*args)['reasons'])
        args = fixture(); args[3][0,0,0] = np.nan
        self.assertIn('invalid-original-world-triangles', check(*args)['reasons'])

    def test_fresh_target_and_exact_join_must_agree(self):
        args = fixture(); args[4]['target'] = {'uid': 'landsd/2:0', 'objectId': 2}
        args[4]['exactObjectAndCSUID'] = False
        result = check(*args)
        self.assertIn('fresh-current-identity-differs:target', result['reasons'])
        self.assertIn('fresh-current-exact-object-csuid', result['reasons'])

    def test_original_bytes_are_still_hash_checked(self):
        args = fixture(); args[1]['sourceSHA256'] = '0'*64
        self.assertIn('original-byte-integrity', check(*args)['reasons'])


if __name__ == '__main__': unittest.main()
