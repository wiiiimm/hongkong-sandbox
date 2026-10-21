"""Refresh complete original bounds after an explicitly verified installation.

Reuse immutable bounds for unchanged sources; bind each addition to actual renderer
attributes and the installed receipt. No installation or optimisation is performed.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'prior', 'attributes', 'installed']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, receipts = [Path(__file__)], {}
    for name in [args.prior, args.attributes, args.installed]:
        receipt, pins = authenticate(base / name)
        receipts[name] = (receipt, pins)
        refs.append(base / name / 'result.json')

    def take(name, filename):
        path = base / name / filename
        assert digest(path.read_bytes()) == receipts[name][1][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = take(args.prior, 'complete-bounds.json.gz')
    attributes = take(args.attributes, 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    installed = receipts[args.installed][0]
    pointerpath = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointerpath)['snapshotId'] == installed['snapshotId']
    refs.append(pointerpath)
    for filename in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / filename
        assert digest(path.read_bytes()) == receipts[args.prior][1][str(path.relative_to(ROOT))]
        refs.append(path)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == installed['manifest']['sha256']
    manifest = read(manifestpath)
    refs.append(manifestpath)
    models, assets = {}, {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == receipts[args.installed][1][str(path.relative_to(ROOT))]
        catalogue = read(path)
        assert catalogue['rootTranslation'] == [-834500, 0, 816500]
        refs.append(path)
        for entry in catalogue['models']:
            uid = entry['uid']
            assert uid not in models
            models[uid], assets[uid] = entry, path.parent / entry['asset']
    rows = inventory['rows']
    oldids = {r['uid'] for r in rows}
    assert len(oldids) == len(rows) and oldids <= set(models)
    added = set(models) - oldids
    assert added == set(installed['installedUids'])
    for row in rows:
        uid = row['uid']
        assert row['sourceSHA256'] == models[uid]['sha256'] == digest(assets[uid].read_bytes())
        row.pop('disjoint', None)
    captured = {r['uid']: r for r in attributes['rows']}
    assert added <= captured.keys()
    for uid in sorted(added):
        row, asset = captured[uid], assets[uid]
        raw = asset.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == models[uid]['sha256']
        proof = packed_world_bounds(raw)
        rows.append(dict(uid=uid, sourceSHA256=row['sourceSHA256'], completeFourWorldBounds=[proof['originalWholeSourceBounds'], row['completeLiteralWorldBounds'], row['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'], row['completeExplicitBalancedFloat32ModelMatrixWorldBounds']], completeOriginalPOSITIONProof=proof))
    assert len(rows) == len(models)
    tiles = {}
    for entry in manifest['tiles']:
        path = ROOT / '3d-viewer' / entry['url']
        tiles[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
    save(doc / 'complete-bounds.json.gz', dict(rows=rows, currentFormTileHashes=tiles))
    result = dict(uids=sorted(added), currentNativeActors=len(rows), freshAddedBounds=sorted(added), installationApproved=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    refs.extend(assets.values())
    refs.append(HERE / 'exact_packed_world_bounds_v3_20261010.py')
    module('refresh_bounds_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-current-original-inventory-bounds', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
