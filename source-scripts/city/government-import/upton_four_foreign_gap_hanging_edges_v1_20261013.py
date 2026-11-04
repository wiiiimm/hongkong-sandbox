"""Locate exact hanging-edge nominations for the completed four foreign gap packet."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import json, sys, time, uuid, subprocess
import numpy as np
import upton_scoped_four_foreign_gap_location_draft_v2_20261013 as Q
import upton_saved_hanging_subdivision_investigation_draft_v1_20261013 as H
from run import ROOT, HERE, read, save, connect, reservations

BATCH = 'government-xl-upton-four-foreign-gap-hanging-edges-v1-20261013'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PROPOSAL = DOC.with_name(BATCH + '-proposal')
LOCAL = HERE / 'local' / BATCH
JOB = '7a12f89dad439367d77416e8c33d433fde659908cb4aa1f5d89fc7d29658ae5c'


def inputs():
    pins = read(PROPOSAL / 'pins.json')
    for pin in pins['refs']:
        Q.check(pin)
    values = Q.load()
    result = read(Q.DOC / 'result.json')
    assert result['jobId'] == JOB
    for pin in result['evidenceRefs']:
        Q.check(pin)
    gaps = read(Q.DOC / 'complete-four-foreign-gap-locations-and-ancestors.json.gz')
    assert len(gaps['rows']) == 13 and gaps['uniqueForeignFacets'] == 4
    return pins, values, result, gaps


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not DOC.exists()
    last = time.monotonic()
    def pulse():
        nonlocal last
        if time.monotonic() - last > 15:
            assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease)
            last = time.monotonic()
    pins, values, result, gaps = inputs()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (JOB,)).fetchone() == ('complete', result)
    _, _, _, nomination, provenance, raw, drawn, _, _ = values
    ideal, actual, incidents, packed = [], [], defaultdict(list), {}
    protected = set()
    for i, origin in enumerate(provenance):
        points = origin.get('exactOriginalPlanePoints')
        triangle = tuple(tuple(F(v) for v in p) for p in points) if points is not None else H.prior.exact(raw[i])
        cast = np.asarray(raw[i], dtype=np.float32).astype('<f8')
        order = [0, 1, 2] if drawn[i].tobytes() == cast.tobytes() else [0, 2, 1]
        assert drawn[i].tobytes() == cast[order].tobytes()
        triangle = tuple(triangle[j] for j in order)
        real = H.prior.exact(drawn[i])
        ideal.append(triangle)
        actual.append(real)
        if origin.get('region') == 'wholeCurrentProtectionFacet':
            protected.add(i)
        for v, (point, real_point) in enumerate(zip(triangle, real)):
            assert point not in packed or packed[point] == real_point
            packed[point] = real_point
            incidents[point].append(dict(candidateFace=i, vertex=v))
        pulse()
    assert len(protected) == 68
    targets, point_rows = defaultdict(list), []
    cache = {}
    for row in gaps['rows']:
        saved = row['savedSourceRowVerbatim']
        proof = row['locationOnlyProof']
        for piece_id, polygon in enumerate(proof['exactRemainingPolygonsXZ']):
            points = [tuple(F(v) for v in p) for p in polygon]
            # Saved subtraction pieces are convex; vertex mean is an interior
            # nomination, never a whole-piece or whole-source coverage proof.
            point = tuple(sum(p[k] for p in points) / len(points) for k in range(2))
            candidate_ids = sorted({o['candidateFace'] for g in proof['completeSelectedGroundOrigins'] for o in g['allByteExactOrigins'] if o['kind'] == 'candidateNative'})
            key = (point, tuple(candidate_ids))
            if key not in cache:
                containing = []
                for i in candidate_ids:
                    area, sides = H.oriented_sides(point, ideal[i])
                    if area == 0 or not all(s >= 0 for s in sides):
                        continue
                    packed_area, packed_sides = H.oriented_sides(point, actual[i])
                    edges = [e for e, side in enumerate(packed_sides) if side < 0] if packed_area else []
                    containing.append(dict(candidateFace=i, packedRejectingEdges=edges,
                        packedProjectedCollapse=packed_area == 0, provenanceVerbatim=provenance[i]))
                cache[key] = containing
            relations = cache[key]
            context = dict(uid=saved['uid'], mode=saved['mode'], face=saved['face'],
                piece=piece_id, exactSavedGapPointXZ=point)
            point_rows.append(dict(**context, idealContainingPackedRejectingFacets=relations,
                noWholeCoverageOrRepairClaim=True))
            for relation in relations:
                for edge in relation['packedRejectingEdges']:
                    targets[relation['candidateFace'], edge].append(context)
            pulse()
    edge_rows = []
    for (i, edge), contexts in sorted(targets.items()):
        a, b = ideal[i][edge], ideal[i][(edge + 1) % 3]
        pa, pb = actual[i][edge], actual[i][(edge + 1) % 3]
        nodes = []
        for point in sorted(incidents):
            if not all(min(a[k], b[k]) <= point[k] <= max(a[k], b[k]) for k in (0, 2)):
                continue
            protected_incident = any(z['candidateFace'] in protected for z in incidents[point])
            relation = H.subdivision_relation(point, a, b, packed[point], pa, pb,
                i in protected, protected_incident)
            if relation is not None:
                nodes.append(dict(exactIdealXYZ=point, actualPackedXYZ=packed[point], **relation,
                    completeVertexIncidents=incidents[point]))
            pulse()
        edge_rows.append(dict(candidateFace=i, edge=edge, provenanceVerbatim=provenance[i],
            exactIdealLongEdgeXYZ=[a, b], actualPackedLongEdgeXYZ=[pa, pb],
            completeInteriorSubdivisionNodes=nodes, savedGapContexts=contexts,
            protectedTarget=i in protected, noGeometryOrCoverageCredit=True))
    DOC.mkdir()
    save(DOC / 'four-foreign-gap-hanging-edge-nominations.json.gz', Q.serial(dict(
        pointRows=point_rows, rejectingEdgeRows=edge_rows, completeCandidateFacets=len(raw),
        wholeCurrentProtectedFacets=68, all13SavedRowsRetained=True, all4ForeignFacetsRetained=True,
        sourceOnly=True, repairConstructed=False, currentAcceptance=False, physicalAccepted=False)))
    refs = pins['refs'] + result['evidenceRefs'] + [Q.ref(PROPOSAL / 'pins.json')]
    refs += [Q.ref(p) for p in DOC.iterdir() if p.is_file()]
    for pin in refs:
        Q.check(pin)
        pulse()
    Q.load()  # Re-check the complete original pinned tuple, not only our output.
    assert reservations.owns(lease)
    Q.prior.baseline.module(Q.prior.baseline.FREEZER, 'upton_foreign_edge_freezer').freeze(
        BATCH, 'exact-saved-four-foreign-gap-hanging-edge-nominations-only',
        [Q.check(pin) for pin in {(p['path'], p['sha256']): p for p in refs}.values()],
        dict(uids=Q.prior.baseline.OWNED + [Q.prior.baseline.SECONDARY, Q.prior.baseline.NATIVE],
            sourceOnly=True, physicalAccepted=False, currentAcceptance=False, newlyInstalled=0))


def main():
    if '--preflight-only' in sys.argv:
        inputs()
        print(json.dumps(dict(passed=True, noLease=True, noGeometryPredicates=True)))
        return
    if '--owned' in sys.argv:
        return owned()
    assert '--inspect-four-foreign-hanging-edges-only' in sys.argv
    assert not DOC.exists() and not LOCAL.exists()
    inputs()
    uids = Q.prior.baseline.OWNED + [Q.prior.baseline.SECONDARY, Q.prior.baseline.NATIVE, Q.prior.baseline.FOREIGN]
    resources = ['building:' + u for u in uids] + ['terrain-patch:' + u for u in uids] + ['immutable-source-proof:' + BATCH]
    claim = reservations.claim('upton-four-foreign-edges-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
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
