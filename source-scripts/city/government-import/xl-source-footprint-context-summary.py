"""Reuse complete source captures and exact official GIS snapshots, without acceptance.

The older snapshot's manifest is historical. Rebind only the unchanged exact
source forms, not its physical/terrain checks, to today's manifest.
"""
import argparse
import math
import uuid
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT, read, save, digest, connect, reservations, jobs, Jsonb, dict_row


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def loader_excess(bounds, polygon):
    west, north, east, south = polygon.bounds
    margin = max(20, math.hypot(east-west, south-north))
    lo, hi = bounds
    return {'marginM': margin, 'maxExcessM': max(0, west-margin-lo[0],
            hi[0]-east-margin, north-margin-lo[2], hi[2]-south-margin)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures', required=True)
    parser.add_argument('--official', required=True)
    parser.add_argument('--batch', required=True)
    args = parser.parse_args()
    assert Path(args.batch).name == args.batch and args.batch.startswith('government-xl-')
    captures, official = ROOT/args.captures, ROOT/args.official
    doc = ROOT/'docs/astra-city/government-import'/args.batch
    assert not doc.exists(), 'Fresh evidence only'
    before, snapshot_result = read(captures/'result.json'), read(official/'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        for result in [before, snapshot_result]:
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                               (result['jobId'],)).fetchone() == ('complete', result)
    snapshot_path = ROOT/snapshot_result['snapshot']['path']
    assert ref(snapshot_path) == snapshot_result['snapshot']
    snapshot, inputs = read(snapshot_path), read(captures/'inputs.json')
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    current_manifest_sha = digest(manifest_path.read_bytes())
    historical_manifest_sha = snapshot['manifestSHA256']
    refs = [ref(p) for p in [Path(__file__), manifest_path, snapshot_path,
                            captures/'result.json', official/'result.json']]
    for item in [*before['evidenceRefs'], *snapshot['evidenceRefs']]:
        if item['path'] == str(manifest_path.relative_to(ROOT)):
            assert item['sha256'] == historical_manifest_sha
            continue  # Preserve its old hash explicitly; do not claim it is current.
        assert ref(ROOT/item['path']) == item
        refs.append(item)
    for path, pinned in read(captures/'render.json')['inputHashes'].items():
        item = ref(ROOT/path)
        assert item['sha256'] == pinned
        refs.append(item)
    wanted = {m['uid'] for m in inputs['models']}
    assert len(wanted) == before['sourcesCaptured'] == len(before['views'])
    scope = {b['uid'] for m in inputs['models'] for b in m['forms']}
    found = {}
    for tile in read(manifest_path)['tiles']:
        path = ROOT/'3d-viewer'/tile['url']
        forms = [b for b in read(path)['buildings'] if b['uid'] in scope]
        if forms:
            refs.append(ref(path))
            for b in forms:
                assert b['uid'] not in found
                found[b['uid']] = b
    assert set(found) == scope
    for m in inputs['models']:
        for b in m['forms']:
            assert found[b['uid']] == b, 'Current footprint context changed'
    official_rows = {r['uid']: r for r in snapshot['rows'] if r['uid'] in wanted}
    assert set(official_rows) == wanted
    raw_records = []
    for item in snapshot['evidenceRefs']:
        if '/official/' in item['path'] and item['path'].endswith('.json.gz'):
            raw_records.extend(read(ROOT/item['path'])['features'])
    rows = []
    for m in inputs['models']:
        b = found[m['uid']]
        old = official_rows[m['uid']]
        assert old['state'] == 'current-official-exact-identity'
        assert old['sourceSHA256'] == m['sourceSHA256'] and old['currentSource']['building'] == b
        records = [f for f in raw_records if f['attributes']['BuildingCSUID'] == b['buildingCSUID']]
        assert len(records) == 1 and records[0]['attributes'] == old['officialAttributes']
        original, fresh = Polygon(b['rings'][0], b['rings'][1:]), Polygon(old['officialRings'][0], old['officialRings'][1:])
        assert original.is_valid and fresh.is_valid and original.area > 0 and fresh.area > 0
        rows.append({'uid': m['uid'], 'modelId': m['modelId'], 'sourceSHA256': m['sourceSHA256'],
            'buildingCSUID': b['buildingCSUID'], 'viewerObjectId': b['objectId'],
            'snapshotOfficialObjectId': old['officialAttributes']['OBJECTID'],
            'snapshotOfficialObjectIdChanged': old['officialAttributes']['OBJECTID'] != b['objectId'],
            'footprintDifferenceAreaM2': original.symmetric_difference(fresh).area,
            'footprintHausdorffDistanceM': original.hausdorff_distance(fresh),
            'currentFootprintLoaderBounds': loader_excess(m['worldBounds'], original),
            'officialFootprintLoaderBounds': loader_excess(m['worldBounds'], fresh),
            'snapshotDateQualification': 'Reuse of saved official query; no new government request.',
            'identityAccepted': False, 'installationApproved': False,
            'nextStep': 'Resolve original whole-source/component coverage; a refresh of this exact official GIS footprint does not resolve the measured bounds failure.'})
    assert all(r['officialFootprintLoaderBounds']['maxExcessM'] > .02 for r in rows)
    refs = list({r['path']: r for r in refs}.values())
    claim = reservations.claim('codex-xl-footprint-context-'+str(uuid.uuid4()),
        [('building:' if uid.startswith('landsd/') else 'source-form:')+uid for uid in sorted(scope)], batch=args.batch)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        payload = {'captureJobId': before['jobId'], 'officialSnapshotJobId': snapshot_result['jobId'],
                   'historicalSnapshotManifestSHA256': historical_manifest_sha,
                   'currentManifestSHA256': current_manifest_sha,
                   'evidenceRefs': refs, 'sourceSHA256s': {m['uid']: m['sourceSHA256'] for m in inputs['models']}}
        stage = 'original-source-exact-official-footprint-context-v1'
        jid = jobs.enqueue(args.batch, stage, payload)
        job = jobs.claim(args.batch, lease['owner'], [stage], lease_seconds=1800)
        assert job and job['id'] == jid
        result = {**payload, 'jobId': jid, 'batch': args.batch, 'rows': rows,
            'sourcesCompared': len(rows), 'officialFootprintRefreshResolvesBounds': 0,
            'newlyInstalled': 0, 'publication': False, 'architectureReview': False,
            'modelGeometryChanges': 0, 'scriptExternalAICalls': 0, 'activeWorkers': 0,
            'qualification': 'Numeric metadata comparison only. Exact stable CSUIDs reuse one official record each. Current source forms are unchanged; historical manifest is explicitly retained. The saved official shapes still fail the same loader bounds rule. No corruption, architecture, identity, physical or publication acceptance is inferred.'}
        with connect() as con:
            con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
            con.row_factory = dict_row
            assert reservations._current(con, lease)
            for item in refs:
                assert ref(ROOT/item['path']) == item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()", (Jsonb(result), jid, job['owner'], job['token'])).rowcount == 1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
        save(doc/'result.json', result)
        save(doc/'neon-sync.json', {'jobId': jid, 'resultVerified': True})
        print({'compared': len(rows), 'footprintRefreshResolvesBounds': 0, 'jobId': jid, 'neonVerified': True}, flush=True)
    finally:
        assert reservations.release(lease)


if __name__ == '__main__':
    main()
