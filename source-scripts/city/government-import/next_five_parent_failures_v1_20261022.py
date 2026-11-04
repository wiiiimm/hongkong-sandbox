"""Measure failed current-parent constructions without granting rejection credit."""
from pathlib import Path
import math
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
PARENT = 'government-xl-next-five-original-replacement-checks-v1-20261022'
BATCH = 'government-xl-next-five-parent-failure-context-v1-20261022'


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    receipt, _ = authenticate(BASE / PARENT)
    refs = [Path(__file__), BASE / PARENT / 'result.json']
    output = []
    for row in receipt['rows']:
        if row['status'] != 'terrain-investigation':
            continue
        batch = row['batches']['terrain']
        result, pins = authenticate(BASE / batch)

        def take(path):
            assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
            refs.append(path)
            return read(path)

        refs.append(BASE / batch / 'result.json')
        failure = take(BASE / batch / 'failure.json')
        scope = take(BASE / batch / 'scope.json')
        item = dict(uid=row['uid'], failure=failure, bounds=scope['bounds'],
                    permanentRejection=False, installationApproved=False)
        parentpath = HERE / 'local' / batch / 'parent.json'
        if parentpath.exists():
            captured = take(parentpath)
            tri = np.asarray(captured['triangles'])
            union = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]]))
            extent = shapely.box(*scope['bounds'])
            missing, outside = extent.difference(union), union.difference(extent)
            item.update(parentFaces=len(tri), missingAreaM2=float(missing.area),
                        outsideAreaM2=float(outside.area))
            if not missing.is_empty:
                save(doc / (row['uid'].split('/')[1] + '-missing.json'),
                     shapely.to_geojson(missing))
                item['nextAction'] = 'Recover an explicit source-backed coastal terrain domain; the full rectangular parent premise is false. Do not bypass coverage.'
            else:
                parent = take(ROOT / '3d-viewer/city/data/terrain.json')
                g, w, h = parent['meta']['georef'], parent['w'], parent['h']

                def at(k):
                    rendered = parent.get('renderedElev', [])
                    a = rendered[k] if rendered else None
                    return a if a is not None else max(1.2, parent['elev'][k]) if parent['elev'][k] > 0 else -4

                def sample(x, z):
                    c, r = (x + 834500 - g['bE']) / g['aE'], (816500 - z - g['bN']) / g['aN']
                    i, j = max(0, min(w-2, math.floor(c))), max(0, min(h-2, math.floor(r)))
                    u, v = c-i, r-j
                    a, b, d, e = at(j*w+i), at(j*w+i+1), at((j+1)*w+i), at((j+1)*w+i+1)
                    return a+(b-a)*u+(d-a)*v if u+v <= 1 else e+(d-e)*(1-u)+(b-e)*(1-v)

                a, b, c, d = scope['bounds']
                vertices = np.unique(tri.reshape(-1, 3), axis=0)
                edge = [p for p in vertices if min(abs(p[0]-a), abs(p[0]-c), abs(p[2]-b), abs(p[2]-d)) < .002]
                assert edge
                item['currentParentVsRootBoundaryMaximumM'] = max(abs(float(y)-sample(float(x), float(z))) for x, y, z in edge)
                item['nextAction'] = 'Choose a parent scope that preserves existing refined boundary surfaces and joins the root; retain every affected existing terrain actor.'
        else:
            item['nextAction'] = 'Capture and account for current terrain faces crossing the proposed parent rectangle; do not drop or invent faces.'
        output.append(item)
    assert len(output) == 4
    summary = dict(rows=output, uids=[r['uid'] for r in output], newlyInstalled=0,
                   permanentRejections=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', summary)
    refs.append(ROOT / 'source-scripts/city/island-detail-integration/native_terrain_validation.py')
    module('parent_failure_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'measured-current-parent-construction-failures', refs, summary)
    print([{k: v for k, v in r.items() if k != 'failure'} for r in output], flush=True)


if __name__ == '__main__':
    main()
