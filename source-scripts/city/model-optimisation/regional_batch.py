"""Explicit regional compression: committed GLBs and exact existing-render exports.

This adapter never installs originals or publishes candidates. It reuses global
source/recipe identities, shared reservations, job fencing and existing codecs.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid

import batch
import registry
from db import connect, CONFIG, transaction
import jobs
import reservations
from psycopg.rows import dict_row

HERE, ROOT = batch.HERE, batch.ROOT
ACTOR = 'codex-islands-compression-20261106'
TIERS = ('original', 'high', 'balanced', 'lightweight')


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FrozenTree:
    """Read only regular, unchanged files at one exact source commit."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()
        self.format = self.git('rev-parse', '--show-object-format').decode().strip()
        self.staged = set(self.git('diff', '--cached', '--name-only', self.commit).decode().splitlines())
        self.blobs = {}
        for row in self.git('ls-tree', '-rz', self.commit).split(b'\0'):
            if row:
                metadata, path = row.split(b'\t', 1)
                mode, kind, oid = metadata.decode().split()
                if mode == '100644' and kind == 'blob':
                    self.blobs[path.decode()] = oid
        self.hashes = {}

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root)

    def read(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Source escapes its frozen repository')
        relative = path.relative_to(self.root).as_posix()
        data = path.read_bytes()
        oid = hashlib.new(self.format, b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if self.blobs.get(relative) != oid:
            raise ValueError(f'Source is not unchanged committed bytes: {relative}')
        if relative in self.staged:
            raise ValueError(f'Staged source change: {relative}')
        self.hashes[relative] = hashlib.sha256(data).hexdigest()
        return data

    def modules(self, relative):
        """Pin the renderer's complete local static import closure."""
        seen = set()
        def visit(path):
            path = (self.root/path).resolve().relative_to(self.root).as_posix()
            if path in seen:
                return
            seen.add(path)
            data = self.read(path).decode()
            for url in re.findall(r'(?:from\s*|import\s*)[\'"]([^\'"]+)[\'"]', data):
                if not url.startswith('.'):
                    raise ValueError('Renderer has an unpinned external import')
                visit(str(Path(path).parent/url))
        visit(relative)
        return {path: self.hashes[path] for path in sorted(seen)}


def island_mask(tree, definition):
    """Use retained OSM island geometry; no guessed latitude split."""
    from pyproj import Transformer
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    data = json.loads(gzip.decompress(tree.read(definition['snapshot'])))
    kind, oid = definition['source'].split('/')
    rows = [e for e in data['elements'] if e['type'] == kind and e['id'] == int(oid)]
    if len(rows) != 1:
        raise ValueError('Missing/ambiguous retained island polygon')
    transform = Transformer.from_crs(4326, 2326, always_xy=True)
    lines = {'outer': [], 'inner': []}
    for member in rows[0]['members']:
        role = member.get('role', 'outer')
        if member.get('geometry') and role in lines:
            coords = [transform.transform(p['lon'], p['lat']) for p in member['geometry']]
            lines[role].append(LineString([(x-834500, 816500-y) for x, y in coords]))
    outer = unary_union(list(polygonize(unary_union(lines['outer']))))
    inner = unary_union(list(polygonize(unary_union(lines['inner']))))
    mask = outer.difference(inner)
    if mask.is_empty or not mask.is_valid:
        raise ValueError('Invalid retained island polygon')
    return mask.buffer(definition.get('bufferMetres', 0))


def checked_response(process, request):
    process.stdin.write(json.dumps(request)+'\n'); process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError('Producer exited; retain attempt and stop')
    response = json.loads(line)
    if not response.get('ok'):
        raise ValueError(response.get('error', 'Producer failed'))
    return response


def private_directory(path):
    path = Path(path).resolve()
    staging = ROOT/'source-scripts/city/model-optimisation/staging'
    if not path.is_relative_to(staging) or not path.relative_to(staging).parts[0].startswith('regional-'):
        raise ValueError('Use an explicitly ignored regional-* private staging directory')
    if subprocess.run(['git', 'check-ignore', '-q', str(path/'probe')], cwd=ROOT).returncode:
        raise ValueError('Private staging is not ignored by Git')
    return path


def freeze(source_root, scope_path, output):
    from shapely.geometry import Polygon
    from shapely.strtree import STRtree
    output = private_directory(output)
    tree = FrozenTree(source_root)
    scope = registry.read(scope_path)
    if scope.get('schemaVersion') != 1 or scope.get('includeBase') not in (True, False):
        raise ValueError('Explicit base inclusion policy required')
    sections = json.loads(tree.read('3d-viewer/city/data/review-sections.json'))['sections']
    selected_sections = {s['id']: s for s in sections if s['id'] in scope['sections']}
    if set(selected_sections) != set(scope['sections']):
        raise ValueError('Unknown/duplicate geographic section')
    masks = {d['sectionId']: island_mask(tree, d) for d in scope.get('islandMasks', [])}
    polygons, owners = [], []
    for sid, section in selected_sections.items():
        for item in section['polygons']:
            poly = Polygon(item['rings'][0], item['rings'][1:])
            if sid in masks:
                poly = poly.intersection(masks[sid])
            polygons.append(poly); owners.append(sid)
    index = STRtree(polygons)
    manifest = json.loads(tree.read('3d-viewer/city/data/manifest.json'))
    # Preserve the existing progressive-source identity exactly, enabling reuse.
    previous_root = batch.ROOT
    try:
        batch.ROOT = tree.root
        all_progressive = batch.snapshot('installed-v1')
    finally:
        batch.ROOT = previous_root
    progressive = {s['uid']: s for s in all_progressive['selected']}
    renderer = tree.modules('3d-viewer/city/building-geometry.js')
    exporter = subprocess.Popen(['node', str(HERE/'export_render_mesh.mjs'), str(tree.root)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=ROOT)
    selected, census, seen = [], [], set()
    total = 0
    try:
        for tile in manifest['tiles']:
            path = '3d-viewer/'+tile['url']
            raw = tree.read(path)
            for building in json.loads(raw)['buildings']:
                total += 1
                centre = Polygon(building['rings'][0], building['rings'][1:]).centroid
                hits = {owners[i] for i in index.query(centre) if polygons[i].covers(centre)}
                if not hits:
                    continue
                if len(hits) != 1 or building['uid'] in seen:
                    raise ValueError('Ambiguous section or duplicate building UID')
                uid = building['uid']; seen.add(uid); sid = hits.pop()
                kind = ('progressive-glb-v1' if uid in progressive else
                    'embedded-render-v1' if building.get('modelGeometry') else 'base-render-v1')
                census.append({'uid': uid, 'name': building.get('name', ''), 'sectionId': sid,
                    'kind': kind, 'tile': path, 'centre': [centre.x, centre.y]})
                if kind == 'base-render-v1' and not scope['includeBase']:
                    continue
                if kind == 'progressive-glb-v1':
                    row = dict(progressive[uid]); row['kind'] = kind
                    relative = str((Path(row['source']['catalogue']).parent/row['source']['entry']['asset']))
                    tree.read(relative)
                    row['inputPath'] = str(tree.root/relative)
                else:
                    response = checked_response(exporter, {'tile': path, 'tileSha256': tree.hashes[path],
                        'uid': uid, 'kind': kind, 'directory': str(output/'render-inputs')})
                    entry = {'uid': uid, 'sha256': response['sha256'],
                        'asset': Path(response['path']).name,
                        'triangles': response['triangles'], 'supportDependencies': []}
                    source = {'kind': kind, 'entry': entry, 'tile': path, 'tileSha256': tree.hashes[path],
                        'buildingRecordSha256': registry.digest(building),
                        'rendererBuildingJsonSha256': response['buildingJsonSha256'],
                        'rendererModules': renderer, 'exporterSha256': file_sha(HERE/'export_render_mesh.mjs'),
                        'renderAttributes': response['attributes'], 'rootTranslation': [0, 0, 0],
                        'crs': 'EPSG:2326', 'verticalDatum': 'Hong Kong Principal Datum',
                        'coordinatePolicy': 'Existing local-world renderer arrays at fixed 1x; identity scene pose. Includes existing illustrative foundation where present.',
                        'originalModelGeometrySha256': registry.digest(building['modelGeometry']) if building.get('modelGeometry') else None,
                        'datasetId': building.get('sourceDataset'), 'tileSource': building.get('modelGeometry', {}).get('sourceHashes')}
                    row = {'revisionId': registry.digest(source), 'uid': uid, 'sourceSha256': entry['sha256'],
                        'sourceCommit': tree.commit, 'source': source, 'kind': kind, 'inputPath': response['path']}
                row['sectionId'] = sid
                selected.append(row)
    finally:
        exporter.stdin.close(); exporter.wait(timeout=30)
    if total != manifest['counts']['buildings']:
        raise ValueError('Incomplete whole-map census')
    # Add catalogues and the exact GLBs used by this cohort to the frozen inputs.
    tree.hashes.update(all_progressive['catalogueHashes'])
    snapshot = {'schemaVersion': 1, 'adapter': 'regional-existing-mesh-v1', 'selectionPolicy': 'installed-v1',
        'sourceRoot': str(tree.root), 'sourceCommit': tree.commit, 'scope': scope,
        'scopeSha256': file_sha(scope_path), 'sourceInputs': tree.hashes,
        'processorSha256': file_sha(__file__), 'exporterSha256': file_sha(HERE/'export_render_mesh.mjs'),
        'selected': sorted(selected, key=lambda r: r['uid']), 'census': census, 'territoryForms': total,
        'counts': dict(Counter(r['kind'] for r in census)), 'published': False}
    batch.write(output/'sources.json', snapshot)
    return snapshot


def preflight(snap):
    if snap['adapter'] != 'regional-existing-mesh-v1' or snap['processorSha256'] != file_sha(__file__):
        raise ValueError('Regional producer/snapshot mismatch')
    if snap['exporterSha256'] != file_sha(HERE/'export_render_mesh.mjs'):
        raise ValueError('Render exporter changed')
    tree = FrozenTree(snap['sourceRoot'])
    # Unrelated later commits can be used only if every frozen source is exact.
    for path, expected in snap['sourceInputs'].items():
        if hashlib.sha256(tree.read(path)).hexdigest() != expected:
            raise ValueError(f'Frozen regional source changed: {path}')
    for row in snap['selected']:
        if registry.digest(row['source']) != row['revisionId']:
            raise ValueError('Revision identity changed')
        if file_sha(row['inputPath']) != row['sourceSha256']:
            raise ValueError('Frozen mesh input changed')


def check_recipe(recipe):
    registry.validate_recipe(recipe)
    producer = batch.adapter_file(recipe)
    if recipe['status'] != 'ready' or recipe['tier'] not in TIERS:
        raise ValueError('Explicit ready tier required')
    if subprocess.check_output(['node', '--version'], text=True).strip().removeprefix('v') != recipe['tools']['node']:
        raise ValueError('Node version changed')
    for key, path in [('adapterSha256', producer), ('npmLockSha256', HERE/'package-lock.json'),
            ('runtimeDecoderSha256', ROOT/'3d-viewer/vendor/meshopt_decoder.module.js')]:
        if file_sha(path) != recipe['parameters'][key]:
            raise ValueError('Recipe tool/decoder changed')
    if registry.read(HERE/'node_modules/meshoptimizer/package.json')['version'] != recipe['tools']['meshoptimizer']:
        raise ValueError('Meshopt version changed')
    return producer


def output_path(relative):
    path = (ROOT/relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Result escapes processing repository')
    return path


def lease_snapshot_owned(lease, connection):
    """Same active-token/all-members rule as _current, in one read snapshot.

    This is the existing compression branch's read-only ownership query. Claims,
    renewals, release and job completion retain their ordinary locking/fencing.
    """
    with transaction(connection) as con:
        con.row_factory = dict_row
        row = con.execute('''SELECT
            (SELECT count(*) FROM astra_modelling.reservations r
                WHERE r.resource=ANY(g.resources) AND r.token=g.token)
                = cardinality(g.resources) AS owned
            FROM astra_modelling.reservation_groups g
            WHERE g.token=%s AND g.owner=%s AND g.released_at IS NULL
                AND g.lease_until>clock_timestamp()''',
            (uuid.UUID(str(lease['token'])), lease['owner'])).fetchone()
        return bool(row and row['owned'])


def verify_result(source, recipe, variant, result, auditor):
    for key, expected in [('variantId', variant), ('revisionId', source['revisionId']),
            ('recipeSha256', registry.digest(recipe)), ('sourceSha256', source['sourceSha256'])]:
        if result.get(key) != expected:
            raise ValueError('Existing result identity mismatch')
    report = output_path(result['report'])
    if file_sha(report) != result['reportSha256']:
        raise ValueError('Result receipt hash mismatch')
    if registry.read(report) != {k: v for k, v in result.items() if k not in ('report', 'reportSha256')}:
        raise ValueError('Database result differs from immutable receipt')
    metrics = result['metrics']
    readback = checked_response(auditor, {'source': source['inputPath'],
        'artifact': str(output_path(result['artifact']['path'])), 'sourceSha256': source['sourceSha256'],
        'artifactSha256': result['artifact']['sha256'], 'exactBufferViewSha256': metrics['exactBufferViewSha256'],
        'recipe': recipe, 'metrics': metrics})
    if (readback['sourceBytes'] != metrics['originalDownloadBytes'] or
            readback['outputBytes'] != metrics['downloadBytes'] or
            metrics['beneficial'] != (readback['outputBytes'] < readback['sourceBytes'])):
        raise ValueError('Transfer measurement mismatch')


def worker(snapshot_path, recipe_path, output, batch_name, shard, workers):
    output = private_directory(output)
    snap, recipe = registry.read(snapshot_path), registry.read(recipe_path)
    preflight(snap); producer = check_recipe(recipe)
    connection = connect(); connection.autocommit = True; connection.row_factory = dict_row
    processes = [subprocess.Popen(['node', str(path)], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, text=True, cwd=ROOT) for path in (producer, HERE/'audit_codec.mjs')]
    codec, auditor = processes
    pool = ThreadPoolExecutor(max_workers=1)
    outcomes, lease = [], None
    try:
        for group in batch.source_groups(snap['selected'], shard, workers):
            claim = reservations.claim(ACTOR, sorted({k for s in group for k in batch.resources(s)}),
                ttl=1800, batch=batch_name, connection=connection)
            if not claim['ok']:
                outcomes.extend({'uid': s['uid'], 'state': 'held-reservation', 'error': claim['error']} for s in group)
                continue
            lease = claim['reservation']
            if not reservations.owns(lease, connection=connection):
                raise ValueError('Reservation lost immediately after claim')
            renewed = time.monotonic()
            variants = batch.register_group(connection, group, recipe, batch_name)
            records = connection.execute('''SELECT v.variant_id,j.id,j.batch,j.status,j.result,j.error
                FROM astra_modelling.optimisation_variants v JOIN astra_modelling.jobs j ON j.id=v.job_id
                WHERE v.variant_id=ANY(%s)''', (list(variants),)).fetchall()
            for record in records:
                variant = record['variant_id']; source = variants[variant]
                if record['status'] == 'complete':
                    verify_result(source, recipe, variant, record['result'], auditor)
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'state': 'reused-verified'})
                    continue
                if record['status'] == 'failed':
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'state': 'held-prior-failure', 'error': record['error']})
                    continue
                job = jobs.claim(record['batch'], ACTOR, [registry.STAGE], lease_seconds=300,
                    connection=connection, job_ids=[record['id']])
                if not job:
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'state': 'held-job-lease'})
                    continue
                try:
                    request = {'source': source['inputPath'], 'sourceSha256': source['sourceSha256'],
                        'artifactDirectory': str(output/recipe['tier']/'artifacts'), 'recipe': recipe}
                    pending = pool.submit(checked_response, codec, request)
                    while True:
                        try:
                            response = pending.result(timeout=20); break
                        except TimeoutError:
                            if not jobs.heartbeat(job, lease_seconds=300, connection=connection) or not reservations.heartbeat(lease, ttl=1800, connection=connection)['ok']:
                                raise ValueError('Lease lost during compression')
                    if not lease_snapshot_owned(lease, connection):
                        raise ValueError('Reservation lost')
                    artifact = response['artifact']
                    artifact['path'] = str(Path(artifact['path']).relative_to(ROOT))
                    result = {'variantId': variant, 'revisionId': source['revisionId'], 'uid': source['uid'],
                        'sourceSha256': source['sourceSha256'], 'sourceCommit': source['sourceCommit'],
                        'recipeSha256': registry.digest(recipe), 'executor': ACTOR,
                        'artifact': artifact, 'metrics': response['metrics'], 'sourceKind': source['kind'],
                        'gates': {'sourceIdentity': 'passed', 'geometry': 'passed', 'placement': 'untested',
                            'visual': 'untested', 'collision': 'untested', 'devicePerformance': 'untested'},
                        'validationStatus': 'unreviewed', 'published': False,
                        'qualification': 'Private offline candidate. Embedded/base inputs are exports of the existing renderer, including its existing foundations. Export baseline bytes are not network tile savings. No physical/runtime or device approval.'}
                    receipt = output/recipe['tier']/'results'/f'{variant}.json'
                    result_sha = batch.write(receipt, result)
                    result['report'] = str(receipt.relative_to(ROOT)); result['reportSha256'] = result_sha
                    verify_result(source, recipe, variant, result, auditor)
                    if not jobs.finish(job, result=result, connection=connection):
                        raise ValueError('Job lease lost before completion')
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'state': 'processed-verified'})
                except Exception as error:
                    jobs.finish(job, error=str(error)[:600], connection=connection)
                    outcomes.append({'uid': source['uid'], 'variantId': variant, 'state': 'failed', 'error': str(error)[:600]})
                    if codec.poll() is not None or auditor.poll() is not None:
                        raise
                if time.monotonic() - renewed >= 60:
                    if not reservations.heartbeat(lease, ttl=1800, connection=connection)['ok']:
                        raise ValueError('Reservation lost between models')
                    renewed = time.monotonic()
            if not reservations.release(lease, connection=connection)['ok']:
                raise ValueError('Reservation release failed')
            lease = None
            print(json.dumps({'tier': recipe['tier'], 'shard': shard, 'verified': len(outcomes),
                'states': dict(Counter(r['state'] for r in outcomes))}), flush=True)
        report = {'schemaVersion': 1, 'snapshotSha256': file_sha(snapshot_path), 'recipeSha256': registry.digest(recipe),
            'branchId': CONFIG['branch_id'], 'tier': recipe['tier'], 'shard': shard, 'workers': workers,
            'states': dict(Counter(r['state'] for r in outcomes)), 'outcomes': outcomes,
            'published': False, 'validationStatus': 'unreviewed'}
        batch.write(output/recipe['tier']/'workers'/f'{time.time_ns()}-{shard}.json', report)
    finally:
        if lease:
            reservations.release(lease)
        for process in processes:
            process.stdin.close(); process.terminate(); process.wait(timeout=15)
        pool.shutdown(wait=False, cancel_futures=True); connection.close()


def launch(snapshot_path, recipes, output, batch_name, workers):
    batch.source_groups([], 0, workers)
    preflight(registry.read(snapshot_path))
    for tier in TIERS:
        recipe = recipes/f'{tier}-recipe.json'
        check_recipe(registry.read(recipe))
        logs = output/tier/'logs'/str(time.time_ns()); logs.mkdir(parents=True)
        children = []
        try:
            for shard in range(workers):
                log = (logs/f'{shard}.log').open('w')
                child = subprocess.Popen([sys.executable, '-u', str(Path(__file__).resolve()), 'worker',
                    '--snapshot', str(snapshot_path), '--recipe', str(recipe), '--output', str(output),
                    '--batch', batch_name+'-'+tier, '--shard', str(shard), '--workers', str(workers)],
                    cwd=ROOT, stdout=log, stderr=log)
                children.append((child, log))
            failures = []
            for child, log in children:
                code = child.wait(); log.close()
                if code:
                    failures.append(code)
            print(json.dumps({'tier': tier, 'workerFailures': failures, 'logs': str(logs)}), flush=True)
            if failures:
                raise RuntimeError('Regional worker failed; inspect retained logs')
        finally:
            for child, log in children:
                if child.poll() is None:
                    child.terminate()
                child.wait(); log.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('freeze')
    p.add_argument('--source-root', type=Path, required=True); p.add_argument('--scope', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('launch')
    p.add_argument('--recipes', type=Path, required=True)
    for name in ('worker',):
        p = sub.add_parser(name); p.add_argument('--recipe', type=Path, required=True)
        p.add_argument('--shard', type=int, required=True)
    for name in ('launch', 'worker'):
        p = sub.choices[name]
        p.add_argument('--snapshot', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
        p.add_argument('--batch', required=True); p.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.command == 'freeze':
        snap = freeze(args.source_root, args.scope, args.output)
        print(json.dumps({'selected': len(snap['selected']), 'counts': snap['counts']}))
    elif args.command == 'launch':
        launch(args.snapshot.resolve(), args.recipes.resolve(), args.output.resolve(), args.batch, args.workers)
    else:
        worker(args.snapshot.resolve(), args.recipe.resolve(), args.output.resolve(), args.batch, args.shard, args.workers)


if __name__ == '__main__':
    main()
