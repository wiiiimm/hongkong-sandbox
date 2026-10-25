"""Recover explicit uniquely nominated original components; exact bytes only, no approval."""
import argparse, copy, json, sys, uuid, zipfile
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import canonical_bytes, scan, acquire, _convert_one, entry


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'nominations', 'scope']: p.add_argument('--' + key, required=True)
    p.add_argument('--uid', action='append', required=True)
    a = p.parse_args()
    assert all(n.startswith('government-xl-') and '/' not in n for n in [a.batch, a.nominations, a.scope])
    wanted = set(a.uid); assert 0 < len(wanted) == len(a.uid) <= 40
    base = ROOT / 'docs/astra-city/government-import'; out = base / a.batch; local = HERE / 'local' / a.batch
    assert not out.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]; refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    nominated = take(a.nominations, 'nominations.json')
    scope = take(a.scope, 'summary.json'); forms = {}
    for row in scope['rows']:
        for item in take(a.scope, row['uid'].split('/')[1] + '-forms.json.gz'):
            uid = item['building']['uid']
            if uid in wanted:
                if uid in forms: assert forms[uid] == item
                forms[uid] = item
    assert set(forms) == wanted
    selected = {}
    for uid in sorted(wanted):
        matches = [r for r in nominated['rows'] if r['uid'] == uid]
        assert len(matches) == 1 and len(matches[0]['exactOfficialCandidates']) == 1
        n = matches[0]; assert n['source'] == forms[uid]['building']
        selected[uid] = n
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == scope['currentManifestSHA256']; refs.append(manifest)
    installed = set()
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url; refs.append(path)
        installed.update(m['uid'] for m in read(path)['models'])
    assert not wanted & installed
    for f in forms.values():
        path = ROOT / '3d-viewer' / f['tile']; assert digest(path.read_bytes()) == f['tileSHA256']
        assert next(b for b in read(path)['buildings'] if b['uid'] == f['building']['uid']) == f['building']; refs.append(path)
    claim = reservations.claim(a.batch + '-' + str(uuid.uuid4()), ['building:' + u for u in sorted(wanted)], batch=a.batch, ttl=3600)
    assert claim['ok']; lease = claim['reservation']; save(local / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    rows, recoveries = [], []
    try:
        for sheet in sorted({n['sheet'] for n in selected.values()}):
            group = [n for n in selected.values() if n['sheet'] == sheet]
            with connect() as db:
                db.execute('SET TRANSACTION READ ONLY')
                for n in group:
                    found = db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN, n['nativeStageKey'])).fetchone()
                    assert found and found[0] == n['nativeStageSHA256']
                    assert next(m for m in found[1]['models'] if m['modelId'] == n['model']['modelId']) == n['model']
                value = db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1", (sheet,)).fetchone()
                assert value; pinned = value[0]
            folder = local / 'sheets' / sheet
            directory, _ = scan(dict(SHEETNO=sheet, Format_glTF=pinned['sourceURL'], REVISIONDATE=pinned['revision']), folder / 'directory')
            ids = {n['model']['modelId'] for n in group}
            directory['models'] = [m for m in directory['models'] if m['modelId'] in ids]
            assert {m['modelId'] for m in directory['models']} == ids
            acquisition = acquire(directory, folder / 'directory/zip-directory.bin', folder / 'original')
            packed = folder / 'packed'; packed.mkdir(exist_ok=True)
            with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as archive:
                for n in group:
                    assert reservations.owns(lease)
                    m = n['model']; sha = m['asset']['sha256']; uid = n['uid']
                    converted = _convert_one(archive, archive.getinfo(m['sourceEntry']), folder / 'decoded', packed, {}, dict(modelId=m['modelId']))
                    raw = canonical_bytes((packed / converted['asset']['asset']).read_bytes(), sha)
                    assert digest(raw) == sha and len(raw) == m['asset']['bytes']
                    assert len(decode_original_world_triangles(raw)) == m['triangles']
                    dest = local / 'assets' / (sha + '.glb.gz'); dest.parent.mkdir(exist_ok=True); dest.write_bytes(raw); refs.append(dest)
                    native = dict(cacheKey=n['nativeStageKey'], resultSha=n['nativeStageSHA256'], sheet=sheet, model=m)
                    e = entry(native, forms[uid]['building']); e['asset'] = 'assets/' + dest.name
                    assert not any(e.get(k) for k in ['sourceIdentityReviewed', 'placementReviewed', 'publicationApproved', 'identityReviewApproved'])
                    rows.append(dict(uid=uid, sourceSHA256=sha, modelId=m['modelId'], triangles=m['triangles'], native=native, source=forms[uid], candidate=dict(entry=e, path=str(dest.relative_to(ROOT)))))
                    recoveries.append(dict(uid=uid, sourceSHA256=sha, exactPreparedBytes=True, originalFaces=m['triangles']))
                    assert reservations.heartbeat(lease)['ok']
            save(out / (sheet + '-acquisition.json'), acquisition)
        assert {r['uid'] for r in rows} == wanted and digest(manifest.read_bytes()) == manifest_sha
        save(out / 'selection.json.gz', dict(rows=rows, manifestSHA256=manifest_sha))
        save(out / 'recovery.json', dict(rows=recoveries, sourceGeometryChanges=0, installationApproved=False))
        refs.extend(f for f in local.rglob('*') if f.is_file() and f.name != 'reservation.json')
        refs.extend([HERE.parent / 'enhancement-screening/shape_prepare.py', HERE / 'exact_packed_world_geometry_20261009.py'])
        module('nominated_original_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-nominated-original-companion-byte-recovery', list(dict.fromkeys(refs)), dict(uids=sorted(wanted), recovered=len(rows), exactPreparedBytes=True, sourceGeometryChanges=0, sourcePoseChanges=0, installationApproved=False, publication=False, aiGeometryModelling=False))
    finally:
        if reservations.owns(lease): assert reservations.release(lease)['ok']


if __name__ == '__main__': main()
