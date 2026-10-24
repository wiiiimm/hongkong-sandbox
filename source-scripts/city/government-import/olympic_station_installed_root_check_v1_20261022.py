"""Independently read back the installed source, ledger, counts and new evidence."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect

BASE = ROOT / 'docs/astra-city/government-import'
INSTALL = BASE / 'government-xl-olympic-station-original-installed-v3-20261022'
BATCH = 'government-xl-olympic-station-installed-root-check-v1-20261022'


def main():
    doc = BASE / BATCH
    assert not doc.exists()
    result = read(INSTALL / 'result.json')
    aliases = {}
    for row in result['historicalMutableByteSnapshots']:
        q = row['savedHistoricalBytes']
        p = ROOT / q['path']
        assert digest(p.read_bytes()) == q['sha256'] == row['originalSHA256']
        aliases[row['originalPath'], row['originalSHA256']] = p
    # Explicit new numerical/review scope. Older receipt files remain bound
    # context, without recursively unfolding unrelated historical inventories.
    names = [
        'olympic-facet-band-return', 'olympic-band-anchor-precision',
        'olympic-station-band-runtime', 'olympic-station-band-continuous',
        'olympic-station-band-scope', 'olympic-station-band-neighbours',
        'olympic-hoi-yu-unchanged-terrain', 'olympic-station-original-attributes',
        'olympic-station-original-wall-paths-v2', 'olympic-four-stream-transport',
        'olympic-station-band-rim-attribution', 'olympic-station-raised-rim-contacts',
        'olympic-original-endpoint-paths-v2', 'olympic-original-low-component-joins',
        'olympic-original-strict-anchor-paths', 'olympic-rim-four-stream-replay',
        'olympic-station-band-identity', 'olympic-station-source-identity-review',
        'olympic-station-foreign-scope-plan', 'olympic-station-current-foreign-attributes',
        'olympic-station-full-foreign-intersections', 'olympic-station-private-browser',
        'olympic-station-private-mobile', 'olympic-station-qualified-source-review',
        'olympic-station-qualified-stage-v2'
    ]
    folders = [INSTALL]
    for name in names:
        stem = name if name.endswith('-v2') else name + '-v1'
        folders.append(BASE / ('government-xl-' + stem + '-20261022'))
    checked, reports = {}, []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in folders:
            receipt = read(folder / 'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                              (receipt['jobId'],)).fetchone() == ('complete', receipt)
            reports.append(dict(batch=folder.name, jobId=receipt['jobId']))
            for q in receipt['evidenceRefs']:
                key = q['path'], q['sha256']
                if key in checked:
                    continue
                p = aliases.get(key, ROOT / q['path'])
                assert digest(p.read_bytes()) == q['sha256'], q['path']
                checked[key] = dict(path=q['path'], sha256=q['sha256'],
                                    resolvedBytes=str(p.relative_to(ROOT)))
        assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews '
                          'WHERE snapshot_id=%s AND uid=%s',
                          (result['snapshotId'], 'landsd/81242:0')).fetchone() == (
                              'installed-verified', result['sourceSHA256ByUid']['landsd/81242:0'])
    counts = read(INSTALL / 'full-xl-current-count.json')
    assert counts['counts'] == result['fullXLCurrentCounts'] == dict(total=521, installedVerified=325, remaining=196)
    pointer = read(ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json')
    assert pointer['snapshotId'] == result['snapshotId']
    manifest = ROOT / result['manifest']['path']
    assert digest(manifest.read_bytes()) == result['manifest']['sha256']
    models = [m for url in read(manifest)['officialModelCatalogues']
              for m in read(ROOT / '3d-viewer' / url)['models']]
    assert len(models) == len({m['uid'] for m in models}) == 6842
    model = next(m for m in models if m['uid'] == 'landsd/81242:0')
    assert model['sha256'] == result['sourceSHA256ByUid'][model['uid']]
    assert model['publicationApproved'] and model['placementReviewed'] and model['identityReviewApproved']
    assert model['proceduralWindows'] is False and model['triangles'] == 14051
    images = []
    for width in [390, 1280]:
        report = read(INSTALL / str(width) / 'live-browser.json')
        assert report['passed'] and not report['errors']
        for name in [f'live-landsd-81242-0-{width}-1500.png',
                     f'live-landsd-81242-0-{width}-2200.png',
                     f'live-local-joint-olympic-north-neighbour-{width}.png']:
            p = INSTALL / str(width) / name
            assert (str(p.relative_to(ROOT)), digest(p.read_bytes())) in checked
            images.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
    proof = dict(installedJobId=result['jobId'], snapshotId=result['snapshotId'],
                 fullXLCounts=counts['counts'], catalogueActors=len(models),
                 verifiedCompletedReports=reports, distinctVerifiedReferences=len(checked),
                 verifiedReferences=list(checked.values()), currentManifest=result['manifest'],
                 liveImagesActuallyInspected=images, modelGeometryChanges=0,
                 aiGeometryModelling=False, newInstallationCredit=0,
                 qualification='Independent read-only exact Neon/job/ledger/current catalogue/count readback and all direct references of the explicit new numerical/review scope. Historical mutable bytes resolve through immutable installer archives. ROOT inspected both source day/night exports and focused joint on both widths. Existing installation verified, no duplicate credit.')
    save(doc / 'verification.json', proof)
    print({k: v for k, v in proof.items() if k not in ['verifiedReferences', 'verifiedCompletedReports', 'liveImagesActuallyInspected']}, flush=True)


if __name__ == '__main__':
    main()
