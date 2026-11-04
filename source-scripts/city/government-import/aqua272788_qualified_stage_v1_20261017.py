"""Qualify unchanged Aqua Marine Block 2 with its verified installed original podium."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-aqua272788-';BATCH=PREFIX+'qualified-stage-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/272788:0';SHA='dba1c8804136ce3c086cef7f6a7ac013b3b15eb17648160e9ffb899442872da5';SOURCES={UID:SHA};PODIUM='landsd/193086:0';HOST='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91'
PREVIOUS=BASE/'government-xl-tai-kwei-original-installed-v1-20261017/full-xl-current-count.json';SOURCE_KEY=next(r['sourceKey']for r in read(PREVIOUS)['rows']if r['uid']==UID)
def folder(n):return BASE/(PREFIX+n+'-20261017')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def main():
 assert not DOC.exists()and not STAGE.exists();refs={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in ['current-junction-resolution-v1','current-physical-v3','four-world-junction-v1','private-browser-v1']:
   p=folder(name)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(p)]:
    assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():check(q)
 resolution=read(folder('current-junction-resolution-v1')/'resolution.json');assert resolution['sourceSpecificJunctionAccepted']and not resolution['remainingSourceSpecificReasons'];assert resolution['sourceSHA256ByUid']=={UID:SHA,PODIUM:HOST}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==resolution['currentManifestSHA256']==read(PREVIOUS)['manifestSHA256'];previous=read(PREVIOUS);row=next(r for r in previous['rows']if r['sourceKey']==SOURCE_KEY);assert not row['installedVerified']and row['indexedSourceSHA256']==SHA
 finite=read(folder('four-world-junction-v1')/'summary.json');assert finite['allFourModesVerified']
 images=read(folder('current-junction-resolution-v1')/'ROOT-IMAGE-INSPECTION.json');assert images['sourceGeometryAppearanceAccepted']and len(images['reviewedImages'])==4
 for q in images['reviewedImages']:check(q)
 prior=HERE/'local'/folder('private-browser-v1').name;cat=read(prior/'catalogue.json');assert len(cat['models'])==1;e=cat['models'][0];assert e['uid']==UID and e['sha256']==SHA and e['proceduralWindows']is False and not e.get('suppressesBuildingUids')
 assert len(e['supportDependencies'])==1 and e['supportDependencies'][0]['uid']==PODIUM and e['supportDependencies'][0]['sha256']==HOST and e['supportDependencies'][0]['state']=='installed'
 pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(pointer['snapshotId'],PODIUM)).fetchone()==('installed-verified',HOST)
 DOC.mkdir();STAGE.mkdir();q=dict(uid=UID,sourceSHA256=SHA,privateStageQualified=True,currentManifest=ref(manifest),sourceResolution=ref(folder('current-junction-resolution-v1')/'result.json'),completeFiniteEvidence=ref(folder('four-world-junction-v1')/'result.json'),currentPhysical=ref(folder('current-physical-v3')/'result.json'),requiredInstalledSupport=e['supportDependencies'][0],rawDiagnosticsRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,publication=False)
 save(DOC/'qualification.json',q);save(DOC/'ROOT-IMAGE-INSPECTION.json',images)
 e.update(originalSourceKey=SOURCE_KEY,sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=ref(folder('current-physical-v3')/'identity-proofs.json'),sourceFunctionalApplicability=ref(DOC/'qualification.json'),sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Original geometry and source placement at1x. Complete current compound foundation and two exact near-coincident wall-junction interpretation checked in all coordinate modes; strict340podium contacts, current identity/neighbours and staged desktop/mobile checks. Raw flags retained.')
 dest=STAGE/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(prior/e['asset'],dest);assert ref(dest)['sha256']==SHA
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json');url='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Aqua Marine Block 2 original',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url)]));config=read(prior/'browser-config.json');assert config['terrain']==[];config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=url);save(STAGE/'browser-config.json',config)
 pub=module('aqua_qualified_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for q in refs.values():check(q)
 out=module('aqua_qualified_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-qualified-original-stage-v1',[Path(__file__),PREVIOUS,*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*')if p.is_file()]],dict(uids=[UID],privateStageQualified=True,publisherDryRunPassed=True,publication=False,nextStep='Guarded original installation with exact current evidence, rollback and live browser checks.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
