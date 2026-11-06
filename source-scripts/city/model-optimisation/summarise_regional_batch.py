"""Final source-bound Neon/file readback after independently verified workers."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

import regional_batch as regional
import registry
from db import connect, CONFIG


def aggregate(records):
    """Keep delivered GLB and newly exported embedded baselines separate."""
    groups = {}
    for kind, tier, metrics, source_triangles in records:
        key = kind+' / '+tier
        d = groups.setdefault(key, {'models': 0, 'sourceBytes': 0, 'candidateBytes': 0,
            'effectiveBytesKeepingSmaller': 0, 'beneficialModels': 0,
            'sourceTriangles': 0, 'candidateTriangles': 0})
        source, output = metrics['originalDownloadBytes'], metrics['downloadBytes']
        if metrics['beneficial'] != (output < source):
            raise ValueError('Incorrect benefit measurement')
        d['models'] += 1; d['sourceBytes'] += source; d['candidateBytes'] += output
        d['effectiveBytesKeepingSmaller'] += min(source, output)
        d['beneficialModels'] += output < source
        d['sourceTriangles'] += source_triangles; d['candidateTriangles'] += metrics['triangles']
    for d in groups.values():
        d['potentialSavingsPercent'] = 100*(1-d['effectiveBytesKeepingSmaller']/d['sourceBytes']) if d['sourceBytes'] else None
    return groups


def immutable_gzip(path, data):
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()+b'\n'
    packed = gzip.compress(raw, compresslevel=9, mtime=0)
    if path.exists() and path.read_bytes() != packed:
        raise ValueError('Different immutable compressed report already exists')
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(packed)
    return hashlib.sha256(packed).hexdigest()


def summarise(snapshot, recipes, staging, output, apply=False):
    snap = registry.read(snapshot); regional.preflight(snap)
    recipe_hashes = {t: registry.digest(registry.read(recipes/f'{t}-recipe.json')) for t in regional.TIERS}
    expected = {registry.digest([s['revisionId'], h]): (s, tier)
        for s in snap['selected'] for tier, h in recipe_hashes.items()}
    verified, reports = set(), []
    for tier in regional.TIERS:
        for path in sorted((staging/tier/'workers').glob('*.json')):
            report = registry.read(path)
            if report['snapshotSha256'] != regional.file_sha(snapshot):
                continue
            if report['recipeSha256'] != recipe_hashes[tier] or report['tier'] != tier:
                raise ValueError('Worker recipe mismatch')
            reports.append({'path': str(path.relative_to(regional.ROOT)), 'sha256': regional.file_sha(path)})
            for row in report['outcomes']:
                if row['state'] not in ('processed-verified', 'reused-verified'):
                    continue
                source, expected_tier = expected[row['variantId']]
                if source['uid'] != row['uid'] or expected_tier != tier:
                    raise ValueError('Worker source mismatch')
                verified.add(row['variantId'])
    if verified != set(expected):
        raise ValueError(f'Independent worker readback incomplete: {len(verified)}/{len(expected)}')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        rows = con.execute('''SELECT variant_id,processing_status,validation_status,result
            FROM astra_modelling.optimisation_status WHERE variant_id=ANY(%s)
            ORDER BY variant_id''', (list(expected),)).fetchall()
    if len(rows) != len(expected) or any(row[1] != 'complete' for row in rows):
        raise ValueError('Neon does not contain every complete expected variant')
    original_triangles = {expected[v][0]['uid']: result['metrics']['triangles']
        for v, _, _, result in rows if expected[v][1] == 'original'}
    metrics, index, checked_hashes = [], [], {}
    for variant, _, review, result in rows:
        source, tier = expected[variant]
        for key, value in [('variantId', variant), ('revisionId', source['revisionId']),
                ('recipeSha256', recipe_hashes[tier]), ('sourceSha256', source['sourceSha256'])]:
            if result.get(key) != value:
                raise ValueError('Final result identity mismatch')
        for relative, sha in [(result['artifact']['path'], result['artifact']['sha256']),
                (result['report'], result['reportSha256'])]:
            if relative not in checked_hashes:
                checked_hashes[relative] = regional.file_sha(regional.output_path(relative))
            if checked_hashes[relative] != sha:
                raise ValueError('Final file hash mismatch')
        receipt = registry.read(regional.output_path(result['report']))
        if receipt != {k:v for k,v in result.items() if k not in ('report', 'reportSha256')}:
            raise ValueError('Neon differs from immutable receipt')
        if result.get('published') is not False:
            raise ValueError('Unexpected publication state')
        metrics.append((source['kind'], tier, result['metrics'], original_triangles[source['uid']]))
        index.append({'uid': source['uid'], 'sectionId': source['sectionId'], 'kind': source['kind'],
            'tier': tier, 'variantId': variant, 'revisionId': source['revisionId'],
            'sourceSha256': source['sourceSha256'], 'recipeSha256': recipe_hashes[tier],
            'artifact': result['artifact'], 'report': result['report'],
            'reportSha256': result['reportSha256'], 'validationStatus': review,
            'bytes': result['metrics']['downloadBytes'], 'triangles': result['metrics']['triangles'],
            'beneficial': result['metrics']['beneficial']})
    output.mkdir(parents=True, exist_ok=True)
    index_sha = immutable_gzip(output/'variants.json.gz', index)
    source_packed = gzip.compress(snapshot.read_bytes(), compresslevel=9, mtime=0)
    source_archive = output/'sources.json.gz'
    if source_archive.exists() and source_archive.read_bytes() != source_packed:
        raise ValueError('Different immutable source archive already exists')
    if not source_archive.exists():
        source_archive.write_bytes(source_packed)
    source_sha = hashlib.sha256(source_packed).hexdigest()
    summary = {'schemaVersion': 1, 'executor': regional.ACTOR, 'branchId': CONFIG['branch_id'],
        'sourceCommit': snap['sourceCommit'], 'sourceSnapshotSha256': regional.file_sha(snapshot),
        'sourceArchiveSha256': source_sha, 'variantIndexSha256': index_sha,
        'models': len(snap['selected']), 'variants': len(expected), 'tiers': list(regional.TIERS),
        'sourceKinds': dict(Counter(s['kind'] for s in snap['selected'])),
        'sections': dict(Counter(s['sectionId'] for s in snap['selected'])),
        'reviewStates': dict(Counter(r[2] for r in rows)), 'failedVariants': 0,
        'workerReports': reports, 'verifiedFileCount': len(checked_hashes),
        'measurementsBySourceKindAndTier': aggregate(metrics),
        'published': False, 'sourceGeometryChanges': 0, 'modelReviewWrites': 0,
        'qualification': 'All expected variants complete with independent worker decoder checks and final Neon/file/receipt readback. Embedded bytes are a new rendered-GLB export baseline, not existing JSON tile transfer savings. Visual/physical/collision/device approval and runtime publication remain separate.'}
    summary_sha = regional.batch.write(output/'summary.json', summary)
    if apply:
        name = 'lantau-installed-compression-readback-20261106'
        claimed = regional.reservations.claim(regional.ACTOR+'-final', ['source-context:'+name], ttl=600, batch=name)
        if not claimed['ok']:
            raise ValueError('Final checkpoint already reserved')
        lease = claimed['reservation']
        try:
            payload = {'snapshotSha256': regional.file_sha(snapshot), 'summarySha256': summary_sha,
                'variantIndexSha256': index_sha, 'workerReports': reports}
            job_id = regional.jobs.enqueue(name, 'model-optimisation-regional-readback-v1', payload)
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                previous = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (job_id,)).fetchone()
            if previous[0] != 'complete':
                job = regional.jobs.claim(name, lease['owner'], ['model-optimisation-regional-readback-v1'], lease_seconds=600)
                if not job or job['id'] != job_id or not regional.reservations.owns(lease):
                    raise ValueError('Checkpoint job/source lease unavailable')
                if not regional.jobs.finish(job, result=summary):
                    raise ValueError('Checkpoint job fence lost')
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                if con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (job_id,)).fetchone() != ('complete', summary):
                    raise ValueError('Final Neon checkpoint readback mismatch')
            regional.batch.write(output/'neon-sync.json', {'jobId': job_id, 'exactResultMatch': True,
                'summarySha256': summary_sha, 'modelReviewWrites': 0, 'published': False})
        finally:
            regional.reservations.release(lease)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('workerReports', 'measurementsBySourceKindAndTier')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('snapshot', 'recipes', 'staging', 'output'):
        parser.add_argument('--'+key, type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    a = parser.parse_args()
    summarise(a.snapshot.resolve(), a.recipes.resolve(), a.staging.resolve(), a.output.resolve(), a.apply)
