"""Byte-exact saved-nomination binding; no terrain computation or acceptance."""
import hashlib
import math
import struct


def triplet_bytes(face):
    assert len(face) == 3 and all(len(point) == 3 for point in face)
    values = [float(value) for point in face for value in point]
    assert all(math.isfinite(value) for value in values)
    return struct.pack('<9d', *values)


def validate_binding(new, previous, original, *, target, protected_count):
    """Check the one new split and exact composition with the saved old map."""
    before = previous['candidateRawPositionTriplets']
    after = new['candidateRawPositionTriplets']
    mapping = new['computedCurrentRing12PreviousCandidateMapping']
    assert len(after) == len(before) + 1 and len(mapping) == len(before)
    assert 0 <= target < len(before)
    assert [row['candidateFace'] for row in new['candidateFaceProvenance']] == list(range(len(after)))
    assert [row['oldCandidateFace'] for row in mapping] == list(range(len(before)))
    assert [face for row in mapping for face in row['newCandidateFaces']] == list(range(len(after)))
    for old_id, row in enumerate(mapping):
        ids = row['newCandidateFaces']
        assert len(ids) == (2 if old_id == target else 1)
        assert row['allOldRawBytesUnchanged'] is (old_id != target)
        for new_id in ids:
            record = new['candidateFaceProvenance'][new_id]
            assert record['rawNominationFaceSHA256'] == hashlib.sha256(triplet_bytes(after[new_id])).hexdigest()
            if old_id != target:
                assert triplet_bytes(after[new_id]) == triplet_bytes(before[old_id])
                expected = {**previous['candidateFaceProvenance'][old_id], 'candidateFace': new_id}
                assert record == expected
    old_map = previous['completeOldNewIndexMapping']
    new_map = new['completeOldNewIndexMapping']
    assert len(old_map) == len(new_map) == len(original['candidateRawPositionTriplets'])
    for old_id, (old, current) in enumerate(zip(old_map, new_map)):
        assert old['oldCandidateFace'] == current['oldCandidateFace'] == old_id
        expected = {**old,
            'newCandidateFaces': [face for prior in old['newCandidateFaces'] for face in mapping[prior]['newCandidateFaces']],
            'allOldRawBytesUnchanged': old['allOldRawBytesUnchanged'] and target not in old['newCandidateFaces']}
        assert current == expected
        if current['allOldRawBytesUnchanged']:
            assert len(current['newCandidateFaces']) == 1
            assert triplet_bytes(after[current['newCandidateFaces'][0]]) == triplet_bytes(original['candidateRawPositionTriplets'][old_id])
    assert [face for row in new_map for face in row['newCandidateFaces']] == list(range(len(after)))
    protected = previous['protectedWholeCurrentTripletsUnchanged']
    assert len(protected) == len(new['protectedWholeCurrentTripletsUnchanged']) == protected_count
    for old, current in zip(protected, new['protectedWholeCurrentTripletsUnchanged']):
        prior = old['newCandidate']
        assert prior != target and len(mapping[prior]['newCandidateFaces']) == 1
        expected = {**old, 'newCandidate': mapping[prior]['newCandidateFaces'][0]}
        assert current == expected
        assert triplet_bytes(after[current['newCandidate']]) == triplet_bytes(before[prior])
    assert new['originalNomination'] == previous['originalNomination']
    assert new['originalSourceTriplets'] == previous['originalSourceTriplets']
    assert new['exactSourceFamilyPartitionProof'] == previous['exactSourceFamilyPartitionProof']
    assert new['completeSavedFailuresVerbatim'] == previous['completeSavedFailuresVerbatim']
    assert new['completeUnchangedSource35677CandidateFamily'] == previous['completeUnchangedSource35677CandidateFamily']
    assert new['allOther11575RawCandidateTripletsUnchanged'] is True
    assert new['allFreshActualDrawAndFullActorRuntimeAcceptancePending'] is True
    assert new['physicalAccepted'] is False and new['installationApproved'] is False
    assert new['originalBuildingGeometryPoseChanges'] == 0
    return True
