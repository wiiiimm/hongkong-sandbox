"""Capture adjacent rectangular parent domains under unchanged coverage checks.

This supplies diagnostic parent bases for a coordinated terrain correction.
It constructs no replacement terrain and grants no placement/publication credit.
"""
import argparse
import json
import subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from inherited_parent_coverage_v1 import qualify
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    args = parser.parse_args()
    plan_path = (ROOT / args.plan).resolve()
    base = ROOT / 'docs/astra-city/government-import'
    assert plan_path.is_relative_to(base)
    plan = read(plan_path)
    batch = plan['batch']
    assert batch.startswith('government-xl-') and '/' not in batch
    out, local = base / batch, HERE / 'local' / batch
    assert not out.exists() and not local.exists()
    runtime = base / plan['runtime']
    receipt, pins = authenticate(runtime)
    assert receipt['uids'] == plan['uids'] and len(plan['uids']) == 1
    refs = [Path(__file__), plan_path, runtime / 'result.json', HERE / 'inherited_parent_coverage_v1.py',
            HERE / 'float32_coverage.py', HERE / 'native_patch_resolution.py']
    geometry_path = HERE / 'local' / plan['runtime'] / 'runtime-geometry.json.gz'
    assert digest(geometry_path.read_bytes()) == pins[str(geometry_path.relative_to(ROOT))]
    refs.append(geometry_path)
    geometry = next(r for r in read(geometry_path)['rows'] if r['uid'] == plan['uids'][0])
    triangles = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
    projection = shapely.union_all(shapely.polygons(triangles[:, :, [0, 2]]))
    outer = projection.buffer(1, join_style='mitre').buffer(3, join_style='mitre')
    regions = [shapely.box(*bounds) for bounds in plan['domains']]
    assert 1 < len(regions) <= 8
    for i, region in enumerate(regions):
        assert region.area > 0
        for other in regions[:i]:
            assert region.intersection(other).area == 0, 'Partition domains overlap'
    union = shapely.union_all(regions)
    assert union.covers(outer) and outer.distance(union.boundary) > 0, 'Whole model and return band must be inside partition union'
    tool = HERE / 'selected_original_parent_capture_v2.mjs'
    refs.append(tool)
    rows = []
    for index, bounds in enumerate(plan['domains']):
        scope_path = out / ('scope-' + str(index) + '.json')
        parent_path = local / ('parent-' + str(index) + '.json')
        save(scope_path, dict(uids=plan['uids'], bounds=bounds))
        subprocess.run(['node', str(tool), str(scope_path.relative_to(ROOT)), str(parent_path.relative_to(ROOT))],
                       cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
        captured = read(parent_path)
        assert captured['domain'] == bounds
        for name, sha in captured['inputHashes'].items():
            path = ROOT / name
            assert digest(path.read_bytes()) == sha
            if name in pins:
                assert pins[name] == sha, 'Captured renderer differs from original runtime'
            refs.append(path)
        faces = np.asarray(captured['triangles'], dtype=float)
        proof = qualify(faces, bounds)
        save(out / ('coverage-' + str(index) + '.json'), proof)
        refs.extend([scope_path, parent_path])
        rows.append(dict(index=index, bounds=bounds, faces=len(faces), coverage=proof,
                         capturePath=str(parent_path.relative_to(ROOT)), captureSHA256=digest(parent_path.read_bytes())))
    for name, sha in pins.items():
        assert digest((ROOT / name).read_bytes()) == sha
    result = dict(uids=plan['uids'], sourceSHA256=geometry['sourceSHA256'], rows=rows,
                  completeModelAndReturnBandInsidePartitionUnion=True,
                  rawProjectionAreaM2=projection.area, outerWKT=outer.wkt,
                  sourceGeometryChanges=0, installationApproved=False, publication=False,
                  qualification='Actual current renderer captured independently in every adjacent rectangle. Existing full-rectangle Float32 coverage rules unchanged. No candidate terrain, seam approval, support approval or installation.')
    result = json.loads(json.dumps(result))
    save(out / 'summary.json', result)
    module('partitioned_parent_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'complete-original-model-partitioned-current-parent-capture', list(dict.fromkeys(refs)), result)
    print([dict(index=r['index'], faces=r['faces'], bounds=r['bounds']) for r in rows], flush=True)


if __name__ == '__main__':
    main()
