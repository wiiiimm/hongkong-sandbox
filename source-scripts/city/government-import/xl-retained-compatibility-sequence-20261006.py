"""Fresh full compatibility and installation attempts for exact retained XL holds.

Only completed explicit active-goal cohorts. Current review/source and fenced
previous evidence must agree. Preserve complete old terrain including overlap,
then require full source/foundation/basic/native/runtime/browser acceptance.
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect

BATCH = 'government-xl-retained-compatibility-sequence-20261006'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
AFTER = ROOT / 'docs/astra-city/government-import/government-xl-uncovered-source-sequence-20261006/commands.json'
COHORTS = [('government-xl-owned-57-sequence-20261006', 'owned'),
           ('government-xl-full-cell-34-sequence-20261006', 'cell'),
           ('government-xl-uncovered-qualified-sequence-20261006', 'cell')]


def current_installed(uid, sha):
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    models = [m for url in manifest['officialModelCatalogues']
              for m in read(ROOT / '3d-viewer' / url)['models'] if m['uid'] == uid]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        review = con.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], uid)).fetchone()
    if not models:
        return False
    assert len(models) == 1 and models[0]['sha256'] == sha
    assert review == ('installed-verified', sha), 'Runtime and current installed review disagree'
    return True


def main():
    assert not (DOC / 'commands.json').exists(), 'Fresh explicit sequence only'
    LOCAL.mkdir(parents=True, exist_ok=True)
    while not AFTER.exists():
        time.sleep(10)
    preceding = read(AFTER)
    assert preceding['activeWorkers'] == 0 and preceding['queuedFollowups'] == 0
    selected = []
    skipped = []
    frozen = []
    for cohort, policy in COHORTS:
        path = ROOT / 'docs/astra-city/government-import' / cohort / 'commands.json'
        if not path.exists() and cohort == 'government-xl-uncovered-qualified-sequence-20261006':
            assert preceding['positiveIdentityPassed'] == 0, 'Expected qualified source sequence is missing'
            continue
        source = read(path)
        assert source['activeWorkers'] == 0 and source['queuedFollowups'] == 0
        frozen.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        for row in source['rows']:
            result = row['steps'][0]['result']
            reasons = result.get('reasons', []) if result else []
            if row['installed'] or not reasons or not all(r.startswith(('terrain-regresses-neighbour:', 'terrain-construction-guard:')) for r in reasons):
                continue
            previous = ROOT / 'docs/astra-city/government-import' / result['batch']
            assert read(previous / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
            for ref in result['evidenceRefs']:
                assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
            base = ROOT / row['base']
            selected_row = next(r for r in read(base / 'check-selection.json.gz')['rows'] if r['uid'] == row['uid'])
            assert selected_row['sourceSHA256'] == row['sourceSHA256']
            import importlib.util
            spec = importlib.util.spec_from_file_location('retained_current_route', HERE / 'xl-cell-source-sequence.py')
            route = importlib.util.module_from_spec(spec); spec.loader.exec_module(route)
            retained = route.retained_route(selected_row)
            if not retained:
                skipped.append({'uid': row['uid'], 'reason': 'not-one-current-simple-native-patch', 'previousJobId': result['jobId']})
                continue
            if current_installed(row['uid'], row['sourceSHA256']):
                continue
            # Hoi Wing has its own complete fresh successor directly before us.
            if row['uid'] == 'landsd/313032:0':
                skipped.append({'uid': row['uid'], 'reason': 'dedicated-preceding-Hoi-Wing-follow-up', 'previousJobId': result['jobId']})
                continue
            selected.append({k: row[k] for k in ['uid', 'name', 'sourceSHA256', 'base']} | {
                'policy': policy, 'previous': str(previous.relative_to(ROOT)), 'previousJobId': result['jobId'], 'retained': retained})
    scripts = ['xl-owned-retained-overlap-followthrough.py', 'xl-owned-retained-overlap-contact.py',
               'xl-cell-retained-overlap-followthrough.py', 'xl-cell-retained-overlap-contact.py',
               'xl-explicit-owned-retained-install.py', 'xl-explicit-cell-assembly-install.py', 'resolution-assembly-browser.mjs',
               'xl-cell-source-sequence.py', 'xl-owned-indexed-terrain-continuation.py',
               'xl-cell-indexed-terrain-continuation.py', 'xl-retained-compatibility-sequence-20261006.py']
    frozen += [{'path': str((HERE / name).relative_to(ROOT)), 'sha256': digest((HERE / name).read_bytes())}
               for name in scripts]
    save(DOC / 'routing.json', {'rows': selected, 'skipped': skipped, 'evidenceRefs': frozen,
                               'scriptExternalAICalls': 0, 'publication': False})
    outcomes = []
    for i, row in enumerate(selected, 1):
        for ref in frozen:
            assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
        token = row['uid'].split('/')[1].replace(':', '-')
        outcome = {**row, 'steps': [], 'installed': False}
        save(DOC / 'working-commands.json', {'finished': outcomes, 'running': outcome, 'queued': len(selected) - i})
        print(json.dumps({'starting': row['uid'], 'position': i, 'total': len(selected)}), flush=True)

        def phase(label, script, arguments):
            batch = BATCH + '-' + token + '-' + label
            command = [sys.executable, str(HERE / script), '--batch', batch, *arguments]
            log = LOCAL / (token + '-' + label + '.log')
            with log.open('w') as output:
                status = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT).returncode
            path = ROOT / 'docs/astra-city/government-import' / batch
            result = read(path / 'result.json') if (path / 'result.json').exists() else None
            outcome['steps'].append({'command': command, 'returncode': status, 'result': result, 'log': str(log.relative_to(ROOT))})
            return status, result, str(path.relative_to(ROOT))

        policy = row['policy']
        if current_installed(row['uid'], row['sourceSHA256']):
            outcome['nextStep'] = 'Already verified installed with exact current review/source; no repeat computation.'
            outcomes.append(outcome)
            continue
        status, result, source = phase('complete-retained', 'xl-' + policy + '-retained-overlap-followthrough.py',
             ['--uid', row['uid'], '--base', row['base'], '--retained', row['retained'], '--allow-basic-targets'])
        if status == 0 and result and result['scriptChecksPassed']:
            installer = 'xl-explicit-cell-assembly-install.py' if policy == 'cell' else 'xl-explicit-owned-retained-install.py'
            status, result, source = phase('installed', installer, ['--uid', row['uid'], '--source', source, '--base', row['base']])
            outcome['installed'] = bool(status == 0 and result and result.get('installedUids') == [row['uid']])
            if outcome['installed']:
                save(DOC / ('commit-required-' + token + '.json'), {'uid': row['uid'], 'installation': Path(source).name})
        outcomes.append(outcome)
        save(DOC / 'working-commands.json', {'finished': outcomes, 'running': None, 'queued': len(selected) - i})
        print(json.dumps({'finished': row['uid'], 'installed': outcome['installed'], 'reasons': result.get('reasons') if result else ['command-failure-see-log']}), flush=True)
    save(DOC / 'commands.json', {'batch': BATCH, 'rows': outcomes, 'skipped': skipped,
         'newlyInstalled': sum(r['installed'] for r in outcomes), 'activeWorkers': 0, 'queuedFollowups': 0,
         'scriptExternalAICalls': 0, 'modelGeometryChanges': 0,
         'qualification': 'Fresh full scripted/browser/installed acceptance for the explicit completed XL goal cohorts; no original source edits, invented elevations or changed limits. Goal continues beyond this sequence.'})


if __name__ == '__main__':
    main()
