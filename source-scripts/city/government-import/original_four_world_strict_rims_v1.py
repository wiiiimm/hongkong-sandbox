"""Check ordinary complete-source clearance and regenerated strict rims in four worlds.

No role exceptions: changed XZ, unused vertices or missing continuous minima stop
this adapter rather than transferring an incomplete proof.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'runtime', 'attributes', 'continuous', 'uid']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, cached = [Path(__file__)], {}

    def take(batch, path):
        if batch not in cached:
            cached[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == cached[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    r = next(r for r in take(a.runtime, base / a.runtime / 'selection.json.gz')['rows'] if r['uid'] == a.uid)
    g = next(r for r in take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows'] if r['uid'] == a.uid)
    attr = next(r for r in take(a.attributes, base / a.attributes / 'attributes.json.gz')['rows'] if r['uid'] == a.uid)
    ctx = take(a.continuous, base / a.continuous / (a.uid.split('/')[1] + '.json.gz'))
    assert ctx['wholeSourceUncoveredFaces'] == 0 and not ctx['continuousAffectedFaces']
    asset = ROOT / r['candidate']['path']
    assert digest(asset.read_bytes()) == r['sourceSHA256'] == g['sourceSHA256'] == attr['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attr['completeLiteralWorldPosition']).reshape(-1, 3)
    assert len(set(ix.ravel())) == len(literal), 'Unused source vertices require their own original transform capture'
    original_tri = decode_original_world_triangles(asset.read_bytes())
    original = literal.copy()
    original[ix.reshape(-1)] = original_tri.reshape(-1, 3)
    assert np.array_equal(original[ix], original_tri)
    lt = literal[ix]
    assert digest(lt.tobytes()) == ctx['sourceBinding']['decodedWorldTrianglesSHA256']
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    polygons = shapely.polygons(ground[:, :, [0, 2]])
    valid = shapely.area(polygons) > 1e-10
    ground, polygons = ground[valid], polygons[valid]
    tree = shapely.STRtree(polygons)
    sampler = module('four_strict_rim_sampler', HERE / 'xl-final-script-pass.py')
    worlds = dict(original=original, literal=literal,
                  leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3),
                  balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3))
    rows = []
    for mode, vertices in worlds.items():
        tri = vertices[ix]
        assert np.array_equal(tri[:, :, [0, 2]], lt[:, :, [0, 2]])
        # Positive, close binary heights satisfy Sterbenz exact subtraction.
        assert np.all(tri[:, :, 1] > .5 * lt[:, :, 1]) and np.all(tri[:, :, 1] < 2 * lt[:, :, 1])
        delta = np.abs(tri[:, :, 1] - lt[:, :, 1]).max(1)
        minima = np.array([c['minimum']['minimumGapM'] for c in ctx['faces']])
        lower = np.nextafter(minima - delta, -np.inf)
        assert lower.min() >= -.5, 'New continuous source clearance failure'
        bottom = float(vertices[:, 1].min())
        samples = original_samples(vertices, ix, bottom)
        assert all(s['originalIncidentFaces'] for s in samples)
        points = np.asarray([s['point'] for s in samples])
        heights = sampler.s.context.shared.samples(points[:, [0, 2]], ground, tree)
        assert np.isfinite(heights).all()
        gaps = points[:, 1] - heights
        low = points[:, 1] <= bottom + .35
        assert low.any() and gaps.min() >= -.5 and gaps[low].min() <= .1 and gaps[low].max() <= 1
        assert np.any((gaps[low] >= -.1) & (gaps[low] <= .1)), 'Missing strict grade anchor'
        item = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()), completeSourceFaces=len(tri),
                    completeRuntimeSamples=len(samples), lowRimSamples=int(low.sum()),
                    minimumSampleGapM=float(gaps.min()), minimumRimGapM=float(gaps[low].min()),
                    maximumRimGapM=float(gaps[low].max()), maximumYDisplacementM=float(delta.max()),
                    continuousClearanceLowerBoundM=float(lower.min()), passed=True)
        rows.append(item)
        print(item, flush=True)
    result = dict(uids=[a.uid], sourceSHA256=r['sourceSHA256'], rows=rows, installationApproved=False,
                  sourceGeometryChanges=0, newlyInstalled=0,
                  qualification='Every ordinary source face keeps continuous clearance via identical XZ/convex Y bounds. All indexed original vertices and original sampling rules regenerated in each source representation; strict -.5m clearance, .1m minimum-contact and1m rim maximum unchanged. No exceptions, current-neighbour, identity or publication approval.')
    save(doc / 'summary.json', result)
    refs.extend(HERE / n for n in ['original_wall_rim_accounting_20261009.py',
                                  'exact_packed_world_geometry_20261009.py', 'xl-final-script-pass.py'])
    module('four_strict_rim_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'complete-four-world-ordinary-clearance-and-strict-rims', refs, result)


if __name__ == '__main__':
    main()
