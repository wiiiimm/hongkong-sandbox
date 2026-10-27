"""Record bounded current-source non-installability after original-only recovery.

This closes the unchanged-source route, not every possible future source revision
or separately authorised repair. No installed review or inventory row is changed.
"""
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-current-source-gap-disposition-v1-20261028'
DOC = BASE/BATCH
PREFIX = 'government-xl-southside-'
INPUTS = ['original-gap-sections-v1', 'original-support-proximity-graph-v2',
          'source-gap-provenance-v1', 'raw-source-pose-parity-v1',
          'project-original-recovery-v1', 'project-original-rim-contacts-v1']
INVENTORY = BASE/'government-xl-after-north-pair-unfinished-exact-source-inventory-v1-20261028'
TARGETS = ['landsd/311759:0', 'landsd/311763:0', 'landsd/330243:0', 'landsd/330244:0']


def main():
    assert not DOC.exists()
    refs, pins, results = [Path(__file__)], {}, {}
    for name in INPUTS:
        directory = BASE/(PREFIX+name+'-20261028')
        result, bound = authenticate(directory)
        results[name] = result
        refs.append(directory/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
    inventory, bound = authenticate(INVENTORY)
    refs.append(INVENTORY/'result.json')
    for path, sha in bound.items():
        assert path not in pins or pins[path] == sha
        pins[path] = sha

    def take(name, filename):
        path = BASE/(PREFIX+name+'-20261028')/filename
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    graph = take('original-support-proximity-graph-v2', 'summary.json')
    sections = take('original-gap-sections-v1', 'summary.json')
    selection = take('project-original-recovery-v1', 'selection.json.gz')['rows']
    rims = take('project-original-rim-contacts-v1', 'contacts.json.gz')['rows']
    fixed = {r['uid']: r for r in inventory['rows'] if r['uid'] in TARGETS}
    assert set(fixed) == set(TARGETS[:3])
    assert {r['uid'] for r in graph['targets']} == set(TARGETS)
    assert all(not r['optimisticPathToAssumedRoot'] and not r['reachableUnknownSourceUnits'] for r in graph['targets'])
    image = ROOT/sections['image']['path']
    assert digest(image.read_bytes()) == sections['image']['sha256']
    refs.append(image)
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest_path.read_bytes()) == inventory['currentManifestSHA256']
    refs.append(manifest_path)
    installed = set()
    for url in read(manifest_path)['officialModelCatalogues']:
        path = ROOT/'3d-viewer'/url
        refs.append(path)
        installed.update(r['uid'] for r in read(path)['models'])
    assert not installed.intersection(TARGETS)
    records = []
    for uid in TARGETS:
        selected = next(r for r in selection if r['uid'] == uid)
        source_key = selected['native']['cacheKey']+'/'+selected['modelId']
        if uid in fixed:
            assert fixed[uid]['sourceKey'] == source_key
        source_sha = selected['sourceSHA256']
        assert sections['originalSourceHashes'][uid] == source_sha
        path = ROOT/selected['candidate']['path']
        assert digest(path.read_bytes()) == source_sha
        refs.append(path)
        rim = next(r for r in rims if r['uid'] == uid)
        assert rim['stillUnresolved'] == rim['samples'] and rim['samples'] > 0
        records.append(dict(uid=uid, sourceKey=source_key, sourceSHA256=source_sha,
            inFixedXLScope=uid in fixed,
            disposition='not-installable-as-unchanged-current-source',
            humanStatus='not-installable-current-source',
            reason='Complete original tower has no qualifying support path to the original podium or private source-bound ground; nearby indexed original building and infrastructure recovery did not bridge the gap.',
            scope='Exact packed original revision at fixed 1x source pose under the existing original-only installation policy.',
            rawUnresolvedRimSamples=rim['stillUnresolved'],
            exactDiagnosticRadiusM=graph['diagnosticRadiusM'],
            originalSourceCorruption=False, permanentRejection=False,
            automaticRetryWithoutChangedEvidence=False,
            requiresHumanDecision=False, requiresAIProcessing=False,
            furtherUnchangedComputeCanInstall=False,
            retainCurrentModel=True, installationApproved=False,
            revisitTrigger='An authenticated provider revision or additional original supporting geometry spanning the documented gap; alternatively a separately authorised geometry repair. A changed source requires fresh identity/physical/current-neighbour/runtime/browser acceptance. Do not repeat unchanged source acquisition, move the tower, invent support, widen tolerances or claim a possible future source is impossible.'))
    claim = reservations.claim('southside-current-source-disposition-'+str(uuid.uuid4()),
        sorted(['building:'+uid for uid in TARGETS]+['native-model:'+r['sourceKey'] for r in records]),
        batch=BATCH, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        # The source-only image was actually opened and inspected by root before
        # preparing this review: all eight sections show separated tower/podium.
        review = dict(reviewer='Codex root', evidenceImage=sections['image'],
            reviewedPanels=8, sourceIdentityOrStructuralAcceptanceGranted=False,
            observation='All eight displayed sections show original tower geometry above the podium. The plotted maximal sampled gaps are 8.828, 8.114, 13.447 and 8.663 metres. This visual corroboration is bounded to its section planes; the separately bound full-original exact proximity graph supplies the complete negative test.',
            aiUse='Evidence interpretation and code only; no geometry modelling.')
        summary = dict(uids=TARGETS, rows=records, visualReview=review,
            fixedXLCurrentSourceDispositions=3, auxiliarySourceDispositions=1,
            installedFixedXL=inventory['installed'], nonInstalledFixedXL=inventory['unfinished'], fixedXLTotal=inventory['fixedXLTotal'],
            globalBacklogRecountPerformed=False, allOtherXLDispositionsUnchanged=True,
            sourceGeometryChanges=0, publication=False, newlyInstalled=0,
            qualification='Bounded final disposition for this unchanged original-source route. Not corruption, not permanent rejection of every future revision, not approval for geometry repair, and not closure of the whole XL backlog. Existing catalogue/review/snapshot rows remain untouched.')
        save(DOC/'summary.json', summary)
        assert reservations.owns(lease)
        module('southside_gap_disposition_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'current-original-source-no-support-installability-disposition', list(dict.fromkeys(refs)), summary)
        print(dict(fixedXLCurrentSourceDispositions=3, auxiliary=1, newlyInstalled=0), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
