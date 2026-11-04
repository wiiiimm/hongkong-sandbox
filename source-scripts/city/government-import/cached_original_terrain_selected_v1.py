"""Check explicitly selected captured originals against verified cached source terrain.

Diagnostic only: no current-world acceptance, geometry edits or publication.
Unlike the XL-only batch, this also accepts auxiliary original support sources.
"""
import argparse
import subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--uid', action='append', required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, cap = base / args.batch, base / args.capture
    assert not doc.exists()
    _, pins = authenticate(cap)
    refs = [Path(__file__), cap / 'result.json']

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selected = take(cap / 'selection.json.gz')['rows']
    runtime = {r['uid']: r for r in take(HERE / 'local' / cap.name / 'runtime-geometry.json.gz')['rows']}
    wanted = set(args.uid)
    rows = [r for r in selected if r['uid'] in wanted]
    assert len(rows) == len(wanted) == len(args.uid)
    names = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.gltf', 'source-scripts/city'], cwd=ROOT, text=True).splitlines()
    by_name = defaultdict(list)
    for name in names:
        by_name[Path(name).name].append(ROOT / name)
    decoder = module('selected_source_terrain', HERE / 'xl-second-pass.py')
    final = module('selected_source_foundation', HERE / 'xl-final-script-pass.py')
    results = []
    for row in rows:
        uid = row['uid']
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256']
        refs.append(asset)
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            sha, stage = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['native']['cacheKey'],)).fetchone()
        assert sha == row['native']['resultSha']
        model = next(m for m in stage['models'] if m['modelId'] == row['modelId'])
        assert model['asset']['sha256'] == row['sourceSHA256']
        terrain_records, paths = stage.get('terrain', []), []
        for record in terrain_records:
            hashes, entry = record.get('sourceHashes'), record.get('sourceEntry')
            if not hashes or not entry:
                continue
            for candidate in by_name[Path(entry).name]:
                members = [candidate.parent / Path(n).name for n in hashes]
                if all(p.exists() and digest(p.read_bytes()) == h for p, h in zip(members, hashes.values())):
                    paths.append(candidate)
                    refs.extend(members)
                    break
        result = dict(uid=uid, sourceSHA256=row['sourceSHA256'], nativeResultSHA256=sha, installationApproved=False)
        if not paths or len(paths) != len(terrain_records):
            result.update(status='cached-original-terrain-missing', expectedTerrainRecords=len(terrain_records), verifiedTerrainRecords=len(paths))
        else:
            ground = np.concatenate([decoder.terrain_triangles(p) for p in paths])
            g = runtime[uid]
            assert g['sourceSHA256'] == row['sourceSHA256']
            tri = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
            lo, hi = tri.min((0, 1)), tri.max((0, 1))
            ground = ground[(ground[:, :, 0].max(1) >= lo[0]-10) & (ground[:, :, 0].min(1) <= hi[0]+10) & (ground[:, :, 2].max(1) >= lo[2]-10) & (ground[:, :, 2].min(1) <= hi[2]+10)]
            b = row['source']['building']
            foundation = final.foundation_context(tri, ground, Polygon(b['rings'][0], b['rings'][1:]))
            result.update(status='original-terrain-checked', originalTerrainFoundation=foundation, sourceTerrainPaths=[str(p.relative_to(ROOT)) for p in paths])
        save(doc / (uid.split('/')[1] + '.json'), result)
        results.append(result)
        print(dict(uid=uid, status=result['status'], buried=result.get('originalTerrainFoundation', {}).get('fullyBuriedTriangles')), flush=True)
    summary = dict(uids=sorted(wanted), rows=results, installationApproved=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Exact historical captured geometry against byte-verified original source terrain only. Current terrain, identity, complete support, neighbours and publication remain separate.')
    save(doc / 'summary.json', summary)
    refs.extend([HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py'])
    module('selected_source_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'selected-cached-original-terrain-foundations', list(dict.fromkeys(refs)), summary)


if __name__ == '__main__':
    main()
