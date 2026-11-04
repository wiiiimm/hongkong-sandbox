"""Refresh all original bounds across an explicit verified installation chain.

Preserves prior source bounds only under identical assets/renderer modules. Every
new actor binds exact decoded whole-source and all captured Float32 bounds.
"""
import argparse
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--chain', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    specpath = ROOT / a.chain
    spec = read(specpath)
    assert spec['additions']
    receipts = {}
    refs = [specpath, __file__]
    for name in [spec['prior'], *[r[k] for r in spec['additions'] for k in ['installed', 'attributes']]]:
        assert name.startswith('government-xl-') and '/' not in name
        receipts[name] = authenticate(base / name)
        refs.append(base / name / 'result.json')

    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == receipts[name][1][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = take(spec['prior'], 'complete-bounds.json.gz')
    rows = inventory['rows']
    old = {r['uid'] for r in rows}
    assert len(old) == len(rows)
    pointerpath = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer_name = str(pointerpath.relative_to(ROOT))
    previous_pointer_sha = receipts[spec['prior']][1][pointer_name]
    additions = {}
    previous_snapshot = None
    for step in spec['additions']:
        installed = receipts[step['installed']][0]
        history = [r for r in installed['historicalMutableByteSnapshots'] if r['originalPath'] == pointer_name]
        assert len(history) == 1
        historic = history[0]
        path = ROOT / historic['savedHistoricalBytes']['path']
        assert digest(path.read_bytes()) == historic['originalSHA256'] == historic['savedHistoricalBytes']['sha256']
        if previous_snapshot is None:
            assert historic['originalSHA256'] == previous_pointer_sha
        else:
            assert read(path)['snapshotId'] == previous_snapshot
        refs.append(path)
        attrs = take(step['attributes'], 'attributes.json.gz')
        assert attrs['startEndAllInputsVerified']
        captured = {r['uid']: r for r in attrs['rows']}
        assert set(installed['installedUids']) == set(installed['sourceSHA256ByUid'])
        for uid in installed['installedUids']:
            assert uid not in old and uid not in additions
            row = captured[uid]
            assert row['sourceSHA256'] == installed['sourceSHA256ByUid'][uid]
            additions[uid] = row
        previous_snapshot = installed['snapshotId']
    assert read(pointerpath)['snapshotId'] == previous_snapshot
    refs.append(pointerpath)
    for name in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / name
        assert digest(path.read_bytes()) == receipts[spec['prior']][1][str(path.relative_to(ROOT))]
        refs.append(path)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == installed['manifest']['sha256']
    refs.append(manifestpath)
    manifest = read(manifestpath)
    models, assets = {}, {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == receipts[spec['additions'][-1]['installed']][1][str(path.relative_to(ROOT))]
        cat = read(path)
        assert cat['rootTranslation'] == [-834500, 0, 816500]
        refs.append(path)
        for model in cat['models']:
            assert model['uid'] not in models
            models[model['uid']], assets[model['uid']] = model, path.parent / model['asset']
    assert old | set(additions) == set(models) and not old & set(additions)
    for row in rows:
        uid = row['uid']
        assert row['sourceSHA256'] == models[uid]['sha256'] == digest(assets[uid].read_bytes())
        row.pop('disjoint', None)
    for uid, row in sorted(additions.items()):
        raw = assets[uid].read_bytes()
        assert digest(raw) == row['sourceSHA256'] == models[uid]['sha256']
        proof = packed_world_bounds(raw)
        rows.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], completeFourWorldBounds=[proof['originalWholeSourceBounds'], row['completeLiteralWorldBounds'], row['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'], row['completeExplicitBalancedFloat32ModelMatrixWorldBounds']], completeOriginalPOSITIONProof=proof))
    assert len(rows) == len(models) == spec['expectedCurrentNativeActors']
    tiles = {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        tiles[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
    save(doc / 'complete-bounds.json.gz', dict(rows=rows, currentFormTileHashes=tiles))
    result = dict(uids=sorted(additions), currentNativeActors=len(rows), freshAddedBounds=sorted(additions), installationChain=spec['additions'], currentManifestSHA256=digest(manifestpath.read_bytes()), sourceGeometryChanges=0, installationApproved=False, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    refs.extend(assets.values())
    refs.append(HERE / 'exact_packed_world_bounds_v3_20261010.py')
    refs = [ROOT / r if isinstance(r, str) else r for r in refs]
    module('refresh_chain_bounds_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'complete-current-original-inventory-explicit-installation-chain', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
