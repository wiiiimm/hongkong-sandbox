"""Continue the active XL goal with exact cached sources outside the recent cohorts."""
import json
import subprocess
import sys
import time
from pathlib import Path
from run import ROOT, HERE, read, save, digest

BATCH = 'government-xl-uncovered-source-sequence-20261006'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
AFTER = ROOT / 'docs/astra-city/government-import/government-xl-basic-parent-install-sequence-20261006/commands.json'
AUDIT = ROOT / 'docs/astra-city/government-import/government-xl-uncovered-source-audit-20261006'
BASE_NAME = 'government-xl-uncovered-57-inputs-20261006'
DIAG_NAME = 'government-xl-uncovered-57-cell-identity-20261006'
INPUT_NAME = 'government-xl-uncovered-qualified-inputs-20261006'


def main():
    assert not (DOC / 'commands.json').exists(), 'Fresh explicit sequence only'
    LOCAL.mkdir(parents=True, exist_ok=True)
    while not AFTER.exists():
        time.sleep(10)
    prior = read(AFTER)
    assert prior['activeWorkers'] == 0 and prior['queuedFollowups'] == 0
    uidfile = AUDIT / 'explicit-ready-uids.json'
    ready = read(uidfile)
    assert ready['sourceAuditSHA256'] == digest((AUDIT / 'cached-sources.json').read_bytes())
    assert len(ready['uids']) == 57
    phases = []

    def phase(name, command):
        log = LOCAL / (name + '.log')
        with log.open('w') as output:
            status = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT).returncode
        phases.append({'name': name, 'command': command, 'returncode': status, 'log': str(log.relative_to(ROOT))})
        save(DOC / 'working-commands.json', {'phases': phases, 'activeWorkers': int(status == 0),
             'scriptExternalAICalls': 0, 'publication': False})
        assert status == 0, 'Failed explicit phase retained in ' + str(log)

    base = ROOT / 'docs/astra-city/government-import' / BASE_NAME
    phase('freeze', [sys.executable, str(HERE / 'xl-freeze-explicit-sources.py'), '--uids-file', str(uidfile.relative_to(ROOT)), '--batch', BASE_NAME])
    phase('identity', [sys.executable, str(HERE / 'xl-explicit-cell-identity-diagnostic.py'), '--base', str(base.relative_to(ROOT)), '--batch', DIAG_NAME])
    diagnostic = ROOT / 'docs/astra-city/government-import' / DIAG_NAME / 'result.json'
    result = read(diagnostic)
    allowed = {r['uid'] for r in result['rows'] if r['passed']}
    assert allowed <= set(ready['uids']) and result['newlyInstalled'] == 0 and not result['publication']
    selected = read(base / 'check-selection.json.gz')['rows']
    rows = [{'uid': r['uid'], 'name': r['name'], 'sourceSHA256': r['sourceSHA256'],
             'base': str(base.relative_to(ROOT)),
             'baseMismatchM': abs(r['native']['model']['worldBounds'][0][1] - r['source']['building']['base'])}
            for r in selected if r['uid'] in allowed]
    rows.sort(key=lambda r: (r['baseMismatchM'], r['uid']))
    scripts = ['xl-cell-source-sequence.py', 'xl-cell-indexed-terrain-continuation.py',
               'xl-cell-contact-resolution.py', 'xl-cell-retained-terrain-followthrough.py',
               'xl-explicit-cell-root-install.py', 'xl-explicit-cell-retained-install.py',
               'government_georef_cell_identity.py', 'original_source_ownership.py',
               'test_government_georef_cell_identity.py', 'test_government_owned_identity.py']
    paths = [diagnostic, base / 'check-selection.json.gz', base / 'context.json.gz'] + [HERE / n for n in scripts]
    inputs = ROOT / 'docs/astra-city/government-import' / INPUT_NAME / 'inputs.json'
    save(inputs, {'rows': rows, 'evidenceRefs': [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())} for p in paths],
         'scriptExternalAICalls': 0, 'modelGeometryChanges': 0, 'publication': False,
         'qualification': 'Explicit cached original XL sources from active goal scope only. Positive identity is not installation credit. All current physical/runtime/browser/publication checks required.'})
    print(json.dumps({'sourcesFrozen': 57, 'positiveIdentityPassed': len(rows), 'newlyInstalled': 0}), flush=True)
    if rows:
        phase('full-acceptance', [sys.executable, str(HERE / 'xl-cell-source-sequence.py'), '--inputs', str(inputs.relative_to(ROOT)),
                               '--batch', 'government-xl-uncovered-qualified-sequence-20261006', '--after', str(AFTER.relative_to(ROOT))])
    save(DOC / 'commands.json', {'batch': BATCH, 'rows': phases, 'activeWorkers': 0, 'queuedFollowups': 0,
         'sourcesFrozen': 57, 'positiveIdentityPassed': len(rows), 'scriptExternalAICalls': 0, 'modelGeometryChanges': 0,
         'qualification': 'Actual installed source credit belongs only to verified full-acceptance result successors. The broader100-new-XL goal continues.'})


if __name__ == '__main__':
    main()
