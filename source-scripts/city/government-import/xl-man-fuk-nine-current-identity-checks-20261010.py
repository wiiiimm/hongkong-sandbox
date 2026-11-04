"""Run and persist ordinary full-source identity checks for all nine originals."""
import importlib.util
import subprocess
import sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect

BATCH = 'government-xl-man-fuk-nine-current-identity-checks-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
RECOVERY = DOC.parent / 'government-xl-man-fuk-nine-overlapping-originals-recovery-20261010'


def main():
    assert not DOC.exists(), 'Fresh immutable identity sequence required'
    receipt = read(RECOVERY / 'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    for ref in receipt['evidenceRefs']:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    selected = read(RECOVERY / 'selection.json.gz'); assert not selected['missing'] and len(selected['rows']) == 9
    for row in selected['rows']:
        row['triangles'] = row['native']['model']['triangles']
    input_path = DOC / 'input-selection.json.gz'; save(input_path, selected)
    paths = [Path(__file__), RECOVERY / 'selection.json.gz', RECOVERY / 'result.json', input_path,
        HERE / 'xl-current-original-identity-diagnostic-20261010.py']
    results = []
    for row in selected['rows']:
        uid = row['uid']; batch = 'government-xl-man-fuk-nine-current-identity-' + uid.split('/')[1].replace(':', '-') + '-20261010'
        child = DOC.parent / batch
        subprocess.run([sys.executable, str(HERE / 'xl-current-original-identity-diagnostic-20261010.py'),
            '--uid', uid, '--input', str(input_path.relative_to(ROOT)), '--batch', batch], cwd=ROOT, check=True)
        result = read(child / 'result.json')
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
        results.append(dict(uid=uid, name=row['source']['building'].get('name'),
            rawIdentityPassed=result['rawIdentityPassed'], rawIdentityReasons=result['rawIdentityReasons'],
            resultJobId=result['jobId'], nextStep=result['nextStep'], installationApproved=False))
        paths.extend(p for p in child.rglob('*') if p.is_file())
        save(DOC / 'partial-results.json', dict(rows=results, sourceGeometryChanges=0, installationApproved=False))
    save(DOC / 'diagnostic.json', dict(rows=results, sourceGeometryChanges=0, installationApproved=False))
    spec = importlib.util.spec_from_file_location('man_fuk_nine_identity_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    freeze = importlib.util.module_from_spec(spec); spec.loader.exec_module(freeze)
    freeze.freeze(BATCH, 'nine-current-full-source-identity-diagnoses-v1', paths,
        dict(uids=[r['uid'] for r in results], rawIdentityPassedUids=[r['uid'] for r in results if r['rawIdentityPassed']],
            rawIdentityHeldUids=[r['uid'] for r in results if not r['rawIdentityPassed']],
            sourceGeometryChanges=0, scriptFullAcceptancePassed=False,
            nextStep='Advance source identity passes through complete original assembly/root/terrain/native/basic/runtime/browser checks; preserve every failed raw identity for targeted review.'))


if __name__ == '__main__': main()
