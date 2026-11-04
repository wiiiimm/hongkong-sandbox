"""Persist complete Garden Terrace mathematics and rejected V1 camera evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-garden-terrace2-';BATCH=P+'three-original-progress-checkpoint-v1-20261024'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(suffix,file='summary.json'):
        name=P+suffix+'-20261024'
        if name not in pins:
            result,pins[name]=authenticate(BASE/name);jobs[name]=result['jobId'];refs.append(BASE/name/'result.json')
        path=BASE/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('three-current-runtime-v1','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==3 and sum(r['triangles']for r in selection['rows'])==22814
    for suffix in ['three-current-attributes-v1','three-current-identity-v1','three-current-model-scope-v1','three-current-native-contacts-v1','three-current-basic-contacts-v1','three-original-pair-context-v1','three-context-views-v1']:take(suffix,'attributes.json.gz'if suffix=='three-current-attributes-v1'else'summary.json')
    for uid in ['109491','162285','21894']:
        f=take(uid+'-four-world-foundations-v1');assert len(f['rows'])==4 and all(r['completeTerrainTriangles']==r['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in f['rows'])
    for uid,count in [('109491',328),('21894',371)]:
        take(uid+'-original-podium-support-v1');paths=take(uid+'-original-podium-paths-v1');assert paths['allUnresolvedHaveFinitePaths']and all(r['targets']==r['verifiedPaths']==count and not r['remaining']for r in paths['rows'])
    for uid in ['162285','21894']:take(uid+'-low-faces-v1')
    cap=take('162285-complete-ground-cap-paths-v1');assert cap['allFourCompleteGroundClearCapPaths']and all(len(r['completeGroundClearancePartition']['paths'])==67 for r in cap['rows'])
    cap=take('21894-complete-ground-cap-paths-v1');assert not cap['allFourCompleteGroundClearCapPaths']and all(len(r['completeGroundClearancePartition']['paths'])==5 and all(p['hasExactSharedEdgeClearCapPath']for p in r['completeGroundClearancePartition']['paths'])and r['completeGroundClearancePartition']['negativeNonWallFaces']==[7628,7629,7630,7631]for r in cap['rows'])
    basal=take('21894-basal-ground-context-v1');assert basal['allFourWorldBottomFacesBelowRecordedBaseWithGradeBelowBase']and all(r['faces']==[7628,7629,7630,7631]for r in basal['rows'])
    identity=take('three-compound-identity-v1','identity.json');assert identity['identityAccepted']and identity['requiredUnchangedAssembly']==sources
    browser=P+'three-unapproved-preview-v1-20261024';images=[];sheets=[]
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    for width in [1280,390]:
        report=take('three-unapproved-preview-v1',str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        views=[v for v in report['views']if'time'in v]+report['retainedNativeOwnViews'];assert len(views)==8
        for v in views:
            path=BASE/browser/str(width)/v['file'];r=ref(path);assert pins[browser][r['path']]==r['sha256'];refs.append(path);images.append(r)
        for time in ['1500','2200']:
            path=BASE/(P+'three-root-inspection-v1-20261024')/str(width)/(str(width)+'-'+time+'.jpg');assert path.is_file();refs.append(path);sheets.append(ref(path))
    assert len(images)==16
    actualPlots=[]
    for suffix,file in [('three-context-views-v1','complete-original-assembly.png'),('three-context-views-v1','base-only-diagnostic.png'),('21894-basal-ground-context-v1','basal-ground-context.png')]:
        name=P+suffix+'-20261024';path=BASE/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);actualPlots.append(ref(path))
    rejection=dict(reviewer='ROOT',imagesActuallyViewed=images,inspectionSheetsActuallyViewed=sheets,mathematicalContextPlotsActuallyViewed=actualPlots,visualAcceptance=False,reason='V1mobile Block2 is mostly hidden behind a foreground BASIC building, despite passing active/frustum/fully-framed checks. Podium is also partly foreground-occluded. V2 changes Block2 camera to[0,1.8,-1]and podium camera to[1,3,1]; no geometry, terrain, identity or budget guard change. V2 requires its own actual export inspection.',sourceGeometryChanges=0,aiGeometryModelling=False)
    save(out/'ROOT-V1-REJECTED-INSPECTION.json',rejection)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    remaining=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifestSHA256=selection['manifestSHA256'],completedJobs=jobs,fixedXLTotal=521,fixedXLInstalled=347,fixedXLRemaining=174,currentNativeActors=6881,newlyInstalled=0,sourceFaces=22814,scriptedUnresolvedSupportPathsVerified=699,allFourWorldFoundationsComplete=True,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=True,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,requiresAIGeometry=False,requiresHumanDecision=False,humanState='Held for further processing',remaining=['Observe the already-started private V2 browser, inspect all16new/retained exports, and correct occlusion if necessary. Never restart a live worker solely because observation expires.','Complete bounded source-role/physical review, preserving all strict support/rim negatives and Block3four downward basal-face negatives; grade under those faces remains below the recorded135.9m base in all4worlds.','Prepare a supported model-only installation path with zero terrain changes/no suppressions, both new towers to originalpodium162285, unchanged retainednative304714/no invented migration, all global retainedBASIC guards and all6881oldactor preservation.','Run guarded publication/live devices/ROOTactualinspection/all521readback; derive actual fixedXLdelta (109491and21894are both fixedXL) and commit/push installation.'],qualification='Complete immutable original-source mathematics and V1visual rejection only. No new Garden Terrace installation or permanent rejection. Yoho already installed/pushed920a3537b; keep full174unfinished objective active. No optimisation/migration/AIgeometry modelling.')
    save(out/'remaining-work.json',remaining);module('garden_progress_checkpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-garden-terrace-complete-scripted-proof-and-remaining-installation-obligations',list(dict.fromkeys(refs)),remaining)

if __name__=='__main__':main()
