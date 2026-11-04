"""Exercise the complete Sha Tin plan without approving or publishing originals."""
import argparse
import copy
import shutil
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from three_member_native_boundary_v1_20261027 import private_validator
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-sha-tin-'
BATCH=P+'seven-original-full-plan-dry-run-v2-20261029'
TERRAIN_URL='city/data/government-native-sha-tin-seven-original-v1-20261029.json'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');args=ap.parse_args()
    out=BASE/BATCH;stage=HERE/'local'/BATCH;lp=stage/'reservation.json';assert not out.exists()
    forms=read(BASE/(P+'seven-upward-floor-scope-v1-20261029')/'form-obligations.json.gz')
    resources=sorted({'building:'+b['uid']for b in forms}|{'terrain:city/data/terrain.json'})
    if not args.owned:
        assert not stage.exists()
        claim=reservations.claim('sha-tin-full-plan-dry-run-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    refs=[Path(__file__)];pins={}
    def take(suffix,path):
        batch=P+suffix+'-20261029'
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=take('seven-upward-floor-scope-v1',BASE/(P+'seven-upward-floor-scope-v1-20261029')/'scope.json')
    assert scope['currentNativeActors']==7007 and scope['intersectingForms']==70 and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps']==0
    forms2=take('seven-upward-floor-scope-v1',BASE/(P+'seven-upward-floor-scope-v1-20261029')/'form-obligations.json.gz');assert forms==forms2
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=digest(manifest.read_bytes());refs.append(manifest)
    fixture='source-bound-production-fixture-v1';fixture_batch=P+fixture+'-20261029'
    cfgpath=HERE/'local'/fixture_batch/'config.json';cfg=take(fixture,cfgpath);old=ROOT/cfg['stage'];cat=take(fixture,old/'catalogue.json');source_forms=take(fixture,old/'source-forms.json')
    assert len(cat['models'])==7 and sorted(m['uid']for m in cat['models'])==sorted(scope['uids'])
    for m in cat['models']:
        assert m['placementReviewed']is False and m['publicationApproved']is False
        assert m['proceduralWindows']is False and m.get('verticalPlacementOffsetHKPD',0)==0
        assert not m.get('supportDependencies')and m['activationGroup']==sorted(scope['uids'])
        asset=old/m['asset'];assert digest(asset.read_bytes())==m['sha256'];refs.append(asset)
        dest=stage/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
    save(stage/'catalogue.json',cat);save(stage/'source-forms.json',source_forms)
    fragment_batch=P+'qualified-basic-ground-v1-20261029'
    fragment=take('qualified-basic-ground-v1',BASE/fragment_batch/'plan-fragment.json')
    qualified=take('qualified-basic-ground-v1',BASE/fragment_batch/'summary.json');assert qualified['realPublisherStagersPassed']and qualified['publicFilesWritten']==0
    assert len(fragment['nativeBasicFallbackGrounds'])==3 and len(fragment['illustrativeFoundations'])==1
    terrain_batch=P+'seven-upward-floor-terrain-return-v1-20261029'
    terrain=take('seven-upward-floor-terrain-return-v1',BASE/terrain_batch/'summary.json');asset=ROOT/terrain['candidate']['path'];assert digest(asset.read_bytes())==terrain['candidate']['sha256'];refs.append(asset)
    destination='city/data/official-models/'+P+'seven-original-qualified-stage-v1-20261029/catalogue.json'
    plan=dict(status='unapproved-originals-canonical-dry-run-only',areas=[dict(area='Sha Tin seven unchanged government originals',catalogue=str((stage/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[dict(source=str(asset.relative_to(ROOT)),destination=TERRAIN_URL,sha256=terrain['candidate']['sha256'],resolution=read(asset)['cell'],area='Sha Tin original-source ground')],**copy.deepcopy(fragment))
    assert all(u['terrainURL']==TERRAIN_URL for u in plan['nativeBasicFallbackGrounds'])
    save(stage/'plan.json',plan)
    sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
    pub=module('sha_tin_full_draft_canonical_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=out/'publisher-dry-run'
    argv=sys.argv[:]
    try:
        sys.argv=['publish.py',str((stage/'plan.json').relative_to(ROOT))]
        with private_validator():pub.main()
    finally:sys.argv=argv
    report=read(pub.DOC/'publication-plan.json');assert report['published']is False and digest(manifest.read_bytes())==before
    assert len(report['nativeBasicFallbackGrounds'])==3 and len(report['illustrativeFoundations'])==1
    assert len(report['areas'])==1 and report['areas'][0]['models']==7 and len(report['topLevelTerrainPatches'])==1
    refs.append(HERE/'three_member_native_boundary_v1_20261027.py');refs.extend(pub.PINNED_INPUTS);refs.extend(p for p in stage.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
    result=dict(uids=scope['uids'],currentManifestSHA256=before,canonicalFullPlanDryRunPassed=True,originalApprovalFlagsRemainFalse=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,newlyInstalled=0,publication=False,installationApproved=False,completeOriginalModelAcceptance=False,remainingWork=['Exact original-native pair role and boundary review','Compose full original acceptance from existing evidence','Qualified stage and exact final browser verification','Guarded live publication and independent ledger readback'],plan=str((stage/'plan.json').relative_to(ROOT)),qualification='Complete seven-original, one new native terrain, three source-bound BASIC continuations and one estimated canopy post update pass the unchanged canonical publisher in dry-run mode. This is a publication mechanics check only. False original approval flags remain untouched; no model or public data is installed.')
    save(out/'summary.json',result)
    module('sha_tin_full_plan_dry_run_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-original-complete-unapproved-plan-canonical-dry-run',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
