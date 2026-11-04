import copy
import unittest
from routed_original_cell_identity import verify
from test_government_georef_cell_identity import fixture


def args():
    raw, row, context, tri, current = fixture()
    row['source']['building']['uid'] = row['uid']
    for key in ('officialMatches', 'viewerMatches'):
        row['native']['model']['matching'][key] = []
    return [raw, row, context, tri, current, [copy.deepcopy(row['source'])]]


def check(a):
    return verify(*a[:4], current_identity=a[4], sources=a[5])


class RoutedOriginalIdentity(unittest.TestCase):
    def test_empty_shape_matches_use_actual_unique_component_not_fake_matches(self):
        a = args(); before = copy.deepcopy(a[1]['native'])
        r = check(a)
        self.assertTrue(r['passed'], r['reasons'])
        self.assertEqual(a[1]['native'], before)
        self.assertEqual(r['emptyCachedShapeMatchesReplaced'], ['unique-officialMatches', 'unique-viewerMatches'])
        self.assertIn('unique-viewerMatches', r['rawNativeIdentityReasons'])
        self.assertFalse(r['installationApproved'])

    def test_duplicate_current_parts_are_not_identity(self):
        a = args(); other = copy.deepcopy(a[5][0]); other['building']['uid'] = 'landsd/1:1'; a[5].append(other)
        self.assertFalse(check(a)['passed'])

    def test_multiple_original_records_are_not_disambiguated(self):
        a = args(); a[1]['native']['model']['matching']['officialCandidates'] *= 2
        self.assertFalse(check(a)['passed'])

    def test_nonempty_wrong_or_ambiguous_viewer_matches_remain_failed(self):
        for duplicate in (False, True):
            a = args(); match = copy.deepcopy(a[1]['native']['model']['matching']['officialCandidates'][0]); match['uid'] = 'landsd/2:0'
            a[1]['native']['model']['matching']['viewerMatches'] = [match] * (2 if duplicate else 1)
            self.assertFalse(check(a)['passed'])

    def test_wrong_official_identifier_does_not_borrow_current_route(self):
        a = args(); a[1]['native']['model']['matching']['officialCandidates'][0]['objectId'] = 9
        self.assertFalse(check(a)['passed'])

    def test_all_current_spatial_guards_remain(self):
        for k, v in [('targetCoveredBySourceProjection', .94), ('sourceExcessMaximumDistanceFromTargetM', 10.1), ('sourceExcessCoveredByUnrelatedFormsM2', 1.1)]:
            a = args(); a[2]['identity'][k] = a[4][k] = v
            self.assertFalse(check(a)['passed'])

    def test_original_bytes_pose_and_whole_cell_remain_required(self):
        a = args(); a[1]['sourceSHA256'] = '0' * 64; self.assertFalse(check(a)['passed'])
        a = args(); a[3][:, :, 0] += 100; self.assertFalse(check(a)['passed'])
        a = args(); a[1]['source']['building']['rings'][0] = [[.1,-4],[4,-4],[4,4],[.1,4],[.1,-4]]; a[5] = [copy.deepcopy(a[1]['source'])]
        self.assertFalse(check(a)['passed'])

if __name__ == '__main__': unittest.main()
