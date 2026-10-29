"""Measure actual BASIC upper-bottom / podium-roof coverage; no approval or edits."""
import json
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PREFIX = 'government-xl-kowloon-city-civic-five-after-fuying-'
PRIOR = PREFIX + 'base-only-regression-v1-20261030'
BATCH = PREFIX + 'basic-roof-support-v1-20261030'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
LEASE = LOCAL / 'reservation.json'
PAIRS = [('landsd/82290:0', 'landsd/82291:0'),
         ('landsd/159177:0', 'landsd/230911:0')]


def plane_surface(row, height):
    """Exact Float32 horizontal faces only; no buffering or gap tolerance."""
    positions = np.asarray(row['position']).reshape(-1, 3)
    triangles = positions[np.asarray(row['index']).reshape(-1, 3)]
    selected = triangles[(triangles[:, :, 1] == float(np.float32(height))).all(1)]
    polygons = [Polygon(t[:, [0, 2]]) for t in selected]
    polygons = [p for p in polygons if p.area > 0]
    assert polygons and all(p.is_valid for p in polygons)
    return unary_union(polygons), len(polygons)


def main():
    if '--owned' not in sys.argv:
        assert not DOC.exists() and not LOCAL.exists()
        keys = sorted({'building:' + uid for pair in PAIRS for uid in pair}
                      | {'terrain:city/data/terrain.json'})
        claim = reservations.claim(BATCH + '-' + str(uuid.uuid4()), keys,
                                   batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        lease = claim['reservation']
        save(LEASE, json.loads(json.dumps(lease, default=str)))
        try:
            subprocess.run([sys.executable, str(HERE / 'bounded_reserved_runner_v2_20261022.py'),
                            str(LEASE), sys.executable, __file__, '--owned'], cwd=ROOT, check=True)
        finally:
            if reservations.owns(lease):
                assert reservations.release(lease)['ok']
        return
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    _, pins = authenticate(BASE / PRIOR)
    refs = [Path(__file__), BASE / PRIOR / 'result.json']
    for filename in ('neighbour-inputs.json.gz', 'neighbour-checks.json'):
        path = BASE / PRIOR / filename
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
    inputs = read(refs[2])
    raw = read(refs[3])
    assert inputs['candidateIds'] == []
    for path, sha in inputs['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    mesh_input = dict(rows=inputs['rows'], currentInputHashes=inputs['inputHashes'],
                      manifestSHA256=digest(manifest.read_bytes()))
    save(DOC / 'mesh-input.json', mesh_input)
    tool = HERE / 'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs'
    subprocess.run(['node', str(tool), str((DOC / 'mesh-input.json').relative_to(ROOT)),
                    str((DOC / 'basic-meshes.json').relative_to(ROOT))], cwd=ROOT, check=True)
    meshes = read(DOC / 'basic-meshes.json')
    by_uid = {row['uid']: row for row in meshes['rows']}
    checks = {row['uid']: row for row in raw['rows']}
    assert {uid for uid, row in checks.items() if row['reasons']} == {p[0] for p in PAIRS}
    rows = []
    for upper, lower in PAIRS:
        u, l = by_uid[upper]['currentBuilding'], by_uid[lower]['currentBuilding']
        upper_base, lower_top = u['base'] + (u.get('minimum') or 0), l['base'] + l['height']
        bottom, bottom_faces = plane_surface(by_uid[upper], upper_base)
        roof, roof_faces = plane_surface(by_uid[lower], lower_top)
        missing = bottom.difference(roof)
        rows.append(dict(upper=upper, lower=lower, upperBase=upper_base, lowerTop=lower_top,
                         exactSourcePlanesEqual=upper_base == lower_top,
                         actualFloat32PlanesEqual=float(np.float32(upper_base)) == float(np.float32(lower_top)),
                         upperBottomFaces=bottom_faces, lowerRoofFaces=roof_faces,
                         upperBottomAreaM2=bottom.area, uncoveredBottomAreaM2=missing.area,
                         exactActualMeshCoverage=roof.covers(bottom), missingWKT=missing.wkt,
                         lowerRawRegressions=checks[lower]['reasons'],
                         upperRawRegression=checks[upper],
                         afterTerrainBelowUpperAtEveryGuardSample=checks[upper]['afterGap'][0] > 0))
    result = dict(rows=rows, actualBasicMeshes=len(meshes['rows']), originalsAvailable=False,
                  rawFlagsRetained=True, sourceGeometryChanges=0, runtimeChanges=0,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  qualification='Exact current BASIC renderer horizontal bottom/roof polygon coverage. No buffering, tolerance, source pose or terrain edits. Raw ground-gap warnings retained. Diagnostic graphics support only, not structural certification or installation approval.')
    save(DOC / 'summary.json', result)
    refs += [tool, DOC / 'mesh-input.json', DOC / 'basic-meshes.json']
    for path, sha in meshes['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    assert reservations.owns(lease)
    module('civic_basic_roof_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-current-BASIC-bottom-roof-coverage-diagnostic', refs, result)
    print(json.dumps(rows), flush=True)


if __name__ == '__main__':
    main()
