"""Unexecuted exact source+current-role+private-stage closure declaration.

Only completed current qualification and private-browser artifacts are added.
Every numerical/source dependency remains recursive. The sealed source metadata
boundaries and historical aliases are inherited unchanged; root independently
verifies and seals the declaration. This script performs no live or Git changes.
"""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
BASE = ROOT / 'docs/astra-city/government-import'
SOURCE = BASE / 'xl-terrain-recovery-20261011-twin-regency-completed-source-checkpoint-scope-v2/declared-scope.json'
CERT = BASE / 'government-xl-twin-regency-completed-source-root-closure-v2-20261011/root-closed-scope.json'
ROLE = BASE / 'xl-terrain-recovery-20261011-twin-regency-pair-complete-current-role-v1'
STAGED = 'government-xl-terrain-recovery-twin-regency-two-private-stage-v1-20261011'
DOC = BASE / 'government-xl-twin-regency-source-stage-declared-scope-v1-20261011'
UIDS = {'landsd/222465:0', 'landsd/223206:0'}

def ref(path): return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

def main():
    assert not DOC.exists()
    source = read(SOURCE); cert = read(CERT)
    assert cert['independentlyVerified'] is True and cert['sourceOnly'] is True and cert['newlyInstalled'] == 0
    assert cert['currentManifestSHA256'] == 'df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
    receipt = read(ROLE / 'result.json')
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone() == ('complete', receipt)
    assert receipt['newlyInstalled'] == 0 and ref(ROLE / 'typed-role.json.gz') in receipt['evidenceRefs']
    for pin in receipt['evidenceRefs']: assert ref(ROOT / pin['path']) == pin
    role = read(ROLE / 'typed-role.json.gz')
    assert role['scriptChecksPassed'] is True and role['currentTypedPhysicalAccepted'] is True and role['reasons'] == []
    assert role['installationApproved'] is False and role['newlyInstalled'] == 0 and role['nativeReacceptance'] is False
    acceptance = read(BASE / STAGED / 'acceptance.json'); report = read(BASE / STAGED / 'staged-browser.json')
    assert acceptance['passed'] is True and acceptance['publication'] is False and acceptance['newlyInstalled'] == 0 and set(acceptance['uids']) == UIDS
    assert report['passed'] is True and report['errors'] == [] and len(report['views']) == 10
    normal = [v for v in report['views'] if 'time' in v]
    assert len(normal) == 8 and {(v['uid'], v['width'], v['time']) for v in normal} == {(u, w, t) for u in UIDS for w in (1280, 390) for t in ('15:00', '22:00')}
    failures = [v for v in report['views'] if v.get('phase') == 'failed-download']
    assert len(failures) == 2 and {v['uid'] for v in failures} == UIDS and all(v['fallbackRetained'] is True and v['width'] == 390 for v in failures)
    paths = set(cert['paths']) | set(source['closedExplicitPaths']) | {str(SOURCE.relative_to(ROOT)), str(CERT.relative_to(ROOT)), str(Path(__file__).relative_to(ROOT))}
    paths.update(pin['path'] for pin in receipt['evidenceRefs'])
    for folder in [ROLE, BASE / STAGED, HERE / 'accepted' / STAGED,
        HERE / 'local' / ROLE.name, HERE / 'local' / STAGED,
        BASE / 'xl-terrain-recovery-20261011-twin-regency1120-composition-validation-v1',
        ROOT / 'docs/astra-city/model-integration-20260909' / STAGED]:
        assert folder.exists()
        paths.update(str(path.relative_to(ROOT)) for path in folder.rglob('*') if path.is_file())
    for name in ['xl-terrain-recovery-20261011-twin-regency-pair-complete-current-role-v1.py',
        'xl-terrain-recovery-20261011-twin-regency-two-private-stage-v1.py',
        'twin_regency1120_complete_original_role_composition_v1_20261011.py',
        'twin_regency1120_complete_actual_fixture_v1_20261011.py',
        'test_twin_regency1120_complete_original_role_composition_v1_20261011.py']:
        paths.add(str((HERE / name).relative_to(ROOT)))
    declaration = str((DOC / 'declared-scope.json').relative_to(ROOT)); paths.add(declaration)
    output = dict(closedPaths=sorted(paths), closedExplicitPaths=sorted(paths),
        presentFileBindings=[ref(ROOT / path) for path in sorted(paths) if path != declaration],
        metadataLeafPaths=source['metadataLeafPaths'], metadataLeafJsonPointers=source['metadataLeafJsonPointers'],
        historicalManifestAliases=source['historicalManifestAliases'],
        inheritedMetadataScope=source['inheritedMetadataScope'], sourceDeclaration=ref(SOURCE),
        independentlyVerifiedSourceCertificate=ref(CERT), completedCurrentRoleReceipt=ref(ROLE / 'result.json'),
        stageAcceptance=ref(BASE / STAGED / 'acceptance.json'), stageBrowser=ref(BASE / STAGED / 'staged-browser.json'),
        fullNumericalSourceClosureRequired=True, newMetadataLeaves=False, newMetadataPointerContract=False,
        sourceGeometryChanges=0, nativeReacceptance=False, publication=False, newlyInstalled=0,
        independentlyVerified=False, rootRecursiveVerificationRequired=True, livePublicationRequired=True)
    assert output['metadataLeafPaths'] == cert['metadataLeafPaths'] and output['metadataLeafJsonPointers'] == cert['metadataLeafJsonPointers']
    assert output['historicalManifestAliases'] == cert['historicalManifestAliases']
    save(DOC / 'declared-scope.json', output)
    print(dict(paths=len(paths), publication=False, newNumericLeaves=False), flush=True)

if __name__ == '__main__': main()
