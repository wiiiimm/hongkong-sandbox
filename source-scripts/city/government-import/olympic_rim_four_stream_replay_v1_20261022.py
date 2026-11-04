"""Replay all original rim witnesses and finite paths in four source streams.

Diagnostic only. Preserve failures, own endpoint ceilings and strict grade band.
"""
from pathlib import Path
from collections import Counter
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples
from pool_incident_wall_contacts_v1_20261017 import closest

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-olympic-rim-four-stream-replay-v1-20261022'


def key(w):
    return (w['kind'], tuple(w['originalIncidentFaces']), w['vertex'],
            w['point'][0], w['point'][2])


def transport(point, face, target):
    # Barycentric correspondence on an actual finite, nondegenerate source face.
    uv, _, _, _ = np.linalg.lstsq((face[1:] - face[0]).T,
                                 np.asarray(point) - face[0], rcond=None)
    weights = np.array([1 - uv.sum(), *uv])
    assert weights.min() >= -1e-8 and weights.max() <= 1 + 1e-8
    assert np.linalg.norm(weights @ face - point) <= .001
    return weights @ target


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    refs = [Path(__file__)]

    def take(batch, name, local=False):
        folder = BASE / batch
        _, pins = authenticate(folder)
        p = (HERE / 'local' / batch if local else folder) / name
        assert digest(p.read_bytes()) == pins[str(p.relative_to(ROOT))]
        refs.extend([folder / 'result.json', p])
        return read(p)

    runtime = 'government-xl-olympic-station-band-runtime-v1-20261022'
    selection = take(runtime, 'selection.json.gz')['rows'][0]
    g = take(runtime, 'runtime-geometry.json.gz', True)['rows'][0]
    attrs = take('government-xl-olympic-station-original-attributes-v1-20261022',
                 'attributes.json.gz')['rows'][0]
    old = take('government-xl-olympic-original-endpoint-paths-v2-20261022',
               'paths.json.gz')
    extra = take('government-xl-olympic-original-strict-anchor-paths-v1-20261022',
                 'paths.json.gz')
    paths = {key(r['witness']): r for r in old['rows'] if r['verifiedPath']}
    paths.update({key(r['witness']): r for r in extra['rows'] if r['verifiedPath']})
    assert len(paths) == 53
    ix = np.asarray(attrs['completeOriginalIndex']).reshape(-1, 3)
    literal = np.asarray(attrs['completeLiteralWorldPosition']).reshape(-1, 3)
    asset = ROOT / selection['candidate']['path']
    assert digest(asset.read_bytes()) == g['sourceSHA256']
    refs.append(asset)
    original_tri = decode_original_world_triangles(asset.read_bytes())
    original = literal.copy()
    original[ix.reshape(-1)] = original_tri.reshape(-1, 3)
    assert np.array_equal(original[ix], original_tri)
    streams = dict(original=original, literal=literal,
                   leftF32=np.asarray(attrs['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1, 3),
                   balancedF32=np.asarray(attrs['completeExplicitBalancedFloat32WorldPosition']).reshape(-1, 3))
    lt = literal[ix]
    assert digest(lt.tobytes()) == old['sourceWorldSHA256'] == extra['sourceWorldSHA256']
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    polygons = shapely.polygons(ground[:, :, [0, 2]])
    keep = shapely.area(polygons) > 1e-10
    ground, polygons = ground[keep], polygons[keep]
    tree = shapely.STRtree(polygons)
    sampler = module('olympic_four_rim_ground', HERE / 'xl-final-script-pass.py')
    literal_samples = original_samples(literal, ix, float(literal[:, 1].min()))
    rows = []
    for mode, position in streams.items():
        tri = position[ix]
        samples = original_samples(position, ix, float(position[:, 1].min()))
        assert Counter(map(key, samples)) == Counter(map(key, literal_samples)), 'Changed sample lineage requires fresh attribution'
        heights = sampler.s.context.shared.samples(np.asarray([s['point'] for s in samples])[:, [0, 2]], ground, tree)
        assert np.isfinite(heights).all()
        bottom = float(position[:, 1].min())
        warnings = []
        for sample, height in zip(samples, heights):
            gap = sample['point'][1] - float(height)
            if sample['point'][1] <= bottom + .35 and not -.5 <= gap <= 1:
                warnings.append(dict(**sample, ground=float(height), gap=gap))
        checked = []
        for w in warnings:
            record = paths.get(key(w))
            assert record, 'New unaccounted original rim warning'
            proof = record['verifiedPath']
            faces = proof['faces']
            oldpoints = np.asarray(proof['continuousPath'])
            points = [np.asarray(w['point'])]
            # Map each crossing on its incoming face, then independently verify
            # that the same point remains on both finite incident faces.
            points += [transport(oldpoints[k], lt[faces[k - 1]], tri[faces[k - 1]])
                       for k in range(1, len(oldpoints) - 1)]
            points.append(transport(oldpoints[-1], lt[faces[-1]], tri[faces[-1]]))
            residuals = [float(np.linalg.norm(closest(q, tri[f]) - q))
                         for k, f in enumerate(faces) for q in points[k:k + 2]]
            anchor = points[-1]
            height = float(sampler.s.context.shared.samples(anchor[None, [0, 2]], ground, tree)[0])
            gap = float(anchor[1] - height)
            ceiling = float(max(points[0][1], anchor[1]))
            maximum = float(max(p[1] for p in points))
            checked.append(dict(witness=w, faces=faces, continuousPath=[p.tolist() for p in points],
                                maximumResidualM=max(residuals), gradeGapM=gap,
                                maximumPathHeightM=maximum, ownEndpointCeilingM=ceiling,
                                passed=bool(max(residuals) <= .001 and -.1 <= gap <= .1
                                            and maximum <= ceiling + 1e-9)))
        result = dict(mode=mode, sourceWorldSHA256=digest(tri.tobytes()),
                      originalSamples=len(samples), raisedOrBuriedRimWarnings=len(warnings),
                      verifiedPaths=sum(r['passed'] for r in checked),
                      failedPaths=[r for r in checked if not r['passed']],
                      rows=checked, installationApproved=False)
        save(doc / (mode + '.json.gz'), result)
        rows.append({k: v for k, v in result.items() if k not in ('rows', 'failedPaths')} |
                    dict(failedPaths=len(result['failedPaths'])))
        print(rows[-1], flush=True)
    result = dict(uids=old['uids'], rows=rows, allPathsPassed=all(r['failedPaths'] == 0 for r in rows),
                  sourceGeometryChanges=0, newlyInstalled=0, installationApproved=False,
                  qualification='All actual original sample lineages regenerated; every flagged finite path, strict grade anchor and own endpoint height replayed independently in four source representations. Raw runtime warnings retained. No foreign, identity, visual or publication approval.')
    save(doc / 'summary.json', result)
    refs.extend(HERE / p for p in ['original_wall_rim_accounting_20261009.py',
                                  'pool_incident_wall_contacts_v1_20261017.py',
                                  'exact_packed_world_geometry_20261009.py', 'xl-final-script-pass.py'])
    module('olympic_four_rim_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-four-stream-rim-finite-path-replay', refs, result)


if __name__ == '__main__':
    main()
