"""Archive current four-source evidence, corrected setup failure and next actions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-four-after-hanford-';BATCH=P+'progress-checkpoint-v1-20261024'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];jobs={};records={}
    names=[P+s+'-20261024'for s in ['selection-v1','runtime-v1','identity-v1','attributes-v1','model-scope-v1','native-contacts-v2']]
    names +=[P+u+'-source-plots-v1-20261024'for u in ['229852','258419','259378','335494']]
    names +=['government-xl-ventilation335494-'+s+'-20261024'for s in ['current-foundations-v1','current-low-faces-v1','current-cap-paths-v1','bounded-identity-review-v1','current-basic-contacts-v1','unapproved-preview-v1','source-review-v1']]
    names +=['government-xl-ventilation335494-original-qualified-stage-v1-20261024']
    for name in names:
        result,pins=authenticate(BASE/name);jobs[name]=result['jobId'];records[name]=result;refs.append(BASE/name/'result.json')
        for file in ['summary.json','ROOT-IDENTITY-REVIEW.json','ROOT-PHYSICAL-REVIEW.json','ROOT-SOURCE-REVIEW.json','qualification.json']:
            path=BASE/name/file
            if path.exists():assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path)
    selection=read(BASE/(P+'runtime-v1-20261024')/'selection.json.gz');refs.append(BASE/(P+'runtime-v1-20261024')/'selection.json.gz')
    source_sha={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(source_sha)==4
    failure=BASE/(P+'native-contacts-v1-20261024');failed=[HERE/'selected_original_overlapping_native_contacts_v2_20261024.py',HERE/'selected_original_render_attributes_v1.mjs',*list(failure.glob('*'))];refs.extend(p for p in failed if p.is_file())
    corrected=dict(failedBatch=failure.name,reason='Older raw current entries omit per-entry rootTranslation, inherited from the catalogue by the actual viewer. The original diagnostic called loadOfficialModel directly and failed before geometry capture.',resolution='V3 native runner uses V2 capture with actual production prepareModelCatalogue, authenticates raw entries against full catalogues, and exactly compares all three captured native coordinate-bound representations with current inventory. All three native assets and twelve source/native/world pairs complete. No source or current catalogue metadata changed.',permanentRejection=False,modelCorruption=False,correctedBatch=P+'native-contacts-v2-20261024')
    rows=[
        dict(uid='landsd/335494:0',name='Central-Wan Chai Bypass West Ventilation Building',humanStatus='in-process',requiresCompute=True,requiresAI=False,requiresHumanDecision=False,completed=['Bounded exact-source/provider/official-photo portal-roof identity review; raw extent flags retained.','Complete four-world foundations; nine lower-wall clear-cap paths in each world.','All6894 native scope, zero finite contacts with both retained originals in all four worlds.','All twelve private source/retained desktop/mobile day/night exports actually inspected.','Guarded model-only stage and installer preflight passed; no terrain edits.'],nextActions=['Commit qualification; guarded installation, live twelve exports, independent full521/all6894oldasset readback and push.']),
        dict(uid='landsd/259378:0',name='Harbour Plaza Metropolis',humanStatus='held-compute',requiresCompute=True,requiresAI=False,requiresHumanDecision=False,completed=['Exact unchanged original fresh current capture and identity/extent evidence.','Complete native contact comparison against101394face Fortune Metropolis in all four worlds.'],nextActions=['Run complete original-to-installed-podium support paths; retain every raw contact.','Finish bounded source-role/extent interpretation using exact source graph, current target and adjoining original podium; no geometry edits.']),
        dict(uid='landsd/258419:0',name='GREENFIELD SHOPPING ARCADE',humanStatus='held-compute',requiresCompute=True,requiresAI=False,requiresHumanDecision=False,completed=['Exact unchanged original current capture/attributes and all30current-form scope.','Raw unrelated-overlap/extent flags and complete source plan/perspectives archived.'],nextActions=['Measure exact before/after contacts for all scoped forms, including nine current basic towers and the four unrelated nominations.','Account complete current-ground lower surfaces before source-role/identity review.']),
        dict(uid='landsd/229852:0',name='Unnamed open-sided structure',humanStatus='held-compute',requiresCompute=True,requiresAI=False,requiresHumanDecision=False,completed=['Exact original17127faces current capture, all four coordinate attributes and one-form/no-native scope.','Current identity route explicitly rejects unsupported Open-sided Structure type; raw source/record projection evidence saved.'],nextActions=['Verify authoritative subtype/GeoRef/component mapping without coercing it into the generic Tower/Podium route.','Inspect the complete original extent and coastal source-TIN binding; preserve1.2m source-land and exact coastal no-lowering guards.'])]
    for r in rows:r['sourceSHA256']=source_sha[r['uid']];r['requiresAIGeometryModelling']=False;r['permanentRejection']=False
    preflight=BASE/'government-xl-ventilation335494-original-original-installed-v1-20261024-proposal/installer-preflight.json';assert read(preflight)['passed'];refs.append(preflight)
    result=dict(uids=sorted(source_sha),rows=rows,completedJobs=jobs,correctedSetupFailure=corrected,currentManifestSHA256=selection['manifestSHA256'],fixedXLTotal=521,fixedXLInstalled=350,fixedXLUnfinished=171,currentNativeActors=6894,sourceGeometryChanges=0,sourcePoseChanges=0,activeWorkers=0,workerScope='Sixteen next-four/ventilation diagnostic, preview and qualification handles polled terminal; original failed native capture exit1, all successors exit0. No installation started yet.',installationApproved=False,publication=False,newlyInstalled=0,qualification='Current evidence checkpoint only. No original discarded, corrupted, permanently rejected or installed by diagnostics. AI was used for coding and the bounded ventilation source-evidence interpretation, never geometry generation. Other three next actions are compute/record investigation; no user decision or external access required at this checkpoint.')
    save(out/'remaining-work.json',result)
    module('next_four_current_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-four-source-completed-diagnostics-and-actionable-original-recovery-next-steps',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
