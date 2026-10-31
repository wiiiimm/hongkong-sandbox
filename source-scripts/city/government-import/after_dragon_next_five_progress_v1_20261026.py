"""Persist completed exact-source computation and remaining obligations; no approval."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-dragon-next-five-'
    batch = prefix + 'progress-v1-20261026'; out = base / batch; assert not out.exists()
    suffixes = ['acquire-v1','ground-v1','attributes-v1','identity-v1','primary-v1','scope-v1','directories-v1',
                'west-kowloon-terrain-v1','ocean-centre-terrain-v1','203730-foundation-v1','215934-foundation-v1','30031-foundation-v1']
    refs = [Path(__file__), HERE / 'acquire_explicit_current_originals_v1_20261026.py']; completed = []
    for suffix in suffixes:
        folder = base / (prefix + suffix + '-20261026'); result, _ = authenticate(folder)
        refs.append(folder / 'result.json'); completed.append(dict(batch=folder.name, jobId=result['jobId']))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'; refs.append(manifest)
    installed = base / 'government-xl-dragon-after-podium323546-three-original-installed-v2-20261026'
    receipt, _ = authenticate(installed); refs.append(installed / 'result.json')
    assert receipt['fullXLCurrentCounts'] == dict(total=521, installedVerified=384, remaining=137)
    assert digest(manifest.read_bytes()) == receipt['manifest']['sha256']
    names = {'landsd/182397:0':'West Kowloon Government Offices North Tower', 'landsd/203730:0':'Waterfront Tower VI',
             'landsd/215934:0':'Marco Polo Hongkong Hotel', 'landsd/234188:0':'Ocean Centre', 'landsd/30031:0':'Beverly Garden Block 9'}
    next_by_uid = {
        'landsd/182397:0':'Current ground buries370faces/232upward; pinned original terrain reduces this to35faces/24upward, all buried component centroids outside the recorded target. Need bounded source/terrain-role and full source-neighbour review, not source edits or automatic rejection.',
        'landsd/203730:0':'All four foundations pass with0buried faces; raw extent identity warnings remain. Exact native scan against installed273061 has203738nativefaces; original mode found5620finite/482positive/4area contacts. Await remaining representations and retain every contact for support/interface review.',
        'landsd/215934:0':'All four foundations pass with0buried faces. Four installed native candidates; preserve extent/unrelated-overlap identity warnings. Await complete native scan, then full foreign BASIC and source-role review.',
        'landsd/234188:0':'Current ground buries17faces/13upward. Exact original terrain has0burial but covers10303/10353faces; remaining50require complete coverage resolution. Two installed native candidates, unrelated-overlap identity warning; no installation approval.',
        'landsd/30031:0':'Strict identity and established four-mode foundation policy pass. Four tiny buried wall faces,0upward; raw warnings kept. One installed native29943 needs full finite/context/dependency checks; cannot skip it.'}
    result = dict(uids=sorted(names), completed=completed, currentManifestSHA256=digest(manifest.read_bytes()),
        fullXLCounts=dict(total=521,installedVerified=384,remaining=137), currentNativeActors=6965,
        priorInstallation=dict(commit='eab4a76f9', pushed=True, installedJob=receipt['jobId'], snapshot=receipt['snapshotId']),
        rows=[dict(uid=u,name=names[u],nextAction=next_by_uid[u],newlyInstalled=False,permanentRejection=False,heldForHumanDecision=False,heldForAIProcessing=False,heldForComputeAndCode=True)for u in sorted(names)],
        nativeWorker=dict(batch=prefix+'native-contacts-v1-20261026',execSession=85336,pidObservedLiveByROOT=1464810,
            observed='Worker is computing, not stalled: ROOT observed CPU activity and newly emitted Waterfront original-mode contact results. Poll the same handle/PID before any restart; observation timeout is not termination.'),
        nextCommonCommand='After native worker is terminal with a successful authenticated receipt, run selected_original_model_only_foreign_contacts_v3_20261024.py with --native-contacts government-xl-after-dragon-next-five-native-contacts-v1-20261026, the current five-scope/runtime/attributes batches, and a new --batch. Preserve all positives and installed metadata; original terrain recovery is private evidence, not a published patch.',
        sourceRecovered=5, newlyInstalled=0, transferredBytes=0, sourceGeometryChanges=0, aiGeometryModelling=False,
        scriptExternalAICalls=0, installationApproved=False, publication=False,
        qualification='Twelve completed script phases and explicit remaining source obligations, no new installation credit or permanent rejection. Full137 source-key goal, including both null viewer UID keys, remains active. Shared4176 stays down; private4177 execsession18777 must be checked live before use/restart. No optimisation, migration or new AI subagents.')
    save(out / 'remaining-work.json', result)
    module('after_dragon_progress_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'current-five-original-source-progress-with-explicit-compute-obligations', refs, result)


if __name__ == '__main__':
    main()
