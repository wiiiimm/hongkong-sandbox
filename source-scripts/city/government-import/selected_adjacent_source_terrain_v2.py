"""Complete source-terrain coverage using pinned neighbouring government sheets."""
import argparse
import json
import subprocess
import uuid
from collections import defaultdict
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, NATIVE_RUN, read, save, digest, connect, reservations
from terrain_source_preflight import SourceSheetIndex
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'uid']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--allow-new-terrain-revision', action='store_true')
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local, cap = base / args.batch, HERE / 'local' / args.batch, base / args.capture
    assert not doc.exists() and not local.exists()
    _, pins = authenticate(cap)
    refs = [Path(__file__), cap / 'result.json']
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(cap / 'selection.json.gz')
    row = next(r for r in selected['rows'] if r['uid'] == args.uid)
    geometry = next(r for r in take(HERE / 'local' / cap.name / 'runtime-geometry.json.gz')['rows'] if r['uid'] == args.uid)
    asset = ROOT / row['candidate']['path']
    assert digest(asset.read_bytes()) == row['sourceSHA256'] == geometry['sourceSHA256']
    refs.append(asset)
    indexpath = ROOT / 'source-scripts/city/landmark-acquisition/index.json'
    sheets = sorted({r['sheet'] for r in SourceSheetIndex(read(indexpath)).covering_sheets(row['native']['model']['worldBounds'])})
    refs.append(indexpath)
    names = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.gltf', 'source-scripts/city'], cwd=ROOT, text=True).splitlines()
    cached = defaultdict(list)
    for name in names:
        cached[Path(name).name].append(ROOT / name)
    inputs = {}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s', (row['native']['cacheKey'],)).fetchone() == (row['native']['resultSha'],)
        for sheet in sheets:
            records = db.execute('SELECT i.cache_key,i.source_sha,r.result_sha,r.result FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_members m USING(cache_key) JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE m.run_id=%s AND i.sheet=%s', (NATIVE_RUN, sheet)).fetchall()
            assert len(records) == 1, (sheet, len(records))
            key, source_sha, result_sha, native = records[0]
            directories = [r[0] for r in db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC", (sheet,)).fetchall()]
            matching = [d for d in directories if digest(json.dumps([d['sourceURL'], d['etag'], d['directorySHA256']], separators=(',', ':')).encode()) == source_sha]
            assert matching, 'No exact source-directory metadata for ' + sheet
            inputs[sheet] = dict(cacheKey=key, sourceSHA256=source_sha, resultSHA256=result_sha, terrain=native.get('terrain', []), directory=matching[0])
    claim = reservations.claim(args.batch + '-' + str(uuid.uuid4()), ['building:' + args.uid] + ['source-terrain:' + sheet for sheet in sheets], batch=args.batch, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        save(local / 'reservation.json', json.loads(json.dumps(lease, default=str)))
        decoder = module('adjacent_selected_decoder', HERE / 'xl-second-pass.py')
        decoder.LOCAL = local
        tri = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
        lo, hi = tri.min((0, 1)), tri.max((0, 1))
        parts, paths, recoveries = [], [], []
        revisions = []
        for sheet in sheets:
            record = inputs[sheet]
            found = []
            for terrain in record['terrain']:
                hashes, entry = terrain.get('sourceHashes'), terrain.get('sourceEntry')
                if not hashes or not entry:
                    continue
                for candidate in cached[Path(entry).name]:
                    if all((candidate.parent / Path(name).name).exists() and digest((candidate.parent / Path(name).name).read_bytes()) == sha for name, sha in hashes.items()):
                        found.append(candidate)
                        refs.extend(candidate.parent / Path(name).name for name in hashes)
                        break
            if not found or len(found) != len(record['terrain']):
                changed_revision = False
                try:
                    recovery = decoder.source_sheet(sheet, [], record['directory'], {}, [])
                except AssertionError as error:
                    if str(error) != 'Pinned source revision changed' or not args.allow_new_terrain_revision:
                        raise
                    fresh = read(local / 'sheets' / sheet / 'directory/result.json')
                    fresh_identity = digest(json.dumps([fresh['sourceURL'], fresh['etag'], fresh['directorySHA256']], separators=(',', ':')).encode())
                    assert fresh_identity != record['sourceSHA256']
                    recovery = decoder.source_sheet(sheet, [], fresh, {}, [])
                    changed_revision = True
                    revisions.append(dict(sheet=sheet, originalSourceSHA256=record['sourceSHA256'], currentTerrainSourceSHA256=fresh_identity, currentDirectory={k:v for k,v in fresh.items() if k!='models'}, qualification='New terrain source revision; no old terrain approval transferred. Original model bytes remain unchanged.'))
                recoveries.append(recovery)
                found = [ROOT / name for name in recovery['terrainPaths']]
                for terrain in ([] if changed_revision else record['terrain']):
                    for name, sha in terrain.get('sourceHashes', {}).items():
                        member = next(p.parent / Path(name).name for p in found if p.name == Path(terrain['sourceEntry']).name)
                        assert digest(member.read_bytes()) == sha
            assert found, sheet
            for path in found:
                values = decoder.terrain_triangles(path)
                parts.append(values[(values[:, :, 0].max(1) >= lo[0]-10) & (values[:, :, 0].min(1) <= hi[0]+10) & (values[:, :, 2].max(1) >= lo[2]-10) & (values[:, :, 2].min(1) <= hi[2]+10)])
                paths.append(str(path.relative_to(ROOT)))
            print(dict(sheet=sheet, sourceTerrainFiles=len(found)), flush=True)
            assert reservations.owns(lease)
        ground = np.concatenate(parts)
        building = row['source']['building']
        foundation = module('adjacent_selected_foundation', HERE / 'xl-final-script-pass.py').foundation_context(tri, ground, Polygon(building['rings'][0], building['rings'][1:]))
        save(local / 'original-terrain.json.gz', dict(triangles=ground.tolist(), sourceTerrainPaths=paths))
        resultrow = dict(uid=args.uid, sourceSHA256=row['sourceSHA256'], nativeResultSHA256=row['native']['resultSha'], status='original-terrain-checked', sourceTerrainPaths=paths, originalTerrainFoundation=foundation, installationApproved=False)
        result = dict(uids=[args.uid], rows=[resultrow], sheets=sheets, originalSourceRevisionsVerified=not revisions, terrainRevisionChanges=revisions, sourceRevisionsExplicitlyBound=True, installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
        save(doc / 'summary.json', result)
        save(doc / 'source-inputs.json', dict(inputs=inputs, recoveries=recoveries, terrainRevisionChanges=revisions))
        refs.extend(path for path in local.rglob('*') if path.is_file() and path.name != 'reservation.json')
        refs.extend([HERE / 'xl-second-pass.py', HERE / 'xl-final-script-pass.py', HERE / 'terrain_source_preflight.py'])
        module('adjacent_selected_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-adjacent-selected-original-terrain', list(dict.fromkeys(refs)), result)
        print(dict(faces=foundation['triangles'], covered=foundation['completeTerrainTriangles'], buried=foundation['fullyBuriedTriangles']), flush=True)
    finally:
        if reservations.owns(lease):
            assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
