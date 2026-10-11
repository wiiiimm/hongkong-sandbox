"""Explicit accepted-source snapshot and leased, private lossless compression batch."""
import argparse
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
import jobs
import reservations
from db import connect, CONFIG
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import registry

ACTOR = 'codex-compression-20261012'
ADAPTER = 'meshopt-exact-buffer-views-v1'


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False, default=str) + '\n').encode()
    if path.exists() and path.read_bytes() != data:
        raise ValueError(f'Immutable receipt already exists: {path}')
    if not path.exists():
        path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def accepted(entry):
    # Explicit negative fields take precedence over older affirmative fields.
    return ((entry.get('publicationApproved') is True or entry.get('placementReviewed') is True)
            and entry.get('publicationApproved') is not False
            and entry.get('identityReviewApproved') is not False)


def snapshot():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    fmt = subprocess.check_output(['git', 'rev-parse', '--show-object-format'], cwd=ROOT, text=True).strip()
    tree = subprocess.check_output(['git', 'ls-tree', '-rz', commit, '--',
        '3d-viewer/city/data/manifest.json', '3d-viewer/city/data/official-models'], cwd=ROOT)
    blobs = {}
    for row in tree.split(b'\0'):
        if row:
            metadata, path = row.split(b'\t', 1)
            mode, kind, oid = metadata.decode().split()
            if kind == 'blob' and mode == '100644':
                blobs[path.decode()] = oid

    def frozen(path):
        path = path.resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('Source escapes repository')
        relative = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        blob = hashlib.new(fmt, b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blobs.get(relative) != blob:
            raise ValueError(f'Source is not unchanged committed bytes: {relative}')
        return data

    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest = json.loads(frozen(manifest_path))
    selected, held, bindings, catalogue_hashes, inputs = [], [], {}, {}, [manifest_path]
    for url in manifest['officialModelCatalogues']:
        parts = registry.urlsplit(url)
        if parts.scheme or parts.netloc or parts.query or parts.fragment or parts.path.startswith('/'):
            raise ValueError('Catalogue must be repository-relative')
        path = (ROOT / '3d-viewer' / registry.unquote(parts.path)).resolve()
        data = frozen(path)
        catalogue_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
        inputs.append(path)
        cat = json.loads(data)
        if (cat.get('schemaVersion') != 1 or cat.get('crs') != 'EPSG:2326'
                or cat.get('kind') not in ('official-model-catalogue', 'staged-official-model-catalogue')
                or cat.get('verticalDatum') != 'Hong Kong Principal Datum'
                or cat.get('rootTranslation') != [-834500, 0, 816500]):
            raise ValueError(f'Unsupported source coordinate contract: {path}')
        for entry in cat['models']:
            uid = entry['uid']
            bindings[uid] = bindings.get(uid, 0) + 1
            if not accepted(entry):
                held.append({'uid': uid, 'catalogue': str(path.relative_to(ROOT)),
                    'reason': 'Source acceptance is missing or explicitly negative; not authorised by historical visibility.',
                    'acceptance': {key: entry.get(key) for key in
                        ('publicationApproved', 'placementReviewed', 'identityReviewApproved')},
                    'revisit': 'Resolve current source identity/placement acceptance on Astra parent; re-snapshot.'})
                continue
            asset = (path.parent / entry['asset']).resolve()
            source_bytes = frozen(asset)
            if hashlib.sha256(source_bytes).hexdigest() != registry.sha(entry['sha256']):
                raise ValueError(f'Source hash mismatch: {uid}')
            inputs.append(asset)
            source = {'entry': entry, 'catalogue': str(path.relative_to(ROOT)),
                'rootTranslation': cat['rootTranslation'], 'crs': cat['crs'],
                'verticalDatum': cat['verticalDatum'], 'coordinatePolicy': cat.get('coordinatePolicy'),
                'datasetId': cat.get('datasetId')}
            selected.append({'revisionId': registry.digest(source), 'uid': uid,
                'sourceSha256': entry['sha256'], 'sourceCommit': commit, 'source': source})
    if any(count != 1 for count in bindings.values()):
        raise ValueError('Ambiguous current UID binding')
    if subprocess.run(['git', 'diff', '--cached', '--quiet', commit, '--',
            *(str(path.relative_to(ROOT)) for path in inputs)], cwd=ROOT).returncode:
        raise ValueError('Source inputs have staged changes')
    return {'schemaVersion': 1, 'executor': ACTOR, 'sourceCommit': commit,
        'sourceManifestSha256': hashlib.sha256(frozen(manifest_path)).hexdigest(),
        'catalogueHashes': catalogue_hashes, 'selected': sorted(selected, key=lambda s: s['uid']),
        'held': sorted(held, key=lambda s: s['uid']),
        'scope': 'Every installed UID inventoried; process only explicit affirmative source acceptance with no explicit negative.'}


def register_group(connection, sources, recipe, batch):
    """Same registry identities/queue fencing, pipelined in one bounded transaction."""
    registry.validate_recipe(recipe)
    if recipe['status'] != 'ready' or recipe['parameters'].get('adapter') != ADAPTER:
        raise ValueError('This adapter requires its pinned ready recipe')
    recipe_sha = registry.digest(recipe)
    variants = {registry.digest([s['revisionId'], recipe_sha]): s for s in sources}
    for source in sources:
        if (registry.digest(source['source']) != source['revisionId']
                or source['sourceSha256'] != source['source']['entry']['sha256']):
            raise ValueError('Source identity mismatch')
    with connection.transaction():
        cursor = connection.cursor()
        cursor.executemany('''INSERT INTO astra_modelling.optimisation_sources
            (revision_id,uid,source_sha256,source_commit,source) VALUES(%s,%s,%s,%s,%s)
            ON CONFLICT(revision_id) DO NOTHING''', [(s['revisionId'], s['uid'], s['sourceSha256'],
                s['sourceCommit'], Jsonb(s['source'])) for s in sources])
        cursor.executemany('''INSERT INTO astra_modelling.optimisation_variants
            (variant_id,revision_id,recipe_sha256,tier,recipe,planned_by) VALUES(%s,%s,%s,%s,%s,%s)
            ON CONFLICT(variant_id) DO NOTHING''', [(v, s['revisionId'], recipe_sha,
                recipe['tier'], Jsonb(recipe), ACTOR) for v, s in variants.items()])
        rows = connection.execute('''SELECT variant_id,job_id FROM astra_modelling.optimisation_variants
            WHERE variant_id=ANY(%s) ORDER BY variant_id FOR UPDATE''', (list(variants),)).fetchall()
        new_jobs, links = [], []
        for row in rows:
            if row['job_id']:
                continue
            variant = row['variant_id']
            payload = {'variantId': variant, 'revisionId': variants[variant]['revisionId'],
                'recipeSha256': recipe_sha, 'recipe': recipe}
            identity = registry.digest([batch, registry.STAGE, payload])
            new_jobs.append((identity, batch, registry.STAGE, Jsonb(payload)))
            links.append((identity, variant))
        cursor.executemany('''INSERT INTO astra_modelling.jobs(id,batch,stage,payload)
            VALUES(%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING''', new_jobs)
        cursor.executemany('UPDATE astra_modelling.optimisation_variants SET job_id=%s WHERE variant_id=%s', links)
    return variants


def resources(source):
    keys = {'building:' + source['uid'], 'model-source:' + source['sourceSha256']}
    for dependency in source['source']['entry'].get('supportDependencies', []):
        if dependency.get('uid'):
            keys.add('building:' + dependency['uid'])
    return sorted(keys)


def source_groups(sources, shard_index=0, shard_count=1):
    if not 1 <= shard_count <= 16 or not 0 <= shard_index < shard_count:
        raise ValueError('Use 1–16 explicit independent workers')
    return [sources[offset:offset+100] for index, offset in enumerate(range(0, len(sources), 100))
            if index % shard_count == shard_index]


def run(snapshot_path, recipe_path, output, batch, shard_index=0, shard_count=1):
    snap = registry.read(snapshot_path)
    current = snapshot()
    # Commits can advance with unrelated processor/evidence edits, inputs cannot.
    if (current['sourceManifestSha256'] != snap['sourceManifestSha256']
            or current['catalogueHashes'] != snap['catalogueHashes']
            or [{k: s[k] for k in ('revisionId', 'uid', 'sourceSha256')} for s in current['selected']]
               != [{k: s[k] for k in ('revisionId', 'uid', 'sourceSha256')} for s in snap['selected']]):
        raise ValueError('Selected source inputs changed; select a new immutable batch')
    recipe = registry.validate_recipe(registry.read(recipe_path))
    if recipe['lossy'] is not False or recipe['parameters'].get('quantisation') is not False or recipe['parameters'].get('simplification') is not False:
        raise ValueError('Only the explicitly lossless recipe is supported')
    version = subprocess.check_output(['node', '--version'], text=True).strip().removeprefix('v')
    if version != recipe['tools']['node']:
        raise ValueError('Node version does not match the recipe')
    for key, path in [('adapterSha256', HERE/'codec.mjs'), ('npmLockSha256', HERE/'package-lock.json')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != recipe['parameters'][key]:
            raise ValueError('Processing adapter/tool lock changed')
    if registry.read(HERE/'node_modules/meshoptimizer/package.json')['version'] != recipe['tools']['meshoptimizer']:
        raise ValueError('Encoder version does not match the recipe')
    decoder = ROOT / '3d-viewer/vendor/meshopt_decoder.module.js'
    if hashlib.sha256(decoder.read_bytes()).hexdigest() != recipe['parameters']['runtimeDecoderSha256']:
        raise ValueError('Runtime decoder changed')
    output = output.resolve()
    if not output.is_relative_to(ROOT):
        raise ValueError('Private staging must be inside repository')
    connection = connect()
    connection.autocommit = True
    connection.row_factory = dict_row
    codec = subprocess.Popen(['node', str(HERE / 'codec.mjs')], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=ROOT)
    pool = ThreadPoolExecutor(max_workers=1)
    outcomes = []
    started = time.monotonic()
    lease = None
    groups = source_groups(snap['selected'], shard_index, shard_count)
    shard_sources = [source for group in groups for source in group]
    if shard_index:
        batch = f'{batch}-shard-{shard_index}'
    try:
        for group in groups:
            keys = sorted(set(k for source in group for k in resources(source)))
            deadline = time.monotonic() + 600
            while True:
                claim = reservations.claim(ACTOR, keys, ttl=1800, batch=batch, connection=connection)
                if claim['ok'] or time.monotonic() > deadline:
                    break
                time.sleep(5)
            if not claim['ok']:
                # No takeover: record each affected source and continue other groups.
                for source in group:
                    outcomes.append({'uid': source['uid'], 'status': 'reserved', 'reason': claim['error']})
                continue
            lease = claim['reservation']
            renewed = time.monotonic()
            variants = register_group(connection, group, recipe, batch)
            while True:
                job = jobs.claim(batch, ACTOR, [registry.STAGE], lease_seconds=300, connection=connection)
                if job is None:
                    break
                variant = job['payload']['variantId']
                if variant not in variants:
                    jobs.finish(job, error='Job outside currently reserved explicit source group', connection=connection)
                    continue
                source = variants[variant]
                result_path = output / 'results' / f'{variant}.json'
                try:
                    entry = source['source']['entry']
                    asset = ROOT / source['source']['catalogue']
                    asset = (asset.parent / entry['asset']).resolve()
                    if result_path.exists():
                        previous = registry.read(result_path)
                        if any(previous[key] != value for key, value in
                                [('variantId', variant), ('revisionId', source['revisionId']),
                                 ('recipeSha256', registry.digest(recipe)), ('sourceSha256', source['sourceSha256'])]):
                            raise ValueError('Prior immutable result identity mismatch')
                        response = {'ok': True, 'artifact': previous['artifact'], 'metrics': previous['metrics']}
                        response['artifact']['path'] = str(ROOT / response['artifact']['path'])
                    else:
                        request = {'source': str(asset), 'sourceSha256': source['sourceSha256'],
                            'artifactDirectory': str(output / 'artifacts')}
                        codec.stdin.write(json.dumps(request) + '\n'); codec.stdin.flush()
                        pending = pool.submit(codec.stdout.readline)
                        while True:
                            try:
                                line = pending.result(timeout=20)
                                if not line:
                                    raise RuntimeError('Codec process stopped; abort rather than fail unrelated models')
                                response = json.loads(line)
                                break
                            except TimeoutError:
                                if not jobs.heartbeat(job, lease_seconds=300, connection=connection) or not reservations.heartbeat(lease, ttl=1800, connection=connection)['ok']:
                                    raise ValueError('Lease lost during compression')
                    if not response['ok']:
                        raise ValueError(response['error'])
                    if not reservations.owns(lease, connection=connection):
                        raise ValueError('Reservation lost')
                    if hashlib.sha256(asset.read_bytes()).hexdigest() != source['sourceSha256']:
                        raise ValueError('Source changed during processing')
                    artifact = response['artifact']
                    artifact['path'] = str(Path(artifact['path']).relative_to(ROOT))
                    if hashlib.sha256((ROOT / artifact['path']).read_bytes()).hexdigest() != artifact['sha256']:
                        raise ValueError('Output hash readback failed')
                    result = {'variantId': variant, 'revisionId': source['revisionId'],
                        'recipeSha256': registry.digest(recipe), 'uid': source['uid'],
                        'sourceSha256': source['sourceSha256'], 'sourceCommit': source['sourceCommit'],
                        'executor': ACTOR, 'artifact': artifact, 'metrics': response['metrics'],
                        'gates': {'sourceIdentity': 'passed', 'geometry': 'passed',
                            'placement': 'untested', 'visual': 'untested', 'collision': 'untested',
                            'devicePerformance': 'untested'},
                        'validationStatus': 'unreviewed', 'published': False,
                        'qualification': 'Byte-exact offline codec roundtrip; current terrain/runtime/device acceptance is separate.'}
                    report_sha = write(result_path, result)
                    result['report'] = str(result_path.relative_to(ROOT)); result['reportSha256'] = report_sha
                    if not jobs.finish(job, result=result, connection=connection):
                        raise ValueError('Job lease lost before result commit')
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'status': 'complete',
                        'artifact': artifact, 'report': result['report'], 'reportSha256': report_sha,
                        'originalBytes': result['metrics']['originalDownloadBytes'],
                        'outputBytes': result['metrics']['downloadBytes'],
                        'beneficial': result['metrics']['beneficial']})
                except Exception as error:
                    message = str(error)[:600]
                    failure = {'uid': source['uid'], 'variantId': variant, 'status': 'failed', 'error': message}
                    write(output / 'failures' / f'{variant}.json', failure)
                    jobs.finish(job, error=message, connection=connection)
                    outcomes.append(failure)
                    if codec.poll() is not None:
                        raise RuntimeError('Codec process stopped') from error
                if time.monotonic() - renewed > 60:
                    if not reservations.heartbeat(lease, ttl=1800, connection=connection)['ok']:
                        raise ValueError('Reservation lost between models')
                    renewed = time.monotonic()
                if len(outcomes) % 100 == 0:
                    print(json.dumps({'shard': shard_index, 'processed': len(outcomes), 'total': len(shard_sources),
                        'elapsedSeconds': round(time.monotonic()-started, 1)}), flush=True)
            release = reservations.release(lease, connection=connection)
            if not release['ok']:
                raise ValueError('Reservation release failed')
            lease = None
        # Include previously completed same-recipe jobs on a resumed batch.
        with connection.transaction():
            records = connection.execute('''SELECT s.uid,v.variant_id,j.status,j.result,j.error
                FROM astra_modelling.optimisation_sources s
                JOIN astra_modelling.optimisation_variants v USING(revision_id)
                JOIN astra_modelling.jobs j ON j.id=v.job_id
                WHERE v.variant_id=ANY(%s) ORDER BY s.uid''',
                ([registry.digest([s['revisionId'], registry.digest(recipe)]) for s in shard_sources],)).fetchall()
        complete = [row for row in records if row['status'] == 'complete']
        beneficial = [row for row in complete if row['result']['metrics']['beneficial']]
        report = {'schemaVersion': 1, 'batch': batch, 'executor': ACTOR, 'branchId': CONFIG['branch_id'],
            'sourceCommit': snap['sourceCommit'], 'recipeSha256': registry.digest(recipe),
            'inventoryCount': len(snap['selected']) + len(snap['held']), 'selectedCount': len(snap['selected']),
            'heldCount': len(snap['held']), 'completeCount': len(complete),
            'beneficialCount': len(beneficial), 'nonBeneficialCount': len(complete)-len(beneficial),
            'failedCount': sum(row['status']=='failed' for row in records),
            'originalBytes': sum(row['result']['metrics']['originalDownloadBytes'] for row in complete),
            'allOutputBytes': sum(row['result']['metrics']['downloadBytes'] for row in complete),
            'beneficialOriginalBytes': sum(row['result']['metrics']['originalDownloadBytes'] for row in beneficial),
            'beneficialOutputBytes': sum(row['result']['metrics']['downloadBytes'] for row in beneficial),
            'published': False, 'validationStatus': 'unreviewed', 'outcomes': outcomes}
        write(output / 'summaries' / f'{registry.digest(report)}.json', report)
        print(json.dumps({k:v for k,v in report.items() if k!='outcomes'}), flush=True)
    finally:
        if lease:
            reservations.release(lease, connection=connection)
        codec.stdin.close(); codec.terminate(); codec.wait(timeout=15)
        pool.shutdown(wait=False, cancel_futures=True)
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('snapshot'); p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('run')
    for name in ('snapshot', 'recipe', 'output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--batch', required=True)
    p.add_argument('--shard-index', type=int, default=0)
    p.add_argument('--shard-count', type=int, default=1)
    args = parser.parse_args()
    if args.command == 'snapshot':
        snap = snapshot(); write(args.output, snap)
        print(json.dumps({'selected': len(snap['selected']), 'held': len(snap['held']), 'sourceCommit': snap['sourceCommit']}))
    else:
        run(args.snapshot, args.recipe, args.output, args.batch, args.shard_index, args.shard_count)


if __name__ == '__main__':
    main()
