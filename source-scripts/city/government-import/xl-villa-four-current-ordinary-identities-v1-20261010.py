"""Verify four complete unchanged originals against the current map.

Independent source diagnostics preserve every provider/cell/foreign guard.
This bundle is an identity handoff only; no terrain or installation credit.
"""
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest

IDS = [58497, 63823, 121309, 148052]
BATCH = 'government-xl-villa-four-current-ordinary-identities-v1-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
MANIFEST = '44c9e80ec3999285616bb12a3fdfbe142a15855db7aa7c3216bffab3500f991a'


def one(identifier):
    uid = f'landsd/{identifier}:0'
    prior = DOC.parent / 'government-xl-villa-premiere-four-tower-original-recovery-20261010'
    current = DOC.parent / f'government-xl-villa-four-current-identity-{identifier}-v1-20261010'
    assert not current.exists(), 'Preserve earlier attempts'
    old_row = next(row for row in read(prior / 'selection.json.gz')['rows'] if row['uid'] == uid)
    assert old_row['uid'] == uid
    command = [sys.executable, str(HERE / 'xl-current-original-identity-diagnostic-20261010.py'),
               '--uid', uid, '--input', str((prior / 'selection.json.gz').relative_to(ROOT)),
               '--batch', current.name]
    process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = dict(uid=uid, command=command, exitCode=process.returncode,
                  stdout=process.stdout, stderr=process.stderr, diagnosticDirectory=str(current.relative_to(ROOT)))
    save(DOC / f'{identifier}-process.json', output)
    assert process.returncode == 0, output
    result = read(current / 'result.json')
    proof = read(current / 'identity.json')
    row = read(current / 'selection.json.gz')['rows'][0]
    assert result['manifestSHA256'] == MANIFEST
    assert row['uid'] == uid and row['sourceSHA256'] == old_row['sourceSHA256']
    assert row['candidate'] == old_row['candidate'] and row['triangles'] == old_row['triangles']
    assert row['native'] == old_row['native']
    assert proof['exactRouteManifestSHA256'] == MANIFEST
    assert proof['sourceSHA256'] == row['sourceSHA256']
    return dict(uid=uid, sourceSHA256=row['sourceSHA256'], completeOriginalFaces=row['triangles'],
                passed=proof['passed'], reasons=proof['reasons'], jobId=result['jobId'],
                selectionPath=str((current / 'selection.json.gz').relative_to(ROOT)),
                contextPath=str((current / 'context.json.gz').relative_to(ROOT)),
                identityPath=str((current / 'identity.json').relative_to(ROOT)),
                independentCompletePhysicalRequired=True)


def main():
    assert not DOC.exists()
    before = (ROOT / '3d-viewer/city/data/manifest.json').read_bytes()
    assert digest(before) == MANIFEST
    outcomes = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(one, identifier): identifier for identifier in IDS}
        for future in concurrent.futures.as_completed(futures):
            try:
                outcome = future.result()
                outcomes.append(outcome)
                print(json.dumps(outcome), flush=True)
            except Exception as error:
                failure = dict(identifier=futures[future], error=str(error))
                failures.append(failure)
                print(json.dumps(failure), flush=True)
    assert (ROOT / '3d-viewer/city/data/manifest.json').read_bytes() == before
    outcomes.sort(key=lambda row: int(row['uid'].split('/')[1].split(':')[0]))
    save(DOC / 'identities-summary.json', dict(manifestSHA256=MANIFEST, rows=outcomes, orchestrationFailures=failures,
         physicalAccepted=False, installationApproved=False, modelGeometryChanges=0))
    assert not failures and len(outcomes) == 4, failures
    refs = [Path(__file__), HERE / 'xl-current-original-identity-diagnostic-20261010.py']
    for identifier in IDS:
        current = DOC.parent / f'government-xl-villa-four-current-identity-{identifier}-v1-20261010'
        refs += [p for p in current.rglob('*') if p.is_file()]
    import importlib.util
    spec = importlib.util.spec_from_file_location('villa_four_identity_fence', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    fence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fence)
    result = fence.freeze(BATCH, 'fresh-four-ordinary-original-identities-v1', refs,
        dict(uids=[row['uid'] for row in outcomes], manifestSHA256=MANIFEST,
             ordinaryIdentitiesPassed=sum(row['passed'] for row in outcomes), completeOriginalFaces=sum(row['completeOriginalFaces'] for row in outcomes),
             allFourOrdinaryIdentityPassed=all(row['passed'] and row['reasons'] == [] for row in outcomes),
             currentIdentityDiagnosticOnly=True, physicalAccepted=False, installationApproved=False,
             currentHeldReason='independent-complete-coupled-physical-checks-required',
             nextStep='Check complete original podium/tower attachment and independently prove every source/current foreign/support/terrain/runtime gate before staging.',
             qualification='Fresh four-source ordinary identity handoff only. Full original/provider/cell/95% coverage/10m extent/foreign gates retained. No geometry edits, actor exceptions or installed credit.'))
    print(json.dumps(dict(jobId=result['jobId'], rows=len(outcomes), allPassed=all(row['passed'] for row in outcomes))), flush=True)


if __name__ == '__main__':
    main()
