"""Restore exact completed same-source/recipe artifacts from an existing checkout.

Read-only Neon lookup; copies immutable private cache bytes, never jobs/reviews.
Useful when the processing branch's results already exist on this same machine.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

import regional_batch as regional
import registry
from db import connect


def private_path(root, relative):
    path = (root/relative).resolve()
    staging = root/'source-scripts/city/model-optimisation/staging'
    if not path.is_relative_to(staging):
        raise ValueError('Only private staging artifacts/receipts can be restored')
    return path


def restore(snapshot, recipes, from_root, report):
    snap = registry.read(snapshot)
    regional.preflight(snap)
    expected = {}
    for tier in regional.TIERS:
        recipe = registry.read(recipes/f'{tier}-recipe.json')
        regional.check_recipe(recipe)
        for source in snap['selected']:
            expected[registry.digest([source['revisionId'], registry.digest(recipe)])] = source
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        rows = connection.execute('''SELECT v.variant_id,j.result
            FROM astra_modelling.optimisation_variants v
            JOIN astra_modelling.jobs j ON j.id=v.job_id
            WHERE v.variant_id=ANY(%s) AND j.status='complete' ORDER BY v.variant_id''',
            (list(expected),)).fetchall()
    destinations = set()
    for _, result in rows:
        for relative in (result['artifact']['path'], result['report']):
            if '\0' in relative:
                raise ValueError('Invalid cache filename')
            destinations.add(str(private_path(regional.ROOT, relative)))
    if destinations:
        check = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin', '-z'], cwd=regional.ROOT,
            input=b'\0'.join(p.encode() for p in sorted(destinations))+b'\0', capture_output=True)
        if check.returncode != 0 or set(check.stdout.decode().rstrip('\0').split('\0')) != destinations:
            raise ValueError('Every destination must be ignored by Git')
    restored, existing, seen = 0, 0, set()
    for variant, result in rows:
        source = expected[variant]
        if (result['variantId'] != variant or result['revisionId'] != source['revisionId']
                or result['sourceSha256'] != source['sourceSha256']):
            raise ValueError('Completed result/source mismatch')
        for relative, sha in [(result['artifact']['path'], result['artifact']['sha256']),
                (result['report'], result['reportSha256'])]:
            if (relative, sha) in seen:
                continue
            seen.add((relative, sha))
            dest = private_path(regional.ROOT, relative)
            if dest.exists():
                if regional.file_sha(dest) != sha:
                    raise ValueError('Different existing cache bytes; never overwrite')
                existing += 1
                continue
            src = private_path(from_root, relative)
            if regional.file_sha(src) != sha:
                raise ValueError('Prior cache source hash mismatch')
            dest.parent.mkdir(parents=True, exist_ok=True)
            # New immutable names only; no mutation of the original checkout.
            with dest.open('xb') as output, src.open('rb') as input:
                shutil.copyfileobj(input, output)
            if regional.file_sha(dest) != sha:
                raise ValueError('Restored cache readback mismatch')
            restored += 1
        stored = registry.read(private_path(regional.ROOT, result['report']))
        if stored != {k: v for k, v in result.items() if k not in ('report', 'reportSha256')}:
            raise ValueError('Receipt differs from Neon result')
    value = {'snapshotSha256': regional.file_sha(snapshot), 'selectedSources': len(snap['selected']),
        'completedMatchingVariants': len(rows), 'restoredFiles': restored, 'alreadyPresentFiles': existing,
        'databaseWrites': 0, 'published': False,
        'qualification': 'Hash-verified private cache restoration only. Independent codec readback remains required in the regional processing audit.'}
    regional.batch.write(report, value)
    print(json.dumps(value))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('snapshot', 'recipes', 'from-root', 'report'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    restore(args.snapshot.resolve(), args.recipes.resolve(), args.from_root.resolve(), args.report.resolve())
