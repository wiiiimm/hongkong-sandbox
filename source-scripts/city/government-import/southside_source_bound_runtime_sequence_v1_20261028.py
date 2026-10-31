"""Capture all17 originals against the NEW source-bound single node in <=8 cohorts."""
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-southside-source-bound-runtime-sequence-v1-20261028'
DOC, LOCAL = BASE / BATCH, HERE / 'local' / BATCH
CAP = 'government-xl-southside-project-original-recovery-v1-20261028'
PATCH = 'government-xl-southside-source-bound-surface-contract-v1-20261028'
TOOL = HERE / 'selected_original_source_bound_runtime_v1_20261028.py'
PRIOR = []
COHORTS = [('government-xl-southside-source-bound-main-runtime-v1-20261028',
            ['landsd/311761:0', 'landsd/311762:0']),
           ('government-xl-southside-source-bound-xl-runtime-v1-20261028',
            ['landsd/311758:0', 'landsd/311759:0', 'landsd/311760:0', 'landsd/311763:0', 'landsd/330243:0']),
           ('government-xl-southside-source-bound-companion-runtime-v1-20261028',
            ['landsd/315026:0', 'landsd/315027:0', 'landsd/315028:0', 'landsd/328110:0', 'landsd/328306:0', 'landsd/328308:0', 'landsd/328309:0']),
           ('government-xl-southside-source-bound-last-runtime-v1-20261028',
            ['landsd/328310:0', 'landsd/330244:0'])]



def main():
    assert not DOC.exists() and not LOCAL.exists()
    refs = [Path(__file__), TOOL]
    expected_tool = digest(TOOL.read_bytes())
    authenticate(BASE / CAP)
    authenticate(BASE / PATCH)
    refs.extend([BASE/CAP/'result.json', BASE/PATCH/'result.json'])
    for batch in PRIOR:
        authenticate(BASE/batch)
    state = dict(completed=[], running=True, installationApproved=False)
    save(LOCAL/'state.json', state)
    for index, (batch, uids) in enumerate(COHORTS):
        assert len(uids) + 1 <= 8 and not (BASE/batch).exists() and not (HERE/'local'/batch).exists()
        assert digest(TOOL.read_bytes()) == expected_tool
        command = [sys.executable, str(TOOL), '--batch', batch, '--patch', PATCH, '--capture', CAP]
        for uid in uids:
            command.extend(['--extra-uid', uid])
        state['phase'] = batch
        save(LOCAL/'state.json', state)
        logpath = LOCAL/('phase-' + str(index) + '.log')
        with logpath.open('w') as log:
            proc = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        assert proc.returncode == 0, 'Child failed; preserve evidence, do not infer installation eligibility'
        assert digest(TOOL.read_bytes()) == expected_tool
        receipt, _ = authenticate(BASE/batch)
        assert all(r['status'] == 'captured' for r in receipt['rows'])
        state['completed'].append(dict(batch=batch, jobId=receipt['jobId']))
        save(LOCAL/'state.json', state)
        refs.extend([logpath, BASE/batch/'result.json'])
        print(dict(completed=batch, models=len(receipt['rows'])), flush=True)
    captured = {}
    for batch in PRIOR + [name for name, _ in COHORTS]:
        receipt, pins = authenticate(BASE/batch)
        assert all(r['status'] == 'captured' for r in receipt['rows'])
        path = BASE/batch/'selection.json.gz'
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        for row in read(path)['rows']:
            assert row['uid'] not in captured or captured[row['uid']] == row['sourceSHA256']
            captured[row['uid']] = row['sourceSHA256']
        refs.extend([BASE/batch/'result.json', path])
    original = read(BASE/CAP/'selection.json.gz')
    assert captured == {r['uid']: r['sourceSHA256'] for r in original['rows']} and len(captured) == 17
    state['running'] = False
    save(LOCAL/'state.json', state)
    result = dict(uids=sorted(captured), capturedOriginals=17, actualRendererCohorts=PRIOR + [n for n, _ in COHORTS],
                  originalSourceSHA256ByUid=captured, installationApproved=False, identityAccepted=False,
                  physicalAccepted=False, sourceGeometryChanges=0,
                  qualification='All17 recovered exact originals captured against the same NEW source-bound single-node terrain in cohorts of at most8; the existing cohort guard was not raised. Duplicate podium captures bind the same exact source hash. Foundation/identity/support negatives remain independent; no installation or physical/identity approval.')
    save(DOC/'summary.json', result)
    refs.extend([BASE/CAP/'selection.json.gz', LOCAL/'state.json'])
    module('southside_remaining_runtime_sequence_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'complete-17-originals-actual-renderer-capture-cohorts', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
