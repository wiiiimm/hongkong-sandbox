"""Bind complete expanded terrain dependencies before expensive source repairs.

Diagnostic only. Does not construct terrain, approve models or start workers.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_envelope_closure_v1_20261023 import closure


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'patch', 'capture']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    prior, pp = authenticate(base / a.patch)
    _, cp = authenticate(base / a.capture)
    refs = [Path(__file__), base / a.patch / 'result.json', base / a.capture / 'result.json', HERE / 'retained_envelope_closure_v1_20261023.py']
    def take(path, pins):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(base / a.capture / 'selection.json.gz', cp)
    assert set(prior['uids']) <= {r['uid'] for r in selected['rows']}
    for r in selected['rows']:
        if r['uid'] in prior['uids']:
            path = ROOT / r['candidate']['path']
            assert digest(path.read_bytes()) == r['sourceSHA256']
            refs.append(path)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = take(manifestpath, cp)
    assert digest(manifestpath.read_bytes()) == selected['manifestSHA256']
    parent = take(ROOT / '3d-viewer/city/data/terrain.json', cp)
    if 'candidate' in prior:
        candidatepath = ROOT / prior['candidate']['path']
        candidate = take(candidatepath, pp)
        assert digest(candidatepath.read_bytes()) == prior['candidate']['sha256']
        cells = candidate['coarseCells']
    else:
        # A completed held constructor still binds its proposed domain. No
        # candidate or approval is invented from this failure record.
        assert prior['installationApproved'] is False
        scope = take(base / a.patch / 'scope.json', pp)
        assert set(scope['uids']) == set(prior['uids'])
        cells = scope['cells']
    assert len(cells) == 4 and all(type(x) is int for x in cells)
    builder = module('retention_preflight_extent', HERE / 'resolve-pass-indexed-parent-clipping.py')
    nodes = []
    for e in manifest['terrainPatches']:
        path = ROOT / '3d-viewer' / e['url']
        terrain = take(path, cp)
        packed = []
        def visit(n):
            if n.get('nativeMesh'):
                values = np.asarray(n['nativeMesh']['position']).reshape(-1, 3)
                values = np.concatenate([values, values.astype('float32').astype('float64')])
                low, high = values.min(0), values.max(0)
                packed.append([float(low[0]), float(low[2]), float(high[0]), float(high[2])])
            for child in n.get('patches', []):
                visit(child)
        visit(terrain)
        nodes.append(dict(url=e['url'], sha256=digest(path.read_bytes()), coarseBounds=builder.extent(terrain['coarseCells'], parent), packedBounds=packed, retainedUids=terrain['meta'].get('targetUids', [])))
    result = closure(builder.extent(cells, parent), nodes)
    result.update(uids=prior['uids'], parents=[n for n in nodes if n['url'] in result['requiredUrls']], currentManifestSHA256=selected['manifestSHA256'], installationApproved=False, publication=False, sourceGeometryChanges=0, status='complete-expanded-terrain-dependency-preflight', qualification='Positive-area coarse and original/Float32 packed extents closed transitively. Required retention is a dependency nomination only; low-face preservation, native validators, source support, identity, all current neighbours and browser checks remain mandatory. No terrain constructed.')
    assert digest(manifestpath.read_bytes()) == selected['manifestSHA256']
    save(out / 'summary.json', result)
    module('retention_preflight_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'original-terrain-retention-dependency-preflight', refs, result)
    print(dict(requiredParents=len(result['requiredUrls']), bounds=result['bounds']), flush=True)


if __name__ == '__main__':
    main()
