"""Process every currently unfinished XL original against verified cached source terrain.

Original-world diagnostics and unapproved source selections only. No quality skip
credit, installation, optimisation, geometry edits or external AI calls.
"""
import argparse
import json
import subprocess
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'installed', 'source-inventory', 'recovery']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.installed, args.source_inventory, args.recovery]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            if key not in ['3d-viewer/city/data/manifest.json']:
                assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    audit = take(base / args.installed / 'full-xl-current-count.json')
    inventory = take(base / args.source_inventory / 'inventory.json')
    pending = [r for r in audit['rows'] if not r['installedVerified']]
    assert len(audit['rows']) == 521 and len(pending) == audit['counts']['remaining']
    full_remaining = len(pending)
    recovery = take(base / args.recovery / 'summary.json')
    restored_keys = {r['cacheKey'] for r in recovery['rows'] if r['error'] is None}
    pending = [r for r in pending if r['sourceKey'].split('/', 1)[0] in restored_keys]
    assert pending and all(r['uid'] for r in pending)
    for row in recovery['rows']:
        if row['cacheKey'] in restored_keys:
            for item in row['files'].values():
                path = ROOT / item['path']
                assert digest(path.read_bytes()) == item['sha256']
                refs.append(path)
    available = {r['sourceKey']: r for r in inventory['rows']}
    assert all(r['sourceKey'] in available and r['indexedSourceSHA256'] == available[r['sourceKey']]['indexedSourceSHA256'] for r in pending)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifestpath.read_bytes())
    assert manifest_sha == audit['manifestSHA256']
    refs.append(manifestpath)
    forms = {}
    wanted = {r['uid'] for r in pending if r['uid'] is not None}
    for entry in read(manifestpath)['tiles']:
        path = ROOT / '3d-viewer' / entry['url']
        raw = path.read_bytes()
        for building in json.loads(raw)['buildings']:
            if building['uid'] in wanted:
                assert building['uid'] not in forms
                forms[building['uid']] = dict(building=building, tile=entry['url'], tileSHA256=digest(raw))
                refs.append(path)
    keys, ids = set(), set()
    for row in pending:
        key, modelid = row['sourceKey'].split('/', 1)
        assert len(key) == 64 and modelid.startswith('B')
        keys.add(key)
        ids.add(modelid)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        records = db.execute("SELECT i.cache_key,i.sheet,r.result_sha,r.result->'terrain',(SELECT jsonb_agg(m) FROM jsonb_array_elements(r.result->'models') m WHERE m->>'modelId'=ANY(%s)) FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=ANY(%s)", (sorted(ids), sorted(keys))).fetchall()
    native = {key: dict(sheet=sheet, resultSha=sha, terrain=terrain, models={m['modelId']: m for m in models or []}) for key, sheet, sha, terrain, models in records}
    assert set(native) == keys
    sourcepaths = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.gltf', 'source-scripts/city'], cwd=ROOT, text=True).splitlines()
    by_name = defaultdict(list)
    for name in sourcepaths:
        by_name[Path(name).name].append(ROOT / name)
    decoder = module('remaining_original_terrain_decode', HERE / 'xl-second-pass.py')
    decoder.LOCAL = local
    final = module('remaining_original_foundation', HERE / 'xl-final-script-pass.py')
    contact = module('remaining_original_contact', HERE / 'resolve-pass-indexed-parent-clipping.py')

    @lru_cache(maxsize=2)
    def terrain_geometry(name):
        return decoder.terrain_triangles(ROOT / name)

    terrain_cache = {}
    def locate(key):
        if key in terrain_cache:
            return terrain_cache[key]
        records = native[key]['terrain'] or []
        paths = []
        for record in records:
            hashes, entry = record.get('sourceHashes'), record.get('sourceEntry')
            if not hashes or not entry:
                continue
            for candidate in by_name[Path(entry).name]:
                members = [candidate.parent / Path(name).name for name in hashes]
                if all(p.exists() and digest(p.read_bytes()) == sha for p, sha in zip(members, hashes.values())):
                    paths.append(str(candidate.relative_to(ROOT)))
                    refs.extend(members)
                    break
        terrain_cache[key] = paths if records and len(paths) == len(records) else None
        return terrain_cache[key]

    selection, outcomes = [], []
    for number, item in enumerate(sorted(pending, key=lambda r: r['sourceKey']), 1):
        uid = item['uid']
        key, modelid = item['sourceKey'].split('/', 1)
        model = native[key]['models'][modelid]
        asset = ROOT / available[item['sourceKey']]['assetPath']
        sha = item['indexedSourceSHA256']
        assert model['asset']['sha256'] == digest(asset.read_bytes()) == sha
        refs.append(asset)
        result = dict(uid=uid, sourceKey=item['sourceKey'], modelId=modelid, sourceSHA256=sha, geometryBasis='original-source-world', installationApproved=False, permanentRejection=False)
        try:
            tri = decode_original_world_triangles(asset.read_bytes())
            assert len(tri) == model['triangles'] and 10000 <= len(tri) < 50000
            result['originalSourceTriangles'] = len(tri)
            result['originalWorldSHA256'] = digest(tri.astype('<f8').tobytes())
            if uid not in forms:
                result.update(status='current-source-form-investigation')
            else:
                source = forms[uid]
                building = source['building']
                matches = [c for c in model['matching']['officialCandidates'] if c.get('objectId') == building['objectId'] and c.get('buildingCSUID') == building['buildingCSUID']]
                entry = dict(model['asset'], uid=uid, objectId=building['objectId'], buildingCSUID=building['buildingCSUID'], label=building.get('name') or modelid, modelId=modelid, triangles=model['triangles'], worldBounds=model['worldBounds'], rootTranslation=[-834500, 0, 816500], sourceTile=native[key]['sheet'], priority='unreviewed', proceduralWindows=False, placementReviewed=False, publicationApproved=False)
                if len(matches) == 1:
                    entry.update(matches[0])
                    entry['uid'] = uid
                selected = dict(uid=uid, modelId=modelid, triangles=model['triangles'], sourceSHA256=sha, candidate=dict(path=str(asset.relative_to(ROOT)), entry=entry), source=source, native=dict(cacheKey=key, resultSha=native[key]['resultSha'], model=model), originalGeometryOnly=True)
                selection.append(selected)
                paths = locate(key)
                if not paths:
                    result.update(status='source-terrain-recovery-required', nativeCacheKey=key, nativeTerrainStates=[r.get('state') for r in native[key]['terrain'] or []])
                else:
                    lo, hi = tri.min((0, 1)), tri.max((0, 1))
                    parts = []
                    for path in paths:
                        ground = terrain_geometry(path)
                        parts.append(ground[(ground[:, :, 0].max(1) >= lo[0]-10) & (ground[:, :, 0].min(1) <= hi[0]+10) & (ground[:, :, 2].max(1) >= lo[2]-10) & (ground[:, :, 2].min(1) <= hi[2]+10)])
                    ground = np.concatenate(parts)
                    foundation = final.foundation_context(tri, ground, Polygon(building['rings'][0], building['rings'][1:]))
                    points, bottom = contact.sample_points(dict(position=tri.reshape(-1).tolist(), index=list(range(tri.size//3))))
                    interface = contact.audit_native(points, bottom, ground)
                    result.update(status='original-terrain-checked', sourceTerrainPaths=paths, originalTerrainFoundation=foundation, rawGroundContact=interface, nativeResultSHA256=native[key]['resultSha'], exactOfficialObjectAndCSUIDCandidate=len(matches) == 1, readyForCurrentSceneChecks=foundation['completeTerrainTriangles'] == foundation['triangles'] and foundation['fullyBuriedTriangles'] == 0 and interface['passed'] and len(matches) == 1)
        except Exception as error:
            result.update(status='source-diagnostic-investigation', errorType=type(error).__name__, reason=str(error))
        save(doc / ((uid.split('/')[1] if uid else modelid) + '.json'), result)
        outcomes.append(result)
        print(dict(number=number, total=len(pending), uid=uid, status=result['status'], ready=result.get('readyForCurrentSceneChecks', False)), flush=True)
        assert digest(manifestpath.read_bytes()) == manifest_sha
    save(doc / 'selection.json.gz', dict(rows=selection, manifestSHA256=manifest_sha, geometryBasis='original-source-world', nativeResultSHA256ByKey={key: value['resultSha'] for key, value in native.items()}))
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        actual = dict(db.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)', (sorted(keys),)).fetchall())
    assert actual == {key: value['resultSha'] for key, value in native.items()}
    counts = dict(Counter(r['status'] for r in outcomes))
    result = dict(uids=sorted(wanted), sourceKeys=sorted(r['sourceKey'] for r in pending), unmatchedSourceKeys=[r['sourceKey'] for r in pending if r['uid'] is None], rows=outcomes, counts=counts, readyForCurrentSceneChecks=sum(r.get('readyForCurrentSceneChecks', False) for r in outcomes), allRemainingXL=full_remaining, processedRecoveredSubset=len(pending), installationApproved=False, newlyInstalled=0, sourceGeometryChanges=0, scriptExternalAICalls=0, qualification='Only newly recovered terrain sources among the full unfinished fixed XL cohort; exact original-world geometry against verified original government terrain. Passing rows still require current terrain composition, full identity/neighbours, actual renderer/browser checks and guarded installation. No skip credit or permanent rejection.')
    save(doc / 'summary.json', result)
    refs.extend(path for path in local.rglob('*') if path.is_file())
    refs.extend([HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py', HERE / 'resolve-pass-indexed-parent-clipping.py'])
    # Hash each immutable file once, even when many sources share a terrain sheet.
    module('remaining_original_batch_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'recovered-xl-original-terrain-diagnostics', list(dict.fromkeys(refs)), result)
    print(dict(completed=len(outcomes), counts=counts, readyForCurrentSceneChecks=result['readyForCurrentSceneChecks']), flush=True)


if __name__ == '__main__':
    main()
