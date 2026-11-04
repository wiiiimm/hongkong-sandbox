"""Qualify the exact original pool pair; private publisher dry run only."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sham-shui-po-pool-'
BATCH=PREFIX+'qualified-stage-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PODIUM='landsd/265480:0';TOWER='landsd/271043:0'
SOURCES={PODIUM:'94e8a0199e420baee0673b9c227b1e2411aca086b3459245a7d899bace82a36b',TOWER:'fc1b0d304c3b50903c479cff16789ed94673dbec4ad59b87de8344dbd812991c'}
NAMES=['preserved-neighbours-v6','native-regression-v5','basic-finite-v3','four-world-foundation-v3','original-group-browser-v5','original-support-review-v1','original-pair-identity-review-v1','original-group-v2','loader-validation-v2']
def folder(n):return BASE/(PREFIX+n+'-20261017')
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
 finite=data('basic-finite-v3','summary.json');assert finite['all84ActorsComplete'] and finite['noIntroducedFailures'] and len(finite['rows'])==84
 assert all(not r['introducedUnproved'] and not r['afterUncovered'] for r in finite['rows'])
 foundation=data('four-world-foundation-v3','summary.json');assert foundation['allStrictPass'] and len(foundation['rows'])==8
 native=data('native-regression-v5','summary.json');assert set(native['resolved'])=={'landsd/113733:0','landsd/138091:0','landsd/99395:0'} and len(native['rows'])==3 and all(r['passed'] for r in native['rows'])
 ordinary=native['ordinaryRegressions'];assert len(ordinary)==1 and ordinary[0]['uid']==TOWER and ordinary[0]['reasons']==['increased-neighbour-ground-gap']
 identity=data('original-pair-identity-review-v1','ROOT-SOURCE-REVIEW.json');support=data('original-support-review-v1','ROOT-SUPPORT-REVIEW.json')
 assert identity['sourceIdentityRelationshipAccepted'] and identity['sourceSHA256ByUid']==SOURCES
 assert support['sourceSpecificSupportAccepted'] and support['sourceSHA256ByUid']==SOURCES and support['requiredOriginalSupportUid']==PODIUM and support['supportedUid']==TOWER
 oldworld=read(BASE/(PREFIX+'four-world-foundation-v2-20261017')/'world-triangles.json.gz');assert oldworld==data('four-world-foundation-v3','world-triangles.json.gz')
 metric=data('original-group-v2','metrics.json');policy=module('pool_policy',HERE/'acceptance-policy.py');raw={};remaining={}
 for m in metric['rows']:
  u=m['uid'];row=dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[u]);raw[u]=policy.reasons(row,m,metric['profiles']['mobile']);row['identityProof']=identity['proof'];reasons=policy.reasons(row,m,metric['profiles']['mobile'])
  if u==TOWER:assert reasons==['ground-contact-unresolved'];reasons=[]
  else:assert reasons==[]
  remaining[u]=reasons
 assert set(raw)==set(SOURCES)
 loader=data('loader-validation-v2','validation.json');assert len(loader['results'])==2 and all(r['outcome']=='runtime-accepted-placement-unreviewed' for r in loader['results'])
 report=data('original-group-browser-v5','staged-browser.json');assert report['passed'] and not report['errors'];views=[v for v in report['views'] if 'time'in v];assert len(views)==8 and len(report['jointViews'])==4 and len(report['retainedNativeOwnViews'])==12
 for v in views:assert v['fullyFramed'] and v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==SOURCES[v['uid']] and not v['fallbackFaces']
 for j in report['jointViews']:assert {m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained'] and failed[0]['dependentFallbacks']=={TOWER:{'active':False}}
 review=data('original-group-browser-v5','ROOT-ASSEMBLY-IMAGE-REVIEW.json');assert review['reviewer']=='Codex ROOT' and review['wholeAssemblyVisualAcceptance'] and len(review['reviewedImages'])==4
 for q in review['reviewedImages']:assert ref(ROOT/q['path'])==q
 previous=BASE/'government-xl-science-museum-original-installed-v1-20261016/full-xl-current-count.json';source=next(r for r in read(previous)['rows']if r['uid']==PODIUM);assert not source['installedVerified'] and source['indexedSourceSHA256']==SOURCES[PODIUM]
 prior=HERE/'local'/folder('original-group-browser-v5').name;cat=read(prior/'catalogue.json');assert {e['uid']:e['sha256']for e in cat['models']}==SOURCES
 DOC.mkdir();STAGE.mkdir();qualification=dict(sourceSHA256ByUid=SOURCES,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),privateStageQualified=True,rawPolicyReasons=raw,remainingPolicyReasons=remaining,sourceIdentityReview=ref(folder('original-pair-identity-review-v1')/'ROOT-SOURCE-REVIEW.json'),sourceSupportReview=ref(folder('original-support-review-v1')/'ROOT-SUPPORT-REVIEW.json'),foundation=ref(folder('four-world-foundation-v3')/'summary.json'),completeBasicNeighbours=84,completeNativeNeighbours=3,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False)
 save(DOC/'qualification.json',qualification);save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 for e in cat['models']:
  assert e['proceduralWindows']is False and not e.get('suppressesBuildingUids')
  assert e['supportDependencies']==([]if e['uid']==PODIUM else [dict(uid=PODIUM,state='candidate',csuid='3404421334P20060311',sha256=SOURCES[PODIUM])])
  e.update(sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=qualification['sourceIdentityReview'],sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Unchanged original source pose/1x scale. Exact source identity and scoped original wall/podium support review; complete four-world foundation, 84 basic and three native neighbours, and staged desktop/mobile assembly/failure-retry checks pass. Raw canonical warnings retained in qualification.')
  if e['uid']==PODIUM:e['originalSourceKey']=source['sourceKey']
  dest=STAGE/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prior/e['asset'],dest);assert ref(dest)['sha256']==e['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 config=read(prior/'browser-config.json');old=config['terrain'][0];terrain=STAGE/'pool-original-terrain.json';shutil.copyfile(ROOT/old['source'],terrain);t={**old,'source':str(terrain.relative_to(ROOT)),'sha256':ref(terrain)['sha256']};patch=read(terrain);fullcheck=folder('native-regression-v5')/'native-neighbour-checks.json'
 replacement=dict(status='approved-for-integration',supersededURL=t['replaces']['url'],supersededSHA256=t['replaces']['sha256'],replacementSHA256=t['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=['landsd/113733:0','landsd/138091:0'],replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(fullcheck),qualification='Original shared terrain replacement; all three touching native originals checked, original geometry unchanged.')
 save(DOC/'native-replacement-review.json',replacement);t['nativeReview']=ref(DOC/'native-replacement-review.json');destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',dict(areas=[dict(area='Sham Shui Po Park Swimming Pool original pair',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[t]));config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[t]);save(STAGE/'browser-config.json',config)
 pub=module('pool_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for q in refs.values():assert ref(ROOT/q['path'])==q
 paths=[Path(__file__),HERE/'acceptance-policy.py',previous,folder('original-group-browser-v5')/'ROOT-ASSEMBLY-IMAGE-REVIEW.json',*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*')if p.is_file()],HERE.parent/'island-detail-integration/publish.py']
 out=module('pool_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-two-original-pool-private-stage-v1',paths,dict(uids=list(SOURCES),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],publisherDryRunPassed=True),flush=True)
if __name__=='__main__':main()
