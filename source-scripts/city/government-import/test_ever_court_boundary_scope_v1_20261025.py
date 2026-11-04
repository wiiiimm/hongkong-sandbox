"""Adversarial checks against the completed, immutable current-scene evidence."""
import copy
import gzip
import json
from pathlib import Path
import unittest
from ever_court_boundary_scope_v1_20261025 import merge, retained_views, NATIVE

BASE = Path(__file__).resolve().parents[3] / 'docs/astra-city/government-import'
P = 'government-xl-ever-court-current-'


def read(name, filename):
    path = BASE / (P + name + '-v1-20261025') / filename
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


class BoundaryScope(unittest.TestCase):
    def setUp(self):
        self.scope = read('inset-scope', 'scope.json')
        self.forms = read('inset-scope', 'form-obligations.json.gz')
        self.model = {r['building']['uid']: r['building'] for r in read('source-scope', '158003:0-forms.json.gz')}
        self.native = read('inset-neighbours', 'summary.json')
        self.resolution = read('basic-supports', 'summary.json')

    def run_contract(self):
        return merge(self.model, self.forms, self.scope, self.native, self.resolution)

    def test_completed_evidence_preserves_all_25_forms(self):
        self.assertEqual(set(self.run_contract()), {f['uid'] for f in self.forms})

    def test_positive_area_overlap_rejected_even_with_stale_zero_counter(self):
        self.scope['terrainContacts'][0]['packedContacts'][0]['overlapAreaM2'] = 1e-12
        with self.assertRaises(AssertionError): self.run_contract()

    def test_missing_boundary_native_rejected(self):
        self.scope['touchingNativeUids'] = []
        with self.assertRaises(AssertionError): self.run_contract()

    def test_incomplete_native_mesh_rejected(self):
        self.native['nativeRows'][0]['triangles'] -= 1
        with self.assertRaises(AssertionError): self.run_contract()

    def test_changed_retained_ground_rejected(self):
        self.native['nativeRows'][0]['terrain']['minimumGapAfter'] += 1e-8
        with self.assertRaises(AssertionError): self.run_contract()

    def test_new_native_burial_rejected(self):
        self.native['nativeRows'][0]['terrain']['newlyWhollyBuried'] = 1
        with self.assertRaises(AssertionError): self.run_contract()

    def test_missing_form_rejected(self):
        self.forms.pop()
        with self.assertRaises(AssertionError): self.run_contract()

    def test_changed_same_uid_form_rejected(self):
        uid = next(iter(self.model))
        self.model[uid] = copy.deepcopy(self.model[uid])
        self.model[uid]['height'] += .01
        with self.assertRaises(AssertionError): self.run_contract()

    def test_support_proof_reassignment_rejected(self):
        self.resolution['proofs'][0]['supportUid'] = 'landsd/158003:0'
        with self.assertRaises(AssertionError): self.run_contract()

    def test_weaker_support_threshold_rejected(self):
        self.resolution['proofs'][0]['horizontalToleranceMetres'] = .003
        with self.assertRaises(AssertionError): self.run_contract()

    def test_unresolved_neighbour_rejected(self):
        self.resolution['allBasicFlagsResolved'] = False
        with self.assertRaises(AssertionError): self.run_contract()

    def test_duplicate_support_proof_rejected(self):
        self.resolution['proofs'].append(copy.deepcopy(self.resolution['proofs'][0]))
        with self.assertRaises(AssertionError): self.run_contract()

    def test_changed_terrain_extent_rejected(self):
        self.scope['terrainContacts'][0]['extent'][0] -= .01
        with self.assertRaises(AssertionError): self.run_contract()


class RetainedExports(unittest.TestCase):
    def setUp(self):
        report = BASE / 'government-xl-ever-court-current-private-browser-v1-20261025/1280/staged-browser.json'
        self.views = json.loads(report.read_text())['retainedNativeOwnViews']
        self.current = {NATIVE: dict(sha256=self.views[0]['sourceSHA256'], triangles=63844)}

    def test_complete_retained_exports(self):
        self.assertTrue(retained_views(self.views, self.current, 1280))

    def test_duplicate_daytime_rejected(self):
        self.views[1] = copy.deepcopy(self.views[0])
        with self.assertRaises(AssertionError): retained_views(self.views, self.current, 1280)

    def test_wrong_source_rejected(self):
        self.current[NATIVE]['sha256'] = '0' * 64
        with self.assertRaises(AssertionError): retained_views(self.views, self.current, 1280)

    def test_retained_fallback_rejected(self):
        self.views[0]['fallbackFaces'] = 1
        with self.assertRaises(AssertionError): retained_views(self.views, self.current, 1280)

    def test_hidden_retained_mesh_rejected(self):
        self.views[0]['meshVisibility'] = [False]
        with self.assertRaises(AssertionError): retained_views(self.views, self.current, 1280)

    def test_missing_material_witness_rejected(self):
        self.views[0]['wireframeFlags'] = []
        with self.assertRaises(AssertionError): retained_views(self.views, self.current, 1280)


if __name__ == '__main__':
    unittest.main()
