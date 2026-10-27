"""Refresh complete original bounds; unbound scheduler code must be byte-identical to prior.

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
    for key in ['batch', 'prior', 'attributes', 'installed', 'installed-readback']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / args.batch
    assert not doc.exists()
    refs, receipts = [Path(__file__)], {}
    for name in [args.prior, args.attributes, args.installed, args.installed_readback]:
        receipt, pins = authenticate(base / name)
        receipts[name] = (receipt, pins)
        refs.append(base / name / 'result.json')

    installed_receipt,installed_pins=receipts[args.installed]
    checked,checked_pins=receipts[args.installed_readback]
    assert checked['installationIndependentlyVerified'] and checked['snapshotId']==installed_receipt['snapshotId']
    assert checked['sourceSHA256ByUid']==installed_receipt['sourceSHA256ByUid']
    merged=dict(installed_pins)
    for path,sha in checked_pins.items():
        assert path not in merged or merged[path]==sha, 'Installed/readback input hashes differ'
        merged[path]=sha
    receipts[args.installed]=(installed_receipt,merged)

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
    runtime_provenance=[]
    for filename in ['official-models.js', 'official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / filename
        key=str(path.relative_to(ROOT));actual=digest(path.read_bytes());historical=receipts[args.prior][1][key]
        if filename=='official-models.js':
            # This file schedules activation; packed geometry transforms are in
            # the unchanged asset decoder and geo module checked below. Rebind
            # scheduling code to the fresh completed installed HTTP checks.
            installed_pin=receipts[args.installed][1].get(key)
            if installed_pin is not None:assert actual==installed_pin
            else:assert actual==historical, 'Unbound scheduling code differs from prior exact code'
        else:assert actual==historical, 'Geometry transform implementation changed: '+filename
        runtime_provenance.append(dict(path=key,historicalSHA256=historical,currentSHA256=actual,historicalRuntimeApprovalTransferred=False,installedDirectCodeBindingPresent=key in receipts[args.installed][1],currentCodeEqualsHistorical=actual==historical,geometryTransformCodeUnchanged=filename!='official-models.js'))
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
    result['runtimeProvenance']=runtime_provenance
    save(doc / 'runtime-provenance.json',dict(rows=runtime_provenance,qualification='Immutable prior geometric bounds reused only with unchanged source bytes, asset decoder and geo transform implementation. Activation scheduling is independently rebound to exact fresh completed installed HTTP evidence, not historical runtime approval.'))
    save(doc / 'summary.json', result)
    refs.extend(assets.values())
    refs.append(HERE / 'exact_packed_world_bounds_v3_20261010.py')
    module('refresh_bounds_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-current-original-inventory-bounds', list(dict.fromkeys(refs)), result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
