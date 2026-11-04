"""Private computed-terrain nomination for the verified current-ring hanging node."""
from pathlib import Path
from fractions import Fraction as F
import json, sys, time, uuid, subprocess
import numpy as np
import upton_scoped_four_foreign_gap_location_draft_v2_20261013 as Q
import upton_four_foreign_gap_hanging_edges_v1_20261013 as E
from upton_source_family_exact_subdivision_v1_20261013 import subdivide_source_triangle
from run import ROOT, HERE, read, save, connect, reservations

BATCH = 'government-xl-upton-current-ring12-exact-subdivision-v1-20261013'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PROPOSAL = DOC.with_name(BATCH + '-proposal')
LOCAL = HERE / 'local' / BATCH
JOB = 'b73ec2b945ba6f2862458686a54d7eadf42948485a2d6ca0385dcbec946fdee0'


def inputs():
    pins = read(PROPOSAL / 'pins.json')
    for pin in pins['refs']:
        Q.check(pin)
    values = Q.load()
    receipt = read(E.DOC / 'result.json')
    assert receipt['jobId'] == JOB
    for pin in receipt['evidenceRefs']:
        Q.check(pin)
    edges = read(E.DOC / 'four-foreign-gap-hanging-edge-nominations.json.gz')
    eligible = [(r, n) for r in edges['rejectingEdgeRows'] for n in r['completeInteriorSubdivisionNodes'] if n['eligibleComputed3DHangingSubdivisionNomination']]
    assert len(eligible) == 1
    row, node = eligible[0]
    assert row['candidateFace'] == 1159 and row['edge'] == 2 and not row['protectedTarget']
    assert row['provenanceVerbatim']['kind'] == 'capturedCurrentRing' and row['provenanceVerbatim']['originalFace'] == 12
    assert not node['protectedWholeCurrentNodeIncident'] and not node['projectedOnlyDifferentHeightLayer']
    return pins, values, receipt, row, node


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not DOC.exists()
    last = time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic() - last > 15:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()
    pins, values, receipt, edge, nominated = inputs()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (JOB,)).fetchone() == ('complete', receipt)
    _, _, _, nomination, provenance, raw, drawn, _, _ = values
    origin = provenance[1159]
    points = origin.get('exactOriginalPlanePoints')
    original = tuple(tuple(F(v) for v in p) for p in points) if points is not None else tuple(tuple(F(v) for v in p) for p in raw[1159])
    cast = np.asarray(raw[1159], dtype=np.float32).astype('<f8')
    order = [0, 1, 2] if drawn[1159].tobytes() == cast.tobytes() else [0, 2, 1]
    assert drawn[1159].tobytes() == cast[order].tobytes()
    triangle = tuple(original[j] for j in order)
    assert Q.serial([triangle[2], triangle[0]]) == edge['exactIdealLongEdgeXYZ']
    node = tuple(F(v) for v in nominated['exactIdealXYZ'])
    proof = subdivide_source_triangle(triangle, node, 2)
    expected = np.asarray([float(F(v)) for v in nominated['actualPackedXYZ']], dtype='<f8')
    candidate, new_provenance, mapping = [], [], []
    for i, (face, record) in enumerate(zip(raw, provenance)):
        faces = [face]
        records = [record]
        if i == 1159:
            faces, records = [], []
            for part, piece in enumerate(proof['exactPiecesXYZ']):
                value = np.asarray([[float(v) for v in p] for p in piece], dtype='<f4').astype('<f8')
                for k, point in enumerate(piece):
                    if point in triangle:
                        value[k] = raw[i][order[triangle.index(point)]]
                    if point == node:
                        assert value[k].tobytes() == expected.tobytes()
                faces.append(value)
                records.append(dict(**record, computedFragment=True, savedInputByteExact=False))
                records[-1]['exactOriginalPlanePoints'] = Q.serial(piece)
                records[-1]['computedCurrentRingSubdivision'] = dict(oldCandidateFace=i,
                    originalCurrentFace=12, part=part, exactNodeXYZ=Q.serial(node),
                    governmentBuildingGeometryUnchanged=True, noOtherLayerBridge=True)
        ids = []
        for face, record in zip(faces, records):
            value = np.asarray(face, dtype='<f8')
            j = len(candidate)
            candidate.append(value)
            new_provenance.append({**record, 'candidateFace': j,
                'rawNominationFaceSHA256': Q.prior.sha(value)})
            ids.append(j)
        if i != 1159:
            assert len(ids) == 1 and candidate[ids[0]].tobytes() == raw[i].tobytes()
        mapping.append(dict(oldCandidateFace=i, newCandidateFaces=ids,
            allOldRawBytesUnchanged=i != 1159))
        pulse()
    candidate = np.asarray(candidate, dtype='<f8')
    assert candidate.shape == (11577, 3, 3)
    protected = []
    for old in nomination['protectedWholeCurrentTripletsUnchanged']:
        previous = old['newCandidate']
        current = mapping[previous]['newCandidateFaces']
        assert len(current) == 1 and previous != 1159
        assert candidate[current[0]].tobytes() == raw[previous].tobytes()
        protected.append({**old, 'newCandidate': current[0]})
    assert len(protected) == 68
    # Compose the original 11575 -> 11576 mapping with this 11576 -> 11577
    # mapping, retaining the earlier immutable subdivision's provenance.
    cumulative = []
    for old in nomination['completeOldNewIndexMapping']:
        previous = old['newCandidateFaces']
        cumulative.append({**old, 'newCandidateFaces': [j for i in previous for j in mapping[i]['newCandidateFaces']],
            'allOldRawBytesUnchanged': old['allOldRawBytesUnchanged'] and 1159 not in previous})
    output = {**nomination, 'candidateRawPositionTriplets': candidate.tolist(),
        'candidateFaceProvenance': new_provenance, 'completeOldNewIndexMapping': cumulative,
        'protectedWholeCurrentTripletsUnchanged': protected,
        'computedCurrentRing12PartitionProof': proof,
        'computedCurrentRing12PreviousCandidateMapping': mapping,
        'previousEdgeDiagnostic': Q.ref(E.DOC / 'result.json'),
        'allOther11575RawCandidateTripletsUnchanged': True,
        'allFreshActualDrawAndFullActorRuntimeAcceptancePending': True,
        'physicalAccepted': False, 'installationApproved': False,
        'originalBuildingGeometryPoseChanges': 0}
    DOC.mkdir()
    save(DOC / 'private-source-family-subdivision-nomination.json.gz', Q.serial(output))
    refs = pins['refs'] + receipt['evidenceRefs'] + [Q.ref(PROPOSAL / 'pins.json')]
    refs += [Q.ref(p) for p in DOC.iterdir() if p.is_file()]
    for pin in refs:
        Q.check(pin)
        pulse()
    Q.load()
    assert reservations.owns(lease)
    Q.prior.baseline.module(Q.prior.baseline.FREEZER, 'upton_ring12_nomination_freezer').freeze(
        BATCH, 'private-current-ring12-exact-representation-only',
        [Q.check(pin) for pin in {(p['path'], p['sha256']): p for p in refs}.values()],
        dict(uids=Q.prior.baseline.OWNED + [Q.prior.baseline.SECONDARY, Q.prior.baseline.NATIVE],
            sourceOnly=True, privateNomination=True, physicalAccepted=False, newlyInstalled=0))


def main():
    if '--preflight-only' in sys.argv:
        inputs()
        print(json.dumps(dict(passed=True, noLease=True, noSubdivision=True)))
        return
    if '--owned' in sys.argv:
        return owned()
    assert '--nominate-current-ring12-subdivision-only' in sys.argv
    assert not DOC.exists() and not LOCAL.exists()
    inputs()
    uids = Q.prior.baseline.OWNED + [Q.prior.baseline.SECONDARY, Q.prior.baseline.NATIVE, Q.prior.baseline.FOREIGN]
    resources = ['building:' + u for u in uids] + ['terrain-patch:' + u for u in uids] + ['immutable-source-proof:' + BATCH]
    claim = reservations.claim('upton-current-ring12-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
            'run', '--lease-file', str(LOCAL / 'reservation.json'), '--ttl', '3600', '--',
            sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
