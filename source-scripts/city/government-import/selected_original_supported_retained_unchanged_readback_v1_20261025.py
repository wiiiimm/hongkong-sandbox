"""Independent full-inventory readback; every existing actor must remain unchanged."""
from pathlib import Path
import os
from run import ROOT, HERE, read, save, digest, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope


def main():
    base = ROOT / 'docs/astra-city/government-import'
    cfgpath = (ROOT / os.environ['ORIGINAL_INSTALL_CONFIG']).resolve()
    assert cfgpath.is_relative_to(base)
    cfg = read(cfgpath)
    prefix, date = cfg['prefix'], cfg['date']
    installed = base / (prefix + '-supported-retained-unchanged-original-installed-v1-' + date)
    out = base / (prefix + '-supported-retained-unchanged-root-readback-v1-' + date)
    assert not out.exists()
    receipt, pins = authenticate(installed)
    refs = [Path(__file__), cfgpath, installed / 'result.json']
    for path, sha in pins.items():
        p = ROOT / path
        assert digest(p.read_bytes()) == sha, path
        refs.append(p)
    sources = cfg['sources']
    n = cfg['previousInstalled'] + cfg['expectedFixedXLDelta']
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=n, remaining=521-n)
    assert receipt['sourceSHA256ByUid'] == sources and receipt['newlyInstalled'] == cfg['expectedFixedXLDelta']
    physical = read(base / cfg['physical'] / 'ROOT-PHYSICAL-REVIEW.json')
    assert physical['installedMetadataChanges'] is False and 'installedSupportUpdate' not in physical
    inventory = base / cfg['previousNativeInventory']
    _, oldpins = authenticate(inventory)
    refs.append(inventory / 'result.json')
    oldcats = {p: h for p, h in oldpins.items() if p.startswith('3d-viewer/city/data/official-models/') and p.endswith('/catalogue.json')}
    assert oldcats
    oldmodels = {}
    for path, sha in oldcats.items():
        p = ROOT / path
        assert digest(p.read_bytes()) == sha, path
        refs.append(p)
        for m in read(p)['models']:
            assert m['uid'] not in oldmodels
            oldmodels[m['uid']] = m
            asset = p.parent / m['asset']
            assert digest(asset.read_bytes()) == m['sha256']
            refs.append(asset)
    assert len(oldmodels) == cfg['currentNativeActors']
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    after = read(manifest)
    aliases = {r['originalPath']: r for r in receipt['historicalMutableByteSnapshots']}
    history = aliases[str(manifest.relative_to(ROOT))]
    saved = history['savedHistoricalBytes']
    oldpath = ROOT / saved['path']
    assert digest(oldpath.read_bytes()) == saved['sha256'] == history['originalSHA256']
    before = read(oldpath)
    refs.append(oldpath)
    assert set(oldcats) == {'3d-viewer/' + u for u in before['officialModelCatalogues']}
    assert after['officialModelCatalogues'][:-1] == before['officialModelCatalogues']
    models = [m for u in after['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / u)['models']]
    by = {m['uid']: m for m in models}
    assert len(models) == len(by) == cfg['currentNativeActors'] + len(sources) == receipt['completeCurrentCatalogueModels']
    assert {u: m for u, m in by.items() if u not in sources} == oldmodels
    new = [m for m in models if m['uid'] in sources]
    assert verify_support_scope(new, sources, cfg['supportByUid'])
    for m in new:
        assert all(m.get(k) is True for k in ['publicationApproved', 'placementReviewed', 'identityReviewApproved'])
        assert not m.get('retainedBasicSupportDependencies') and m.get('verticalPlacementOffsetHKPD', 0) == 0
    plan = read(HERE / 'accepted' / (prefix + '-supported-retained-unchanged-qualified-stage-v1-' + date) / 'plan.json')
    assert not plan.get('dependencyReviews') and not plan.get('catalogueUpdates')
    assert len(plan['topLevelTerrainPatches']) == 1
    patch = plan['topLevelTerrainPatches'][0]
    replacement = patch['replaces']
    assert len(after['terrainPatches']) == len(before['terrainPatches'])
    assert sum(p['url'] == replacement['url'] for p in before['terrainPatches']) == 1
    assert not any(p['url'] == replacement['url'] for p in after['terrainPatches'])
    assert sum(p['url'] == patch['destination'] for p in after['terrainPatches']) == 1
    assert [p for p in after['terrainPatches'] if p['url'] != patch['destination']] == [p for p in before['terrainPatches'] if p['url'] != replacement['url']]
    assert {k: v for k, v in after.items() if k not in ['officialModelCatalogues', 'terrainPatches']} == {k: v for k, v in before.items() if k not in ['officialModelCatalogues', 'terrainPatches']}
    for url, sha in [(replacement['url'], replacement['sha256']), (patch['destination'], patch['sha256'])]:
        p = ROOT / '3d-viewer' / url
        assert digest(p.read_bytes()) == sha
        refs.append(p)
    assert set(read(ROOT / '3d-viewer' / patch['destination'])['meta']['targetUids']) == set(replacement['retainedUids']) | set(sources)
    previous = base / cfg['previousCountReport']
    oldcounts, counts = read(previous), read(installed / 'full-xl-current-count.json')
    a, b = {r['sourceKey']: r for r in oldcounts['rows']}, {r['sourceKey']: r for r in counts['rows']}
    assert set(a) == set(b) and len(a) == 521
    changed = [r for k, r in b.items() if a[k] != r]
    expected = set(receipt['fixedXLDelta']['newFixedXLUids'])
    assert len(changed) == len(expected) == cfg['expectedFixedXLDelta'] and {r['uid'] for r in changed} == expected
    for r in changed:
        assert r['installedVerified'] and r['runtimeSourceSHA256'] == r['indexedSourceSHA256'] == sources[r['uid']]
    inspectionpath = installed / 'ROOT-LIVE-EXPORT-INSPECTION.json'
    inspection = read(inspectionpath)
    assert inspection['reviewer'] == 'ROOT' and inspection['visualAcceptance']
    inspected = {q['path']: q['sha256'] for q in inspection['imagesActuallyViewed'] + inspection['retainedImagesActuallyViewed']}
    retained = set(physical['retainedNativeUids'])
    assert len(inspected) == 4 * (len(sources) + len(retained))
    viewed = set()
    for width in [390, 1280]:
        folder = installed / ('viewport-' + str(width))
        r = read(folder / 'live-browser.json')
        assert r['passed'] and not r['errors']
        views = [v for v in r['views'] if 'time' in v]
        assert {(v['uid'], v['time']) for v in views} == {(u, t) for u in sources for t in ['15:00', '22:00']}
        for v in views:
            assert v['pick'] == v['collision'] == v['uid'] and v['sourceSHA256'] == sources[v['uid']]
            assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces']
        native = r['retainedNativeOwnViews']
        assert {(v['uid'], v['time']) for v in native} == {(u, t) for u in retained for t in ['15:00', '22:00']}
        for v in native:
            assert v['sourceSHA256'] == by[v['uid']]['sha256'] and v['originalTriangles'] == by[v['uid']]['triangles']
            assert v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces'] and all(v['meshVisibility']) and not any(v['wireframeFlags'])
        for v in views + native:
            p = folder / v['file']
            key = str(p.relative_to(ROOT))
            assert digest(p.read_bytes()) == inspected[key] == pins[key]
            viewed.add(key)
    assert viewed == set(inspected)
    support = {}
    helper = module('unchanged_retained_global_support', HERE.parent / 'island-detail-integration/retained_basic_support.py')
    helper.stage_retained_basic_support(ROOT, after, {}, support, read)
    assert {(r['uid'], r['supportUid']) for r in support['retainedBasicSupportChecks']} >= {('landsd/312858:0', 'landsd/176739:0'), ('landsd/6801:0', 'landsd/304712:0')}
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointer)['snapshotId'] == receipt['snapshotId']
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for uid, sha in sources.items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (receipt['snapshotId'], uid)).fetchone() == ('installed-verified', sha)
    result = dict(uids=sorted(sources), passed=True, installedJobId=receipt['jobId'], snapshotId=receipt['snapshotId'], fullXLCurrentCounts=receipt['fullXLCurrentCounts'], completeCurrentCatalogueModels=len(models), unchangedOldCatalogueActors=len(oldmodels), allOldActorEntriesAndAssetsIdentical=True, completeFixedXLRowsCompared=521, onlyChangedFixedXLUids=sorted(expected), retainedBasicSupportChecks=support['retainedBasicSupportChecks'], sourceGeometryChanges=0, aiGeometryModelling=False, ROOTLiveVisualInspection=inspection)
    save(out / 'ROOT-READBACK.json', result)
    refs += [manifest, pointer, previous, inspectionpath, HERE / 'original_supported_catalogue_scope_v1_20261024.py', HERE.parent / 'island-detail-integration/retained_basic_support.py']
    module('unchanged_retained_root_readback', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name, 'independent-installed-original-assembly-full-inventory-unchanged-readback', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
