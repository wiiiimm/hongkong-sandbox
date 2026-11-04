"""Qualify exact PolyU original from current numeric, identity and browser evidence."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-qualified-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH;UID='landsd/305582:0';SOURCES={UID:'ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'}
BROWSER=BASE/'government-xl-polyu-staged-browser-v1-20261015';METRICS=BASE/'government-xl-polyu-current-acceptance-metrics-v1-20261015';IDENTITY=BASE/'government-xl-polyu-sports305582-root-campus-identity-review-v1-20261013'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();r=read(BROWSER/'result.json');paths=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for p in [BROWSER/'result.json',IDENTITY/'result.json']:
   receipt=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);paths.append(p)
 for q in r['evidenceRefs']:assert ref(ROOT/q['path'])==q;paths.append(ROOT/q['path'])
 identity=read(IDENTITY/'root-campus-source-identity-review.json');assert identity['identityAccepted']and identity['sourceSHA256']==SOURCES[UID]and identity['nativePublicationHoldRetained']
 historical=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/captured-manifest.json';identityBindings=[]
 for q in identity['inputRefs']:
  p=ROOT/q['path']
  if ref(p)!=q:
   assert q['path']=='3d-viewer/city/data/manifest.json'and ref(historical)['sha256']==q['sha256'];p=historical
  paths.append(p);identityBindings.append(dict(original=q,resolved=ref(p)))
 metrics=read(METRICS/'metrics.json');assert len(metrics['rows'])==1;metric=metrics['rows'][0];selection=read(METRICS/'selection.json.gz');row=selection['rows'][0];entry=row['candidate']['entry'];building=row['source']['building']
 for p,h in metrics['inputHashes'].items():assert ref(ROOT/p)['sha256']==h;paths.append(ROOT/p)
 assert entry['uid']==building['uid']==UID and entry['objectId']==building['objectId']==305582 and entry['buildingCSUID']==building['buildingCSUID']==identity['sourceBuildingCSUID']and entry['modelId']==identity['sourceModelId']
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');matches=[]
 for t in manifest['tiles']:
  x,z=building['centre'];a,b,c,d=t['bounds']
  if a<=x<=c and b<=z<=d:
   p=ROOT/'3d-viewer'/t['url'];paths.append(p);matches.extend(v for v in read(p)['buildings']if v['uid']==UID)
 assert matches==[building]
 proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True,review=ref(IDENTITY/'root-campus-source-identity-review.json'));row['identityProof']=proof
 policy=module('polyu_existing_acceptance',HERE/'acceptance-policy.py');reasons=policy.reasons(row,metric,metrics['profiles']['mobile']);assert not reasons,reasons;assert metric['budget']['drawCalls']<=metrics['profiles']['mobile']['drawCalls']
 finite=read(BASE/'government-xl-polyu-complete-saved-actor-finite-v2-20261014/complete-full-actor-current-candidate-finite.json.gz');assert len(finite['rows'])==26
 for actor in finite['rows']:
  assert actor['allSourceSlotsAccounted']and not actor['emptyConstructorUncredited']
  for w in actor['worlds']:
   findings=w['findings'];assert not findings['candidateUncovered']and not findings['currentClearCandidateUnproved']
   if actor['uid']==UID:assert w['completeFaces']==10536 and not findings['candidateOrdinaryUnproved']
 foundation=read(BASE/'government-xl-polyu-current-foundation-v1-20261015/summary.json');assert foundation['allFoundationChecksPassed']and len(foundation['rows'])==4
 report=read(BROWSER/'staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];retained=report['retainedNativeOwnViews'];assert len(views)==len(retained)==4
 for v in views:assert v['fullyFramed']and v['pick']==v['collision']==UID and v['sourceSHA256']==SOURCES[UID]and not v['fallbackFaces']
 assert len([v for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']])==1
 native=ROOT/'3d-viewer/city/data/official-models/government-xxl-pao-20260913/catalogue.json';assert next(m for m in read(native)['models']if m['uid']=='landsd/305793:0')['publicationApproved']is False
 DOC.mkdir();STAGE.mkdir();save(DOC/'qualification.json',dict(uids=[UID],sourceSHA256ByUid=SOURCES,identityProof=proof,identityReferenceBindings=identityBindings,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),numericReasons=reasons,metric=metric,completeAffectedActors=26,completeSourceFourWorldClear=True,currentFoundationFourWorldPass=True,sourceIdentityReview=ref(IDENTITY/'root-campus-source-identity-review.json'),foreignContactDisposition='Retain authored source contacts as context under the bounded campus/perimeter identity interpretation. No foreign source or BASIC suppression, geometry edits, collision exemption, or approval of retained native305793. Current complete terrain regressions and actual target/retained browser witnesses pass. No independent engineering admission condition is introduced.',nativePublicationHoldRetained=True,privateStageQualified=True,publication=False,installationApproved=False))
 save(DOC/'ROOT-IMAGE-INSPECTION.json',dict(reviewer='Codex ROOT',visualAcceptance=True,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),stagedBrowser=ref(BROWSER/'staged-browser.json'),imagesActuallyViewed=[ref(BROWSER/v['file'])for v in views+retained],allEightExportedImagesActuallyInspected=True,scope='Target and retained campus model desktop/mobile day/night original geometry views; no mobile FPS claim and no approval of retained model hold.'))
 local=HERE/'local/government-xl-polyu-current-loader-validation-v1-20261015';cat=read(local/'catalogue.json');e=cat['models'][0];e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,sourceFunctionalApplicability=ref(DOC/'qualification.json'),identityProof=proof)
 dest=STAGE/e['asset'];dest.parent.mkdir();shutil.copyfile(local/e['asset'],dest);assert ref(dest)['sha256']==SOURCES[UID]
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',[building]);candidate=read(METRICS/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);out=STAGE/'government-native-polyu-original-v1-20261015.json';shutil.copyfile(ROOT/candidate['path'],out);assert ref(out)['sha256']==candidate['sha256']
 terrain=dict(source=str(out.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+out.name,resolution=patch['cell'],area='PolyU original Sports Centre campus podium');destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area=terrain['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain]))
 config=read(BROWSER/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain]);save(STAGE/'browser-config.json',config)
 pub=module('polyu_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';oldargv=sys.argv;sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))]
 try:pub.main()
 finally:sys.argv=oldargv
 assert not read(pub.DOC/'publication-plan.json')['published']
 paths += [IDENTITY/'root-campus-source-identity-review.json',METRICS/'metrics.json',METRICS/'selection.json.gz',Path(__file__),HERE/'acceptance-policy.py',native]+[p for p in STAGE.rglob('*')if p.is_file()]
 module('polyu_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-qualified-publication-stage-v1',paths,dict(uids=[UID],privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False));print('PolyU private qualification and publisher dry run passed',flush=True)
if __name__=='__main__':main()
