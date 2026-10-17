import copy
import gzip
import hashlib
import json
import struct
import unittest

import numpy as np
from shapely.geometry import box
from government_owned_identity import geographic_cell, verify
from test_original_source_ownership import fixture as graph_fixture


def fixture():
    mid = 'B345001650001063C0'; csuid = '3450016500T20250101'
    graph = graph_fixture(); graph['nodes'][0]['name'] = mid
    graph['accessors'][1]['count'] = 6
    payload = json.dumps(graph).encode(); payload += b' ' * (-len(payload) % 4)
    raw = gzip.compress(struct.pack('<III', 0x46546c67, 2, 20 + len(payload)) +
                        struct.pack('<II', len(payload), 0x4e4f534a) + payload)
    sha = hashlib.sha256(raw).hexdigest()
    tri = np.array([[[-5, 5, -5], [5, 5, -5], [5, 5, 5]],
                    [[-5, 5, -5], [5, 5, 5], [-5, 5, 5]]], dtype=float)
    match = {'objectId': 1, 'buildingCSUID': csuid, 'uid': 'landsd/1:0',
             'overlapOfSmallerFootprint': 1, 'footprintCentroidDistanceMetres': 0}
    form = {'objectId': 1, 'buildingCSUID': csuid, 'structureType': 'Tower',
            'rings': [list(box(-4, -4, 4, 4).exterior.coords)]}
    row = {'uid': 'landsd/1:0', 'sourceSHA256': sha, 'modelId': mid, 'triangles': 2,
           'source': {'building': form}, 'native': {'model': {
               'modelId': mid, 'asset': {'sha256': sha}, 'worldBounds': [[-5, 5, -5], [5, 5, 5]],
               'matching': {key: [copy.deepcopy(match)] for key in ['officialCandidates', 'officialMatches', 'viewerMatches']}}}}
    context = {'sourceSHA256': sha, 'identity': {'exactObjectAndCSUID': True,
        'targetCoveredBySourceProjection': 1, 'sourceProjectionAreaM2': 100,
        'sourceProjectionInsideTarget': .64, 'sourceExcessMaximumDistanceFromTargetM': 2,
        'sourceExcessCoveredByUnrelatedFormsM2': 0}}
    return raw, row, context, tri


class GovernmentOwnedIdentity(unittest.TestCase):
    def test_cell_preserves_lost_fraction_and_northing_direction(self):
        cell = geographic_cell('B135792468001063C0', '1357924680T20100101', 'Tower')
        self.assertEqual(cell.bounds, (-20921, -8181, -20920, -8180))

    def test_owned_source_can_identify_a_roof_larger_than_the_base(self):
        result = verify(*fixture())
        self.assertTrue(result['passed'], result['reasons'])
        self.assertFalse(result['installationApproved'])

    def test_identifier_type_mismatch_fails(self):
        for mid, csuid, kind in [('B135792468002063C0', '1357924680T20100101', 'Tower'),
                                  ('B135792468001063C0', '1357924681T20100101', 'Tower'),
                                  ('B135792468001063C0', '1357924680T20100101', 'Unknown')]:
            with self.assertRaises(ValueError): geographic_cell(mid, csuid, kind)

    def test_shifted_source_cannot_borrow_identifier(self):
        raw, row, context, tri = fixture(); tri[:, :, 0] += 100
        result = verify(raw, row, context, tri)
        self.assertFalse(result['passed'])
        self.assertIn('original-world-pose-or-bounds', result['reasons'])
        self.assertIn('original-source-does-not-cover-whole-georef-cell', result['reasons'])

    def test_uncertain_cell_boundary_is_not_recovered_as_an_exact_point(self):
        raw, row, context, tri = fixture()
        row['source']['building']['rings'] = [list(box(.1, -4, 4, 4).exterior.coords)]
        self.assertIn('current-target-does-not-cover-whole-georef-cell', verify(raw, row, context, tri)['reasons'])

    def test_spatial_hazards_and_ambiguous_matches_remain_held(self):
        raw, row, context, tri = fixture()
        row['native']['model']['matching']['viewerMatches'] *= 2
        context['identity']['sourceExcessCoveredByUnrelatedFormsM2'] = 2
        context['identity']['sourceExcessMaximumDistanceFromTargetM'] = 11
        result = verify(raw, row, context, tri)
        for reason in ['unique-viewerMatches', 'full-source-unrelated-overlap', 'full-source-maximum-extent']:
            self.assertIn(reason, result['reasons'])

    def test_stale_projection_or_nonfinite_geometry_fails(self):
        raw, row, context, tri = fixture(); context['identity']['sourceProjectionAreaM2'] = 99
        self.assertIn('full-source-projection-evidence-differs', verify(raw, row, context, tri)['reasons'])
        tri[0, 0, 0] = np.nan
        self.assertIn('invalid-original-world-triangles', verify(raw, row, context, tri)['reasons'])


if __name__ == '__main__': unittest.main()
