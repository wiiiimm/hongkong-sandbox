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

def complete_inputs(full_rows, additions, bounds):
    """Require an exact actor census; legacy additions cannot overwrite rows."""
    rows={}
    for row in full_rows:
        uid=row['uid'];assert uid not in rows
        assert set(['rawCurrentEntry','currentBuilding','source'])<=set(row)
        rows[uid]=row
    for row in additions:
        uid=row['uid'];assert uid not in rows,'Conflicting/repeated actor in incremental chain'
        rows[uid]=dict(uid=uid,rawCurrentEntry=row['entry'],currentBuilding=row['building'],
            source=dict(path=row['path'],sha256=row['entry']['sha256']))
    expected={r['uid']:r for r in bounds};assert len(expected)==len(bounds)and set(rows)==set(expected),'Incomplete bounds/input actor census'
    for uid,r in rows.items():
        assert uid==r['rawCurrentEntry']['uid']==r['currentBuilding']['uid']
        assert r['source']['sha256']==r['rawCurrentEntry']['sha256']==expected[uid]['sourceSHA256']
    return rows


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
    runtime_path=BASE/a.prior/'inventory.json.gz'
    if runtime_path.exists():
        oldruntime=take(a.prior,'inventory.json.gz')
        assert oldinput['currentBoundOnly']
        inputs=complete_inputs(oldinput['rows'],[],old['rows'])
    else:
        # V1 produced only the additions' renderer input, not a full inventory
        # input. Recover the authenticated original full capture from its own
        # evidence refs and merge only V1's independently loaded additions.
        candidates=[path for path in pins[a.prior]if path.endswith('/inventory.json.gz')]
        assert len(candidates)==1,'Legacy incremental input requires one exact full-capture ancestor'
        runtime_path=ROOT/candidates[0]
        assert digest(runtime_path.read_bytes())==pins[a.prior][candidates[0]]
        refs.append(runtime_path);oldruntime=read(runtime_path)
        ancestor=runtime_path.with_name('input.json.gz')
        assert digest(ancestor.read_bytes())==pins[a.prior][str(ancestor.relative_to(ROOT))]
        refs.append(ancestor);full=read(ancestor)
        assert full['currentBoundOnly']and oldruntime['successfullyCapturedActors']==len(full['rows'])
        assert oldinput['currentManifest']==old['currentManifest']
        inputs=complete_inputs(full['rows'],oldinput['rows'],old['rows'])
    assert oldruntime['startAndEndInputHashesVerified'] and not oldruntime['errors']
    assert oldruntime['wholeUnusedPositionVerticesIncluded']
    assert len(inputs)==len(old['rows'])
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
    # recorded by the authenticated full production exporter, rather than inventing a pin.
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
    save(out / 'addition-input.json.gz', dict(currentManifest=ref(manifest), currentCatalogueRefs=cats,
        evidenceRefs=[ref(BASE / a.installed / 'result.json'), ref(BASE / a.readback / 'result.json')],
        expectedSourceByUid={u: [models[u]['sha256'], models[u]['triangles']] for u in sorted(added)},
        rows=[dict(uid=u, entry=models[u], building=forms[u], path=str(assets[u].relative_to(ROOT))) for u in sorted(added)]))
    tool = HERE / 'selected_original_render_attributes_v1.mjs'
    with (out / 'worker.log').open('w') as log:
        subprocess.run(['node', str(tool), str((out / 'addition-input.json.gz').relative_to(ROOT)), str((out / 'attributes.json.gz').relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
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
    # Persist complete current tuples and dependency provenance, so the next
    # additive installation does not need to reconstruct the legacy chain.
    complete=[dict(uid=u,rawCurrentEntry=models[u],currentBuilding=forms[u],source=ref(assets[u]))for u in sorted(models)]
    assert set(complete_inputs(complete,[],rows))==set(models)
    save(out/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=cats,currentBoundOnly=True,rows=complete))
    save(out/'inventory.json.gz',dict(startAndEndInputHashesVerified=True,errors=[],wholeUnusedPositionVerticesIncluded=True,
        successfullyCapturedActors=len(models),freshEveryActorActualLoad=False,oldActualRuntimeRowsReused=True,
        freshlyLoadedAdditionUids=sorted(added),inputHashes={**modules,str(manifest.relative_to(ROOT)):start},
        qualification='The legacy actor-count field includes authenticated reused measurements; only declared additions were loaded again. All complete entry/form/source inputs and every recorded production geometry dependency are checked.'))
    for f in [out/'input.json.gz',out/'inventory.json.gz',out/'addition-input.json.gz']:refs.append(f)
    result = dict(uids=sorted(added), currentNativeActors=len(rows), reusedExactOldActors=len(oldrows),
        sourceSHA256ByUid=installed['sourceSHA256ByUid'], currentManifestSHA256=start,
        installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0,
        qualification='Chainable full current input schema. Exact old complete bounds reused only after entry/form/asset/full captured geometry dependency identity; every additive actor freshly loaded. No acceptance transfer.')
    save(out / 'summary.json', result)
    refs.append(tool)
    module('incremental_fresh_bounds_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'verified-additive-current-complete-native-bounds', list(dict.fromkeys(refs)), result)

if __name__ == '__main__':
    main()
