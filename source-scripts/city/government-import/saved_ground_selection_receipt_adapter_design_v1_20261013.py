"""Future-only metadata authentication adapter; no DB or worker entry point.

ROOT must supply the exact pinned Neon SELECT result and live independently
bound source/world/scope hashes inside the future canonical owned caller.
This module neither queries Neon nor establishes trust in caller-supplied data.
It is not imported by any active numerical caller.
"""
import gzip
import hashlib
import json
from pathlib import PurePosixPath
from exact_saved_ground_selection_delta_v1_20261013 import selection_sha


class AuthenticatedSelectionReceipt:
    def __init__(self, receipt_ref, expected_job_id, exact_neon_status_result, read_bytes):
        self._read_bytes = read_bytes
        self.receipt_ref = dict(receipt_ref)
        receipt = self._read_json(receipt_ref)
        assert receipt['jobId'] == expected_job_id
        assert exact_neon_status_result == ('complete', receipt)
        self.refs = {}
        for q in receipt['evidenceRefs']:
            path = q['path']
            assert path not in self.refs or self.refs[path] == q
            self.refs[path] = dict(q)
        # All complete receipt refs, including chunks/source/context/code, once.
        for q in self.refs.values():
            self._bytes(q)
        self.receipt = receipt

    def _bytes(self, q):
        path = PurePosixPath(q['path'])
        assert not path.is_absolute() and '..' not in path.parts
        b = self._read_bytes(q['path'])
        assert hashlib.sha256(b).hexdigest() == q['sha256']
        return b

    def _read_json(self, q):
        b = self._bytes(q)
        if q['path'].endswith('.gz'):
            b = gzip.decompress(b)
        return json.loads(b)

    def _evidence(self, q):
        assert self.refs.get(q['path']) == q, 'Not an exact completed receipt member'
        return self._read_json(q)

    def bind_world(self, summary_ref, *, uid, mode, actor_kind, role,
                   live_world_sha, complete_face_count, complete_scope,
                   old_ground_sha, independently_bound_input_refs,
                   live_source_sha=None):
        """Authenticate all selected faces, including negative rows, as one set.

        Before this call ROOT proves the whole complete actor census, modes,
        BASIC rows and outside-domain obligations. Input refs must bind the
        exact source/index/positions/world/scope inputs used for these values.
        Missing/stale evidence raises; the caller uses the full original
        selector for that entire affected world, never guessed partial reuse.
        """
        assert independently_bound_input_refs
        for q in independently_bound_input_refs:
            assert self.refs.get(q['path']) == q
            self._bytes(q)
        summary = self._evidence(summary_ref)
        assert summary['newGroundSHA256'] == old_ground_sha
        assert not summary['physicalAccepted'] and not summary['installationApproved']
        if actor_kind == 'source-actor':
            actors = [r for r in summary['actors'] if r['uid'] == uid]
            assert len(actors) == 1
            actor = actors[0]
            assert actor['role'] == role and actor['sourceSHA256'] == live_source_sha
            worlds = actor['worlds']
        else:
            assert actor_kind == 'affected-BASIC' and role == 'complete-affected-BASIC-regression'
            actors = [r for r in summary['completeBasicRows'] if r['uid'] == uid]
            assert len(actors) == 1 and actors[0]['completeScope'] == complete_scope
            assert actors[0]['completeFaces'] == complete_face_count
            worlds = actors[0]['findings']['worlds']
        matches = [r for r in worlds if r['mode'] == mode]
        assert len(matches) == 1
        world = matches[0]
        assert world['wholeWorldSHA256'] == live_world_sha
        assert world['completeFaces'] == complete_face_count and world['completeScope'] == complete_scope
        ids = complete_scope['selectedFaceIDs']
        assert ids == sorted(set(ids)) and all(type(i) is int and 0 <= i < complete_face_count for i in ids)
        rows = {}
        for q in world['findings']['chunks']:
            chunk = self._evidence(q)
            assert chunk['uid'] == uid and chunk['wholeWorldSHA256'] == live_world_sha
            # Some prior mode-cache records share an identical world across
            # mode labels. Hash equality is mandatory; never relabel that chunk.
            assert chunk['completeNewGroundSHA256'] == old_ground_sha
            for row in chunk['rows']:
                face = row['face']
                assert type(face) is int and face not in rows
                assert row['completeNewGroundSelection']['completeGroundSHA256'] == old_ground_sha
                rows[face] = row
        assert set(rows) == set(ids)
        assert world['findings']['completeProcessedFaces'] == len(ids)
        return AuthenticatedWorldSelections(rows, world, self.receipt_ref, summary_ref)

    def verify_end(self):
        assert self._read_json(self.receipt_ref) == self.receipt
        for q in self.refs.values():
            self._bytes(q)


class AuthenticatedWorldSelections:
    def __init__(self, rows, world, receipt_ref, summary_ref):
        # Snapshots prevent caller mutations from altering authenticated tokens.
        self._rows_json = {i: json.dumps(r, sort_keys=True, allow_nan=False) for i, r in rows.items()}
        self._world_json = json.dumps(world, sort_keys=True, allow_nan=False)
        self.receipt_ref = dict(receipt_ref)
        self.summary_ref = dict(summary_ref)

    def face(self, face_id, independently_bound_source_face_sha):
        row = json.loads(self._rows_json[face_id])
        assert row['currentBaselineVerbatim']['sourceFaceSHA256'] == independently_bound_source_face_sha
        selection = row['completeNewGroundSelection']
        return dict(selection=selection, authenticated_selection_sha=selection_sha(selection),
                    authenticated_selected_ground_sha=row['completeRelevantGroundSHA256'],
                    priorCandidateRowVerbatim=row, priorWorldVerbatim=json.loads(self._world_json),
                    completedReceipt=dict(self.receipt_ref), completedSummary=dict(self.summary_ref),
                    oldKernelHashesAndNegativeContextRemainVerbatim=True,
                    noRoleRootPhysicalOrInstallationAcceptance=True)
