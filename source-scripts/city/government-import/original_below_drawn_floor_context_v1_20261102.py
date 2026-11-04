"""Prove below-floor burial context without granting a source-role exception.

Every sampled buried face is retained. Only faces wholly below the minimum
actual drawn-ground vertex height can receive an exact coverage certificate.
This does not resolve any raw foundation, collision or publication failure.
"""
import argparse
import sys
import uuid
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate, face_diagnostics
from exact_original_projection_coverage_20261009 import exact_coverage
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['batch', 'runtime', 'attributes', 'uid']:
        p.add_argument('--' + name, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.runtime, a.attributes])
    base = ROOT / 'docs/astra-city/government-import'
    out, lp = base / a.batch, HERE / 'local' / a.batch / 'reservation.json'
    assert not out.exists()
    if not a.owned:
        assert not lp.parent.exists()
        c = reservations.claim('below-drawn-floor-' + str(uuid.uuid4()), ['building:' + a.uid], batch=a.batch, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}
    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selection = take(a.runtime, base / a.runtime / 'selection.json.gz')
    source = next(r for r in selection['rows'] if r['uid'] == a.uid)
    geom = next(r for r in take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    attr = next(r for r in take(a.attributes, base / a.attributes / 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    asset = ROOT / source['candidate']['path']
    assert digest(asset.read_bytes()) == source['sourceSHA256'] == geom['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ground = np.asarray(geom['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    assert len(ground) and np.isfinite(ground).all()
    floor = Fraction(float(ground[:, :, 1].min()))
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = {'original': decode_original_world_triangles(asset.read_bytes())}
    for name, field in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[name] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[ix]
    final = module('below_floor_actual_sampler', HERE / 'xl-final-script-pass.py')
    rows = []
    for mode, tri in worlds.items():
        assert len(tri) == source['triangles']
        sampled = face_diagnostics(final, tri, ground)
        faces = []
        for face in sampled['buriedFaces']:
            t = tri[face['faceIndex']]
            ceiling = Fraction(float(t[:, 1].max()))
            item = dict(face, entirelyBelowObservedGroundMinimum=ceiling < floor)
            if ceiling < floor:
                coverage = exact_coverage(t, ground)
                item.update(exactCoverage=coverage, exactVerticalSeparationLowerBoundM=str(floor - ceiling), belowFloorFullyCovered=coverage['exactProjectionCovered'])
            faces.append(item)
        record = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()), completeGroundSHA256=digest(ground.tobytes()), exactObservedGroundMinimumY=str(floor), completeSourceFaces=len(tri), uncoveredSampledFaces=sampled['uncoveredFaceIndices'], buriedFaces=faces)
        save(out / (mode + '.json.gz'), record)
        rows.append(dict(mode=mode, buriedFaces=len(faces), upwardBuriedFaces=sum(f['upward'] for f in faces), belowFloorCoveredFaces=sum(f.get('belowFloorFullyCovered', False) for f in faces), aboveFloorOrNotExactlyCoveredFaceIds=[f['faceIndex'] for f in faces if not f.get('belowFloorFullyCovered', False)]))
        print(rows[-1], flush=True)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == selection['manifestSHA256']
    refs.extend([manifest, HERE / 'exact_original_projection_coverage_20261009.py', HERE / 'china_ferry_current_foundations_v1_20261020.py', HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'xl-final-script-pass.py'])
    result = dict(uids=[a.uid], sourceSHA256=source['sourceSHA256'], rows=rows, sourceGeometryChanges=0, sourcePoseChanges=0, physicalAcceptance=False, sourceRoleAccepted=False, installationApproved=False, publication=False, qualification=__doc__)
    save(out / 'summary.json', result)
    module('below_drawn_floor_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-original-below-drawn-floor-context-no-acceptance', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
