"""Read-only installed ledger/evidence audit for an explicit completed source scope."""
import argparse
from run import ROOT, read, save, digest, connect


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
    retained = spec['retainedNativeSourceByUid']
    retained_images = set()
    assert retained and not set(retained).intersection(final['sourceSHA256ByUid'])
    for width in [390, 1280]:
        folder = install / ('viewport-' + str(width))
        report = read(folder / 'live-browser.json')
        views = report['retainedNativeOwnViews']
        assert len(views) == 2 * len(retained)
        assert {(v['uid'], v['time']) for v in views} == {(uid, time) for uid in retained for time in ['15:00', '22:00']}
        for view in views:
            expected = retained[view['uid']]
            assert view['active'] and view['visible'] and view['fullyFramed'] and not view['fallbackFaces']
            assert all(view['meshVisibility']) and not any(view['wireframeFlags'])
            assert view['sourceSHA256'] == expected['sha256'] and view['originalTriangles'] == expected['triangles']
            retained_images.add(str((folder / view['file']).relative_to(ROOT)))
    assert len(spec['retainedNativeImagesReviewedViaContactSheets']) == len(retained_images) == 4 * len(retained)
    assert {q['path'] for q in spec['retainedNativeImagesReviewedViaContactSheets']} == retained_images
    for q in spec['retainedNativeImagesReviewedViaContactSheets']:
        assert digest((ROOT / q['path']).read_bytes()) == q['sha256']
        assert (q['path'], q['sha256']) in checked
    for uid, expected in retained.items():
        model = next(m for m in models if m['uid'] == uid)
        assert model['sha256'] == expected['sha256'] and model['triangles'] == expected['triangles']
    sheets = spec['retainedNativeContactSheetsActuallyViewed']
    bindings = spec['retainedNativeContactSheetBindings']
    assert len(sheets) == len(bindings) == 2
    bound_inputs = set()
    for item, bindingref in zip(sheets, bindings):
        assert digest((ROOT / item['path']).read_bytes()) == item['sha256']
        assert digest((ROOT / bindingref['path']).read_bytes()) == bindingref['sha256']
        binding = read(ROOT / bindingref['path'])
        assert binding['output'] == item
        reportref = binding['report']
        assert (reportref['path'], reportref['sha256']) in checked
        for q in binding['inputs']:
            assert (q['path'], q['sha256']) in checked
            assert digest((ROOT / q['path']).read_bytes()) == q['sha256']
            bound_inputs.add((q['path'], q['sha256']))
    assert bound_inputs == {(q['path'], q['sha256']) for q in spec['retainedNativeImagesReviewedViaContactSheets']}
    replacement = spec['terrainReplacement']
    histories = [r for r in final['historicalMutableByteSnapshots'] if r['originalPath'] == final['manifest']['path']]
    assert len(histories) == 1
    before = read(ROOT / histories[0]['savedHistoricalBytes']['path'])
    after = read(manifest)
    assert sum(p['url'] == replacement['oldURL'] for p in before['terrainPatches']) == 1
    assert not any(p['url'] == replacement['oldURL'] for p in after['terrainPatches'])
    assert sum(p['url'] == replacement['newURL'] for p in after['terrainPatches']) == 1
    assert len(after['terrainPatches']) == len(before['terrainPatches'])
    assert [p for p in after['terrainPatches'] if p['url'] != replacement['newURL']] == [p for p in before['terrainPatches'] if p['url'] != replacement['oldURL']]
    oldpath, newpath = ROOT / '3d-viewer' / replacement['oldURL'], ROOT / '3d-viewer' / replacement['newURL']
    assert digest(oldpath.read_bytes()) == replacement['oldSHA256']
    assert digest(newpath.read_bytes()) == replacement['newSHA256']
    assert set(read(oldpath)['meta']['targetUids']) == set(replacement['retainedUids'])
    assert set(read(newpath)['meta']['targetUids']) == set(replacement['retainedUids']) | set(final['sourceSHA256ByUid'])
    oldmodels = [m for url in before['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']]
    assert models[:len(oldmodels)] == oldmodels and len(models) == len(oldmodels) + len(final['sourceSHA256ByUid'])
    proof = dict(installedJobId=final['jobId'], snapshotId=final['snapshotId'], currentManifest=final['manifest'],
                 fullXLCounts=counts['counts'], catalogueActors=len(models), completedReports=reports,
                 distinctVerifiedReferences=len(checked), verifiedReferences=list(checked.values()),
                 imagesActuallyViewed=spec['imagesActuallyViewed'], retainedNativeImagesReviewedViaContactSheets=spec['retainedNativeImagesReviewedViaContactSheets'], retainedNativeContactSheetsActuallyViewed=sheets, terrainReplacementVerified=replacement, specSHA256=digest(specpath.read_bytes()),
                 newInstallationCredit=0, aiGeometryModelling=False,
                 qualification='Independent read-only exact completed-job/reference/ledger/current-count/catalogue/pointer readback. Explicit new phase scope; historical mutable bytes resolved only through immutable installer archives. No duplicate installation credit or expansion into unrelated historical inventories.')
    save(specpath.parent / 'verification.json', proof)
    print({k: proof[k] for k in ['installedJobId', 'snapshotId', 'currentManifest', 'fullXLCounts', 'catalogueActors', 'distinctVerifiedReferences', 'newInstallationCredit']}, flush=True)


if __name__ == '__main__':
    main()
