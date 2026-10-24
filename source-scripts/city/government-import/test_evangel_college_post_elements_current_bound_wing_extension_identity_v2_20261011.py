"""Actual frozen current bindings; production verify_files is a separate replay."""
from copy import deepcopy
from functools import lru_cache
import unittest
from run import read,ROOT
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import current_binding, named_identity, PROPOSAL, UID, source_proposal_pin_path,HISTORICAL_MANIFEST_SHA,HISTORICAL_MANIFEST
# Hermetic pre-Elements fixture; the separate producer performs fresh production replay.
RAW=ROOT/'docs/astra-city/government-import/government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011'
from test_evangel_college_original_wing_extension_identity_20261011 import ActualSource
def fixture():
    ActualSource.setUpClass(); return ActualSource().args()
@lru_cache(None)
def binding_fixture():
    row = read(RAW / 'selection.json.gz')['rows'][0]
    context = read(RAW / 'context.json.gz')['rows'][0]
    forms = read(RAW / 'complete-current-forms.json.gz')['rows']
    raw = (RAW / 'captured-manifest.json').read_bytes()
    return [row, context, deepcopy(row), deepcopy(context), forms, deepcopy(forms), raw, raw, [(row['native']['resultSha'],)], []]
class CurrentBindingCounterexamples(unittest.TestCase):
    def reject(self, mutate):
        f = deepcopy(binding_fixture()); mutate(f)
        with self.assertRaises(AssertionError): current_binding(*f)
    def test_exact_actual_frozen_inputs(self): self.assertTrue(current_binding(*binding_fixture()))
    def test_stale_current_manifest(self): self.reject(lambda f: f.__setitem__(6, f[6] + b' '))
    def test_changed_candidate_path(self): self.reject(lambda f: f[2]['candidate'].__setitem__('path', 'another'))
    def test_changed_native_result(self): self.reject(lambda f: f[2]['native'].__setitem__('resultSha', '0' * 64))
    def test_changed_source_sha(self): self.reject(lambda f: f[2].__setitem__('sourceSHA256', '0' * 64))
    def test_changed_source_uid(self): self.reject(lambda f: f[2].__setitem__('uid', 'landsd/1:0'))
    def test_changed_model_id(self): self.reject(lambda f: f[2].__setitem__('modelId', 'other'))
    def test_changed_current_own_shape(self): self.reject(lambda f: f[2]['source']['building']['rings'][0][0].__setitem__(0, 0))
    def test_changed_context_tile_sha(self): self.reject(lambda f: f[3]['neighbourTileHashes'].__setitem__(next(iter(f[3]['neighbourTileHashes'])), '0' * 64))
    def test_omitted_context_field(self): self.reject(lambda f: f[3].pop('identity'))
    def test_missing_current_form(self): self.reject(lambda f: f[4].pop())
    def test_added_current_foreign_form(self): self.reject(lambda f: f[4].append({'uid': 'new-foreign', 'rings': []}))
    def test_changed_current_foreign_actor(self):
        def mutate(f):
            p = next(x for x in f[4] if x['uid'] != UID); p['rings'][0][0][0] += .001
        self.reject(mutate)
    def test_duplicate_current_form(self): self.reject(lambda f: f[4].append(deepcopy(f[4][0])))
    def test_duplicate_captured_form(self): self.reject(lambda f: f[5].append(deepcopy(f[5][0])))
    def test_missing_native_membership(self): self.reject(lambda f: f.__setitem__(8, []))
    def test_ambiguous_native_versions(self): self.reject(lambda f: f[8].append(f[8][0]))
    def test_wrong_native_membership_sha(self): self.reject(lambda f: f.__setitem__(8, [('0' * 64,)]))
    def test_already_installed_owned_uid(self): self.reject(lambda f: f[9].append(UID))
class FrozenProposalBinding(unittest.TestCase):
    def test_named_current_identity_has_no_physical_credit(self):
        r = named_identity(*fixture(), read(PROPOSAL / 'diagnostic.json.gz'))
        self.assertTrue(r['passed']); self.assertEqual(r['reasons'], [])
        for k in ['physicalAccepted', 'physicalSupportExemption', 'runtimeExemption', 'structuralSupportAccepted', 'installationApproved']: self.assertFalse(r[k])
        self.assertEqual(len(r['completeWingExtensionInterpretation']['namedOriginalWingExtensionFaceIDs']), 136)
    def test_changed_frozen_proposal_rejected(self):
        p = read(PROPOSAL / 'diagnostic.json.gz'); p['structuralRootOrBridgeCredit'] = True
        with self.assertRaises(AssertionError): named_identity(*fixture(), p)
class HistoricalSourcePinBoundary(unittest.TestCase):
    def test_exact_historical_manifest_has_actual_archive(self):
        self.assertEqual(source_proposal_pin_path(dict(path='3d-viewer/city/data/manifest.json',sha256=HISTORICAL_MANIFEST_SHA)),HISTORICAL_MANIFEST)
        self.assertEqual(__import__('hashlib').sha256(HISTORICAL_MANIFEST.read_bytes()).hexdigest(),HISTORICAL_MANIFEST_SHA)
    def test_changed_manifest_sha_rejected(self):
        with self.assertRaises(AssertionError):source_proposal_pin_path(dict(path='3d-viewer/city/data/manifest.json',sha256='0'*64))
    def test_whitespace_path_receives_no_alias(self):
        p='3d-viewer/city/data/manifest.json '
        self.assertEqual(source_proposal_pin_path(dict(path=p,sha256=HISTORICAL_MANIFEST_SHA)),ROOT/p)
    def test_other_manifest_receives_no_alias(self):
        p='3d-viewer/city/data/other-manifest.json'
        self.assertEqual(source_proposal_pin_path(dict(path=p,sha256=HISTORICAL_MANIFEST_SHA)),ROOT/p)
    def test_tile_with_old_manifest_sha_receives_no_alias(self):
        p='3d-viewer/city/data/tiles/5_-1.json'
        self.assertEqual(source_proposal_pin_path(dict(path=p,sha256=HISTORICAL_MANIFEST_SHA)),ROOT/p)
    def test_other_geometry_receives_no_alias(self):
        p='source-scripts/city/government-import/local/unknown.glb.gz'
        self.assertEqual(source_proposal_pin_path(dict(path=p,sha256=HISTORICAL_MANIFEST_SHA)),ROOT/p)
if __name__ == '__main__': unittest.main()
