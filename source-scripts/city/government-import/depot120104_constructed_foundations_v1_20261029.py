"""Measure four original coordinate representations on unapproved private terrain."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    batch = 'government-xl-depot120104-constructed-foundations-v1-20261029'
    construction = 'government-xl-depot120104-land-inset-construction-v3-20261029'
    current = 'government-xl-oceanwalk-depot-current-v1-20261029'
    base = ROOT / 'docs/astra-city/government-import'
    out = base / batch
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    summary = take(construction, base / construction / 'summary.json')
    ground = np.asarray(take(construction, HERE / 'local' / construction / 'global-triangles.json.gz')['triangles'])
    assert len(ground) == summary['globalTerrainFaces']
    row = next(r for r in take(current + '-runtime', base / (current + '-runtime') / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/120104:0')
    attr = next(r for r in take(current + '-attributes', base / (current + '-attributes') / 'attributes.json.gz')['rows'] if r['uid'] == row['uid'])
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == attr['sourceSHA256'] == summary['sourceSHA256']
    refs.append(asset)
    ix = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
    worlds = dict(original=decode_original_world_triangles(asset.read_bytes()))
    for mode, key in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode] = np.asarray(attr[key]).reshape(-1, 3)[ix]
    rings = row['source']['building']['rings']
    context = module('depot_constructed_foundation', HERE / 'xl-final-script-pass.py')
    rows = []
    for mode, triangles in worlds.items():
        assert len(triangles) == row['triangles']
        proof = context.foundation_context(triangles, ground, shapely.Polygon(rings[0], rings[1:]))
        save(out / (mode + '.json.gz'), proof)
        item = dict(mode=mode, sourceWorldSHA256=digest(triangles.astype('<f8').tobytes()), **{k: proof[k] for k in ['completeTerrainTriangles', 'fullyBuriedTriangles', 'fullyBuriedUpwardTriangles', 'minimumGapM']})
        rows.append(item)
        print(item, flush=True)
    result = dict(uids=[row['uid']], sourceSHA256=row['sourceSHA256'], rows=rows,
                  groundSHA256=digest(ground.astype('<f8').tobytes()),
                  actualRendererCapture=False, existingLowParentGuard=summary['existingLowParentGuard'],
                  physicalAcceptance=False, installationApproved=False,
                  qualification='Complete unchanged original facets in all four coordinate representations against the unapproved derived surface. This measures foundation diagnostics only; low-parent, native patch, actual renderer, neighbour and browser checks remain outstanding. No source geometry or production guard change.')
    save(out / 'summary.json', result)
    refs.extend([HERE / 'xl-final-script-pass.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    module('depot_constructed_foundation_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'private-unapproved-terrain-four-world-foundation-diagnostics', refs, result)


if __name__ == '__main__':
    main()
