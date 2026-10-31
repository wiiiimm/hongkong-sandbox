"""Hermetic actual-source proposal counterexamples; no mocked current approval."""
from copy import deepcopy
from functools import lru_cache
import unittest
import numpy as np
import shapely
from run import ROOT, read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from king_cheung_complete_ancillary_proposal_20261011 import proposal, spatial_metrics, ROLE_IDS
BASE = ROOT / 'docs/astra-city/government-import'
@lru_cache(None)
def fixture():
    raw = BASE / 'government-xl-king-cheung-95691-current-original-identity-v1-20261011'
    row = read(raw / 'selection.json.gz')['rows'][0]
    return [read(raw / 'identity.json'), row, decode_original_world_triangles((ROOT / row['candidate']['path']).read_bytes()),
            read(raw / 'complete-current-forms.json.gz')['rows'],
            read(BASE / 'government-xl-king-cheung-95691-primary-relations-v1-20261011/exact-current-one-primary.json'),
            read(BASE / 'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011/diagnostic.json.gz')['completeTopology'],
            read(BASE / 'government-xl-king-cheung-95691-complete-low-parts-contacts-v1-20261011/diagnostic.json.gz')]
class ActualOriginalCounterexamples(unittest.TestCase):
    def reject(self, mutate):
        f = deepcopy(fixture()); mutate(f)
        with self.assertRaises(AssertionError): proposal(*f)
    def test_complete_proposal_preserves_all_faces_and_no_acceptance(self):
        r = proposal(*fixture())
        self.assertEqual((r['completeFaces'], len(r['proposedAncillaryFaceIds']), r['ordinaryExtentFaces']), (18742, 104, 18638))
        self.assertTrue(r['proposalSpatialGuardsSatisfied'])
        for key in ['identityAccepted', 'currentAcceptance', 'physicalAccepted', 'installationApproved', 'planRegistrationAccepted', 'canopyToMainBodyContactAccepted']: self.assertFalse(r[key])
    def test_changed_source_vertex(self): self.reject(lambda f: f[2].__setitem__((0, 0, 1), f[2][0, 0, 1] + .01))
    def test_missing_source_face(self): self.reject(lambda f: f.__setitem__(2, f[2][:-1]))
    def test_changed_source_uid(self): self.reject(lambda f: f[1].__setitem__('uid', 'landsd/1:0'))
    def test_changed_source_model(self): self.reject(lambda f: f[1].__setitem__('modelId', 'another-root'))
    def test_changed_source_sha(self): self.reject(lambda f: f[1].__setitem__('sourceSHA256', '0' * 64))
    def test_raw_unknown_failure(self): self.reject(lambda f: f[0]['reasons'].append('unknown'))
    def test_unverified_scene_ownership(self): self.reject(lambda f: f[0]['originalOwnership'].__setitem__('sourceGraphVerified', False))
    def test_failed_whole_georef_cell(self): self.reject(lambda f: f[0]['exactWholeCellCoverage'].__setitem__('covered', False))
    def test_omitted_role_face(self): self.reject(lambda f: f[5]['sharedEdgeConnectedComponents'][39].pop())
    def test_added_unrelated_role_face(self): self.reject(lambda f: f[5]['sharedEdgeConnectedComponents'][39].append(0))
    def test_omitted_low_complete_face(self): self.reject(lambda f: f[6]['completeLowParts'][0]['completeOriginalFaceIds'].pop())
    def test_invented_isolated_post_contact(self): self.reject(lambda f: f[6]['completeLowParts'][1]['contacts']['contacts'].append({'otherRealComponent': 23, 'dimension': 1}))
    def test_relabelled_contact_to_main(self): self.reject(lambda f: f[6]['completeLowParts'][0]['contacts']['contacts'][0].__setitem__('otherRealComponent', 23))
    def test_omitted_contact_scan(self): self.reject(lambda f: f[6]['completeLowParts'][0].__setitem__('allOtherOriginalFacesExamined', 1))
    def test_duplicate_current_actor(self): self.reject(lambda f: f[3].append(deepcopy(f[3][0])))
    def test_primary_wrong_csuid(self): self.reject(lambda f: f[4]['features'][0]['attributes'].__setitem__('BuildingCSUID', 'wrong'))
    def test_primary_wrong_type(self): self.reject(lambda f: f[4]['features'][0]['attributes'].__setitem__('BuildingBlockType', 'Podium'))
    def test_primary_wrong_date(self): self.reject(lambda f: f[4]['features'][0]['attributes'].__setitem__('DateCreate', 0))
    def test_primary_ambiguous(self): self.reject(lambda f: f[4]['features'].append(deepcopy(f[4]['features'][0])))
    def test_all_full_projection_foreign_overlap_retained(self):
        f = deepcopy(fixture())
        tri = f[2][ROLE_IDS]
        lo, hi = tri.min((0, 1)), tri.max((0, 1))
        foreign = {'uid': 'foreign:added', 'rings': [[[lo[0]-1, lo[2]-1], [hi[0]+1, lo[2]-1], [hi[0]+1, hi[2]+1], [lo[0]-1, hi[2]+1], [lo[0]-1, lo[2]-1]]]}
        f[3].append(foreign); r = proposal(*f)
        self.assertFalse(r['proposalSpatialGuardsSatisfied'])
        self.assertIn('foreign:added', r['allOtherForeignUIDs'])
        self.assertGreater(r['fullSourceSpatialChecks']['current']['completeSourceForeignExcessM2'], 1)
    def test_role_does_not_remove_source_projection(self):
        f = fixture(); target = shapely.Polygon(f[1]['source']['building']['rings'][0])
        with_role = spatial_metrics(f[2], ROLE_IDS, target, shapely.GeometryCollection())
        without = spatial_metrics(f[2], [], target, shapely.GeometryCollection())
        for k in ['completeSourceProjectionAreaM2', 'completeSourceTargetCoverage', 'fullRawVertexExtentMetres', 'completeSourceForeignExcessM2']:
            self.assertEqual(with_role[k], without[k])
        self.assertFalse(without['ordinarySpatialGuardsOnCompleteProjectionAndRemainingFaces'])
if __name__ == '__main__': unittest.main()
