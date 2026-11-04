"""UNEXECUTED pure resume-schema draft; does not create descriptors or stop workers."""
import hashlib
import json

SCHEMA = 'southside-root-issued-complete-mode-resume-v1'
UID = 'landsd/315025:0'
MODE = 'providerOriginal'
FACES = 11699
ALL_GROUND = 774477
SELECTED_GROUND = 25388
PRIOR_BATCH = 'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v1-20261012'
MANIFEST = '2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
SOURCE = '85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c'
FIELDS = {'schema', 'priorBatch', 'uid', 'arithmetic', 'sourceSHA256',
          'currentManifestSHA256', 'completeOriginalFaces',
          'completeFullOriginalGroundFacets', 'completeFullOriginalGroundSHA256',
          'selectedOriginalGroundFacets', 'selectedOriginalGroundSHA256',
          'completeWorldSHA256', 'checkpointPin', 'completionLogPin',
          'rootRetirementPin', 'rootCoverageValidationPin', 'inputPins',
          'codePins', 'currentAcceptance', 'installationApproved'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(value):
    assert set(value) == {'path', 'sha256'}
    assert isinstance(value['path'], str) and value['path'] and not value['path'].startswith('/')
    assert '..' not in value['path'].split('/')
    assert isinstance(value['sha256'], str) and len(value['sha256']) == 64
    assert all(c in '0123456789abcdef' for c in value['sha256'])


def validate_descriptor(descriptor, *, trusted, blobs, completed_v1_exists,
                        prior_processes_absent, prior_lease_released):
    """Validate only. ROOT constructs trusted pins separately after actual retirement.

    `trusted` is independently bound by the reviewed caller/ROOT contract, never
    copied from the candidate descriptor. `blobs` contains bytes actually read.
    This routine has no database, process, filesystem, or geometry side effects.
    """
    assert descriptor is not None, 'Missing descriptor fails closed'
    assert not completed_v1_exists, 'Completed v1 takes precedence over resume'
    assert prior_processes_absent is True and prior_lease_released is True
    assert set(descriptor) == FIELDS and set(trusted) == FIELDS
    assert descriptor == trusted, 'Candidate cannot supply its own trusted pins'
    assert descriptor['schema'] == SCHEMA and descriptor['priorBatch'] == PRIOR_BATCH
    assert descriptor['uid'] == UID and descriptor['arithmetic'] == MODE
    assert descriptor['sourceSHA256'] == SOURCE and descriptor['currentManifestSHA256'] == MANIFEST
    assert type(descriptor['completeOriginalFaces']) is int and descriptor['completeOriginalFaces'] == FACES
    assert type(descriptor['completeFullOriginalGroundFacets']) is int and descriptor['completeFullOriginalGroundFacets'] == ALL_GROUND
    assert type(descriptor['selectedOriginalGroundFacets']) is int and descriptor['selectedOriginalGroundFacets'] == SELECTED_GROUND
    assert descriptor['currentAcceptance'] is False and descriptor['installationApproved'] is False
    for key in ['completeFullOriginalGroundSHA256', 'selectedOriginalGroundSHA256', 'completeWorldSHA256']:
        pin({'path': key, 'sha256': descriptor[key]})
    for key in ['checkpointPin', 'completionLogPin', 'rootRetirementPin', 'rootCoverageValidationPin']:
        p = descriptor[key]; pin(p); assert sha(blobs[p['path']]) == p['sha256']
    for key in ['inputPins', 'codePins']:
        entries = descriptor[key]; assert isinstance(entries, list) and entries
        assert len({q['path'] for q in entries}) == len(entries)
        for p in entries:
            pin(p); assert sha(blobs[p['path']]) == p['sha256']
    retirement = json.loads(blobs[descriptor['rootRetirementPin']['path']])
    assert retirement['kind'] == 'root-issued-southside-complete-mode-retirement-v1'
    assert retirement['priorBatch'] == PRIOR_BATCH and retirement['currentManifestSHA256'] == MANIFEST
    assert retirement['priorLeaseReleased'] is True and retirement['noOwnedOrSupervisorProcessRemaining'] is True
    assert retirement['currentAcceptance'] is False
    validation = json.loads(blobs[descriptor['rootCoverageValidationPin']['path']])
    assert validation['testsRun'] == 13 and validation['exitCode'] == 0 and validation['result'] == 'OK'
    assert validation['helperSHA256'] in {p['sha256'] for p in descriptor['codePins']}
    assert validation['testSHA256'] in {p['sha256'] for p in descriptor['codePins']}
    return {'descriptorValidated': True, 'completeOriginalFaces': FACES,
            'currentAcceptance': False, 'installationApproved': False}


def validate_complete_mode(row, descriptor, *, world_bytes, current_records,
                           current_failed_ids, full_ground_sha256,
                           selected_ground_sha256, completion_log):
    """Bind all 11,699 saved original records; no clearance predicates rerun.

    Full-ground and selected-ground hashes must come from the caller's fresh,
    unchanged 774,477-facet decode and closed-AABB selection of 25,388 facets.
    Their source, decoder and input file pins are checked by validate_descriptor.
    """
    assert len(world_bytes) == FACES * 9 * 8
    assert full_ground_sha256 == descriptor['completeFullOriginalGroundSHA256']
    assert selected_ground_sha256 == descriptor['selectedOriginalGroundSHA256']
    assert sha(world_bytes) == descriptor['completeWorldSHA256'] == row['completeWorldSHA256']
    assert row['uid'] == UID and row['arithmetic'] == MODE and row['sourceSHA256'] == SOURCE
    assert row['completeUnfilteredSelectedGroundSHA256'] == selected_ground_sha256
    assert row['noCurrentFiniteRecomputation'] is True
    assert row['currentAcceptance'] is False and row['currentGroundReplacementProposed'] is False
    records = row['completeOriginalFaceComparisons']
    assert len(records) == len(current_records) == FACES
    assert all(type(q['sourceFace']) is int for q in records + current_records)
    assert [q['sourceFace'] for q in records] == list(range(FACES))
    assert [q['sourceFace'] for q in current_records] == list(range(FACES))
    for i, (saved, old) in enumerate(zip(records, current_records)):
        face_sha = sha(world_bytes[i * 72:(i + 1) * 72])
        assert saved['completeOriginalFacetSHA256'] == old['completeOriginalFacetSHA256'] == face_sha
        assert saved['orientationDescriptiveOnly'] == old['exactOrientationDiagnostic']
        assert saved['currentDrawnGroundComparisonRetainedVerbatim'] == old['currentDrawnGroundComparison']
        comparison = saved['unfilteredAuthenticatedOriginalGroundComparison']
        coarse, paired = comparison['coarse'], comparison['paired']
        assert type(coarse['existingOrdinaryClearanceBoundProved']) is bool
        for proof in [coarse] + ([] if paired is None else [paired]):
            assert proof['sourceFaceSHA256'] == face_sha
            assert proof['completeCurrentGroundSHA256'] == selected_ground_sha256
            assert proof['fullAcceptance'] is False and proof['installationApproved'] is False
            assert type(proof['existingOrdinaryClearanceBoundProved']) is bool
        assert (paired is None) == coarse['existingOrdinaryClearanceBoundProved']
        assert type(comparison['completeFiniteOrdinaryBoundProved']) is bool
        assert comparison['completeFiniteOrdinaryBoundProved'] == bool(coarse['existingOrdinaryClearanceBoundProved'] or (paired and paired['existingOrdinaryClearanceBoundProved']))
    failed = [q['sourceFace'] for q in records if not q['unfilteredAuthenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved']]
    failed_set = set(failed)
    upward = [q['sourceFace'] for q in records if q['sourceFace'] in failed_set and q['orientationDescriptiveOnly'] == 'upward-nonsteep']
    assert failed == row['allAuthenticatedGroundFailuresRetained']
    assert upward == row['authenticatedGroundUpwardFailuresRetained']
    assert row['allCurrentFailuresRetainedVerbatim'] == current_failed_ids
    lines = [json.loads(s) for s in completion_log.splitlines() if s.startswith('{')]
    assert any(q.get('uid') == UID and q.get('mode') == MODE and
               q.get('authenticatedFailures') == len(failed) and
               q.get('authenticatedUpwardFailures') == len(upward) for q in lines), 'A progress count is not a completed-mode record'
    return {'completeOrderedOriginalProofRecords': FACES, 'originalFailuresRetained': failed,
            'originalUpwardFailuresRetained': upward, 'currentAcceptance': False}
