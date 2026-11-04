"""Persist current A/D diagnostics and exact actionable work after F/E installation."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-beverly-ad-after-fe-progress-v1-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins, completed = [Path(__file__)], {}, []

    def take(batch, name):
        if batch not in pins:
            receipt, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
            completed.append(dict(batch=batch, jobId=receipt['jobId']))
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    prefix = 'government-xl-beverly-ad-after-fe-'
    selection = take(prefix + 'runtime-v1-20261025', 'selection.json.gz')
    take(prefix + 'selection-v1-20261025', 'summary.json')
    take(prefix + 'attributes-v1-20261025', 'attributes.json.gz')
    identity = take(prefix + 'identity-v1-20261025', 'summary.json')
    scope = take(prefix + 'model-scope-v1-20261025', 'summary.json')
    take(prefix + 'continuous-v1-20261025', 'summary.json')
    primary = take(prefix + 'primary-records-v1-20261025', 'summary.json')
    native = take(prefix + 'native-contacts-v1-20261025', 'summary.json')
    fallback = take(prefix + 'native-fallback-contacts-v1-20261025', 'summary.json')
    assert {r['uid']: r['passed'] for r in identity['rows']} == {'landsd/255539:0': True, 'landsd/255541:0': False}
    assert not primary['missingRequestedCSUIDs']
    assert all(r['currentNativeActorsChecked'] == 6957 for r in scope['rows'])
    ab = next(r for r in native['rows'] if r['uid'] == 'landsd/255539:0' and r['nativeUid'] == 'landsd/256136:0')
    assert all(m['finiteContactPairs'] == 35 and m['areaContactPairs'] == 5 for m in ab['modes'])
    assert ab['rawCurrentNativeEntry']['publicationApproved'] is False
    assert ab['rawCurrentNativeEntry']['label'] == 'Beverly Hill Block B'
    fb = next(r for r in fallback['rows'] if r['uid'] == 'landsd/255539:0' and r['nativeFallbackUid'] == 'landsd/256136:0')
    assert all(m['finiteContactPairs'] == 13 for m in fb['modes'] if m['mode'] != 'before-basic')
    assert all(m['finiteContactPairs'] == 0 for r in fallback['rows'] if r != fb for m in r['modes'] if m['mode'] != 'before-basic')
    images = []
    for uid in ['255539', '255541']:
        batch = 'government-xl-beverly-' + uid + '-after-fe-source-views-v1-20261025'
        take(batch, 'summary.json')
        for filename in ['whole-source-plan.png', 'whole-source-perspectives.png']:
            path = BASE / batch / filename
            assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
            refs.append(path)
            images.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    installed = 'government-xl-beverly-fe-finite-original-original-installed-v2-20261025'
    receipt, _ = authenticate(BASE / installed)
    refs.append(BASE / installed / 'result.json')
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=380, remaining=141)
    assert receipt['completeCurrentCatalogueModels'] == 6957
    exact = take('government-xl-after-beverly-fe-unfinished-exact-source-inventory-v1-20261025', 'summary.json')
    assert exact['unfinished'] == 141 and exact['unmatchedViewerUIDs'] == 2
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256']
    refs.append(manifest)
    result = dict(
        uids=['landsd/255539:0', 'landsd/255541:0'], currentManifestSHA256=selection['manifestSHA256'],
        installedXL=380, unfinishedXL=141, totalFixedXL=521, currentNativeActors=6957,
        newlyInstalled=0, installationApproved=False, publication=False, physicalAcceptance=False,
        sourceGeometryChanges=0, aiGeometryModelling=False, humanDecisionRequired=False,
        state='held-for-compute', completed=completed, sourceDiagramsActuallyViewedByRoot=images,
        sourceObservation='ROOT opened both individual plan and perspective diagrams for A and D. Both show complete coherent tower bodies, roofs and repeating facade details. D has visible outline differences, including low appendages and a northern footprint strip; these diagnostic diagrams do not alone prove exact architectural roles, identity acceptance or browser suitability.',
        rawFailuresPreserved=[
            'D generic identity still fails targetCoveredBySourceProjection/full-source-target-coverage at 0.9342413622267347; exact CSUID/stable ID/GeoRef cell routing remains separate, not an invented generic pass.',
            'A versus exact native B256136 has35 finite contacts, including5 tiny area pairs, in all4 worlds. Its13 contacts with B BASIC fallback require explicit availability ordering and source/native role review.',
            'Native B publicationApproved:false is retained unchanged and not reapproved. Older A/E256136 labels were wrong; this UID is Block B.',
            'Prior canonical support failures remain false. Prior40 A/196 D finite roof paths must be rebound to exact current source/ground/support arrays or independently recomputed before admission.',
        ],
        remainingWork=[
            'A: review exact35 native B contacts/5 roof patches. Require A->B exact SHA/CSUID availability metadata because B BASIC fallback has13 contacts. Preserve B held flags/bytes. Test deliberate B failure keeps A own BASIC and inspect source plus both retained native views on desktop/mobile.',
            'D: source-role investigation of full original versus exact primary footprint, including missing northern outline strip and29.965553m2 source excess; keep93.424% coverage failure explicit. D versus both detailed and BASIC neighbour255544 has0 contacts in all4 worlds; unrelated70279 current source contacts remain a separate fresh check.',
            'Bind current support/continuous/source numerical inputs before reusing prior finite paths. Use a distinct tested finiteV2/native-aware admission; old K one-source V1 contract and old canonical guards remain frozen. Do not mislabel raw no-vertical-support as canonical pass.',
            'Complete fresh foreign-BASIC, source/native role and actual private browser inspection before any physical/publication qualification. Then commit/push qualification, guarded install, inspect fresh live exports/full6957oldassets/521/globalBASIC+manifest readback, refresh inventory and commit/push.',
            'Keep P233218 BASIC/unsuppressed for installedK/F/E and future dependants. Preserve both null-UID source keys. No geometry modelling, optimisation, shared4176 restart or main merge.',
        ],
        installedCommit='7823c5ded', trackerCommentId='e821f44b-478c-47bb-afe5-3562a95b7e88')
    save(out / 'remaining-work.json', result)
    module('beverly_ad_progress_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'current-beverly-ad-source-native-and-fallback-actionable-holds', list(dict.fromkeys(refs)), result)
    print(dict(completed=len(completed), state=result['state'], newlyInstalled=0), flush=True)


if __name__ == '__main__':
    main()
