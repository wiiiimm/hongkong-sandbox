"""UNEXECUTED draft; schema cases are synthetic, full-record cases require real v1.

No project modules, DB clients, workers, predicates or descriptor builders load.
The actual checkpoint tests fail closed if its complete first-mode file is absent.
The synthetic full-ground scalar is only an equality-guard fixture, not evidence
that the original 774,477 facets were decoded; production must freshly bind them.
"""
import copy
import gzip
import json
import struct
import unittest
from pathlib import Path
import southside_whole_mode_resume_descriptor_draft_v1_20261012 as draft


def fixture():
    blobs = {'checkpoint': b'synthetic schema-only envelope', 'log': b'{}',
             'source-contract': b'bound source contract', 'caller': b'caller',
             'helper': b'helper', 'test': b'test'}
    blobs['retirement'] = json.dumps(dict(kind='root-issued-southside-complete-mode-retirement-v1',
        priorBatch=draft.PRIOR_BATCH, currentManifestSHA256=draft.MANIFEST,
        priorLeaseReleased=True, noOwnedOrSupervisorProcessRemaining=True,
        currentAcceptance=False)).encode()
    blobs['validation'] = json.dumps(dict(testsRun=13, exitCode=0, result='OK',
        helperSHA256=draft.sha(blobs['helper']), testSHA256=draft.sha(blobs['test']))).encode()
    def p(name): return dict(path=name, sha256=draft.sha(blobs[name]))
    descriptor = dict(schema=draft.SCHEMA, priorBatch=draft.PRIOR_BATCH, uid=draft.UID,
        arithmetic=draft.MODE, sourceSHA256=draft.SOURCE, currentManifestSHA256=draft.MANIFEST,
        completeOriginalFaces=11699, completeFullOriginalGroundFacets=774477,
        completeFullOriginalGroundSHA256='a'*64, selectedOriginalGroundFacets=25388,
        selectedOriginalGroundSHA256='b'*64, completeWorldSHA256='c'*64,
        checkpointPin=p('checkpoint'), completionLogPin=p('log'), rootRetirementPin=p('retirement'),
        rootCoverageValidationPin=p('validation'), inputPins=[p('source-contract')],
        codePins=[p('caller'), p('helper'), p('test')], currentAcceptance=False,
        installationApproved=False)
    return dict(descriptor=descriptor, trusted=copy.deepcopy(descriptor), blobs=blobs,
                completed_v1_exists=False, prior_processes_absent=True, prior_lease_released=True)


def change_both(q, key, value):
    q['descriptor'][key]=value; q['trusted'][key]=copy.deepcopy(value)


def replace_blob_with_consistent_pins(q, name, value, pin_key):
    q['blobs'][name]=json.dumps(value).encode()
    change_both(q,pin_key,dict(path=name,sha256=draft.sha(q['blobs'][name])))


class DescriptorSchema(unittest.TestCase):
    def call(self, q): return draft.validate_descriptor(q.pop('descriptor'), **q)
    def reject(self, mutate):
        q=fixture(); mutate(q)
        with self.assertRaises((AssertionError, KeyError, ValueError)): self.call(q)
    def test_positive_schema_only(self): self.assertFalse(self.call(fixture())['currentAcceptance'])
    def test_missing_descriptor(self): self.reject(lambda q:q.update(descriptor=None))
    def test_completed_v1_precedes_resume(self): self.reject(lambda q:q.update(completed_v1_exists=True))
    def test_surviving_process(self): self.reject(lambda q:q.update(prior_processes_absent=False))
    def test_unreleased_lease(self): self.reject(lambda q:q.update(prior_lease_released=False))
    def test_changed_source(self): self.reject(lambda q:change_both(q,'sourceSHA256','f'*64))
    def test_partial_4001_record_count(self): self.reject(lambda q:change_both(q,'completeOriginalFaces',4001))
    def test_full_ground_scope_changed(self): self.reject(lambda q:change_both(q,'completeFullOriginalGroundFacets',774476))
    def test_roi_scope_changed(self): self.reject(lambda q:change_both(q,'selectedOriginalGroundFacets',25387))
    def test_actual_checkpoint_bytes_changed(self): self.reject(lambda q:q['blobs'].update(checkpoint=b'changed'))
    def test_root_audit_bytes_changed(self): self.reject(lambda q:q['blobs'].update(retirement=b'{}'))
    def test_caller_bytes_changed(self): self.reject(lambda q:q['blobs'].update(caller=b'changed'))
    def test_candidate_cannot_add_self_trusted_pin(self): self.reject(lambda q:q['descriptor']['codePins'].append(dict(path='new',sha256='d'*64)))
    def test_extra_descriptor_field(self): self.reject(lambda q:q['descriptor'].update(allowPartial=True))
    def test_approval_flag(self): self.reject(lambda q:change_both(q,'installationApproved',True))
    def test_wrong_current_manifest_even_if_consistent(self): self.reject(lambda q:change_both(q,'currentManifestSHA256','f'*64))
    def test_floating_face_count_is_not_declared_integer(self): self.reject(lambda q:change_both(q,'completeOriginalFaces',11699.0))
    def test_retirement_with_active_child_even_if_pin_matches(self):
        def alter(q):
            audit=json.loads(q['blobs']['retirement']);audit['noOwnedOrSupervisorProcessRemaining']=False
            replace_blob_with_consistent_pins(q,'retirement',audit,'rootRetirementPin')
        self.reject(alter)
    def test_wrong_validation_count_even_if_pin_matches(self):
        def alter(q):
            validation=json.loads(q['blobs']['validation']);validation['testsRun']=12
            replace_blob_with_consistent_pins(q,'validation',validation,'rootCoverageValidationPin')
        self.reject(alter)
    def test_wrong_validation_code_binding_even_if_pin_matches(self):
        def alter(q):
            validation=json.loads(q['blobs']['validation']);validation['helperSHA256']='f'*64
            replace_blob_with_consistent_pins(q,'validation',validation,'rootCoverageValidationPin')
        self.reject(alter)


class ActualWholeMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=Path(__file__).resolve().parents[3];base=root/'docs/astra-city/government-import'
        checkpoint=root/'source-scripts/city/government-import/local'/draft.PRIOR_BATCH/'completed-315025-0-providerOriginal.json.gz'
        # Intentionally no skip or synthetic replacement when the real file is absent.
        with gzip.open(checkpoint,'rt')as h: cls.row=json.load(h)
        capture=base/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012/complete-two-actor-four-stream-ground-inputs.json.gz'
        with gzip.open(capture,'rt')as h: captured=json.load(h)['rows'][draft.UID]
        world=captured['completeWorldStreams'][draft.MODE]['completeWorldTriangles']
        cls.world=b''.join(struct.pack('<9d',*(v for p in face for v in p)) for face in world)
        grade=base/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012/diagnostic.json.gz'
        with gzip.open(grade,'rt')as h: rows=json.load(h)['rows']
        cls.old=next(q for q in rows if q['uid']==draft.UID and q['arithmetic']==draft.MODE)
        cls.log=Path('/tmp/xl-southside-unfiltered-original-sheets-comparison-v1-20261012.log').read_text()
    def case(self):
        d=fixture()['descriptor'];d['completeWorldSHA256']=draft.sha(self.world)
        d['selectedOriginalGroundSHA256']=self.row['completeUnfilteredSelectedGroundSHA256']
        return dict(row=copy.deepcopy(self.row),descriptor=d,world_bytes=self.world,
          current_records=copy.deepcopy(self.old['allCompleteOriginalFiniteRecords']),
          current_failed_ids=self.old['allRawFailedFaces'],full_ground_sha256=d['completeFullOriginalGroundSHA256'],
          selected_ground_sha256=d['selectedOriginalGroundSHA256'],completion_log=self.log)
    def reject(self, mutate):
        q=self.case();mutate(q)
        with self.assertRaises((AssertionError, KeyError, ValueError)): draft.validate_complete_mode(**q)
    def test_actual_complete_ordered_11699(self):
        self.assertEqual(draft.validate_complete_mode(**self.case())['completeOrderedOriginalProofRecords'],11699)
    def test_partial_records(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'].pop())
    def test_reordered_records(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'].reverse())
    def test_duplicate_face(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'][1].update(sourceFace=0))
    def test_bool_is_not_integer_face_id(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'][1].update(sourceFace=True))
    def test_changed_full_facet(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'][0].update(completeOriginalFacetSHA256='f'*64))
    def test_changed_world_bytes(self): self.reject(lambda q:q.update(world_bytes=q['world_bytes'][:-1]+bytes([q['world_bytes'][-1]^1])))
    def test_changed_full_original_ground_binding(self): self.reject(lambda q:q.update(full_ground_sha256='f'*64))
    def test_changed_selected_original_ground_binding(self): self.reject(lambda q:q.update(selected_ground_sha256='f'*64))
    def test_current_comparison_changed(self): self.reject(lambda q:q['row']['completeOriginalFaceComparisons'][0]['currentDrawnGroundComparisonRetainedVerbatim'].update(tamper=True))
    def test_old_negative_omission(self): self.reject(lambda q:q.update(current_failed_ids=q['current_failed_ids'][:-1]))
    def test_failure_list_changed(self): self.reject(lambda q:q['row']['allAuthenticatedGroundFailuresRetained'].append(11699))
    def test_progress_only_does_not_complete_mode(self): self.reject(lambda q:q.update(completion_log=json.dumps(dict(uid=draft.UID,mode=draft.MODE,completedSourceFacets=10000))))
    def test_saved_approval_flag_rejected(self): self.reject(lambda q:q['row'].update(currentAcceptance=True))


if __name__=='__main__':unittest.main()
