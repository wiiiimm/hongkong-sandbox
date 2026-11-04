"""Automatically follow basic-neighbour-only root holds through complete acceptance.

Scope is the two explicitly frozen XL source cohorts. No other sources, geometry
edits, changed limits or model AI calls. Every attempt is fresh and publication is
serial after the active source and Hoi Wing sequences.
"""
import json
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect

BATCH = 'government-xl-basic-parent-complete-handoff-sequence-20261006'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
AFTER = ROOT / 'docs/astra-city/government-import/government-xl-retained-compatibility-sequence-20261006/commands.json'
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
        source = read(path)
        assert source['activeWorkers'] == 0 and source['queuedFollowups'] == 0
        frozen.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path.read_bytes())})
        for row in source['rows']:
            result = row['steps'][0]['result']
            reasons = result.get('reasons', []) if result else []
            if row['installed'] or not reasons or not all(r.startswith('terrain-regresses-neighbour:') for r in reasons):
                continue
            previous = ROOT / 'docs/astra-city/government-import' / result['batch']
            assert read(previous / 'neon-sync.json') == {'jobId': result['jobId'], 'resultVerified': True}
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
            for ref in result['evidenceRefs']:
                assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
            candidate = read(previous / 'terrain-candidates.json')[0]
            if candidate.get('replaces'):
                skipped.append({'uid': row['uid'], 'reason': 'retained-patch-needs-dedicated-preservation', 'previousJobId': result['jobId']})
                continue
            if current_installed(row['uid'], row['sourceSHA256']):
                continue
            # Hoi Wing has its own complete fresh successor directly before us.
            if row['uid'] == 'landsd/313032:0':
                skipped.append({'uid': row['uid'], 'reason': 'dedicated-preceding-Hoi-Wing-follow-up', 'previousJobId': result['jobId']})
                continue
            selected.append({k: row[k] for k in ['uid', 'name', 'sourceSHA256', 'base']} | {
                'policy': policy, 'previous': str(previous.relative_to(ROOT)), 'previousJobId': result['jobId']})
    scripts = ['xl-owned-installation-recheck.py', 'xl-cell-installation-recheck.py',
               'xl-owned-installation-parent-followthrough.py', 'xl-cell-parent-terrain-followthrough.py',
               'xl-explicit-root-install.py', 'xl-explicit-cell-root-install.py']
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
        status, result, source = phase('current', 'xl-' + policy + '-installation-recheck.py',
                                     ['--previous', row['previous'], '--base', row['base']])
        if status == 0 and result and result['reasons'] and all(r.startswith('terrain-regresses-neighbour:') for r in result['reasons']):
            parent = 'xl-cell-parent-terrain-followthrough.py' if policy == 'cell' else 'xl-owned-installation-parent-followthrough.py'
            current = source
            status, result, source = phase('outside-parent', parent, ['--previous', current, '--mask', 'outside-source'])
            if status == 0 and result and result['reasons'] and all(r.startswith('terrain-regresses-neighbour:') for r in result['reasons']):
                status, result, source = phase('complete-parent', parent, ['--previous', current, '--mask', 'complete-basic-footprint'])
        if status == 0 and result and result['scriptChecksPassed']:
            # Parent preservation is physical evidence; installers additionally need fresh
            # routing/source identity and pinned predecessor handoff files.
            if not (ROOT/source/'recheck-inputs.json').exists() or not (ROOT/source/'indexed-preflight.json').exists():
                status, result, source = phase('complete-handoff', 'xl-' + policy + '-installation-recheck.py',
                                              ['--previous', source, '--base', row['base']])
        if status == 0 and result and result['scriptChecksPassed']:
            installer = 'xl-explicit-cell-root-install.py' if policy == 'cell' else 'xl-explicit-root-install.py'
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
         'qualification': 'Fresh full scripted/browser/installed acceptance for the explicit two XL cohorts; no original source edits, invented elevations or changed limits. Goal continues beyond this sequence.'})


if __name__ == '__main__':
    main()
