"""Independent bounded-domain, lineage and original-byte audit; no acceptance."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-school-ramp-return-independent-readback-v1-20261025'
OLD = 'government-xl-quality-music-school-three-original-inset-v1-20261025'
NEW = 'government-xl-quality-music-school-original-ramp-return-v5-20261025'
RAMPS = 'government-xl-quality-music-school-podium-eight-ramp-context-v1-20261025'


def coefficients(t):
    return np.linalg.solve(np.column_stack((t[:, 0], t[:, 2], np.ones(3))), t[:, 1])


def main():
    out = BASE / BATCH
    assert not out.exists()
    receipts, pins, refs = {}, {}, [Path(__file__)]

    def take(batch, path):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    take(OLD, BASE / OLD / 'terrain-source-context.json')
    a = take(OLD, ROOT / receipts[OLD]['candidate']['path'])
    proof = take(NEW, BASE / NEW / 'inset-proof.json.gz')
    b = take(NEW, ROOT / receipts[NEW]['candidate']['path'])
    ramps = np.asarray([r['vertices'] for r in take(RAMPS, BASE / RAMPS / 'summary.json')['rows']])
    assert receipts[OLD]['sourceSHA256ByUid'] == receipts[NEW]['sourceSHA256ByUid']
    assert {k: v for k, v in a.items() if k not in ('meta', 'nativeMesh')} == {k: v for k, v in b.items() if k not in ('meta', 'nativeMesh')}
    for key in ('meta', 'nativeMesh'):
        excluded = ('source',) if key == 'meta' else ('source', 'position', 'index', 'sourceOverlap')
        assert {k: v for k, v in a[key].items() if k not in excluded} == {k: v for k, v in b[key].items() if k not in excluded}
        assert {k: v for k, v in a[key]['source'].items() if k != 'numericalCoverageGap'} == {k: v for k, v in b[key]['source'].items() if k not in ('authoredRampInset', 'numericalCoverageGap')}

    def faces(p):
        m = p['nativeMesh']
        return np.asarray(m['position']).reshape(-1, 3)[np.asarray(m['index']).reshape(-1, 3)]

    old, new = faces(a), faces(b)
    core, outer = (shapely.from_wkt(proof[k]) for k in ('coreWKT', 'outerWKT'))
    ramp_planes = np.asarray([coefficients(t) for t in ramps])
    assert len(proof['outputLineage']) == len(new)
    changed = set(proof['changedTerrainFaceIndices'])
    children, untouched = {}, set()
    max_lowering = max_outside_residual = max_core_residual = max_boundary_residual = 0.
    for t, line in zip(new, proof['outputLineage']):
        i = line['parentFace']
        p = shapely.Polygon(t[:, [0, 2]])
        if line['kind'] == 'unchanged':
            assert i not in changed and i not in untouched and np.array_equal(t, old[i])
            untouched.add(i)
            continue
        assert i in changed
        children.setdefault(i, []).append(p)
        assert p.difference(shapely.Polygon(old[i][:, [0, 2]])).area < 1e-8
        xz = t[:, [0, 2]]
        xy1 = np.column_stack((xz, np.ones(3)))
        parent_y = xy1 @ coefficients(old[i])
        floor_y = np.min(xy1 @ ramp_planes.T, axis=1)
        assert np.all(t[:, 1] <= parent_y + 1e-8)
        max_lowering = max(max_lowering, float((parent_y - t[:, 1]).max()))
        if line['kind'] == 'parent-fragment':
            residual = float(abs(parent_y - t[:, 1]).max())
            max_outside_residual = max(max_outside_residual, residual)
            assert residual < 1e-8
        else:
            assert line['kind'] in ('ramp-plane-core', 'ramp-derived-return')
            assert p.difference(outer).area < 1e-8
            assert np.all(t[:, 1] >= np.minimum(parent_y, floor_y) - 1e-8)
            if line['kind'] == 'ramp-plane-core':
                assert p.difference(core).area < 1e-8
                residual = float(abs(t[:, 1] - floor_y).max())
                max_core_residual = max(max_core_residual, residual)
                assert residual < 1e-8
            for vertex, y in zip(t, parent_y):
                if shapely.Point(vertex[[0, 2]]).distance(outer.boundary) < 1e-8:
                    residual = abs(float(vertex[1] - y))
                    max_boundary_residual = max(max_boundary_residual, residual)
                    assert residual < 1e-8
    assert set(children) == changed and untouched | changed == set(range(len(old)))
    max_area_error = 0.
    for i, polys in children.items():
        union = shapely.union_all(polys)
        parent = shapely.Polygon(old[i][:, [0, 2]])
        error = max(union.symmetric_difference(parent).area, abs(sum(p.area for p in polys) - union.area))
        max_area_error = max(max_area_error, error)
        assert error < 1e-6
    assert abs(max_lowering - proof['maximumLoweringM']) < 1e-8
    result = dict(uids=receipts[NEW]['uids'], passed=True, oldTerrainFaces=len(old), newTerrainFaces=len(new), exactUnchangedTerrainFaces=len(untouched), changedParentFaces=len(changed), maximumLoweringM=max_lowering, maximumOutsidePlaneResidualM=max_outside_residual, maximumCoreOriginalRampPlaneResidualM=max_core_residual, maximumOuterBoundaryParentResidualM=max_boundary_residual, maximumParentPartitionAreaErrorM2=max_area_error, sourceSHA256ByUid=receipts[NEW]['sourceSHA256ByUid'], sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, qualification='Independent complete per-parent projected partition and unchanged-face audit. Lowering stays inside bounded return, never below the minimum original ramp plane or above the parent. Core vertices lie on the minimum original ramp plane; outer boundary vertices meet original parent height. This does not claim actual-site visual acceptance or new global engineering guarantees.')
    out.mkdir()
    save(out / 'summary.json', result)
    module('school_ramp_return_readback_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'independent-original-ramp-bounded-return-readback', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
