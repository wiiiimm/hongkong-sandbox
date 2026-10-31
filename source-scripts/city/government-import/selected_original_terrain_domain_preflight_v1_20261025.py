"""Nominate complete existing terrain obligations before an expensive inset.

Conservative diagnostic only: no placement, geometry, replacement or publication
approval. Read each installed terrain once for the entire explicit source batch.
"""
import argparse
import math
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def bounds(terrain):
    g = terrain['meta']['georef']
    x, z = g['bE'] - 834500, 816500 - g['bN']
    return [x, z, x + (terrain['w'] - 1) * g['aE'], z - (terrain['h'] - 1) * g['aN']]


def overlaps(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'inventory']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.capture, a.inventory])
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    _, cp = authenticate(base / a.capture)
    _, ip = authenticate(base / a.inventory)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest_path.read_bytes())
    key = str(manifest_path.relative_to(ROOT))
    assert sha == cp[key] == ip[key]
    selection_path = base / a.capture / 'selection.json.gz'
    assert digest(selection_path.read_bytes()) == cp[str(selection_path.relative_to(ROOT))]
    selection = read(selection_path)
    assert selection['manifestSHA256'] == sha and 0 < len(selection['rows']) <= 40
    manifest = read(manifest_path)
    root_path = ROOT / '3d-viewer/city/data/terrain.json'
    parent = read(root_path)
    g = parent['meta']['georef']
    assert g['aE'] == -g['aN'] == parent['cell']
    refs = [__file__, manifest_path, root_path, selection_path, base / a.capture / 'result.json', base / a.inventory / 'result.json']
    terrains = []
    for entry in manifest['terrainPatches']:
        url = entry['url'] if isinstance(entry, dict) else entry
        path = (ROOT / '3d-viewer' / url).resolve()
        assert path.is_relative_to((ROOT / '3d-viewer/city/data').resolve())
        terrain = read(path)
        if not terrain.get('nativeMesh'):
            continue
        refs.append(path)
        terrains.append(dict(url=url, sha256=digest(path.read_bytes()), bounds=bounds(terrain),
                             parentTerrain=terrain['meta']['parentTerrain'],
                             coarseCells=terrain.get('coarseCells'),
                             retainedTargets=terrain['meta']['targetUids'],
                             nativeFaces=len(terrain['nativeMesh']['index']) // 3))
    rows = []
    for row in selection['rows']:
        # The existing inset uses 1m + 3m mitre buffers (mitre_limit=5).
        # 20m is a conservative bound on their combined coordinate excursion.
        # False-positive nominations remain for the exact later domain check.
        lo, hi = row['candidate']['entry']['worldBounds']
        assert row['candidate']['entry']['sha256'] == row['sourceSHA256']
        v = np.asarray([lo, hi], dtype=float)
        f = v.astype(np.float32).astype(float)
        low, high = np.minimum(v[0], f[0]), np.maximum(v[1], f[1])
        cells = [math.floor((low[0] - 20 + 834500 - g['bE']) / parent['cell']),
                 math.floor((low[2] - 20 - 816500 + g['bN']) / parent['cell']),
                 math.ceil((high[0] + 20 + 834500 - g['bE']) / parent['cell']),
                 math.ceil((high[2] + 20 - 816500 + g['bN']) / parent['cell'])]
        c0, r0, c1, r1 = cells
        domain = [g['bE'] + c0*g['aE'] - 834500, 816500-g['bN']-r0*g['aN'],
                  g['bE'] + c1*g['aE'] - 834500, 816500-g['bN']-r1*g['aN']]
        candidates = [t for t in terrains if overlaps(domain, t['bounds'])]
        rows.append(dict(uid=row['uid'], sourceSHA256=row['sourceSHA256'], conservativeCoarseCells=cells,
                         conservativeDomain=domain, existingNativeTerrainCandidates=candidates,
                         requiresExactTerrainObligationCheck=bool(candidates), installationApproved=False))
    assert digest(manifest_path.read_bytes()) == sha
    from pathlib import Path
    refs = [Path(x) for x in refs]
    result = dict(uids=sorted(r['uid'] for r in rows), rows=rows, currentManifestSHA256=sha,
                  sourceGeometryChanges=0, installationApproved=False, publication=False,
                  qualification='Conservative source-bound/coarse-domain nominations only. Exact eventual edit and replacement domain must bind every replaced old terrain extent and target, affected actor, seam and runtime check. No candidate terrain is accepted; absence here is not publication credit.')
    save(out / 'summary.json', result)
    module('terrain_preflight_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'original-terrain-domain-obligation-preflight', list(dict.fromkeys(refs)), result)
    print([dict(uid=r['uid'], terrainCandidates=[t['url'] for t in r['existingNativeTerrainCandidates']]) for r in rows], flush=True)


if __name__ == '__main__':
    main()
