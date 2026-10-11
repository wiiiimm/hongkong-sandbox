"""Recognise only the exact immutable Lippo preapply approval attempt.

Pure phase guard, never an absence/installed-state waiver or physical approval.
Live caller must independently reload all declared file pins and Neon rows.
"""
import hashlib
import json

UID = 'landsd/239465:0'
SOURCE = '2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c'
SNAPSHOT = '8d35b6f1d6f6bcdc'
PREVIOUS = '0063f9701137947c'
MANIFEST = '4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
ATTEMPT = 'government-xl-lippo-tower-current-basic-unchanged-installed-v1-20261011'
EVIDENCE = 'docs/astra-city/government-import/' + ATTEMPT + '/acceptance.json'
EVIDENCE_SHA = 'f191d93907f340180e7dfd6eb87122620c6f15325fad9d8a8362c62ef2280ff1'
REQUEST = ATTEMPT + '-approved-' + SNAPSHOT
EVENT_ID = 11922
OWNER = 'lippo-unchanged-install-463f45f1-bddb-448b-9c0d-be263e9022e7'
TOKEN = '70e2a2f9-36e3-48b3-a773-99c942e13792'

def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)

def verify(context, reviews, events, current_refs, current_files):
    assert context['uid'] == UID and context['sourceSHA256'] == SOURCE
    assert context['snapshotId'] == SNAPSHOT and context['previousSnapshotId'] == PREVIOUS
    assert context['eventId'] == EVENT_ID and context['requestId'] == REQUEST
    assert context['sourceOnly'] is True and context['publication'] is False
    assert context['installationApproved'] is False and context['newlyInstalled'] == 0
    assert current_refs == context['exactLiveFiles']
    assert current_files == context['fixtureFiles']
    assert current_refs['attemptAcceptance'] == dict(path=EVIDENCE, sha256=EVIDENCE_SHA)
    assert current_refs['manifest'] == dict(path='3d-viewer/city/data/manifest.json', sha256=MANIFEST)
    assert len(reviews) == len(events) == 1
    assert reviews == context['liveReadOnlyNeonRows']['model_reviews']
    assert events == context['liveReadOnlyNeonRows']['model_review_events']
    row, event = reviews[0], events[0]
    assert row['uid'] == event['uid'] == UID
    assert row['snapshot_id'] == event['snapshot_id'] == SNAPSHOT
    assert row['review_state'] == event['review_state'] == 'approved-for-integration'
    assert row['source_state'] == 'prepared-for-review' and row['source_sha256'] == SOURCE
    assert row['result'] == event['result']
    assert event['id'] == EVENT_ID and event['request_id'] == REQUEST
    assert event['owner'] == OWNER and event['token'] == TOKEN
    result = row['result']
    assert result['evidence'] == EVIDENCE and result['sha256'] == EVIDENCE_SHA
    assert result['source_sha256'] == SOURCE and result['productionPublished'] is False
    assert result['wholeLandmarkComplete'] is False
    assert result['effort']['run_id'] == SNAPSHOT and result['effort']['output_ref'] == EVIDENCE
    assert event['effort'] == result['effort']
    attempt = current_files['attemptAcceptance']
    assert attempt['batch'] == ATTEMPT and attempt['uids'] == [UID]
    assert attempt['sourceSHA256s'] == {UID: SOURCE}
    assert attempt['checksPassed'] is True and attempt['passed'] is True
    assert attempt['publication'] is False and attempt['newlyInstalled'] == 0
    assert attempt['modelGeometryChanges'] == 0 and attempt['terrainProposalGeometryChanged'] is False
    assert attempt['manifestBeforeSHA256'] == MANIFEST and attempt['livePublicationRequired'] is True
    assert attempt['wholeBasicReaccepted'] is False and attempt['originalGovernmentPodiumUsedAsRuntimeSupport'] is False
    pending, previous, pointer = [current_files[k] for k in ['pendingInventory', 'previousInventory', 'pointer']]
    assert pending['snapshotId'] == SNAPSHOT and pending['derivedFrom'] == previous['snapshotId'] == PREVIOUS
    assert pointer['snapshotId'] == PREVIOUS and pointer['inventory'] == current_refs['previousInventory']['path']
    assert current_refs['pendingInventory']['path'] == 'docs/astra-city/model-integration-20260909/source-review-inventory-' + SNAPSHOT + '.json'
    parts = pending['parts']
    assert parts == sorted(parts, key=lambda p: p['uid']) and len(parts) == len({p['uid'] for p in parts})
    old = {p['uid']: p for p in previous['parts']}
    new = {p['uid']: p for p in parts}
    assert set(new) == set(old) | {UID} and UID not in old
    assert all(new[u] == p for u, p in old.items())
    assert new[UID]['candidate'] == {'sha256': SOURCE}
    assert new[UID]['sourceProgress'] == 'prepared-for-review' and new[UID]['csuid'] == '3551817554T20050430'
    assert new[UID]['objectId'] == 239465 and new[UID]['knownHold'] is False
    # Same exact snapshot construction used by the original ledger producer.
    assert hashlib.sha256(encode([parts, attempt]).encode()).hexdigest()[:16] == SNAPSHOT
    role, receipt, stage = [current_files[k] for k in ['completeRole', 'completeRoleReceipt', 'stageAcceptance']]
    assert role['physicalAccepted'] is True and role['acceptanceReadyForStaging'] is True
    assert role['installationApproved'] is False and role['reasons'] == []
    assert role['sourceSHA256'] == SOURCE and role['uid'] == UID
    assert role['currentManifest'] == receipt['currentManifest'] == stage['currentManifest'] == current_refs['manifest']
    assert receipt['physicalAccepted'] and receipt['newlyInstalled'] == 0 and not receipt['publication']
    assert stage['passed'] and stage['failures'] == [] and stage['uids'] == [UID]
    assert stage['newlyInstalled'] == stage['sourceGeometryChanges'] == stage['terrainGeometryChanges'] == 0
    assert stage['publication'] is False and stage['livePublicationRequired'] is True
    return dict(contract='exact-own-lippo-approved-preapply-attempt-v1',
                uid=UID, snapshotId=SNAPSHOT, eventId=EVENT_ID,
                exactOwnApprovedPendingAttemptRecognised=True,
                installedStateAccepted=False, historicalReviewDeleted=False,
                numericOrPhysicalExemption=False, installationApproved=False)
