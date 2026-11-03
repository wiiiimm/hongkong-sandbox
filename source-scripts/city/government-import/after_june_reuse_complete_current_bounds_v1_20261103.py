"""Rebind all 7101 current actors to already measured complete source bounds.

The six additions were measured during the full parent-scope investigation;
their provisional status is superseded only by exact installed readback.
No model loading, bounds computation, source acceptance or public-data change.
"""
import copy
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from refresh_fresh_native_bounds_additions_v2_20261102 import complete_inputs

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-after-june-current-native-bounds-reused-v1-20261103'
LOCAL = HERE / 'local' / BATCH
PRIOR = 'government-xl-after-observatory-current-native-bounds-v1-20261102'
SCOPE = 'government-xl-silvercord-lippo-full-current-parent-scope-v3-20261103'
ATTR = 'government-xl-tower3-june-garden-six-originals-current-v1-20261102-attributes'
INSTALLED = 'government-xl-june-garden-original-installed-v4-20261103'
READBACK = 'government-xl-june-garden-installed-root-readback-v3-20261103'


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease) and not (BASE / BATCH).exists()
    out = BASE / BATCH
    refs, pins, receipts = [Path(__file__)], {}, {}

    def take(batch, filename):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    old = take(PRIOR, 'complete-bounds.json.gz')
    old_input = take(PRIOR, 'input.json.gz')
    old_runtime = take(PRIOR, 'inventory.json.gz')
    old_rows = {r['uid']: r for r in old['rows']}
    old_tuples = complete_inputs(old_input['rows'], [], old['rows'])
    assert len(old_rows) == len(old_tuples) == 7095 and old_runtime['wholeUnusedPositionVerticesIncluded']
    assert old_runtime['startAndEndInputHashesVerified'] and not old_runtime['errors']
    measured = take(SCOPE, 'complete-current-actor-bounds.json.gz')['rows']
    attrs = take(ATTR, 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows']) == 6
    installed = take(INSTALLED, 'installed-acceptance.json')
    checked = take(READBACK, 'ROOT-READBACK.json')
    assert checked['installationIndependentlyVerified'] and checked['allOldCatalogueBytesAndEntriesIdentical']
    assert checked['installedJobId'] == receipts[INSTALLED]['jobId'] and checked['snapshotId'] == installed['snapshotId']
    assert checked['oldOriginalAssetsVerified'] == 7095 and checked['completeCurrentCatalogueModels'] == 7101
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest.read_bytes())
    assert manifest_sha == installed['manifest']['sha256'] == pins[SCOPE][str(manifest.relative_to(ROOT))]
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer_sha = digest(pointer.read_bytes())
    assert read(pointer)['snapshotId'] == installed['snapshotId']
    refs += [manifest, pointer]
    # Keep every actual production geometry dependency, while separating
    # additive catalogue/manifest bookkeeping from immutable coordinate data.
    modules = {p: h for p, h in old_runtime['inputHashes'].items() if p.startswith('3d-viewer/') and not p.startswith('3d-viewer/city/data/')}
    modules.update({p: h for p, h in attrs['inputHashes'].items() if p.startswith('3d-viewer/') and not p.startswith('3d-viewer/city/data/')})
    assert '3d-viewer/city/official-model-assets.js' in modules and '3d-viewer/city/geo.js' in modules
    for path, sha in modules.items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    models, assets, catalogues = {}, {}, []

    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[READBACK][str(path.relative_to(ROOT))]
        refs.append(path)
        catalogues.append(ref(path))
        for entry in read(path)['models']:
            assert entry['uid'] not in models
            models[entry['uid']], assets[entry['uid']] = entry, path.parent / entry['asset']
    by = {r['uid']: r for r in measured}
    assert len(by) == len(measured) == len(models) == 7101 and set(by) == set(models)
    added = set(models) - set(old_rows)
    assert added == set(installed['installedUids']) == set(installed['sourceSHA256ByUid']) == {r['uid'] for r in attrs['rows']}
    forms, tiles = {}, {}
    for tile in read(manifest)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        tiles[str(path.relative_to(ROOT))] = digest(path.read_bytes())
        refs.append(path)
        for form in read(path)['buildings']:
            if form['uid'] in models:
                assert form['uid'] not in forms
                forms[form['uid']] = form
    assert set(forms) == set(models)
    fields = ['uid', 'sourceSHA256', 'completeFourWorldBounds', 'completeOriginalPOSITIONProof']
    rows = []
    for uid in sorted(models):
        row = by[uid]
        assert digest(assets[uid].read_bytes()) == models[uid]['sha256'] == row['sourceSHA256']
        assert row['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']
        assert row['completeOriginalPOSITIONProof']['completeOriginalTriangles'] == models[uid]['triangles']
        if uid in old_rows:
            assert all(row[k] == old_rows[uid][k] for k in fields)
            assert models[uid] == old_tuples[uid]['rawCurrentEntry'] and forms[uid] == old_tuples[uid]['currentBuilding']
            assert ref(assets[uid]) == old_tuples[uid]['source']
        else:
            attr = next(r for r in attrs['rows'] if r['uid'] == uid)
            assert attr['sourceSHA256'] == row['sourceSHA256']
            assert row['completeFourWorldBounds'][1:] == [attr['completeLiteralWorldBounds'], attr['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'], attr['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
        refs.append(assets[uid])
        rows.append({k: copy.deepcopy(row[k]) for k in fields})
    tuples = [dict(uid=u, rawCurrentEntry=models[u], currentBuilding=forms[u], source=ref(assets[u])) for u in sorted(models)]
    assert set(complete_inputs(tuples, [], rows)) == set(models)
    save(out / 'complete-bounds.json.gz', dict(rows=rows, currentFormTileHashes=tiles, currentManifest=ref(manifest), currentNativeActors=7101,
         freshEveryActorActualLoad=False, oldActualRuntimeRowsReused=True, unchangedEntryFormAssetAndGeometryModuleProof=True,
         freshlyLoadedAdditionUids=[], previouslyMeasuredExactAdditionUids=sorted(added)))
    save(out / 'input.json.gz', dict(currentManifest=ref(manifest), currentCatalogueRefs=catalogues, currentBoundOnly=True, rows=tuples))
    save(out / 'inventory.json.gz', dict(startAndEndInputHashesVerified=True, errors=[], wholeUnusedPositionVerticesIncluded=True,
         successfullyCapturedActors=7101, freshEveryActorActualLoad=False, oldActualRuntimeRowsReused=True, freshlyLoadedAdditionUids=[],
         previouslyMeasuredExactAdditionUids=sorted(added), inputHashes={**modules, str(manifest.relative_to(ROOT)): manifest_sha},
         qualification='All7101complete current tuples and original/literal/twoFloat32 bounds are authenticated reused measurements. No actor or bounds were recomputed in this rebind. Six prior provisional coordinate measurements now bind exact independently verified installed entries; no acceptance transfer.'))
    assert reservations.owns(lease) and digest(manifest.read_bytes()) == manifest_sha and digest(pointer.read_bytes()) == pointer_sha
    result = dict(uids=sorted(added), currentNativeActors=7101, reusedExactOldActors=7095, reusedPreviouslyMeasuredAdditionActors=6,
                  sourceSHA256ByUid=installed['sourceSHA256ByUid'], currentManifestSHA256=manifest_sha, snapshotId=installed['snapshotId'],
                  newActorLoads=0, newBoundsComputations=0, sourceGeometryChanges=0, installationApproved=False, publication=False,
                  qualification='Chainable complete current inventory after independent June installation verification. Every current catalogue/entry/form/asset and all recorded production geometry dependencies remain bound. All four-stream and unused-original-vertex bounds are copied unchanged from authenticated complete proofs. Diagnostic only; no source reacceptance.')
    save(out / 'summary.json', result)
    refs.append(HERE / 'refresh_fresh_native_bounds_additions_v2_20261102.py')
    module('after_june_reused_bounds_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'verified-additive-complete-native-inventory-reusing-all-exact-coordinate-proofs', list(dict.fromkeys(refs)), result)
    print(dict(currentNativeActors=7101, newActorLoads=0, newBoundsComputations=0), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('after-june-exact-bounds-reuse-' + str(uuid.uuid4()), ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
