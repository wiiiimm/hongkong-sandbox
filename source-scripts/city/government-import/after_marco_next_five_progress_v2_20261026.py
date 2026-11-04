"""Persist completed source checks and explicit remaining work; never acceptance."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-after-marco-next-five-'
    batch = prefix + 'progress-v2-20261026'
    out = base / batch
    assert not out.exists()
    refs, completed = [Path(__file__)], []
    for folder in sorted(base.glob(prefix+'*-20261026')):
        if not (folder/'neon-sync.json').exists() or not (folder/'result.json').exists():
            continue
        result, _ = authenticate(folder)
        refs.append(folder/'result.json')
        completed.append(dict(batch=folder.name, jobId=result['jobId']))
    installed = base/'government-xl-marco-polo-original-original-installed-v2-20261026'
    receipt, _ = authenticate(installed)
    counts = dict(total=521, installedVerified=385, remaining=136)
    assert receipt['fullXLCurrentCounts'] == counts and receipt['completeCurrentCatalogueModels'] == 6966
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == receipt['manifest']['sha256']
    refs.extend([installed/'result.json', manifest])
    actions = {
        'landsd/207957:0': 'Strict identity passes. All36rim warnings and all15negative wall centroids have finite strict-root routes/zeroendpointovershoot inall4worlds. Raw15wall negatives/capFALSE retained. Nativefallback205663has0source contacts inall4worlds (before337positive). Existing source/podium preview inspected in prior continuation. Need bounded wall-role/support physical review and exact supported installation path; not installed.',
        'landsd/213579:0': 'All4complete ground streams pass clear-cap paths for20walls/0nonwalls. Privatebrowser desktop/mobile passes/released; ROOTopened4individualdaynightPNGs plus source plan/perspectives and BASIC71329context diagram. Source is visible with no proceduralwindows; podium conceals lower interface and redcontact lines are not legible enough for visual contact acceptance. Need bounded source14.36mextent/unrelated57855 and all54retainedBASIC71329 contact review. No source-role/identity/installation approval yet.',
        'landsd/265301:0': 'Authentic terrain covers10826faces/0burial. Complete saved candidate125711faces exceeds25kbudget;1805positive-area overlaps,638with floatmeasuredheightdifference>.01m,maximum9.5095m. Measurements diagnostic only, not rational plane proof/sourcecorruption. Need source-plane/return-region construction and exact terrain budget solution; cannot simple duplicate cleanup.95forms remain.',
        'landsd/296699:0': 'Currentground completeclearance has859affectedfaces/163nonwalls ineach4world,capFALSE. Fresh boundterrain revision covers10683faces/0burial;469face rootcandidate passes existing highest-surface validator withunchangedmesh. Rootscope finds one containingcurrenthierarchicalgroup,0touchingnativeactors,7forms. Retainedgroup-v2 passes canonicalvalidation and exact14oldchildren/375789gridnodes retention. Privateactualrenderer has0burial/minGap-.009m;complete4worldclearance has0affectedfaces (rawcapFALSE withnoaffected retained). All5402groupforms pass/0flags. All6966installedassets and10BASICsupports exactchanged-region separation passes/0affected. Private desktop/mobile browser passes/released;ROOTopened4individualexports plus contactdiagram. Exact source-specific review binds originalroot/officialCSUID/cell and21.053mplatformextent, all10platform-wall contacts preserved with97556retained. Confirm ferry-source-review-v1 completed receipt; next guarded exactsingle-source hierarchical qualification/installer and freshlive verification, thencommitpushinstallation. Do not silentlyreuse podium323546 exact3source publisher or reapproveoldnatives. Failedv1source lookup preserved; no oldterrainapprovaltransfer. No installation.',
        'landsd/336667:0': 'All4complete groundstreams have17negativewalls/0nonwalls,clear-cap paths pass. ROOTinspectedsourceplan/perspectives: north end ofredfootprint extends wellbeyond source mesh. Coverage/cell identity warnings remain real investigation, not corruption. Need exactmissingcompanion source coverage and BASIC336671322contacts; both nearby nativecontacts0all4 preserved.'}
    selection = read(base/(prefix+'ground-v1-20261026')/'selection.json.gz')
    assert {r['uid'] for r in selection['rows']} == set(actions)
    result = dict(uids=sorted(actions), completed=completed, fullXLCounts=counts,
        currentNativeActors=6966, currentManifestSHA256=digest(manifest.read_bytes()),
        priorInstalledCommit='b0adf0f33', priorInstalledJobId=receipt['jobId'],
        rows=[dict(uid=r['uid'], name=r['source']['building'].get('name'), sourceSHA256=r['sourceSHA256'],
                   completeSourceFaces=r['triangles'], status='In process', execution='queued',
                   nextAction=actions[r['uid']], permanentRejection=False, requiresHumanDecision=False,
                   requiresAIGeometryModelling=False, remainingWorkUsesComputeAndCode=True)
              for r in selection['rows']],
        workers=[], newlyInstalled=0, publication=False, installationApproved=False,
        sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
        scriptExternalAICalls=0,
        qualification='Every referenced worker is terminal with an authenticated completed receipt. Queued continuation is not a live worker claim or a final hold. All136unfinished source keys, including2null viewerUIDs, remain in scope. No new installation, source rejection, optimisation or geometry modelling credit.')
    result['failedAttempts']=[dict(batch=prefix+'ferry-original-terrain-v1-20261026',terminal=True,reason='Pinned source revision changed; new revision separately acquired and hash-bound in v2, no old approval transferred'),dict(batch=prefix+'ferry-retained-group-v1-20261026',terminal=True,reason='Legacy verifier rejects prior scriptedOriginalChildExtension metadata. V2 preserves exact previous extension provenance chain;10tests pass. V1 did not publish or receive an acceptance receipt.')]
    result['failedAttempts'] += [dict(batch=prefix+n+'-20261026',terminal=True,reason='Legacy helper rejected prior extension provenance before useful runtime/scope completion. Subsequent version uses the tested exact-provenance V2 helper; original source and live terrain unchanged.') for n in ['ferry-group-runtime-v1','ferry-group-scope-v1']]
    observations=[]
    for uid in ['213579','336667','296699']:
        for filename in ['whole-source-plan.png','whole-source-perspectives.png']:
            path=base/(prefix+uid+'-identity-plots-v1-20261026')/filename
            refs.append(path);observations.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyOpenedByROOT=True,acceptance=False))
    path=base/(prefix+'pok-oi-basic71329-views-v1-20261026')/'before-after-contact-context.png'
    refs.append(path);observations.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyOpenedByROOT=True,acceptance=False,limitation='Low interface clipped views show retainedBASIC; redcontacts not sufficiently legible for visual interface acceptance.'))
    for width in [1280,390]:
        for time in ['1500','2200']:
            path=base/(prefix+'pok-oi-private-preview-v1-20261026')/str(width)/('staged-landsd-213579-0-'+str(width)+'-'+time+'-canvas.png')
            refs.append(path);observations.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyOpenedByROOT=True,acceptance=False,observation='Original hospital roof/facades visible; grey day/dark night; low interface partly concealed by retainedpodium.'))
    save(out/'ROOT-OBSERVATIONS.json',dict(images=observations,visualAcceptance=False,identityAccepted=False,physicalAcceptance=False))
    for width in [1280,390]:
        for time in ['1500','2200']:
            path=base/(prefix+'ferry-private-preview-v1-20261026')/str(width)/('staged-landsd-296699-0-'+str(width)+'-'+time+'-canvas.png')
            refs.append(path);observations.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyOpenedByROOT=True,acceptance=False,observation='Terminal roof/controltower/platform readable; foregroundtower partly conceals lowerfacade onmobile. Source grey/day,dark/night,no proceduralwindows.'))
    path=base/(prefix+'ferry-basic97556-views-v1-20261026')/'before-after-contact-context.png'
    refs.append(path);observations.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),actuallyOpenedByROOT=True,acceptance=False))
    save(out/'ROOT-OBSERVATIONS.json',dict(images=observations,visualAcceptance=False,identityAccepted=False,physicalAcceptance=False))
    result['rootInspectedImages']=len(observations)
    result['verificationTests']=dict(strictRootAdversarialTestsPassed=4,hierarchicalRetentionTestsPassed=10)
    for name in ['hierarchical_original_terrain_binding_v2_20261026.py','test_hierarchical_original_terrain_binding_v2_20261026.py','test_original_face_attachment_minimax_v2_20261024.py','selected_original_retained_group_child_v1_20261026.py']:
        refs.append(HERE/name)
    save(out/'remaining-work.json', result)
    module('after_marco_progress_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'current-five-original-compute-progress-with-full-xl-scope-preserved', refs, result)


if __name__ == '__main__':
    main()
