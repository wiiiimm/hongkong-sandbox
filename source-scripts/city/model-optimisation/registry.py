"""Revision-bound optimisation plans; never processes models or publishes assets."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
from db import CONFIG, connect
from jobs import encode
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

STAGE = 'model-optimisation-v1'
TIERS = ('original', 'high', 'balanced', 'lightweight')
GATES = ('sourceIdentity', 'geometry', 'placement', 'visual', 'collision', 'devicePerformance')


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def sha(value):
    if not isinstance(value, str) or not re.fullmatch('[a-f0-9]{64}', value):
        raise ValueError('Expected lowercase SHA-256')
    return value


def read(path):
    return json.loads(Path(path).read_text())


def validate_recipe(recipe):
    if recipe.get('schemaVersion') != 1 or recipe.get('tier') not in TIERS:
        raise ValueError('Invalid recipe version or tier')
    if recipe.get('status') not in ('draft', 'ready'):
        raise ValueError('Recipe status must be draft or ready')
    if not isinstance(recipe.get('lossy'), bool):
        raise ValueError('Explicit lossy flag required')
    if recipe.get('status') == 'ready':
        if any(not isinstance(recipe.get(key), dict) or not recipe[key]
               for key in ('tools', 'parameters', 'acceptance')):
            raise ValueError('Ready recipes require pinned tools, parameters and acceptance criteria')
        for version in recipe['tools'].values():
            if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][\w.-]+)?', version):
                raise ValueError('Pin exact tool versions')
    if recipe.get('tier') == 'original' and recipe.get('lossy') is not False:
        raise ValueError('Original tier must explicitly be lossless')
    return recipe


def source_record(catalogue, uid):
    path = Path(catalogue).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Catalogue must be in this repository')
    cat = read(path)
    if (cat.get('schemaVersion') != 1 or cat.get('kind') not in ('official-model-catalogue', 'staged-official-model-catalogue')
            or cat.get('crs') != 'EPSG:2326' or cat.get('verticalDatum') != 'Hong Kong Principal Datum'
            or cat.get('rootTranslation') != [-834500, 0, 816500]):
        raise ValueError('Expected current official source catalogue with fixed 1x coordinates')
    entries = [entry for entry in cat['models'] if entry['uid'] == uid]
    if len(entries) != 1:
        raise ValueError('Select exactly one existing source UID')
    entry = entries[0]
    asset = (path.parent / entry['asset']).resolve()
    if not asset.is_relative_to(ROOT) or not asset.is_file():
        raise ValueError('Source asset must exist inside repository')
    expected = sha(entry['sha256'])
    if hashlib.sha256(asset.read_bytes()).hexdigest() != expected:
        raise ValueError('Source asset hash mismatch')
    # Placement, assembly, source metadata and bytes all participate in identity.
    source = {'entry': entry, 'catalogue': str(path.relative_to(ROOT)),
              'rootTranslation': cat['rootTranslation'], 'crs': cat['crs'],
              'verticalDatum': cat['verticalDatum'], 'coordinatePolicy': cat.get('coordinatePolicy'),
              'datasetId': cat.get('datasetId')}
    return {'revisionId': digest(source), 'uid': uid, 'sourceSha256': expected,
            'sourceCommit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'source': source}


def migrate():
    with connect() as con:
        if '-pooler.' in con.info.host:
            raise ValueError('Use the pinned direct connection for migrations')
        con.execute("SET LOCAL lock_timeout='5s'")
        con.execute("SET LOCAL statement_timeout='30s'")
        con.execute('SELECT pg_advisory_xact_lock(217004)')
        # Prerequisite must already exist; never bootstrap or migrate unrelated work.
        if not con.execute("SELECT to_regclass('astra_modelling.jobs')").fetchone()[0]:
            raise ValueError('Shared modelling schema must already be installed')
        con.execute((HERE / 'schema.sql').read_text())
    return {'branchId': CONFIG['branch_id'], 'schema': CONFIG['schema'], 'migration': 'optimisation-v1'}


def plan(source, recipe, actor):
    validate_recipe(recipe)
    if (sha(source['revisionId']) != digest(source['source'])
            or source['uid'] != source['source']['entry']['uid']
            or sha(source['sourceSha256']) != source['source']['entry']['sha256']):
        raise ValueError('Source revision identity mismatch')
    if not actor.strip():
        raise ValueError('Planner identity required')
    recipe_hash = digest(recipe)
    variant = digest([source['revisionId'], recipe_hash])
    with connect() as con:
        con.execute('''INSERT INTO astra_modelling.optimisation_sources
            (revision_id,uid,source_sha256,source_commit,source) VALUES(%s,%s,%s,%s,%s)
            ON CONFLICT(revision_id) DO NOTHING''',
            (source['revisionId'], source['uid'], source['sourceSha256'], source['sourceCommit'], Jsonb(source['source'])))
        con.execute('''INSERT INTO astra_modelling.optimisation_variants
            (variant_id,revision_id,recipe_sha256,tier,recipe,planned_by) VALUES(%s,%s,%s,%s,%s,%s)
            ON CONFLICT(variant_id) DO NOTHING''',
            (variant, source['revisionId'], recipe_hash, recipe['tier'], Jsonb(recipe), actor))
    return {'variantId': variant, 'revisionId': source['revisionId'], 'recipeSha256': recipe_hash}


def queue(variant, batch):
    if not batch.strip():
        raise ValueError('Explicit batch required')
    with connect() as con:
        con.row_factory = dict_row
        row = con.execute('SELECT * FROM astra_modelling.optimisation_variants WHERE variant_id=%s FOR UPDATE',
                          (sha(variant),)).fetchone()
        if not row:
            raise ValueError('Unknown variant')
        if row['job_id']:
            return {'jobId': row['job_id'], 'alreadyQueued': True}
        recipe = validate_recipe(row['recipe'])
        if recipe['status'] != 'ready':
            raise ValueError('Draft recipes cannot be queued')
        payload = {'variantId': variant, 'revisionId': row['revision_id'],
                   'recipeSha256': row['recipe_sha256'], 'recipe': recipe}
        job_id = digest([batch, STAGE, payload])
        con.execute('''INSERT INTO astra_modelling.jobs(id,batch,stage,payload) VALUES(%s,%s,%s,%s)
            ON CONFLICT(id) DO NOTHING''', (job_id, batch, STAGE, Jsonb(payload)))
        con.execute('UPDATE astra_modelling.optimisation_variants SET job_id=%s WHERE variant_id=%s', (job_id, variant))
    return {'jobId': job_id, 'adapterImplemented': False}


def validate_result(row, evidence):
    result = row['result'] or {}
    if row['processing_status'] != 'complete':
        raise ValueError('Processing must complete before review')
    for field, column in [('variantId', 'variant_id'), ('revisionId', 'revision_id'), ('recipeSha256', 'recipe_sha256')]:
        if result.get(field) != row[column] or evidence.get(field) != row[column]:
            raise ValueError('Result/evidence belongs to another source revision or recipe')
    artifact = result.get('artifact', {})
    if sha(artifact.get('sha256')) != sha(evidence.get('artifactSha256')):
        raise ValueError('Review must bind exact output bytes')
    if not artifact.get('path') or not result.get('metrics'):
        raise ValueError('Immutable artifact reference and measured metrics required')
    return artifact['sha256']


def review(variant, decision, actor, evidence):
    if decision not in ('approved', 'rejected') or not actor.strip():
        raise ValueError('Explicit decision and reviewer required')
    with connect() as con:
        con.row_factory = dict_row
        con.execute('SELECT variant_id FROM astra_modelling.optimisation_variants WHERE variant_id=%s FOR UPDATE', (sha(variant),))
        row = con.execute('SELECT * FROM astra_modelling.optimisation_status WHERE variant_id=%s', (variant,)).fetchone()
        if not row:
            raise ValueError('Unknown variant')
        artifact_sha = validate_result(row, evidence)
        if decision == 'approved' and any(evidence.get('gates', {}).get(gate) != 'passed' for gate in GATES):
            raise ValueError('All source, geometry, placement, visual, collision and device gates must pass')
        if not evidence.get('report') or not evidence.get('observation'):
            raise ValueError('Evidence report reference and observation required')
        sha(evidence.get('reportSha256'))
        review_id = con.execute('''INSERT INTO astra_modelling.optimisation_reviews
            (variant_id,decision,actor,artifact_sha256,evidence) VALUES(%s,%s,%s,%s,%s) RETURNING id''',
            (variant, decision, actor, artifact_sha, Jsonb(evidence))).fetchone()['id']
    return {'reviewId': review_id, 'decision': decision, 'published': False}


def report(uid=None):
    with connect() as con:
        con.row_factory = dict_row
        rows = con.execute('''SELECT * FROM astra_modelling.optimisation_status
            WHERE (%s::text IS NULL OR uid=%s) ORDER BY uid,revision_id,tier,variant_id''', (uid, uid)).fetchall()
    return {'variants': rows, 'qualification': 'All registered revisions, not current-catalogue readiness. Complete is not approved; approved is not published.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('migrate')
    plan_args = commands.add_parser('plan')
    for name in ('catalogue', 'uid', 'recipe', 'actor'):
        plan_args.add_argument('--' + name, required=True)
    plan_args.add_argument('--apply', action='store_true', help='Write plans only; no jobs or assets')
    queue_args = commands.add_parser('queue')
    for name in ('variant', 'batch'):
        queue_args.add_argument('--' + name, required=True)
    review_args = commands.add_parser('review')
    for name in ('variant', 'actor', 'evidence'):
        review_args.add_argument('--' + name, required=True)
    review_args.add_argument('--decision', choices=['approved', 'rejected'], required=True)
    commands.add_parser('report').add_argument('--uid')
    args = parser.parse_args()
    if args.command == 'migrate':
        result = migrate()
    elif args.command == 'plan':
        source = source_record(args.catalogue, args.uid)
        recipe = validate_recipe(read(args.recipe))
        result = plan(source, recipe, args.actor) if args.apply else {'dryRun': True, 'source': source, 'recipe': recipe}
    elif args.command == 'queue':
        result = queue(args.variant, args.batch)
    elif args.command == 'review':
        result = review(args.variant, args.decision, args.actor, read(args.evidence))
    else:
        result = report(args.uid)
    print(json.dumps(result, indent=2, default=str, allow_nan=False))


if __name__ == '__main__':
    main()
