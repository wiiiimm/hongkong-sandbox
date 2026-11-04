"""Independent full-521, old-asset, support and live-export readback.

Requires a completed installed receipt. No source modification or approval.
"""
from pathlib import Path

from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata
from original_independent_atomic_contract_v1_20261027 import manifest_triple_transition
from june_garden_qualified_stage_v2_20261103 import inspected_exports
from june_garden_publisher_hooks_v2_20261103 import SOURCES, SUPPORTS, P, SMALL
import june_garden_guarded_publish_v4_20261103 as guard
from june_garden_live_install_v4_20261103 import DEFAULT_PREVIOUS, verify_atomic


def verify_fixed_cohort(previous, current):
    assert previous['counts'] == dict(total=521, installedVerified=426, remaining=95)
    assert current['counts'] == dict(total=521, installedVerified=427, remaining=94)
    assert len(previous['rows']) == len(current['rows']) == 521
    a = {r['sourceKey']:r for r in previous['rows']}; b = {r['sourceKey']:r for r in current['rows']}
    assert len(a) == len(b) == 521 and set(a) == set(b)
    for report in [previous,current]:
        assert all(type(r['installedVerified']) is bool for r in report['rows'])
        assert sum(r['installedVerified'] for r in report['rows']) == report['counts']['installedVerified']
        assert sum(r['uid'] is None for r in report['rows']) == 2
    changed = [(key,r) for key,r in b.items() if r != a[key]]
    assert len(changed) == 1
    key,row = changed[0]
    assert a[key]['uid'] == row['uid'] == P and not a[key]['installedVerified'] and row['installedVerified']
    assert a[key]['indexedSourceSHA256'] == row['runtimeSourceSHA256'] == row['indexedSourceSHA256'] == SOURCES[P]
    return row


def main():
    installed = guard.BASE/guard.BATCH
    out = guard.BASE/'government-xl-june-garden-installed-root-readback-v3-20261103'
    assert not out.exists()
    receipt, pins = authenticate(installed)
    assert receipt['sourceSHA256ByUid'] == SOURCES and receipt['newlyInstalled'] == 1
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=427, remaining=94)
    assert receipt['completeCurrentCatalogueModels'] == 7101
    refs = [Path(__file__), installed/'result.json']
    for path, sha in pins.items():
        target = (ROOT/path).resolve(); assert target.is_relative_to(ROOT.resolve())
        assert digest(target.read_bytes()) == sha, path
        refs.append(target)
    history = read(installed/'historical-input-context.json')
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    old = next(r for r in history['mutableCurrentByteSnapshots'] if r['originalPath'] == str(manifest.relative_to(ROOT)))
    oldpath = ROOT/old['savedHistoricalBytes']['path']
    assert digest(oldpath.read_bytes()) == old['originalSHA256']
    before, after = read(oldpath), read(manifest)
    archived, archive_pins = authenticate(guard.BASE/'government-xl-june-garden-desktop-complete-mobile-held-v2-20261103')
    assert archive_pins[str(manifest.relative_to(ROOT))] == old['originalSHA256']
    prior_models = []
    for url in before['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url
        assert digest(path.read_bytes()) == archive_pins[str(path.relative_to(ROOT))]
        for model in read(path)['models']:
            asset = path.parent/model['asset']
            assert digest(asset.read_bytes()) == model['sha256']
            prior_models.append(model); refs.append(asset)
        refs.append(path)
    assert len(prior_models) == len({m['uid'] for m in prior_models}) == 7095
    current_models = [m for url in after['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
    assert len(current_models) == len({m['uid'] for m in current_models}) == 7101
    assert {m['uid']:m for m in current_models if m['uid'] not in SOURCES} == {m['uid']:m for m in prior_models}
    models = [m for m in current_models if m['uid'] in SOURCES]
    originals = read(guard.BASE/guard.BROWSER/'complete-unapproved-source-entries.json')
    verify_metadata(models, SOURCES, SUPPORTS, originals, {P:None, SMALL:None})
    for model in models:
        assert all(model[k] is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])
    planned = read(guard.STAGE/'plan.json')['topLevelTerrainPatches']
    manifest_triple_transition(before, after, planned)
    assert after['officialModelCatalogues'] == before['officialModelCatalogues'] + ['city/data/official-models/'+guard.QUALIFIED+'/catalogue.json']
    assert {k:v for k,v in after.items() if k not in ['officialModelCatalogues','terrainPatches']} == {k:v for k,v in before.items() if k not in ['officialModelCatalogues','terrainPatches']}
    for entry in planned:
        for url, sha in [(entry['replaces']['url'],entry['replaces']['sha256']), (entry['destination'],entry['sha256'])]:
            path = ROOT/'3d-viewer'/url; assert digest(path.read_bytes()) == sha; refs.append(path)
        assert read(ROOT/'3d-viewer'/entry['destination']) == read(ROOT/entry['source'])
    previous = read(DEFAULT_PREVIOUS); counts = read(installed/'full-xl-current-count.json')
    verify_fixed_cohort(previous,counts)
    expected = {r['path']:r['sha256'] for r in read(installed/'live-export-inspection-request.json')['images']}
    assert len(expected) == 307
    inspection = read(installed/'ROOT-LIVE-EXPORT-INSPECTION.json')
    assert inspection['reviewer'] == 'ROOT'; inspected_exports(inspection, expected)
    retained = {r['uid'] for r in read(guard.BASE/guard.TERRAIN/'summary.json')['rows']}
    prior_by_uid = {m['uid']:m for m in prior_models}
    for width in [390,1280]:
        report = read(installed/('viewport-'+str(width))/'live-browser.json')
        assert report['passed'] and not report['errors']
        own = [r for r in report['views'] if 'time' in r]
        held = report['retainedNativeOwnViews']
        assert len(own) == 12 and {(r['uid'],r['time']) for r in own} == {(u,t) for u in SOURCES for t in ['15:00','22:00']}
        assert len(held) == 138 and {(r['uid'],r['time']) for r in held} == {(u,t) for u in retained for t in ['15:00','22:00']}
        for row in [*own,*held]:
            assert row['active'] and row['visible'] and row['fullyFramed'] and not row['fallbackFaces']
            assert row['sourcePixelVisibility']['visiblePixels'] >= 32
            assert row['sourceSHA256'] == (SOURCES[row['uid']] if row['uid'] in SOURCES else prior_by_uid[row['uid']]['sha256'])
            path = installed/('viewport-'+str(width))/row['file']; relative = str(path.relative_to(ROOT))
            assert digest(path.read_bytes()) == expected[relative] == pins[relative]
        for row in own: assert row['pick'] == row['collision'] == row['uid'] and row['solidAppearance']
        for row in held:
            assert row['originalTriangles'] == prior_by_uid[row['uid']]['triangles']
            assert all(row['meshVisibility']) and not any(row['wireframeFlags'])
    assert verify_atomic(read(installed/'atomic-live/report.json'))
    support = {}; checker = module('june_readback_retained_supports', HERE.parent/'island-detail-integration/retained_basic_support.py')
    checker.stage_retained_basic_support(ROOT, after, {}, support, read)
    assert {(r['uid'],r['supportUid']) for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0','landsd/176739:0'),('landsd/6801:0','landsd/304712:0'),('landsd/255543:0','landsd/233218:0')}
    pointer = ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointer)['snapshotId'] == receipt['snapshotId']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid, sha in SOURCES.items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (receipt['snapshotId'],uid)).fetchone() == ('installed-verified',sha)
    result = dict(passed=True, installationIndependentlyVerified=True, uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES,
        fullXLCurrentCounts=counts['counts'], completeFixedXLRowsCompared=521, unmatchedUIDKeysRetained=2,
        onlyNewFixedXLUid=P, oldOriginalAssetsVerified=7095, allOldCatalogueBytesAndEntriesIdentical=True,
        completeCurrentCatalogueModels=7101, rootLiveExportsActuallyInspected=307, retainedBasicSupportChecks=support['retainedBasicSupportChecks'],
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, installedJobId=receipt['jobId'], snapshotId=receipt['snapshotId'])
    save(out/'ROOT-READBACK.json',result)
    refs.extend([oldpath,manifest,pointer,DEFAULT_PREVIOUS,installed/'ROOT-LIVE-EXPORT-INSPECTION.json',installed/'full-xl-current-count.json',guard.STAGE/'plan.json'])
    module('june_installed_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'independent-june-garden-full-xl-and-global-support-installed-readback',list(dict.fromkeys(refs)),result)


if __name__ == '__main__': main()
