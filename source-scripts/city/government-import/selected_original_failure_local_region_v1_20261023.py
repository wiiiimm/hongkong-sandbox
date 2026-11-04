"""Nominate a failure-local terrain edit without weakening whole-source checks."""
import argparse
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'parent', 'uid']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, cache = [Path(__file__)], {}
    def take(batch, path):
        if batch not in cache:
            cache[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        assert digest(path.read_bytes()) == cache[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(a.capture, base / a.capture / 'selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == a.uid)
    runtime = take(a.capture, HERE / 'local' / a.capture / 'runtime-geometry.json.gz')
    g = next(r for r in runtime['rows'] if r['uid'] == a.uid)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == g['sourceSHA256']
    refs.append(asset)
    tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
    ground = np.asarray(g['drawnGroundGeometry']).reshape(-1, 3, 3)
    parent = take(a.parent, HERE / 'local' / a.parent / 'parent.json')
    for name, sha in parent['inputHashes'].items():
        path = ROOT / name
        assert digest(path.read_bytes()) == sha
        refs.append(path)
    assert parent['inputHashes']['3d-viewer/city/data/manifest.json'] == selected['manifestSHA256']
    lo, hi = tri.min((0, 1)), tri.max((0, 1))
    keep = (ground[:, :, 0].max(1) >= lo[0]-1) & (ground[:, :, 0].min(1) <= hi[0]+1) & (ground[:, :, 2].max(1) >= lo[2]-1) & (ground[:, :, 2].min(1) <= hi[2]+1)
    ground = ground[keep]
    polys = shapely.polygons(ground[:, :, [0, 2]])
    valid = shapely.area(polys) > 1e-10
    ground, polys = ground[valid], polys[valid]
    points = np.concatenate([tri, tri.mean(1)[:, None, :]], axis=1)
    tool = module('failure_local_sampler', HERE / 'xl-final-script-pass.py')
    heights = tool.s.context.shared.samples(points[:, :, [0, 2]].reshape(-1, 2), ground, shapely.STRtree(polys)).reshape(-1, 4)
    assert np.isfinite(heights).all(), 'Missing current terrain requires whole coverage investigation'
    gaps = points[:, :, 1] - heights
    failures = np.flatnonzero((gaps < -.5).any(1))
    assert len(failures), 'No sampled burial failures to nominate'
    projection = shapely.union_all([shapely.MultiPoint(f[:, [0, 2]]).convex_hull for f in tri[failures]])
    core = projection.buffer(1, join_style='mitre')
    outer = core.buffer(3, join_style='mitre')
    baseline = np.asarray(parent['triangles'])
    lows = np.flatnonzero(baseline[:, :, 1].min(1) < 1.2)
    lowrows = []
    for i in lows:
        polygon = shapely.MultiPoint(baseline[i][:, [0, 2]]).convex_hull
        lowrows.append(dict(parentFace=int(i), minimumY=float(baseline[i, :, 1].min()), distanceFromEditM=float(polygon.distance(outer))))
    result = dict(uids=[a.uid], sourceSHA256=row['sourceSHA256'], sourceFaces=len(tri), nominatedFaces=failures.tolist(), minimumSampleGapM=float(gaps.min()), coreWKT=core.wkt, outerWKT=outer.wkt, projectionWKT=projection.wkt, existingLowFaces=lowrows, lowFacesStrictlyDisjoint=all(r['distanceFromEditM'] > 0 for r in lowrows), installationApproved=False, sourceGeometryChanges=0, status='failure-local-edit-region-nomination', qualification='Every literal vertex/centroid burial negative nominates its whole source face. This is discovery only, not exact coverage or whole-source acceptance. Smaller terrain edits must still pass all current source/rim/four-world/continuous/identity/neighbour/browser guards. No low-face waiver or source edits.')
    save(out / 'summary.json', result)
    refs.append(HERE / 'xl-final-script-pass.py')
    module('failure_local_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'failure-local-original-terrain-edit-nomination', refs, result)
    print(dict(sourceFaces=len(tri), nominatedFaces=len(failures), lowFacesStrictlyDisjoint=result['lowFacesStrictlyDisjoint']), flush=True)


if __name__ == '__main__':
    main()
