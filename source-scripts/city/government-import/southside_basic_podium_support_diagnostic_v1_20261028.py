"""Measure finite podium projection/base-height witnesses for all raw BASIC flags.

This is diagnostic evidence only. A height-band projection cannot approve a
structural support role, source ownership, identity, placement or installation.
"""
import argparse
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-basic-podium-support-diagnostic-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
RUNTIME = BASE / 'government-xl-southside-six-partition-three-original-runtime-v2-20261028'
REGRESSION = BASE / 'government-xl-southside-six-partition-basic-regressions-v1-20261028'
UID = 'landsd/315025:0'
BAND = .15  # Diagnostic distance only; never an acceptance tolerance.


def height_band(face, low, high):
    points = np.asarray(face, dtype=float)
    assert points.shape == (3, 3) and np.isfinite(points).all() and low <= high
    points = list(points)
    for level, direction in [(low, 1), (high, -1)]:
        output = []
        if not points:
            return np.empty((0, 3))
        previous = points[-1]
        previous_inside = direction * (previous[1] - level) >= 0
        for point in points:
            inside = direction * (point[1] - level) >= 0
            if inside != previous_inside:
                crossing = previous + (point - previous) * ((level-previous[1]) / (point[1]-previous[1]))
                output.append(crossing)
            if inside:
                output.append(point)
            previous, previous_inside = point, inside
        points = output
    return np.asarray(points).reshape(-1, 3)


def self_tests():
    face = np.array([[0, 0, 0], [2, 2, 0], [0, 0, 2]], dtype=float)
    polygon = height_band(face, .5, 1.5)
    assert abs(shapely.Polygon(polygon[:, [0, 2]]).area - 1) < 1e-12
    assert np.max(abs(polygon[:, 1] - polygon[:, 0])) < 1e-12
    assert abs(shapely.Polygon(height_band(face, 0, 1)[:, [0, 2]]).area - 1.5) < 1e-12
    assert len(height_band(face, 3, 4)) == 0
    flat = face.copy(); flat[:, 1] = 1
    assert shapely.Polygon(height_band(flat, 1, 1)[:, [0, 2]]).area == 2
    return ['sloping-band-area-and-plane', 'partial-band-area', 'absent-band-empty', 'horizontal-boundary-preserved']


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    refs, pins = [Path(__file__)], {}
    for batch in [RUNTIME, REGRESSION]:
        _, bound = authenticate(batch)
        refs.append(batch / 'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    tests = self_tests()
    regression = take(REGRESSION / 'summary.json')
    flagged = {r['uid'] for r in regression['basicFlags']}
    assert len(flagged) == 20
    forms = {r['building']['uid']: r['building'] for r in take(REGRESSION / 'neighbour-inputs.json.gz')['rows']}
    assert {'building:' + u for u in flagged | {UID}} <= set(lease['resources'])
    geometry = take(HERE / 'local' / RUNTIME.name / 'runtime-geometry.json.gz')
    source = [r for r in geometry['rows'] if r['uid'] == UID]
    assert len(source) == 1
    source = source[0]
    tri = np.asarray(source['position'], dtype=float).reshape(-1, 3)[np.asarray(source['index']).reshape(-1, 3)]
    assert np.isfinite(tri).all() and len(tri) == 11699
    selection = take(RUNTIME / 'selection.json.gz')
    row = next(r for r in selection['rows'] if r['uid'] == UID)
    assert source['sourceSHA256'] == row['sourceSHA256']
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256']
    refs.append(asset)
    projected = shapely.polygons(tri[:, :, [0, 2]])
    projection = shapely.union_all(projected[shapely.area(projected) > 0])
    normals = np.cross(tri[:, 1]-tri[:, 0], tri[:, 2]-tri[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    upward = np.flatnonzero((lengths > 0) & (normals[:, 1] > .5 * lengths))
    rows = []
    for uid in sorted(flagged):
        form = forms[uid]
        footprint = shapely.GeometryCollection()
        for ring in form['rings']:
            footprint = footprint.symmetric_difference(shapely.Polygon(ring))
        assert footprint.is_valid and footprint.area > 0
        base = form['base'] + (form.get('minimum') or 0)
        witnesses = []
        for faceid in upward:
            face = tri[faceid]
            if face[:, 1].max() < base-BAND or face[:, 1].min() > base+BAND:
                continue
            band = height_band(face, base-BAND, base+BAND)
            if len(band) < 3:
                continue
            area = shapely.Polygon(band[:, [0, 2]]).intersection(footprint)
            if area.area > 0:
                witnesses.append((int(faceid), area))
        covered = shapely.union_all([p for _, p in witnesses]).area if witnesses else 0
        rows.append(dict(uid=uid, name=form.get('name'), recordedBaseY=base, footprintM2=footprint.area,
                         podiumProjectionCoverageM2=projection.intersection(footprint).area,
                         distanceToPodiumProjectionM=footprint.distance(projection),
                         upwardFiniteBaseBandCoverageM2=covered, upwardFiniteBaseBandCoverageFraction=covered/footprint.area,
                         witnessingRuntimeFaces=[i for i, _ in witnesses]))
        assert reservations.owns(lease)
    result = dict(uids=[UID], flaggedBasicForms=20, rows=rows, sourceFaces=len(tri),
                  sourceSHA256=row['sourceSHA256'], runtimeGeometrySHA256=digest(tri.astype('<f8').tobytes()),
                  diagnosticHeightBandM=BAND, geometryKernelChecksPassed=tests,
                  rawGroundGapFlagsPreserved=True, physicalAccepted=False, identityAccepted=False,
                  installationApproved=False, sourceGeometryChanges=0,
                  qualification='All original podium runtime faces retained. Complete projected footprint areas and finite upward (>0.5 vertical cosine) source faces within a +/-0.15m diagnostic band around the current BASIC base, not an acceptance tolerance. Coverage does not prove load paths, collision clearance, model identity, current BASIC geometry correctness, structural support or installation eligibility. No raw neighbour flag cleared.')
    save(DOC / 'summary.json', result)
    assert reservations.owns(lease)
    module('southside_basic_podium_support_diagnostic_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'finite-original-podium-projection-and-base-band-witness-diagnostic', list(dict.fromkeys(refs)), result)
    print([dict(uid=r['uid'], projectionM2=r['podiumProjectionCoverageM2'], baseBandFraction=r['upwardFiniteBaseBandCoverageFraction']) for r in rows], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(self_tests())
        return
    if args.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    authenticate(RUNTIME)
    authenticate(REGRESSION)
    resources = ['building:' + r['uid'] for r in read(REGRESSION / 'summary.json')['basicFlags']] + ['building:' + UID]
    claim = reservations.claim('southside-basic-podium-witnesses-' + str(uuid.uuid4()), sorted(set(resources)), batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()
