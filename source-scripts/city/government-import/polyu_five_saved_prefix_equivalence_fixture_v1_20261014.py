"""UNEXECUTED saved-prefix fixture. No partition replay or candidate writing.

Authenticates 832 completed progress rows, checks indexed-mask selection against
saved IDs, and reconstructs only the already-saved polygon packing. This is not
an actual production-candidate capture or fresh source clearance/coverage proof.
"""
from pathlib import Path
from fractions import Fraction as F
import gzip, json, hashlib, sys
import numpy as np
import polyu_five_mask_source_plane_partition_fast_v1_20261014 as fast

ROOT = Path(__file__).resolve().parents[3]
PROPOSAL = ROOT / 'docs/astra-city/government-import/government-xl-polyu-five-mask-partition-acceleration-code-proposal-v1-20261014'

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def check(pin):
    path = ROOT / pin['path']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == pin['sha256']
    return path

def audit():
    contract = read(PROPOSAL / 'saved-prefix-fixture-pins.json')
    for pin in contract['evidenceRefs']:
        check(pin)
    source = read(check(contract['completedFeasibilityRef']))
    records = []
    for row in source['rows']:
        if row['uid'] in contract['eligibleUIDs']:
            mask = read(check(row['completeMask']))
            records.extend({**mask['rows'][i], 'uid':row['uid'], 'maskEvidence':row['completeMask']}
                           for i in mask['positiveMaskIDs'])
    prepared = fast.PreparedMasks(records)
    rows = []
    for pin in contract['progressRefs']:
        chunk = read(check(pin))
        assert chunk['oldPrivateProcessed'] == len(rows) + 64 and not chunk['unresolved']
        assert len(chunk['oldMappings']) == 64
        rows.extend(chunk['oldMappings'])
    assert len(rows) == 832 and [row['oldPrivateFace'] for row in rows] == list(range(832))
    cursor = 0; output = hashlib.sha256(); proof_bytes = hashlib.sha256()
    for row in rows:
        proof = row['completeExactMaskPartition']
        ideal = row['previousLineageVerbatim']['exactProposedPoints']
        face = fast.oracle.points(ideal)
        # Pure exact selector comparison; never call partition on actual source.
        if not proof.get('projectedVerticalOrZeroPreservedWhole'):
            _, relevant = prepared.relevant(fast.oracle.bb(face))
            assert relevant == proof['completeRelevantClosedAABBMasks']
        if proof.get('projectedVerticalOrZeroPreservedWhole') or F(proof['exactInsideMaskUnionIntrinsicArea']) == 0:
            packed = [row['wholeOldRawTriplet']]
        else:
            polygons = [[tuple(F(v) for v in point) for point in poly] for poly in proof['outside']]
            packed = [piece['packedPieceTriplet'] for piece in fast.oracle.packed_pieces(polygons, ideal)]
        assert row['newCandidateFaces'] == list(range(cursor, cursor + len(packed)))
        cursor += len(packed)
        output.update(np.asarray(packed,dtype='<f8').tobytes())
        proof_bytes.update(json.dumps(proof, sort_keys=True, separators=(',',':')).encode())
    for pin in contract['evidenceRefs']:
        check(pin)
    return dict(savedRows=832, reconstructedPrefixCandidateFaces=cursor,
                completeOrderedMaskOccurrences=len(prepared.masks), exactUniqueOrderedMasks=len(prepared.first_ids),
                savedPartitionRowsRetainedVerbatim=True, actualPartitionCalls=0,
                unchangedPackingKernel='polyu_five_mask_source_plane_partition_v1_20261014.packed_pieces',
                completeOrderedSavedProofSHA256=proof_bytes.hexdigest(),
                reconstructedOrderedPrefixPackedTripletsSHA256=output.hexdigest(),
                prefixPositionBufferNotPersistedSoNoClaimOfActualWholeIntermediateBufferRead=True,
                coverageFiniteRuntimeOrAcceptanceRecomputed=False)

if __name__ == '__main__':
    assert sys.argv[1:] == ['--check-saved-prefix-only']
    print(json.dumps(audit(),sort_keys=True))
