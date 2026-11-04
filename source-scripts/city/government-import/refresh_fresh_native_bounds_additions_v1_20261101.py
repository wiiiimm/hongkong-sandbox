"""Increment fresh scalar bounds only across a verified additive installation.

Reuse old runtime bounds only with identical entries, forms, assets and complete
geometry-module inputs. Load every added original through the current renderer.
This diagnostic neither grants acceptance nor changes public data.
"""
import argparse, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'prior', 'installed', 'readback']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    assert all(v.startswith('government-xl-') and '/' not in v for v in [a.batch, a.prior, a.installed, a.readback])
    out, local = BASE / a.batch, HERE / 'local' / a.batch
    assert not out.exists()
    if not a.owned:
        assert not local.exists()
        c = reservations.claim('incremental-fresh-bounds-' + str(uuid.uuid4()), ['immutable-source-proof:' + a.batch], batch=a.batch, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], local / 'reservation.json', [sys.executable, __file__, *sys.argv[1:], '--owned'])
    lease = read(local / 'reservation.json')
    assert reservations.owns(lease)
    refs, pins, receipts = [Path(__file__)], {}, {}
    for name in [a.prior, a.installed, a.readback]:
        receipts[name], pins[name] = authenticate(BASE / name)
        refs.append(BASE / name / 'result.json')
    def take(name, filename):
        f = BASE / name / filename
        assert digest(f.read_bytes()) == pins[name][str(f.relative_to(ROOT))]
        refs.append(f)
        return read(f)
    old = take(a.prior, 'complete-bounds.json.gz')
    oldinput = take(a.prior, 'input.json.gz')
    oldruntime = take(a.prior, 'inventory.json.gz')
    assert oldruntime['startAndEndInputHashesVerified'] and not oldruntime['errors']
    assert oldruntime['wholeUnusedPositionVerticesIncluded'] and oldinput['currentBoundOnly']
    assert oldruntime['successfullyCapturedActors'] == len(old['rows']) == len(oldinput['rows'])
    installed, checked = receipts[a.installed], receipts[a.readback]
    assert installed['publication'] and checked['passed'] and checked['allOldCatalogueBytesAndEntriesIdentical']
    assert checked['installedJobId'] == installed['jobId'] and checked['snapshotId'] == installed['snapshotId']
    assert checked['previousAssetsVerified'] == len(old['rows'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    start = digest(manifest.read_bytes())
    assert start == installed['manifest']['sha256'] == pins[a.readback][str(manifest.relative_to(ROOT))]
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointer)['snapshotId'] == installed['snapshotId']
    refs.extend([manifest, pointer])
    # Scheduling is not a geometry dependency. Check every dependency actually
    # recorded by the fresh production exporter, rather than inventing a pin.
    modules = {k: v for k, v in oldruntime['inputHashes'].items()
               if k.startswith('3d-viewer/') and not k.startswith('3d-viewer/city/data/')}
    assert '3d-viewer/city/official-model-assets.js' in modules and '3d-viewer/city/geo.js' in modules
    for name, sha in modules.items():
        f = ROOT / name
        assert digest(f.read_bytes()) == sha, 'Changed geometry dependency requires fresh capture: ' + name
        refs.append(f)
    kernel = HERE / 'exact_packed_world_bounds_v3_20261010.py'
    assert digest(kernel.read_bytes()) == pins[a.prior][str(kernel.relative_to(ROOT))]
    refs.append(kernel)
    models, assets, cats = {}, {}, []
    for url in read(manifest)['officialModelCatalogues']:
        f = ROOT / '3d-viewer' / url
        assert digest(f.read_bytes()) == pins[a.readback][str(f.relative_to(ROOT))]
        refs.append(f)
        cats.append(dict(path=str(f.relative_to(ROOT)), sha256=digest(f.read_bytes())))
        for e in read(f)['models']:
            assert e['uid'] not in models
            models[e['uid']], assets[e['uid']] = e, f.parent / e['asset']
    oldrows = {r['uid']: r for r in old['rows']}
    inputs = {r['uid']: r for r in oldinput['rows']}
    assert set(oldrows) == set(inputs) and len(oldrows) == len(old['rows'])
    added = set(models) - set(oldrows)
    assert set(oldrows) <= set(models) and added == set(installed['installedUids']) == set(installed['sourceSHA256ByUid'])
    forms, tiles = {}, {}
    for tile in read(manifest)['tiles']:
        f = ROOT / '3d-viewer' / tile['url']
        tiles[str(f.relative_to(ROOT))] = digest(f.read_bytes())
        refs.append(f)
        for b in read(f)['buildings']:
            if b['uid'] in models:
                assert b['uid'] not in forms
                forms[b['uid']] = b
    assert set(forms) == set(models)
    for uid, r in inputs.items():
        assert models[uid] == r['rawCurrentEntry'] and forms[uid] == r['currentBuilding']
        assert digest(assets[uid].read_bytes()) == oldrows[uid]['sourceSHA256'] == r['source']['sha256']
        refs.append(assets[uid])
    def ref(f): return dict(path=str(f.relative_to(ROOT)), sha256=digest(f.read_bytes()))
    for uid in added:
        assert digest(assets[uid].read_bytes()) == models[uid]['sha256'] == installed['sourceSHA256ByUid'][uid]
        refs.append(assets[uid])
    save(out / 'input.json.gz', dict(currentManifest=ref(manifest), currentCatalogueRefs=cats,
        evidenceRefs=[ref(BASE / a.installed / 'result.json'), ref(BASE / a.readback / 'result.json')],
        expectedSourceByUid={u: [models[u]['sha256'], models[u]['triangles']] for u in sorted(added)},
        rows=[dict(uid=u, entry=models[u], building=forms[u], path=str(assets[u].relative_to(ROOT))) for u in sorted(added)]))
    tool = HERE / 'selected_original_render_attributes_v1.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((out / 'input.json.gz').relative_to(ROOT)), str((out / 'attributes.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
    attrs = read(out / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and {r['uid'] for r in attrs['rows']} == added
    rows = list(old['rows'])
    for r in attrs['rows']:
        uid = r['uid']
        assert r['sourceSHA256'] == models[uid]['sha256']
        proof = packed_world_bounds(assets[uid].read_bytes())
        assert proof['allOriginalPositionVerticesAccounted'] and proof['completeOriginalTriangles'] == models[uid]['triangles']
        rows.append(dict(uid=uid, sourceSHA256=r['sourceSHA256'], completeFourWorldBounds=[proof['originalWholeSourceBounds'],
            r['completeLiteralWorldBounds'], r['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],
            r['completeExplicitBalancedFloat32ModelMatrixWorldBounds']], completeOriginalPOSITIONProof=proof))
    assert len(rows) == len(models) == installed['completeCurrentCatalogueModels']
    for name, sha in attrs['inputHashes'].items():
        f = ROOT / name
        assert digest(f.read_bytes()) == sha
        refs.append(f)
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == start
    save(out / 'complete-bounds.json.gz', dict(rows=rows, currentFormTileHashes=tiles, currentManifest=ref(manifest),
        currentNativeActors=len(rows), freshEveryActorActualLoad=False, oldActualRuntimeRowsReused=True,
        unchangedEntryFormAssetAndGeometryModuleProof=True, freshlyLoadedAdditionUids=sorted(added)))
    result = dict(uids=sorted(added), currentNativeActors=len(rows), reusedExactOldActors=len(oldrows),
        sourceSHA256ByUid=installed['sourceSHA256ByUid'], currentManifestSHA256=start,
        installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0,
        qualification='Exact old complete bounds reused only after entry/form/asset/full captured geometry dependency identity; every additive actor freshly loaded. No acceptance transfer.')
    save(out / 'summary.json', result)
    refs.append(tool)
    module('incremental_fresh_bounds_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'verified-additive-current-complete-native-bounds', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()
