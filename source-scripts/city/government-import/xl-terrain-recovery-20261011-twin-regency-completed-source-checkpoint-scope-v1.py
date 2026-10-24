"""Add completed Twin diagnostics to exact sealed Elements root proof scope.

Inherited metadata leaves/pointers/aliases are unchanged. Every new source,
terrain, module, geometry and numerical reference remains recursive. The
checkpoint grants no Twin current/source-role/root or installation acceptance.
"""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'xl-terrain-recovery-20261011-twin-regency-completed-source-checkpoint-scope-v1'
DOC = BASE / BATCH
OLD = BASE / 'government-xl-elements-installed-root-closure-v1-20261011/root-closed-scope.json'
JOBS = (
    'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v2',
    'xl-terrain-recovery-20261011-twin-regency-complete-internal-original-contact-graph-v1',
    'government-xl-terrain-recovery-twin-regency-tower2-podium-current-probe-v1-20261011',
    'xl-terrain-recovery-20261011-twin-regency-podium-complete-authentic-finite-grade-cap-v1',
    'xl-terrain-recovery-20261011-twin-regency-two-current-render-attribute-capture-v1',
    'xl-terrain-recovery-20261011-twin-regency-pair-current-inputs-v1',
    'government-xl-terrain-recovery-twin-regency-pair-authentic-current-v1-20261011',
    'government-xl-terrain-recovery-twin-regency-pair-proposed-ground-capture-v1-20261011')
IMAGE_AND_FAILURE_FOLDERS = (
    'xl-terrain-recovery-20261011-twin-regency-two-original-source-context-v1',
    'xl-terrain-recovery-20261011-twin-regency-residual-original-source-context-v1',
    'xl-terrain-recovery-20261011-twin-regency-tower2-podium-original-contact-census-v1')

def ref(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists()
    old = read(OLD); assert old['independentlyVerified'] is True
    assert old['currentManifestSHA256'] == 'df35e9ba069dc8445ca873ba1a065cffafcd00e94813a3af040219121469830e'
    paths = set(old['paths'])
    paths.update([str(OLD.relative_to(ROOT)), str(Path(__file__).relative_to(ROOT))])
    receipts = []
    for batch in JOBS:
        folder = BASE / batch; receipt = read(folder / 'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                             (receipt['jobId'],)).fetchone() == ('complete', receipt)
        assert receipt.get('newlyInstalled', 0) == 0 and not receipt.get('installationApproved', False)
        for binding in receipt['evidenceRefs']:
            p = ROOT / binding['path']; assert p.is_file() and ref(p) == binding
            paths.add(binding['path'])
        paths.update(str(p.relative_to(ROOT)) for p in folder.rglob('*') if p.is_file())
        local = HERE / 'local' / batch
        if local.exists():
            paths.update(str(p.relative_to(ROOT)) for p in local.rglob('*') if p.is_file())
        receipts.append(dict(batch=batch, receipt=ref(folder / 'result.json'), jobId=receipt['jobId']))
    for batch in IMAGE_AND_FAILURE_FOLDERS:
        folder = BASE / batch; assert folder.is_dir()
        paths.update(str(p.relative_to(ROOT)) for p in folder.rglob('*') if p.is_file())
    for filename in ['xl-terrain-recovery-20261011-twin-regency-two-original-source-context-v1.py',
                     'xl-terrain-recovery-20261011-twin-regency-residual-original-source-context-v1.py']:
        paths.add(str((HERE / filename).relative_to(ROOT)))
    archive = BASE / JOBS[2] / 'historical-current-manifest.json'
    assert ref(archive)['sha256'] == old['currentManifestSHA256']
    aliases = list(old['historicalManifestAliases'])
    alias = dict(originalPath='3d-viewer/city/data/manifest.json', sha256=ref(archive)['sha256'], archive=ref(archive))
    if alias not in aliases:
        aliases.append(alias)
    paths.add(str(archive.relative_to(ROOT)))
    declaration = str((DOC / 'declared-scope.json').relative_to(ROOT)); paths.add(declaration)
    out = dict(closedPaths=sorted(paths), closedExplicitPaths=sorted(paths),
        presentFileBindings=[ref(ROOT / p) for p in sorted(paths) if p != declaration],
        historicalManifestAliases=aliases, metadataLeafPaths=old['metadataLeafPaths'],
        metadataLeafJsonPointers=old['metadataLeafJsonPointers'], inheritedMetadataScope=old['inheritedMetadataScope'],
        immutablePriorRootScope=ref(OLD), completedFencedSourceReceipts=receipts,
        additiveCompletedTwinSlices=list(JOBS), originalSourceContextAndRawFailures=list(IMAGE_AND_FAILURE_FOLDERS),
        inheritedInstalledElementsProofNotTwinAcceptance=True,
        fullNumericalSourceClosureRequired=True, newMetadataLeaves=False, newMetadataPointerContract=False,
        currentSourceGeometryChanges=0, scriptedUndeployedTerrainCandidatePreserved=True,
        stageAndLiveExcluded=True, sourceOnly=True, currentAcceptance=False,
        hostQualification=False, authoredRoleAccepted=False, structuralRootOrBridgeCredit=False,
        nativeReacceptance=False, newlyInstalled=0)
    assert out['metadataLeafPaths'] == old['metadataLeafPaths']
    assert out['metadataLeafJsonPointers'] == old['metadataLeafJsonPointers']
    assert aliases[:len(old['historicalManifestAliases'])] == old['historicalManifestAliases']
    save(DOC / 'declared-scope.json', out)
    print(dict(paths=len(paths), completedTwinReceipts=len(receipts), newNumericLeaves=False, currentAcceptance=False), flush=True)

if __name__ == '__main__': main()
