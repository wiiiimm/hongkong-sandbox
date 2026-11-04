"""Persist completed exact-source computation and remaining obligations; no approval."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-dragon-next-five-'
    batch = prefix + 'progress-v2-20261026'; out = base / batch; assert not out.exists()
    refs = [Path(__file__)]; completed = []
    folders = sorted(p for p in base.glob(prefix + '*-20261026')
                     if (p / 'neon-sync.json').exists() and (p / 'result.json').exists()
                     and not p.name.startswith(prefix + 'progress-'))
    for folder in folders:
        result, _ = authenticate(folder)
        refs.append(folder / 'result.json')
        completed.append(dict(batch=folder.name, jobId=result['jobId']))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; refs.append(manifest)
    installed = base / 'government-xl-dragon-after-podium323546-three-original-installed-v2-20261026'
    receipt, _ = authenticate(installed); refs.append(installed / 'result.json')
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=384, remaining=137)
    assert digest(manifest.read_bytes()) == receipt['manifest']['sha256']
    names = {'landsd/182397:0':'West Kowloon Government Offices North Tower', 'landsd/203730:0':'Waterfront Tower VI',
             'landsd/215934:0':'Marco Polo Hongkong Hotel', 'landsd/234188:0':'Ocean Centre', 'landsd/30031:0':'Beverly Garden Block 9'}
    next_by_uid = {
        'landsd/182397:0':'Complete native and BASIC scans now finished. Own and wider original terrain still leave35buried/24upward faces. Preserve all source/native272986 and BASIC309340 contacts; inspect actual source roles and a bounded terrain correction before acceptance.',
        'landsd/203730:0':'Exact bounded source identity-only review approved, raw extent failure retained. All4 compound streams retain36negative faces including9real non-wall surfaces, all caused by Elements rather than terrain. Exact diagrams generated. All5strict unresolved witnesses now have shared-original-edge paths to strict anchors with0endpoint overshoot inall4streams. Resolve9nonwall source/native interface roles; no physical or installation approval.',
        'landsd/215934:0':'All38affected current-ground walls have exact clear-cap paths inall4streams. Native and external BASIC contact scans complete, all positives retained. Private retained-native desktop/mobile diagnostic started separately; confirm process/receipt before using exports. Complete exact identity/interface and visual review.',
        'landsd/234188:0':'Adjacent original terrain now covers all10353faces with0burial, resolving50missing faces. Private combined-sheet terrain construction rejects overlapping height surfaces; quantify actual overlapping source planes, preserve native21915 publication hold and all contacts. No source geometry changes or installation credit.',
        'landsd/30031:0':'Native29943 and external BASIC295419 contacts are zero inall4streams. Complete current-ground proof retains6nonwall negatives. Wider original terrain candidate validates at4408faces. Full existing-terrain replacement inset V2 fails terrain-runtime-budget while preserving3retainedtargets/old48726faces. Need bounded retained-surface construction within existing budget checks and full affected-actor regression; no permanent rejection.'}
    result = dict(uids=sorted(names), completed=completed, currentManifestSHA256=digest(manifest.read_bytes()),
        fullXLCounts=dict(total=521,installedVerified=384,remaining=137), currentNativeActors=6965,
        priorInstallation=dict(commit='eab4a76f9', pushed=True, installedJob=receipt['jobId'], snapshot=receipt['snapshotId']),
        rows=[dict(uid=u,name=names[u],nextAction=next_by_uid[u],newlyInstalled=False,permanentRejection=False,heldForHumanDecision=False,heldForAIProcessing=False,heldForComputeAndCode=True)for u in sorted(names)],
        nativeWorker=dict(batch=prefix+'native-contacts-v1-20261026', status='completed',
            jobId='2e42bdaeff76191d51c3a2640bf3e00da207d7c7cc1526472aa2ba4d43511833'),
        nextCommonCommand='Use completed native/foreign receipts and per-source nextAction. Never restart completed native/compound jobs, waive raw negatives or infer corrupted sources from diagnostic failures. Every installed-neighbour metadata hold stays unchanged.',
        sourceRecovered=5, newlyInstalled=0, transferredBytes=0, sourceGeometryChanges=0, aiGeometryModelling=False,
        scriptExternalAICalls=0, installationApproved=False, publication=False,
        qualification='Authenticated completed source phases and explicit remaining obligations; no new installation credit or permanent rejection. Full137 source-key goal, including both null viewer UID keys, remains active. Shared4176 stays down; verify private4177 before use/restart. No optimisation, migration or new AI subagents. Source/evidence interpretation uses AI; scripts make no external AI calls and no AI geometry modelling is used.')
    save(out / 'remaining-work.json', result)
    module('after_dragon_progress_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'current-five-original-source-progress-with-explicit-compute-obligations', refs, result)


if __name__ == '__main__':
    main()
