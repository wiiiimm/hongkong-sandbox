"""Read-only installed ledger/evidence audit for an explicit completed source scope."""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
UID='landsd/75643:0'
SHA='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'
TERRAIN='27853c0201e107cc3c70f383507a21a6a418265495007de1f44cc039ab2b8234'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', required=True)
    a = p.parse_args()
    specpath = ROOT / a.spec
    spec = read(specpath)
    base = ROOT / 'docs/astra-city/government-import'
    install = base / spec['installBatch']
    final = read(install / 'result.json')
    aliases, checked, reports = {}, {}, []
    for row in final['historicalMutableByteSnapshots']:
        q = row['savedHistoricalBytes']
        path = ROOT / q['path']
        assert digest(path.read_bytes()) == q['sha256'] == row['originalSHA256']
        aliases[row['originalPath'], row['originalSHA256']] = path
    assert spec['phaseBatches'] and len(set(spec['phaseBatches'])) == len(spec['phaseBatches'])
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for name in [spec['installBatch'], *spec['phaseBatches']]:
            assert name.startswith('government-xl-') and '/' not in name
            receipt = read(base / name / 'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                              (receipt['jobId'],)).fetchone() == ('complete', receipt)
            reports.append(dict(batch=name, jobId=receipt['jobId']))
            for q in receipt['evidenceRefs']:
                key = q['path'], q['sha256']
                if key not in checked:
                    path = aliases.get(key, ROOT / q['path'])
                    assert digest(path.read_bytes()) == q['sha256'], q['path']
                    checked[key] = dict(**q, resolvedBytes=str(path.relative_to(ROOT)))
        for uid, sha in final['sourceSHA256ByUid'].items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews '
                              'WHERE snapshot_id=%s AND uid=%s', (final['snapshotId'], uid)).fetchone() == ('installed-verified', sha)
    counts = read(install / 'full-xl-current-count.json')
    assert counts['counts'] == final['fullXLCurrentCounts'] == spec['expectedCounts']
    assert len(counts['rows']) == spec['expectedCounts']['total']
    assert sum(bool(r['installedVerified']) for r in counts['rows']) == spec['expectedCounts']['installedVerified']
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    assert pointer['snapshotId'] == final['snapshotId']
    manifest = ROOT / final['manifest']['path']
    assert digest(manifest.read_bytes()) == final['manifest']['sha256']
    models = [m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']]
    assert len(models) == len({m['uid'] for m in models}) == spec['expectedCatalogueActors']
    for uid, sha in final['sourceSHA256ByUid'].items():
        m = next(m for m in models if m['uid'] == uid)
        assert m['sha256'] == sha and m['triangles'] == spec['sourceTriangleCounts'][uid]
        assert m['proceduralWindows'] is False
        assert m['publicationApproved'] and m['placementReviewed'] and m['identityReviewApproved']
    assert spec['reviewer'] == 'ROOT' and spec['visualAcceptance'] is True
    assert len(spec['imagesActuallyViewed']) == 4 * len(final['sourceSHA256ByUid'])
    expected_images = set()
    for width in [390, 1280]:
        folder = install / ('viewport-' + str(width))
        report = read(folder / 'live-browser.json')
        assert report['passed'] and not report['errors']
        expected_images.update(str((folder / v['file']).relative_to(ROOT)) for v in report['views'] if 'time' in v)
    assert {q['path'] for q in spec['imagesActuallyViewed']} == expected_images
    for q in spec['imagesActuallyViewed']:
        assert digest((ROOT / q['path']).read_bytes()) == q['sha256']
        assert (q['path'], q['sha256']) in checked
    histories=[r for r in final['historicalMutableByteSnapshots'] if r['originalPath']==final['manifest']['path']]
    assert len(histories)==1
    before=read(ROOT/histories[0]['savedHistoricalBytes']['path']);after=read(manifest)
    assert after['terrainPatches']==before['terrainPatches']
    assert final['sourceSHA256ByUid']=={UID:SHA}
    for m in models:
        if m['uid'] in final['sourceSHA256ByUid']:
            assert not m.get('activationGroup')
            assert not m.get('supportDependencies') and m['suppressesBuildingUids']==['way/334029318:0']
            assert m['reviewedOsmApronGraphic']['reviewSHA256']=='d9c2a503febf90dee0d67a14ac19520965c5faf793cf417bd19209091f643c48'
            assert m.get('verticalPlacementOffsetHKPD',0) == 0
    assets = 0
    for catalogue_url in after['officialModelCatalogues']:
        catalogue_path = ROOT/'3d-viewer'/catalogue_url
        for m in read(catalogue_path)['models']:
            assert digest((catalogue_path.parent/m['asset']).read_bytes()) == m['sha256']
            assets += 1
    assert assets==spec['expectedCatalogueActors']==7030
    support = {}
    guard = module('civic_independent_support_readback',HERE.parent/'island-detail-integration/retained_basic_support.py')
    guard.stage_retained_basic_support(ROOT,after,{},support,read)
    assert {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0')} <= {(r['uid'],r['supportUid']) for r in support['retainedBasicSupportChecks']}
    previous = read(ROOT/spec['previousCountReport'])
    oldrows = {r['sourceKey']:r for r in previous['rows']}
    newrows = {r['sourceKey']:r for r in counts['rows']}
    assert len(oldrows) == len(newrows) == 521 and set(oldrows) == set(newrows)
    assert [r['uid'] for key,r in newrows.items() if r != oldrows[key]] == [UID]
    assert sum(r['uid'] is None for r in newrows.values()) == 2
    atomic = read(base/spec['atomicBatch']/'browser/report.json')
    assert atomic['passed'] and atomic['liveInstalledHTTP'] and not atomic['catalogueAndTerrainSubstitution'] and not atomic['pageErrors']
    assert len(atomic['cases'])==2 and {c['failedUid'] for c in atomic['cases']} == {None,*final['sourceSHA256ByUid']}
    assert {(c['width'],c['failedUid']) for c in atomic['cases']} == {(1280,None),*[(390,uid) for uid in final['sourceSHA256ByUid']]}
    for case in atomic['cases']:
        assert {r['uid']:r['sha256'] for r in case['sources']} == final['sourceSHA256ByUid']
        assert case['baseOnlyRestoredCompleteGroup'] and case['completeGroupEvicted'] and not case['audit']['violations'] and case['audit']['frames'] > 0
        phases={r['phase']:r for r in case['canopyLifecycle']};assert {'original-active','base-only','auto-restored','evicted-return-base-only'}<=set(phases)
        if case['failedUid']: assert case['failureKeptAllBasics'] and 'failed-download'in phases
    oldmodels=[m for url in before['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
    assert models[:len(oldmodels)]==oldmodels and len(models)==len(oldmodels)+len(final['sourceSHA256ByUid'])
    assert after['tiles']==before['tiles'] and after['counts']==before['counts']
    proof = dict(allInstalledAssetsRehashed=assets,completeFixedXLRowsCompared=521,bothNullUIDKeysPreserved=True,retainedBasicSupportChecks=support,terrainUnchanged=True,allExistingModelTuplesUnchanged=True,installedJobId=final['jobId'], snapshotId=final['snapshotId'], currentManifest=final['manifest'],
                 fullXLCounts=counts['counts'], catalogueActors=len(models), completedReports=reports,
                 distinctVerifiedReferences=len(checked), verifiedReferences=list(checked.values()),
                 imagesActuallyViewed=spec['imagesActuallyViewed'], specSHA256=digest(specpath.read_bytes()),
                 newInstallationCredit=0, aiGeometryModelling=False,
                 qualification='Independent read-only exact completed-job/reference/ledger/current-count/catalogue/pointer readback. Explicit new phase scope; historical mutable bytes resolved only through immutable installer archives. No duplicate installation credit or expansion into unrelated historical inventories.')
    save(specpath.parent / 'verification.json', proof)
    assert spec['readbackBatch'] == specpath.parent.name
    refs = [specpath, specpath.parent/'verification.json', Path(__file__)]
    refs += [ROOT/q['resolvedBytes'] for q in checked.values()]
    refs += [manifest, ROOT/spec['previousCountReport'], HERE.parent/'island-detail-integration/retained_basic_support.py']
    module('civic_independent_readback_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        spec['readbackBatch'], 'whole-installed-independent-western-pier-asset-actor-xl-support-readback', refs,
        dict(uids=sorted(final['sourceSHA256ByUid']), passed=True, installationIndependentlyVerified=True,
             sourceSHA256ByUid=final['sourceSHA256ByUid'], installedJobId=final['jobId'],
             fullXLCurrentCounts=counts['counts'], allCurrentAssetsRehashed=assets,
             oldCatalogueEntriesPreserved=len(oldmodels), completeFixedXLRowsCompared=521,
             bothNullUIDKeysPreserved=True, snapshotId=final['snapshotId'], sourceGeometryChanges=0))
    print({k: v for k, v in proof.items() if k not in ['verifiedReferences', 'completedReports', 'imagesActuallyViewed']}, flush=True)


if __name__ == '__main__':
    main()
