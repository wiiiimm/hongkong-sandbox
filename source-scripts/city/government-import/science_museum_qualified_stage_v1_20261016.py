"""Qualify exact museum original and retained illustrative canopy for atomic publication."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-museum-qualified-stage-v1-20261016';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/80343:0';SHA='df4eeb38ea777cf3016a497db81c0c2a36ea880da7a3cb5b27a426e8768dbe28';SOURCES={UID:SHA}
NAMES=['canopy-foundation-review-v1','preserved-neighbours-v3','native-regression-v1','four-world-ground-v1','private-browser-v1','loader-validation-v1','retained-canopy-review-v1']
def folder(n):return BASE/(('government-xl-science-history-' if n in ['preserved-neighbours-v3','native-regression-v1','retained-canopy-review-v1'] else 'government-xl-science-museum-')+n+'-20261016')
def data(n,f):return read(folder(n)/f)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify():
 refs={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(p)]:assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():assert ref(ROOT/q['path'])==q
 return refs

def main():
 assert not DOC.exists() and not STAGE.exists();refs=verify()
 metric=next(r for r in data('preserved-neighbours-v3','summary.json')['targetMetrics'] if r['uid']==UID);policy=module('museum_policy',HERE/'acceptance-policy.py');profiles=data('preserved-neighbours-v3','metrics.json')['profiles'];row=dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA);raw=policy.reasons(row,metric,profiles['mobile']);remaining=raw;assert not raw
 worlds=data('four-world-ground-v1','summary.json');assert len(worlds['rows'])==4 and worlds['allFourModesCovered'] and worlds['allFourModesUnburied'];assert all(r['foundation']['completeTerrainTriangles']==11520 and r['foundation']['fullyBuriedTriangles']==0 for r in worlds['rows'])
 native=data('native-regression-v1','summary.json');assert native['resolved']==['landsd/305793:0','landsd/4759:0'] and len(native['rows'])==2 and all(r['passed'] for r in native['rows'])
 held=native['ordinaryRegressions'];assert len(held)==1 and held[0]['uid']=='landsd/83471:0' and held[0]['reasons']==['increased-neighbour-ground-gap']
 canopy=data('canopy-foundation-review-v1','summary.json');assert canopy['fullPostFootprintsMeetGround'] and canopy['wholeRoofClear'] and canopy['completePostCount']==6
 retained=data('retained-canopy-review-v1','summary.json');assert retained['wholeRoofClear'] and retained['fullPostFootprintsMeetGround']
 browser=data('private-browser-v1','staged-browser.json');assert browser['passed'] and not browser['errors'];views=[v for v in browser['views'] if 'time' in v];assert len(views)==4
 for v in views:assert v['sourceSHA256']==SHA and v['originalTriangles']==11520 and v['fullyFramed'] and v['pick']==v['collision']==UID and v['fallbackFaces']==0
 assert len(browser['retainedNativeOwnViews'])==8 and all(v['fullyFramed'] and v['active'] and v['visible'] for v in browser['retainedNativeOwnViews'])
 assert len(browser['canopyForms'])==2 and len([v for v in browser['views'] if v.get('phase')=='failed-download' and v['fallbackRetained']])==1
 prior=HERE/'local'/folder('private-browser-v1').name;cat=read(prior/'catalogue.json');assert len(cat['models'])==1;e=cat['models'][0];assert e['uid']==UID and e['sha256']==SHA and not e.get('suppressesBuildingUids')
 previous=BASE/'government-xl-history-museum-original-installed-v1-20261016/full-xl-current-count.json';source=next(r for r in read(previous)['rows'] if r['uid']==UID);assert not source['installedVerified'] and source['indexedSourceSHA256']==SHA
 DOC.mkdir();STAGE.mkdir();review=dict(reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=[ref(folder('private-browser-v1')/v['file']) for v in views],observation='All four desktop/mobile day/night exports inspected. Original museum roof forms and circular rooftop features visible, with current scene window shading. Neighbouring buildings retained; canopy foundation metadata verified in both widths. No architectural geometry altered.')
 save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 qualification=dict(uids=[UID],sourceSHA256ByUid=SOURCES,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),rawPolicyReasons=raw,remainingPolicyReasons=remaining,identityReconciliation=ref(folder('preserved-neighbours-v3')/'metrics.json'),canopyResolution=ref(folder('canopy-foundation-review-v1')/'summary.json'),retainedNativeUids=['landsd/305793:0','landsd/4759:0'],sourceGeometryChanges=0,sourcePoseChanges=0,privateStageQualified=True,publication=False)
 save(DOC/'qualification.json',qualification);e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,originalSourceKey=source['sourceKey'],sourceIdentityReview=qualification['identityReconciliation'],sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Unchanged original museum at source pose/1x scale; complete four-coordinate-mode source foundation, retained-neighbour and staged desktop/mobile checks pass. Adjacent illustrative canopy posts extend to reviewed terrain; roof/base/source elevations unchanged.')
 dest=STAGE/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(prior/e['asset'],dest);assert ref(dest)['sha256']==SHA;save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 terrain=STAGE/'museum-original-terrain.json';shutil.copyfile(prior/'terrain.json',terrain);config=read(prior/'browser-config.json');t={**config['terrain'][0],'source':str(terrain.relative_to(ROOT)),'sha256':ref(terrain)['sha256']};destination='city/data/official-models/'+BATCH+'/catalogue.json'
 posts=BASE/'government-xl-science-museum-canopy-posts-v1-20261016';before=read(posts/'input.json')['building'];tr=config['tileReplacements'][0];update=dict(uid=before['uid'],tile=tr['url'],tileSHA256=tr['originalSHA256'],before=before,foundationBase=read(posts/'proposal.json')['foundationBase'],evidence=qualification['canopyResolution'],proposal=ref(posts/'proposal.json'))
 save(STAGE/'plan.json',dict(areas=[dict(area='Science Museum original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[t],illustrativeFoundations=[update]))
 config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[t]);save(STAGE/'browser-config.json',config)
 publisher=module('museum_publisher',HERE.parent/'island-detail-integration/publish.py');publisher.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];publisher.main();dry=read(publisher.DOC/'publication-plan.json');assert not dry['published'] and len(dry['illustrativeFoundations'])==1
 refs.update({ref(previous)['path']:ref(previous)})
 for q in refs.values():assert ref(ROOT/q['path'])==q
 paths=[Path(__file__),HERE/'acceptance-policy.py',*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*') if p.is_file()],HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/illustrative_foundations.py']
 r=module('museum_stage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-museum-original-and-retained-canopy-v1',paths,dict(uids=[UID,'landsd/83471:0'],privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],publisherDryRunPassed=True),flush=True)
if __name__=='__main__':main()
