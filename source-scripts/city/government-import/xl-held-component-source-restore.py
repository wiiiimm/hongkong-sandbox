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


def restore():
    frozen = read(DOC / 'selection.json.gz'); rows = frozen['rows']
    assert digest((ROOT / '3d-viewer/city/data/manifest.json').read_bytes()) == frozen['manifestSHA256']
    claim = reservations.claim('codex-xl-component-restoration-' + str(uuid.uuid4()), ['building:' + r['uid'] for r in rows], ttl=3600, batch=BATCH)
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
                got = future.result(); outcomes.extend(got); assert reservations.heartbeat(lease, ttl=3600)
                save(DOC / 'restoration-checkpoint.json', {'rows': outcomes, 'expected': len(rows)})
                print({'restoredOrHeld': len(outcomes), 'expected': len(rows), 'last': Counter(r['state'] for r in got)}, flush=True)
        assert {r['uid'] for r in outcomes} == {r['uid'] for r in rows} and len(outcomes) == len(rows)
        result = persist('exact-xl-component-source-restoration-v1', {'routingJobId': frozen['routingJobId'], 'selection': ref(DOC / 'selection.json.gz'), 'restorationRunner': ref(Path(__file__).resolve())}, {'rows': outcomes, 'counts': dict(Counter(r['state'] for r in outcomes))}, lease)
        save(DOC / 'restoration.json', result); save(DOC / 'neon-restoration-sync.json', {'jobId': result['jobId'], 'resultVerified': True})
        print({'counts': result['counts'], 'jobId': result['jobId']}, flush=True)
    finally: assert reservations.release(lease)


if __name__ == "__main__": restore()
