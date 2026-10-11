"""Acquire a new official revision for explicitly held XL originals; never publish.

The current source gets its own hashes and provenance. Old C0 metadata and native
run results remain untouched. Matching, physical and browser acceptance follow
separately; a new version is not evidence that the old geometry is unchanged.
"""
import argparse, json, subprocess, sys, uuid, zipfile
from collections import defaultdict
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row
sys.path.insert(0, str(HERE.parent / 'enhancement-screening'))
from shape_prepare import scan, acquire
sys.path.insert(0, str(HERE.parent / 'citywide-native'))
from convert import _convert_one, official_shape, converter_dependencies
sys.path.insert(0, str(HERE.parent / 'landsd-territory'))
from retain import iter_features
from pyproj import Transformer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous', required=True); p.add_argument('--batch', required=True)
    p.add_argument('--owned', action='store_true'); a = p.parse_args()
    assert a.batch.startswith('government-xl-') and Path(a.batch).name == a.batch
    doc = ROOT / 'docs/astra-city/government-import' / a.batch
    local = HERE / 'local' / a.batch; lease = local / 'reservation.json'
    previous = (ROOT / a.previous).resolve(); assert previous.parent == doc.parent
    prior = read(previous / 'result.json'); uids = prior['uids']
    assert 1 <= len(uids) <= 10 and len(set(uids)) == len(uids)
    assert not prior['publication'] and set(prior['errors']) == set(uids)
    assert all(v == 'source-model-missing-in-current-revision' for v in prior['errors'].values())
    if not a.owned:
        assert not doc.exists(), 'Fresh revision stage required'
        claim = reservations.claim('codex-xl-current-revision-' + str(uuid.uuid4()),
                    ['building:' + u for u in uids], batch=a.batch)
        assert claim['ok'], claim
        save(lease, json.loads(json.dumps(claim['reservation'], default=str)))
        subprocess.run([sys.executable, str(HERE.parent / 'shared-modelling/reservations.py'),
            'run', '--lease-file', str(lease), '--', sys.executable, __file__,
            *sys.argv[1:], '--owned'], cwd=ROOT, check=True); return
    receipt = read(lease); assert reservations.owns(receipt)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                           (prior['jobId'],)).fetchone() == ('complete', prior)
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)', (uids,)).fetchall()
    for ref in prior['evidenceRefs']: assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    macro = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz'
    old = {r['uid']: r for r in read(macro)['rows'] if r['uid'] in uids}; assert set(old) == set(uids)
    for row in old.values(): assert digest((ROOT / '3d-viewer' / row['source']['tile']).read_bytes()) == row['source']['tileSHA256']
    footprints = HERE.parent / 'landsd-territory/landsd-hong-kong-source.geojson.gz'
    by_csuid = defaultdict(list)
    for feature in iter_features(footprints):
        csuid = feature['properties'].get('BuildingCSUID')
        if csuid in {r['source']['building']['buildingCSUID'] for r in old.values()}: by_csuid[csuid].append(feature)
    projection = Transformer.from_crs(4326, 2326, always_xy=True)
    by_ref = defaultdict(list); features = []
    for uid, row in old.items():
        building = row['source']['building']; found = by_csuid[building['buildingCSUID']]
        assert len(found) == 1 and found[0]['properties']['OBJECTID'] == building['objectId']
        feature = found[0]; geom = feature['geometry']; assert geom['type'] in ('Polygon', 'MultiPolygon')
        polygons = [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']
        transformed = {'attributes': feature['properties'], 'geometry': {'rings':
            [[list(projection.transform(*point)) for point in ring] for polygon in polygons for ring in polygon]},
            'viewerUids': [{k: building[k] for k in ('uid', 'rings', 'base', 'height')}]}
        assert str(transformed['attributes']['GeoRefNo']) == row['modelId'][1:11]
        features.append(transformed); by_ref[row['modelId'][1:11]].append((transformed, official_shape(transformed)))
    save(doc / 'official-inputs.json', {'source': str(footprints.relative_to(ROOT)),
         'sourceSHA256': digest(footprints.read_bytes()), 'features': features})
    rows = []; revisions = []; errors = {}
    for sheet in sorted({r['native']['sheet'] for r in old.values()}):
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            historical = con.execute('SELECT result FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1', (sheet,)).fetchone()[0]
        folder = local / 'sheets' / sheet
        current, _ = scan({'SHEETNO': sheet, 'Format_glTF': historical['sourceURL'], 'REVISIONDATE': historical['revision']}, folder / 'directory')
        requested = []
        for uid, earlier in old.items():
            if earlier['native']['sheet'] != sheet: continue
            # Same full GeoRef, structure and geometry format; a distinct source
            # suffix must be unique. Never treat changed member bytes as C0.
            matches = [m for m in current['models'] if m['modelId'][:-1] == earlier['modelId'][:-1]]
            if len(matches) != 1: errors[uid] = 'current-revision-missing-or-ambiguous'; continue
            newer = matches[0]; assert newer['modelId'] != earlier['modelId']
            requested.append((uid, newer))
        if not requested: continue
        subset = {**current, 'models': [m for _, m in requested]}
        download = acquire(subset, folder / 'directory/zip-directory.bin', folder / 'original')
        packed = folder / 'packed'; packed.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(folder / 'original' / (sheet + '.zip')) as zipped:
            for uid, newer in requested:
                entry = next(m['name'] for m in newer['members'] if m['name'].lower().endswith('.gltf'))
                converted = _convert_one(zipped, zipped.getinfo(entry), folder / 'decoded', packed,
                                         by_ref, {'modelId': newer['modelId'], 'sourceEntry': entry})
                asset = packed / converted['asset']['asset']; assert digest(asset.read_bytes()) == converted['asset']['sha256']
                rows.append({'uid': uid, 'source': old[uid]['source'], 'priorModelId': old[uid]['modelId'],
                    'priorSourceSHA256': old[uid]['sourceSHA256'], 'modelId': newer['modelId'],
                    'sourceSHA256': converted['asset']['sha256'], 'assetPath': str(asset.relative_to(ROOT)), 'model': converted})
        revisions.append({'sheet': sheet, 'directory': str((folder / 'directory/result.json').relative_to(ROOT)),
            'directorySHA256': current['directorySHA256'], 'sourceETag': current['etag'],
            'download': str((folder / 'original/download.json').relative_to(ROOT)), 'archiveSHA256': download['sha256']})
    save(doc / 'revisions.json', revisions); save(doc / 'current-originals.json', {'rows': rows, 'errors': errors})
    paths = [macro, previous / 'result.json', Path(__file__), doc / 'official-inputs.json',
             doc / 'revisions.json', doc / 'current-originals.json', *converter_dependencies()]
    for revision in revisions:
        paths += [ROOT / revision['directory'], ROOT / revision['download']]
    refs = [{'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())} for path in paths]
    payload = {'uids': uids, 'evidenceRefs': refs}; stage = 'explicit-current-government-revision-acquisition-v1'
    jid = jobs.enqueue(a.batch, stage, payload); job = jobs.claim(a.batch, receipt['owner'], [stage], lease_seconds=1800)
    assert job and job['id'] == jid
    result = {**payload, 'batch': a.batch, 'jobId': jid, 'rows': rows, 'errors': errors,
        'acquired': len(rows), 'publication': False, 'newlyInstalled': 0, 'modelGeometryChanges': 0,
        'scriptExternalAICalls': 0, 'requiresAI': False, 'requiresHumanDecision': False,
        'qualification': 'New original government revision with fresh hashes, exact footprint identifiers and native packing checks. Whole-source identity, physical terrain/support, neighbours, browser and publication remain pending; prior native run untouched.'}
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,)); con.row_factory = dict_row
        assert reservations._current(con, receipt)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY'); assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
    save(doc / 'result.json', result); save(doc / 'neon-sync.json', {'jobId': jid, 'resultVerified': True})
    print(json.dumps({'acquired': len(rows), 'errors': errors, 'jobId': jid, 'newlyInstalled': 0}), flush=True)


if __name__ == '__main__': main()
