"""Persist complete Hanford source recovery and actionable current-scene findings."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-hanford-ten-original-'
BATCH=P+'progress-checkpoint-v1-20261024'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(batch,file='summary.json'):
        if batch not in pins:
            result,pins[batch]=authenticate(BASE/batch);jobs[batch]=result['jobId'];refs.append(BASE/batch/'result.json')
        path=BASE/batch/file;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def summary(s):return take(P+s+'-20261024')
    selection=take(P+'current-runtime-v1-20261024','selection.json.gz')
    sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==10 and sum(r['triangles']for r in selection['rows'])==28973
    acq='government-xl-next-repairs-hanford-seven-original-companions-v1-20261024';seven=take(acq,'selection.json.gz');assert len(seven['rows'])==7 and not seven['missing']and all(r['sourceSHA256']==sources[r['uid']]for r in seven['rows'])
    tower2='government-xl-next-repairs-hanford-tower2-original-recovery-v1-20261024';extra=take(tower2,'selection.json.gz');assert len(extra['rows'])==1 and extra['rows'][0]['sourceSHA256']==sources['landsd/194247:0']and extra['rows'][0]['recovery']['transferredBytes']==0
    runtime=summary('current-runtime-v1');identity=summary('current-identity-v1')
    take(P+'current-attributes-v1-20261024','attributes.json.gz')
    scope=summary('current-model-scope-v1');assert all(r['currentNativeActorsChecked']==6884 and not r['nearbyNativeActors']for r in scope['rows'])
    pairs=summary('all-pair-context-v1');assert pairs['completeUnorderedPairs']==45 and len(pairs['rows'])==180 and pairs['sourceSHA256ByUid']==sources
    foreign=summary('current-basic-contacts-v1');assert foreign['foreignPairs']==29
    assert all(not m['positiveContactPairs']for r in foreign['rows']if r['foreignUid']not in sources for m in r['modes']if m['mode']!='before-basic')
    summary('current-buried-context-v1')
    support=summary('support-followthrough-v1');assert support['nominatedPairs']==8 and all(r['allUnresolvedHaveFinitePaths']and not r['dependencyAdopted']for r in support['rows'])
    paths=sum(r['pathCounts'][0]['targets']for r in support['rows']);assert paths==872
    terrain=summary('primary-original-terrain-check-v1');assert len(terrain['rows'])==1 and terrain['rows'][0]['originalTerrainFoundation']['fullyBuriedTriangles']==terrain['rows'][0]['originalTerrainFoundation']['fullyBuriedUpwardTriangles']==0
    inset=summary('primary-buried-upward-inset-v1');assert inset['status']=='bounded-inset-investigation'and inset['reason']=='native-terrain-near-water-clamp'and not inset['permanentRejection']
    low=summary('low-parent-context-v1');assert low['lowParentFaces']==3 and low['lowParentRegionInsideOuterAreaM2']>0
    yawname='government-xl-next-repairs-hanford-194725-original-yaw-context-v1-20261024';yaw=take(yawname,'proof.json');assert yaw['sourceBoundRootFramePassed']and yaw['completeNativeBoundsErrorM']==0 and yaw['sourceGeometryChanges']==yaw['sourcePoseChanges']==0
    flagged=[dict(uid=r['uid'],rawReasonsRetained=r['reasons'])for r in identity['rows']if not r['passed']];assert len(flagged)==4
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifestSHA256=selection['manifestSHA256'],completedJobs=jobs,
        fixedXLTotal=521,fixedXLInstalled=349,fixedXLRemaining=172,currentNativeActors=6884,newlyInstalled=0,completeOriginalFaces=28973,
        recoveredPreviouslyMissingOriginals=7,sourceAccessResolved=True,sourceAccessBlocked=False,
        completeOriginalPairs=45,coordinateModes=4,completeCurrentBasicPairs=29,externalPositiveBasicPairs=0,nearbyInstalledDetailedActors=0,
        originalSupportAlternatives=8,allOriginalSupportAlternativesHaveFinitePaths=True,verifiedUnresolvedRimsAcrossAlternativesPerWorld=872,
        rawIdentityPassed=6,identityInvestigations=flagged,sourceGeometryChanges=0,sourcePoseChanges=0,terrainPublished=False,
        requiresHumanDecision=False,requiresExternalAccess=False,requiresAIGeometry=False,humanState='Held for further processing',
        remaining=[
            'Preserve the four raw footprint/cell flags; exact-current component routes are positive. Block4original unit yaw is proved with zero native-bounds error, but its footprint coverage remains unresolved. Inspect source-owned geometry/cell and authored compound evidence; do not silently lower coverage thresholds.',
            'Complete a bounded terrain method that preserves current coastal ground. Narrow upward-face inset failed while constructing its current-parent template, before processing original TIN contributions. Three existing parent triangles below1.2m overlap88.728584m2of the proposed outer return; this is not solely irrelevant terrain outside the correction. Preserve the failure and final height/coverage/coastal nonregression gates.',
            'Bind compatible original terrain provenance for secondarypodium203884native revision1b11e832430ab48243b86144e2d02db90654abc345db26d9689ddbc8c7ccb675; the current compatible donor covers primary276187revisionfebfb538795f9daf04b53b42edbb17d79f18779d29c12033eaf71903435db970. Existing exactTINfor6-SW-11B is available locally but needs revision binding rather than assumed approval.',
            'After terrain/identity qualification, validate complete four-world actual-ground foundations, remaining exposed wall/cap roles, original support graph and all current neighbours for all10 actors. Tower2has alternatives to203884and276187; none is adopted automatically. Then staged/live desktop/mobile visual/picking/collision/failure-retry and guarded installation/readback are still required.'
        ],qualification='Fresh complete source/geometry/contact/support diagnostics and actionable remaining work only. No new Hanford source is installed, physically approved or permanently rejected. GardenTerrace already installed/pushedb73657845; full172unfinishedobjective remains active. Code/source evidence interpretation used AI; geometry acquisition/conversion/diagnostics used scripts with zero external AI calls.')
    save(out/'remaining-work.json',result)
    refs.extend(HERE/n for n in ['acquire_current_original_sources_v1_20261024.py','hanford_seven_original_companions_acquire_v1_20261024.py','original_source_unit_yaw_context_v1_20261024.py','original_assembly_four_world_pair_context_v2_20261024.py','original_assembly_support_followthrough_v1_20261024.py','original_inset_low_parent_context_v1_20261024.py'])
    module('hanford_ten_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-hanford-original-recovery-current-diagnostics-and-actionable-holds',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
