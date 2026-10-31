"""Read back Neon and every source/output byte; append one bounded batch checkpoint."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import batch
import registry
from db import connect, CONFIG
from psycopg.rows import dict_row
import jobs


def audit(snapshot_path, recipe_path, output, checkpoint_batch, apply=False):
    snap = registry.read(snapshot_path)
    batch.check_snapshot(snap)
    recipe = registry.read(recipe_path)
    recipe_sha = registry.digest(recipe)
    expected = {registry.digest([source['revisionId'], recipe_sha]): source for source in snap['selected']}
    with connect() as con:
        con.row_factory = dict_row
        records = con.execute('''SELECT * FROM astra_modelling.optimisation_status
            WHERE variant_id=ANY(%s) ORDER BY uid''', (list(expected),)).fetchall()
    if len(records) != len(expected) or any(row['processing_status'] != 'complete' for row in records):
        missing = set(expected) - {row['variant_id'] for row in records}
        incomplete = [{'uid': row['uid'], 'status': row['processing_status'], 'error': row['error']}
            for row in records if row['processing_status'] != 'complete']
        raise ValueError(f'Incomplete source batch: missing={len(missing)}, states={incomplete[:20]}')
    decoder = subprocess.Popen(['node', str(batch.HERE/'audit_codec.mjs')],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, cwd=batch.ROOT)
    checked = []
    started = time.monotonic()
    try:
        for row in records:
            source = expected[row['variant_id']]
            result = row['result']
            for key, value in [('variantId', row['variant_id']), ('revisionId', source['revisionId']),
                    ('sourceSha256', source['sourceSha256']), ('recipeSha256', recipe_sha)]:
                if result.get(key) != value:
                    raise ValueError('Neon result identity mismatch')
            if row['validation_status'] != 'unreviewed' or result.get('published') is not False:
                raise ValueError('Unexpected review/publication state')
            report_path = (batch.ROOT/result['report']).resolve()
            artifact_path = (batch.ROOT/result['artifact']['path']).resolve()
            if not report_path.is_relative_to(batch.ROOT) or not artifact_path.is_relative_to(batch.ROOT):
                raise ValueError('Output path escapes repository')
            report_bytes = report_path.read_bytes()
            if hashlib.sha256(report_bytes).hexdigest() != result['reportSha256']:
                raise ValueError('Immutable report hash mismatch')
            report = json.loads(report_bytes)
            if report != {k:v for k,v in result.items() if k not in ('report','reportSha256')}:
                raise ValueError('Neon result differs from immutable report')
            metrics = result['metrics']
            catalogue = batch.ROOT/source['source']['catalogue']
            source_path = (catalogue.parent/source['source']['entry']['asset']).resolve()
            decoder.stdin.write(json.dumps({'source': str(source_path),
                'artifact': str(artifact_path), 'sourceSha256': source['sourceSha256'],
                'artifactSha256': result['artifact']['sha256'],
                'exactBufferViewSha256': metrics['exactBufferViewSha256'],
                'recipe': recipe, 'metrics': metrics})+'\n')
            decoder.stdin.flush()
            readback = json.loads(decoder.stdout.readline())
            if not readback['ok']:
                raise ValueError(f"Output roundtrip failed: {source['uid']}: {readback['error']}")
            if (readback['sourceBytes'] != metrics['originalDownloadBytes']
                    or readback['outputBytes'] != metrics['downloadBytes']
                    or metrics['beneficial'] != (readback['outputBytes'] < readback['sourceBytes'])):
                raise ValueError('Transfer metrics mismatch')
            checked.append({'uid': source['uid'], 'variantId': row['variant_id'],
                'revisionId': source['revisionId'], 'jobId': row['job_id'],
                'sourceSha256': source['sourceSha256'], 'artifact': result['artifact'],
                'report': result['report'], 'reportSha256': result['reportSha256'],
                'sourceBytes': readback['sourceBytes'], 'outputBytes': readback['outputBytes'],
                'beneficial': metrics['beneficial']})
            if len(checked) % 500 == 0:
                print(json.dumps({'auditVerified': len(checked), 'total': len(records)}), flush=True)
    finally:
        decoder.stdin.close(); decoder.terminate(); decoder.wait(timeout=15)
    beneficial = [row for row in checked if row['beneficial']]
    original_bytes = sum(row['sourceBytes'] for row in checked)
    output_bytes = sum(row['outputBytes'] for row in checked)
    savings = sum(row['sourceBytes']-row['outputBytes'] for row in beneficial)
    report = {'schemaVersion': 1, 'executor': batch.ACTOR, 'batch': checkpoint_batch,
        'branchId': CONFIG['branch_id'], 'schema': CONFIG['schema'],
        'sourceCommit': snap['sourceCommit'], 'recipeSha256': recipe_sha,
        'sourceSnapshotSha256': hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
        'sourceSnapshot': str(snapshot_path.resolve().relative_to(batch.ROOT)),
        'installedCount': len(snap['selected'])+len(snap['held']),
        'processedCount': len(checked), 'beneficialCount': len(beneficial),
        'nonBeneficialCount': len(checked)-len(beneficial), 'sourceAcceptanceHeldCount': len(snap['held']),
        'failedCount': 0, 'sourceDownloadBytes': original_bytes, 'allOutputDownloadBytes': output_bytes,
        'beneficialSavedBytes': savings, 'effectiveDownloadBytesKeepingNonBeneficialOriginals': original_bytes-savings,
        'effectiveSavingsPercent': savings/original_bytes*100,
        'validationStatus': 'unreviewed', 'publishedCount': 0,
        'qualification': 'Offline source/output/Neon readback only. No current terrain, visual, collision, device or publication approval.',
        'auditSeconds': time.monotonic()-started, 'outputs': checked,
        'held': [{'uid': row['uid'], 'reason': row['reason'], 'revisit': row['revisit']} for row in snap['held']]}
    report_sha = batch.write(output, report)
    if apply:
        # Checkpoint records held sources without creating variant plans for them.
        job_id = jobs.enqueue(checkpoint_batch, 'model-optimisation-audit-v1',
            {'report': str(output.resolve().relative_to(batch.ROOT)), 'reportSha256': report_sha,
                'sourceSnapshotSha256': report['sourceSnapshotSha256'], 'recipeSha256': recipe_sha})
        job = jobs.claim(checkpoint_batch, batch.ACTOR, ['model-optimisation-audit-v1'], job_ids=[job_id])
        if job:
            result = {k:v for k,v in report.items() if k not in ('outputs','held')}
            result.update(report=str(output.resolve().relative_to(batch.ROOT)),reportSha256=report_sha)
            if not jobs.finish(job, result=result):
                raise ValueError('Audit checkpoint lease lost')
        with connect() as con:
            con.row_factory = dict_row
            row = con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()
        if row['status'] != 'complete' or row['result']['reportSha256'] != report_sha:
            raise ValueError('Audit checkpoint readback mismatch')
        receipt = {'jobId': job_id, 'reportSha256': report_sha,
            'branchId': CONFIG['branch_id'], 'status': 'complete', 'exactReadback': True}
        batch.write(output.with_name('neon-sync.json'),receipt)
    print(json.dumps({k:v for k,v in report.items() if k not in ('outputs','held')},indent=2),flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('snapshot','recipe','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--batch',required=True);parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    audit(args.snapshot,args.recipe,args.output,args.batch,args.apply)
