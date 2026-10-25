"""Persist completed Dragon diagnostics and actual image inspection, no approval."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

PREFIX = 'government-xl-dragon-after-podium323546-'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = PREFIX + 'progress-v2-20261026'; out = base / batch
    assert not out.exists()
    refs = [Path(__file__)]; completed = []
    for suffix in ['progress-v1', 'private-diagnostic-v2', 'foreign-interface-views-v1', 'compound-clearance-v1', 'original-pair-contacts-v1', 'assembly-identity-context-v1']:
        folder = base / (PREFIX + suffix + '-20261026')
        result, pins = authenticate(folder)
        refs.append(folder / 'result.json')
        completed.append(dict(batch=folder.name, jobId=result['jobId']))
        if suffix in ['foreign-interface-views-v1', 'assembly-identity-context-v1']:
            for name in sorted(folder.glob('*.png')):
                assert digest(name.read_bytes()) == pins[str(name.relative_to(ROOT))]
                refs.append(name)
    current = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(current.read_bytes()) == '8c640bc523e5a2b04cbaaf92362e6679683a5188acea4f0f88fa2863cd976fe7'
    refs.append(current)
    result = dict(uids=['landsd/226794:0', 'landsd/232428:0'], completed=completed,
        currentManifestSHA256=digest(current.read_bytes()), fullXLCounts=dict(total=521, installedVerified=383, remaining=138), currentNativeActors=6962,
        rootInspection=dict(browserV2IndividualImagesOpened=8, sourceBasicInterfaceDiagramsOpened=6, currentAssemblyIdentityDiagramOpened=True,
            observations=['Tower roof and semicircular balcony facade readable; podium lower interfaces remain hidden by neighbouring buildings in browser images.',
                'Mobile podium own views include tower BASIC fallback during recovery. Final joint report confirms both originals active; no joint image was provided or claimed.',
                'Complete mesh diagrams show two low open-sided BASIC structures under/along stepped podium edges, a small high BASIC cuboid at the podium corner, and two external podium boundary interfaces. These observations do not establish common ownership, complete volume containment, suppression permission or collision acceptance.']),
        compoundClearance=dict(allFourModesCapPathsPassed=True, affectedWallFacesPerMode=19, negativeNonWallFacesPerMode=0, allHighestVerticesExposed=False, strictSupportApproved=False),
        exactPairContacts=dict(originalPositivePairs=120, literalPositivePairs=117, float32PositivePairs=120, areaContactPairsAllModes=0, collisionFree=False),
        sourceRecordContext=dict(bothAssemblyCellsExactlyCovered=True, towerOwnCoverage=.9745795133959747, towerAssemblyCoverage=.9936502636441191, podiumCoverage=.9319711113306939, podiumMissingTargetAreaM2=60.87940016581211, rawIndividualFailuresRetained=True, identityApproved=False),
        remainingWork=['Review the exact source-record mismatch and all five external BASIC interface roles using current source identity evidence; distinct official structure IDs must not be turned into shared ownership.',
            'Original pair contacts and all19 compound affected walls now have fresh four-mode evidence, with clear-cap paths passing. Keep strict support59/40 raw failure and highest-vertex false results; no blanket collision-free claim.',
            'If an actual remaining visible conflict needs the prepared10-face original95231, acquire and check it under existing original-source workflow. No evidence yet requires roof97448/97821 suppression or AI geometry modelling.',
            'After bounded source-role/identity/physical review, use guarded qualification, fresh desktop/mobile live installation and independent installed readback; neither source has installation approval. Continue full138 remaining scope, including both null viewer UID source keys.'],
        heldForHumanDecision=False, heldForAIProcessing=False, heldForComputeAndCode=True,
        visualAcceptance=False, physicalAcceptance=False, identityAccepted=False, installationApproved=False,
        publication=False, newlyInstalled=0, sourceGeometryChanges=0, aiGeometryModelling=False, scriptExternalAICalls=0,
        qualification='Completed diagnostics and actually inspected exports, not acceptance. University Hall approval was already fulfilled before this checkpoint; do not reinstall it. All launched producers are terminal with successful Neon receipts; no worker is claimed active. Original-model work remains incomplete, not permanently rejected or blocked.')
    save(out / 'remaining-work.json', result)
    module('dragon_progress_freeze_v2', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'original-source-completed-diagnostics-and-inspected-exports-progress', refs, result)
    print(dict(installedXL=383, unfinishedXL=138, newlyInstalled=0), flush=True)


if __name__ == '__main__':
    main()
