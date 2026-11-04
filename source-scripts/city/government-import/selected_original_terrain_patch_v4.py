"""Build a private original-terrain candidate with a source-bounds core and parent return.

No live writes or acceptance: neighbours, original support and runtime remain separate.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--terrain-check', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--uid', action='append', default=[])
    parser.add_argument('--core-halo', type=float, default=1.0)
    args = parser.parse_args()
    assert 0 <= args.core_halo <= 10
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.terrain_check, args.capture]:
        folder = base / name
        _, bound = authenticate(folder)
        refs.append(folder / 'result.json')
        for key, value in bound.items():
            assert key not in pins or pins[key] == value
            pins[key] = value

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    checked = take(base / args.terrain_check / 'summary.json')['rows']
    if args.uid:
        assert len(set(args.uid)) == len(args.uid)
        checked = [r for r in checked if r['uid'] in set(args.uid)]
        assert {r['uid'] for r in checked} == set(args.uid)
    assert checked and all(r['status'] == 'original-terrain-checked' for r in checked)
    wanted = {r['uid']: r['sourceSHA256'] for r in checked}
    rows = [r for r in take(base / args.capture / 'selection.json.gz')['rows'] if r['uid'] in wanted]
    assert len(rows) == len(wanted)
    for row in rows:
        assert row['sourceSHA256'] == wanted[row['uid']]
    second = module('selected_patch_geometry', HERE / 'xl-second-pass.py')
    second.LOCAL = local
    parentpath = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(parentpath)
    refs.append(parentpath)
    rects = [second.resolution.rectangle_for(r['native']['model']['worldBounds'], parent) for r in rows]
    cells = [min(r[0] for r in rects), min(r[1] for r in rects), max(r[2] for r in rects), max(r[3] for r in rects)]
    bounds = second.resolution.extent(cells, parent)
    lows = np.min([r['native']['model']['worldBounds'][0] for r in rows], axis=0)
    highs = np.max([r['native']['model']['worldBounds'][1] for r in rows], axis=0)
    core = [float(lows[0]-args.core_halo), float(lows[2]-args.core_halo), float(highs[0]+args.core_halo), float(highs[2]+args.core_halo)]
    sources, parts = [], []
    for name in sorted({p for r in checked for p in r['sourceTerrainPaths']}):
        path = ROOT / name
        gltf = take(path)
        for buffer in gltf.get('buffers', []):
            member = path.parent / buffer['uri']
            assert digest(member.read_bytes()) == pins[str(member.relative_to(ROOT))]
            refs.append(member)
        sources.append(dict(path=name, sha256=pins[name]))
        parts.append(second.terrain_triangles(path))
    terrain = np.concatenate(parts)
    terrain = terrain[(terrain[:, :, 0].max(1) >= bounds[0]) & (terrain[:, :, 0].min(1) <= bounds[2]) & (terrain[:, :, 2].max(1) >= bounds[1]) & (terrain[:, :, 2].min(1) <= bounds[3])]
    builder = module('selected_patch_builder', HERE / 'resolve-pass-indexed-parent-clipping.py')
    save(doc / 'scope.json', dict(uids=sorted(wanted), cells=cells, bounds=bounds, sourceTerrainFaces=len(terrain), nativeCore=core, coreHalo=args.core_halo, installationApproved=False))
    result = dict(uids=sorted(wanted), installationApproved=False, publication=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0)
    try:
        patch = builder.make_patch(dict(cells=cells, uids=sorted(wanted)), parent, terrain, sources, native_core=core, parent_sha256=digest(parentpath.read_bytes()))
    except AssertionError as error:
        result.update(status='terrain-construction-requires-investigation', reason=str(error), permanentRejection=False)
    else:
        path = local / 'candidate-terrain.json'
        save(path, patch)
        refs.append(path)
        result.update(status='private-terrain-validator-passed', terrainTriangles=len(patch['nativeMesh']['index']) // 3, candidate=dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    save(doc / 'summary.json', result)
    refs.extend(path for path in (local / 'terrain-repairs').rglob('*') if path.is_file())
    refs.extend([HERE / 'xl-second-pass.py', HERE / 'resolve-pass-indexed-parent-clipping.py'])
    module('selected_patch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-private-original-terrain-candidate', list(dict.fromkeys(refs)), result)
    print({k: v for k, v in result.items() if k != 'candidate'}, flush=True)


if __name__ == '__main__':
    main()
