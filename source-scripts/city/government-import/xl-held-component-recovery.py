"""Revisit all unmatched XL sources using exact component IDs, without modelling.

Keep the original native run immutable. A newly resolved UID is a separate routing
receipt, never an automatic identity/placement waiver or a new runtime publication.
"""
import argparse
import json
import os
import subprocess
import sys
import tarfile
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations, jobs, Jsonb, dict_row, NATIVE_RUN
from component_type_resolution import resolve

BATCH = 'government-xl-held-component-recovery-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
PRIOR = ROOT / 'docs/astra-city/government-import/government-xl-terminal-dispositions-20261008'


def ref(path): return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())}


def persist(stage, payload, result, lease):
    jid = digest(jobs.encode([BATCH, stage, payload]).encode())
    result = {**result, 'jobId': jid, 'batch': BATCH, 'stage': stage,
              'newlyInstalled': 0, 'publication': False, 'modelGeometryChanges': 0, 'scriptExternalAICalls': 0}
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT pg_advisory_xact_lock(%s)', (reservations.LOCK_ID,))
        assert reservations._current(con, lease)
        con.execute("INSERT INTO astra_modelling.jobs(id,batch,stage,payload,status,result) VALUES(%s,%s,%s,%s,'complete',%s) ON CONFLICT(id) DO NOTHING", (jid, BATCH, stage, Jsonb(payload), Jsonb(result)))
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == {'status': 'complete', 'result': result}
    with connect() as con: assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (jid,)).fetchone() == ('complete', result)
    return result


def prepare():
    assert not DOC.exists(), 'Resume the frozen selection; never overwrite a completed receipt'
    audit = read(PRIOR / 'audit.json.gz'); previous = read(PRIOR / 'result.json')
    rows = [r for r in audit['rows'] if r['disposition'] == 'filed-cannot-install' and r['uid'] is None]
    assert len(rows) == 68
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'; manifest = read(manifestpath)
    pointerpath = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'; pointer = read(pointerpath)
    installed = {m['uid']: (m, ROOT / '3d-viewer' / url) for url in manifest['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    codes = {r['modelId'][1:11] for r in rows}; sources = []; sourcefiles = []
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; raw = path.read_bytes()
        found = [b for b in json.loads(raw)['buildings'] if str(b.get('buildingCSUID') or '')[:10] in codes]
        if found:
            sourcefiles.append(ref(path))
            sources.extend({'building': b, 'tile': tile['url'], 'tileSHA256': digest(raw)} for b in found)
    keys = sorted({r['nativeCacheKey'] for r in rows})
    with connect() as con:
        con.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (previous['jobId'],)).fetchone() == ('complete', previous)
        native = {k: (s, v) for k, s, v in con.execute('SELECT cache_key,result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)', (keys,))}
        profiles = {(k, m): s for k, m, s in con.execute("SELECT cache_key,model_id,source_result_sha FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xl' AND cache_key=ANY(%s)", (NATIVE_RUN, keys))}
        reviews = {u: (state, sha, result) for u, state, sha, result in con.execute('SELECT uid,review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s', (pointer['snapshotId'],))}
    outcomes = []; chosen = []; assets = {}
    for row in rows:
        resultsha, receipt = native[row['nativeCacheKey']]
        assert resultsha == row['nativeResultSHA256'] == profiles[row['nativeCacheKey'], row['modelId']]
        model = next(m for m in receipt['models'] if m['modelId'] == row['modelId'])
        assert model == row['evidence']['nativeModel'] and model['asset']['sha256'] == row['sourceSHA256']
        routing = resolve(model, sources)
        outcome = {'sourceKey': row['sourceKey'], 'sourceSHA256': row['sourceSHA256'], 'modelId': row['modelId'],
                   'originalUid': None, 'priorFilingJobId': row['terminalNeonJobId'], 'routing': routing,
                   'uid': routing.get('uid'), 'state': 'held-no-exact-component', 'reasons': routing['reasons']}
        if routing['qualified']:
            uid = routing['uid']; source = routing['source']; building = source['building']; official = routing['official']
            if uid in installed:
                published, cat = installed[uid]
                assert digest((cat.parent / published['asset']).read_bytes()) == published['sha256']
                outcome['runtimeCatalogue'] = ref(cat); outcome['runtimeAsset'] = ref(cat.parent / published['asset'])
                if published['sha256'] != row['sourceSHA256']:
                    outcome.update(state='held-current-verified-source-differs', reasons=['different-original-source-already-published'])
                    outcomes.append(outcome); continue
                review = reviews.get(uid)
                if review and review[0] == 'installed-verified' and review[1] == published['sha256']:
                    ev = ROOT / review[2]['evidence']; assert digest(ev.read_bytes()) == review[2]['sha256']
                    assert published['modelId'] == row['modelId'] and published['worldBounds'] == model['worldBounds']
                    outcome.update(state='installed-existing-source-verified', reasons=[], reviewSnapshotId=pointer['snapshotId'], reviewEvidence=ref(ev))
                    outcomes.append(outcome); continue
                outcome['historicallyPublished'] = True
            else: outcome['historicallyPublished'] = False
            assert official['sourceBaseHeight'] == building['baseHeightHKPD'] and official['sourceTopHeight'] == building['topHeightHKPD']
            entry = {**model['asset'], 'uid': uid, 'label': building.get('name') or row['modelId'],
                     'objectId': building['objectId'], 'buildingCSUID': building['buildingCSUID'],
                     'modelId': row['modelId'], 'sourceTile': row['sheet'], 'triangles': model['triangles'],
                     'worldBounds': model['worldBounds'], 'rootTranslation': [-834500, 0, 816500],
                     'recordedBaseHeight': building['baseHeightHKPD'], 'recordedTopHeight': building['topHeightHKPD'],
                     'placementReviewed': False, 'publicationApproved': False, 'priority': 'unreviewed',
                     'overlapOfSmallerFootprint': official['overlapOfSmallerFootprint'],
                     'footprintCentroidDistanceMetres': official['footprintCentroidDistanceMetres']}
            chosen.append({'uid': uid, 'modelId': row['modelId'], 'sourceKey': row['sourceKey'], 'sourceSHA256': row['sourceSHA256'],
                           'triangles': row['triangles'], 'source': source, 'routing': routing, 'historicallyPublished': outcome['historicallyPublished'],
                           'candidate': {'entry': entry, 'path': str((LOCAL / entry['asset']).relative_to(ROOT))},
                           'native': {'cacheKey': row['nativeCacheKey'], 'resultSha': resultsha, 'sheet': row['sheet'], 'model': model}})
            assets[row['nativeCacheKey']] = [a for a in receipt['artifacts'] if a['kind'] == 'original-and-prepared-sheet']
            assert len(assets[row['nativeCacheKey']]) == 1
            outcome.update(state='requires-current-complete-physical-checks', reasons=['full-current-identity-contact-foundation-runtime-checks-required'])
        outcomes.append(outcome)
    resources = ['native-model:' + r['sourceKey'] for r in rows] + ['building:' + r['uid'] for r in chosen]
    claim = reservations.claim('codex-xl-component-routing-' + str(uuid.uuid4()), resources, batch=BATCH); assert claim['ok'], claim
    lease = claim['reservation']
    try:
        refs = [ref(PRIOR / 'audit.json.gz'), ref(PRIOR / 'result.json'), ref(manifestpath), ref(pointerpath),
                ref(Path(__file__).resolve()), ref(HERE / 'component_type_resolution.py'), *sourcefiles]
        payload = {'sources': 68, 'evidenceRefs': refs}
        result = persist('exact-xl-component-routing-v1', payload, {'rows': outcomes, 'counts': dict(Counter(r['state'] for r in outcomes)), 'nativeRun': NATIVE_RUN, 'nativeInventoryChanged': False}, lease)
        save(DOC / 'routing.json', result)
        save(DOC / 'selection.json.gz', {'batch': BATCH, 'rows': chosen, 'routingJobId': result['jobId'], 'manifestSHA256': digest(manifestpath.read_bytes()), 'snapshotId': pointer['snapshotId'], 'artifacts': assets})
        save(DOC / 'neon-routing-sync.json', {'jobId': result['jobId'], 'resultVerified': True})
        print({'jobId': result['jobId'], 'counts': result['counts'], 'physicalChecksRequired': len(chosen)}, flush=True)
    finally: assert reservations.release(lease)


def restore():
    frozen = read(DOC / 'selection.json.gz'); rows = frozen['rows']
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == frozen['manifestSHA256']
    claim = reservations.claim('codex-xl-component-restoration-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], ttl=7200, batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        wanted = {r['sourceSHA256']: r for r in rows}; by_model = {r['modelId']: r['sourceSHA256'] for r in rows}
        paths = subprocess.check_output(['rg', '--files', '--hidden', '--no-ignore', '-g', '*.glb.gz', 'source-scripts/city', '3d-viewer/city/data'], cwd=ROOT, text=True).splitlines()
        cached = {}
        for name in paths:
            p = ROOT / name; stem = p.name.removesuffix('.glb.gz'); sha = stem if stem in wanted else by_model.get(stem)
            if sha and sha not in cached and digest(p.read_bytes()) == sha: cached[sha] = p
        groups = defaultdict(list); outcomes = []
        for row in rows:
            sha = row['sourceSHA256']; target = ROOT / row['candidate']['path']; target.parent.mkdir(parents=True, exist_ok=True)
            if sha in cached:
                raw = cached[sha].read_bytes(); assert len(raw) == row['native']['model']['asset']['bytes']; target.write_bytes(raw)
                outcomes.append({'uid': row['uid'], 'sourceSHA256': sha, 'state': 'exact-source-ready', 'method': 'local-exact-cache', 'asset': ref(target)})
            else: groups[row['native']['cacheKey']].append(row)
        sys.path.insert(0, str(HERE.parent / 'landmark-resume')); sys.path.insert(0, str(HERE.parent / 'citywide-native'))
        from r2_snapshot import R2Store, verify_object
        from source_cache import validate_artifact
        from dotenv import dotenv_values
        for key, value in dotenv_values(ROOT / '.env.modelling').items():
            if key.startswith('R2_') and value and value != '[SENSITIVE]': os.environ.setdefault(key, value)

        def one(key, members):
            artifact = validate_artifact(frozen['artifacts'][key][0]); bundle = LOCAL / 'restore' / (artifact['sha256'] + '.tar.gz'); bundle.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not bundle.exists() or digest(bundle.read_bytes()) != artifact['sha256']:
                    verify_object(R2Store('hk-sandbox-assets'), artifact['key'], artifact['sha256'], artifact['bytes'], bundle)
                assert bundle.stat().st_size == artifact['bytes']
                restored = []
                with tarfile.open(bundle, 'r:gz') as archive:
                    files = list(archive)
                    for row in members:
                        sha = row['sourceSHA256']; matches = [m for m in files if Path(m.name).name == sha + '.glb.gz']
                        assert len(matches) == 1 and matches[0].isfile()
                        raw = archive.extractfile(matches[0]).read(); assert digest(raw) == sha and len(raw) == row['native']['model']['asset']['bytes']
                        target = ROOT / row['candidate']['path']; target.write_bytes(raw)
                        restored.append({'uid': row['uid'], 'sourceSHA256': sha, 'state': 'exact-source-ready', 'method': 'verified-native-artifact-restore', 'artifactSHA256': artifact['sha256'], 'asset': ref(target)})
                return restored
            except Exception as error:
                return [{'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'], 'state': 'held-source-cache-unavailable', 'errorType': type(error).__name__, 'errorCode': getattr(error, 'response', {}).get('Error', {}).get('Code')} for row in members]
        print({'localAssetsReady': len(outcomes), 'archivesToRestore': len(groups)}, flush=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(one, k, v) for k, v in groups.items()]
            for future in as_completed(futures):
                got = future.result(); outcomes.extend(got); assert reservations.heartbeat(lease, ttl=7200)
                save(DOC / 'restoration-checkpoint.json', {'rows': outcomes, 'expected': len(rows)})
                print({'restoredOrHeld': len(outcomes), 'expected': len(rows), 'last': Counter(r['state'] for r in got)}, flush=True)
        assert {r['uid'] for r in outcomes} == {r['uid'] for r in rows} and len(outcomes) == len(rows)
        result = persist('exact-xl-component-source-restoration-v1', {'routingJobId': frozen['routingJobId'], 'selection': ref(DOC / 'selection.json.gz')}, {'rows': outcomes, 'counts': dict(Counter(r['state'] for r in outcomes))}, lease)
        save(DOC / 'restoration.json', result); save(DOC / 'neon-restoration-sync.json', {'jobId': result['jobId'], 'resultVerified': True})
        print({'counts': result['counts'], 'jobId': result['jobId']}, flush=True)
    finally: assert reservations.release(lease)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('phase', choices=['prepare', 'restore']); args = parser.parse_args()
    prepare() if args.phase == 'prepare' else restore()
