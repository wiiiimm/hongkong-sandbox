"""Constructed inputs only. No original decode, model worker or DB mutation."""
import copy
import contextlib
import io
import gzip
import json
import struct
import unittest
from unittest.mock import patch, Mock

import numpy as np
from shapely.geometry import Polygon
import china_merchants264206_saved_face_attribution_recipe_v1_20261013 as recipe


def source_glb(vertices, indices):
    position = np.asarray(vertices, dtype='<f4').reshape(-1, 3)
    index = np.asarray(indices, dtype='<u4').reshape(-1)
    data = position.tobytes() + index.tobytes()
    matrix = np.eye(4)
    matrix[:3, 3] = [834500, 0, -816500]
    doc = dict(buffers=[dict(byteLength=len(data))],
        bufferViews=[dict(buffer=0, byteOffset=0, byteLength=position.nbytes),
                     dict(buffer=0, byteOffset=position.nbytes, byteLength=index.nbytes)],
        accessors=[dict(bufferView=0, componentType=5126, type='VEC3', count=len(position)),
                   dict(bufferView=1, componentType=5125, type='SCALAR', count=len(index))],
        meshes=[dict(primitives=[dict(attributes=dict(POSITION=0), indices=1)])],
        nodes=[dict(mesh=0, matrix=matrix.reshape(-1, order='F').tolist())], scenes=[dict(nodes=[0])])
    header = json.dumps(doc).encode()
    header += b' ' * (-len(header) % 4)
    raw = struct.pack('<III', 0x46546c67, 2, 28+len(header)+len(data))
    raw += struct.pack('<II', len(header), 0x4e4f534a) + header
    raw += struct.pack('<II', len(data), 0x004e4942) + data
    return gzip.compress(raw, mtime=0)


def duplicate_mesh_occurrence(raw):
    data = gzip.decompress(raw)
    size = struct.unpack_from('<I', data, 12)[0]
    doc = json.loads(data[20:20 + size])
    binary = data[28 + size:]
    doc['nodes'].append(copy.deepcopy(doc['nodes'][0]))
    doc['scenes'][0]['nodes'] = [0, 1]
    header = json.dumps(doc).encode()
    header += b' ' * (-len(header) % 4)
    return gzip.compress(struct.pack('<III', 0x46546c67, 2, 28+len(header)+len(binary)) +
        struct.pack('<II', len(header), 0x4e4f534a) + header +
        struct.pack('<II', len(binary), 0x004e4942) + binary, mtime=0)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.function = recipe.load_canonical()
        self.pin = recipe.canonical_pin(self.function)
        self.original = np.array([[[0., -1., 0.], [0., -1., 1.], [1., -1., 0.]],
                                  [[10., 1., 0.], [10., 1., 1.], [11., 1., 0.]]])
        self.ground = np.array([[[-100., 0., -100.], [-100., 0., 100.], [100., 0., -100.]],
                                [[100., 0., 100.], [100., 0., -100.], [-100., 0., 100.]]])
        self.raw_source = source_glb(self.original, list(range(6)))
        self.source = recipe.digest(self.raw_source)
        self.original = recipe.decode_original_world_triangles(self.raw_source)
        self.expected = {**recipe.EXPECTED, 'sourceSHA256': self.source, 'faces': 2, 'bodies': 2}
        self.runtime = dict(uid=recipe.UID, sourceSHA256=self.source,
                            position=self.original.reshape(-1).tolist(), index=list(range(6)),
                            drawnGroundGeometry=self.ground.reshape(-1).tolist())
        self.building = dict(uid=recipe.UID, buildingCSUID=recipe.EXPECTED['csuid'],
                             rings=[[[-50., -50.], [50., -50.], [50., 50.], [-50., 50.]]])
        self.selection = dict(uid=recipe.UID, sourceSHA256=self.source,
                              modelId=recipe.EXPECTED['modelId'], triangles=2,
                              source=dict(building=self.building))
        self.census = dict(uid=recipe.UID, sourceSHA256=self.source,
                           components=[dict(sourceFaceIndices=[0], triangles=1, preservedNote='whole body zero'),
                                       dict(sourceFaceIndices=[1], triangles=1, preservedNote='whole body one')])
        self.metrics = self.function(self.original, self.ground, Polygon(self.building['rings'][0]))

    def call(self):
        return recipe.bound_attribution(self.function, self.runtime, self.selection, self.census,
                                        self.raw_source, self.metrics, expected=self.expected, expected_pin=self.pin)

    def test_exact_face_coordinates_complete_census_and_metrics_are_preserved(self):
        before = copy.deepcopy((self.runtime, self.selection, self.census, self.metrics))
        source = self.original.tobytes()
        result = self.call()
        self.assertEqual([0], result['fullyBuriedSourceFaceIndices'])
        group = result['failureGroupsInCanonicalDelegateOrder'][0]
        self.assertEqual(self.original[[0]].tolist(), group['originalSourceFaceVerticesInJournalOrder'])
        self.assertEqual(self.original.tolist(), result['completeOriginalSourceFaceVerticesInOrdinalOrder'])
        self.assertEqual(self.census, result['completeCensusVerbatim'])
        self.assertEqual(self.metrics, result['canonicalFoundationMetrics'])
        self.assertFalse(result['physicalAccepted'])
        self.assertFalse(result['currentAcceptance'])
        self.assertFalse(result['sourceRoleApproved'])
        self.assertNotIn('savedTrueEdgeBodyInventoryRecomputed', result)
        self.assertTrue(result['arithmeticZeroObservationsAreNotExactNonrenderingCertificates'])
        self.assertEqual([], result['nonrenderingSourceFaceIndices'])
        self.assertEqual(before, (self.runtime, self.selection, self.census, self.metrics))
        self.assertEqual(source, self.original.tobytes())

    def test_all_three_source_uid_and_hash_bindings_are_required(self):
        for name in ['runtime', 'selection', 'census']:
            for key in ['uid', 'sourceSHA256']:
                with self.subTest(name=name, key=key):
                    old = getattr(self, name)[key]
                    getattr(self, name)[key] = 'changed'
                    with self.assertRaises(AssertionError):
                        self.call()
                    getattr(self, name)[key] = old

    def test_model_form_csuid_and_full_face_count_changes_are_rejected(self):
        for obj, key, value in [(self.selection, 'modelId', 'another'), (self.selection, 'triangles', 1),
                                (self.building, 'buildingCSUID', 'another'), (self.building, 'uid', 'another')]:
            with self.subTest(key=key):
                old = obj[key]
                obj[key] = value
                with self.assertRaises(AssertionError):
                    self.call()
                obj[key] = old

    def test_reordered_runtime_index_faces_cannot_relabel_source_failures(self):
        self.runtime['index'] = [3, 4, 5, 0, 1, 2]
        with self.assertRaises(AssertionError):
            self.call()

    def test_nearby_index_swap_is_rejected_even_within_old_coordinate_tolerance(self):
        vertices = np.stack([self.original[0], self.original[0] + [.0001, 0., 0.]])
        self.raw_source = source_glb(vertices, list(range(6)))
        source = recipe.digest(self.raw_source)
        self.expected['sourceSHA256'] = source
        for item in [self.runtime, self.selection, self.census]:
            item['sourceSHA256'] = source
        self.runtime['position'] = recipe.decode_original_world_triangles(self.raw_source).reshape(-1).tolist()
        self.runtime['index'] = [3, 4, 5, 0, 1, 2]
        with self.assertRaisesRegex(AssertionError, 'index-slot order'):
            self.call()

    def test_reused_mesh_under_distinct_nodes_has_distinct_offsets_and_paths(self):
        ids, vertices, records = recipe.original_index_order(duplicate_mesh_occurrence(self.raw_source))
        self.assertEqual(list(range(12)), ids.tolist())
        self.assertEqual(12, vertices)
        self.assertEqual([[0], [1]], [r['nodeOccurrencePath'] for r in records])
        self.assertEqual([0, 1], [r['nodeIndex'] for r in records])
        self.assertEqual([0, 2], [r['sourceFaceOffset'] for r in records])

    def test_unused_position_slots_are_retained_by_topology_binding(self):
        raw = source_glb(np.vstack([self.original.reshape(-1, 3), [70., 70., 70.]]), list(range(6)))
        ids, vertices, records = recipe.original_index_order(raw)
        self.assertEqual(7, vertices)
        self.assertEqual(list(range(6)), ids.tolist())
        self.assertEqual(7, records[0]['positionSlotCount'])

    def test_changed_runtime_coordinates_fail_original_correspondence(self):
        self.runtime['position'][0] += .01
        with self.assertRaises(AssertionError):
            self.call()

    def test_invalid_index_types_ranges_and_counts_are_rejected(self):
        for index in [[float(i) for i in range(6)], [False] * 6, [-1, 1, 2, 3, 4, 5],
                      [0, 1, 2, 3, 4, 6], [0, 1, 2]]:
            with self.subTest(index=index):
                self.runtime['index'] = index
                with self.assertRaises(AssertionError):
                    self.call()

    def test_forged_saved_metrics_are_not_accepted_as_reproduction(self):
        self.metrics['fullyBuriedTriangles'] += 1
        with self.assertRaises(AssertionError):
            self.call()

    def test_incomplete_or_duplicate_body_partitions_are_rejected(self):
        self.census['components'][1]['sourceFaceIndices'] = [0]
        with self.assertRaises(AssertionError):
            self.call()

    def test_nonfinite_ground_is_rejected(self):
        self.runtime['drawnGroundGeometry'][0] = float('nan')
        with self.assertRaises(AssertionError):
            self.call()

    def test_no_mode_cannot_claim_or_connect(self):
        with patch.object(recipe.sys, 'argv', ['recipe']), patch.object(recipe, 'connect') as connect, \
             patch.object(recipe.reservations, 'claim') as claim, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exit:
                recipe.main()
            self.assertEqual(2, exit.exception.code)
            connect.assert_not_called()
            claim.assert_not_called()

    def test_preflight_mode_does_not_claim_decode_or_connect(self):
        with patch.object(recipe.sys, 'argv', ['recipe', '--preflight-only']), \
             patch.object(recipe, 'preflight', return_value=(None, None, None, None, [], [])), \
             patch.object(recipe, 'connect') as connect, patch.object(recipe.reservations, 'claim') as claim, \
             patch.object(recipe, 'decode_original_world_triangles') as decode, \
             contextlib.redirect_stdout(io.StringIO()):
            recipe.main()
            connect.assert_not_called()
            claim.assert_not_called()
            decode.assert_not_called()

    def test_wrong_lease_resources_fail_before_ownership_database_check(self):
        with patch.object(recipe.sys, 'argv', ['recipe', '--owned']), \
             patch.object(recipe, 'read', return_value=dict(batch=recipe.BATCH, resources=['building:other'])), \
             patch.object(recipe.reservations, 'owns') as owns, patch.object(recipe, 'connect') as connect:
            with self.assertRaises(AssertionError):
                recipe.main()
            owns.assert_not_called()
            connect.assert_not_called()

    def test_failed_launch_receipt_releases_only_the_mock_claim_and_never_starts_worker(self):
        reservation = dict(owner='synthetic-owner', token='synthetic-token')
        with patch.object(recipe.sys, 'argv', ['recipe', '--execute']), \
             patch.object(recipe, 'preflight', return_value=(None, {}, None, None, [], [])), \
             patch.object(recipe, 'read', return_value=dict(inputHashes={})), \
             patch.object(recipe, 'ref', return_value=dict(path='synthetic-pin', sha256='synthetic-sha')), \
             patch.object(recipe.reservations, 'claim', return_value=dict(ok=True, reservation=reservation)), \
             patch.object(recipe, 'save', side_effect=OSError('synthetic receipt failure')), \
             patch.object(recipe.reservations, 'release', return_value=dict(ok=True)) as release, \
             patch.object(recipe.subprocess, 'run') as start, patch.object(recipe, 'connect') as connect:
            with self.assertRaises(OSError):
                recipe.main()
            release.assert_called_once_with(reservation)
            start.assert_not_called()
            connect.assert_not_called()

    def test_changed_prepared_recipe_tuple_fails_before_claim(self):
        with patch.object(recipe.sys, 'argv', ['recipe', '--execute']), \
             patch.object(recipe, 'preflight', return_value=(None, {}, None, None, [], [dict(path='recipe', sha256='changed')])), \
             patch.object(recipe, 'read', return_value=dict(inputHashes={'recipe': 'approved'})), \
             patch.object(recipe.reservations, 'claim') as claim, patch.object(recipe, 'connect') as connect:
            with self.assertRaises(AssertionError):
                recipe.main()
            claim.assert_not_called()
            connect.assert_not_called()

    def test_wrong_claimed_job_is_returned_to_retry_without_source_work(self):
        wrong = dict(id='wrong', owner='synthetic-owner', token='synthetic-token')
        with patch.object(recipe.jobs, 'enqueue', return_value='wanted'), \
             patch.object(recipe.jobs, 'claim', return_value=wrong), \
             patch.object(recipe.jobs, 'finish', return_value=True) as finish:
            with self.assertRaises(AssertionError):
                recipe.claim_exact_job({}, 'synthetic-owner')
            self.assertTrue(finish.call_args.kwargs['retry'])
            self.assertEqual(wrong, finish.call_args.args[0])

    def recovery_case(self):
        payload = dict(uids=[recipe.UID], sourceSHA256=recipe.SOURCE, canonicalPin={},
                       evidenceRefs=[dict(path='input', sha256='input-sha')])
        jid = recipe.digest(recipe.jobs.encode([recipe.BATCH, recipe.STAGE, payload]).encode())
        result = dict(**payload, batch=recipe.BATCH, stage=recipe.STAGE, jobId=jid,
                      newlyInstalled=0, publication=False, currentAcceptance=False,
                      physicalAccepted=False, sourceRoleApproved=False)
        result['evidenceRefs'] = [*payload['evidenceRefs'],
            dict(path=str((recipe.DOC / 'source-face-attribution.json.gz').relative_to(recipe.ROOT)), sha256='output-sha')]
        return payload, result

    def test_exact_complete_receipt_can_be_recovered_without_calculation(self):
        payload, result = self.recovery_case()
        fetch, verify, write = Mock(return_value=('complete', result)), Mock(), Mock()
        with patch.object(recipe, 'decode_original_world_triangles') as decode, patch.object(recipe, 'bound_attribution') as calculate:
            actual = recipe.recover_completed_result(payload, fetch, verify, write)
            self.assertEqual(result, actual)
            self.assertEqual(len(result['evidenceRefs']), verify.call_count)
            write.assert_called_once()
            decode.assert_not_called()
            calculate.assert_not_called()

    def test_recovery_rejects_running_job_changed_identity_and_acceptance(self):
        for status, key, value in [('running', 'jobId', None), ('complete', 'jobId', 'wrong'),
                                   ('complete', 'sourceSHA256', 'wrong'), ('complete', 'physicalAccepted', True)]:
            with self.subTest(status=status, key=key):
                payload, result = self.recovery_case()
                if value is not None:
                    result[key] = value
                write = Mock()
                with self.assertRaises(AssertionError):
                    recipe.recover_completed_result(payload, lambda jid: (status, result), Mock(), write)
                write.assert_not_called()

    def test_recovery_changed_output_hash_fails_before_receipt_write(self):
        payload, result = self.recovery_case()
        write = Mock()
        with self.assertRaises(AssertionError):
            recipe.recover_completed_result(payload, lambda jid: ('complete', result), Mock(side_effect=AssertionError('changed output')), write)
        write.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
