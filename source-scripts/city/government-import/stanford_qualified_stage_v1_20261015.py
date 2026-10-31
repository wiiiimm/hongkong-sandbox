"""Qualify one explicitly reviewed combined hotel source; retain raw identity mismatch."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-qualified-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/335875:0';PODIUM='landsd/305584:0';SHA='f1415300ae3ea9848213bb0e64975a00b2d3a86cceb11537bad88bd7eae3efc5';SOURCES={UID:SHA}
FOLDERS=['bounded-gap-infill-v5','join-runtime-capture-v5','basic-finite-v5','native-parent-scope-v1','four-world-ground-v5','current-loader-validation-v1','current-placement-metrics-v1','private-browser-v1','combined-identity-context-v1','combined-source-review-v1']
def folder(n):return BASE/('government-xl-stanford-'+n+'-20261015')
def data(n,f):return read(folder(n)/f)
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def check(q):assert ref(ROOT/q['path'])==q,q['path']
def verify_inputs():
 refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in FOLDERS:
   d=folder(n);r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(d/'result.json')]:
    assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():check(q)
 return refs

def main():
 assert not DOC.exists()and not STAGE.exists();refs=verify_inputs()
 identity=data('combined-source-review-v1','ROOT-SOURCE-REVIEW.json');assert identity['identityAccepted']and identity['sourceSHA256']==SHA and identity['primaryUID']==UID and identity['bundledPodiumUID']==PODIUM and not identity['exactLegacyGeoRefClaimed']
 ground=data('four-world-ground-v5','summary.json');assert len(ground['rows'])==4 and ground['allFourModesCovered']and ground['allFourModesUnburied']
 for r in ground['rows']:assert not r['continuousBelowHalfMetreFaces']and not r['exactUncoveredFaces']and r['foundation']['completeTerrainTriangles']==r['foundation']['triangles']==10049 and r['foundation']['fullyBuriedTriangles']==0
 basic=data('basic-finite-v5','summary.json');assert basic['all13ActorsComplete']and basic['noIntroducedFailures']and len(basic['rows'])==13
 assert all(not r['introducedUnproved']and not r['afterUncovered']for r in basic['rows'])
 assert data('native-parent-scope-v1','result.json')['touchingNativeUids']==[]
 assert data('join-runtime-capture-v5','result.json')['strictExteriorUnchanged']
 metrics=data('current-placement-metrics-v1','metrics.json');metric=metrics['rows'][0];row=data('current-placement-metrics-v1','selection.json.gz')['rows'][0]
 context=data('combined-identity-context-v1','context.json');own=next(x for x in context['rows'][0]['overlaps']if x['uid']==UID)
 metric={**metric,'identity':{'overlap':own['targetCoverage'],'centroidDistance':own['centroidDistanceM']}}
 raw=module('stanford_unmodified_policy',HERE/'acceptance-policy.py').reasons(row,metric,metrics['profiles']['mobile']);assert raw==['strict-identity-fit'],raw
 assert all(r['unrelatedOverlapM2']==0 for r in context['rows']);remaining=[r for r in raw if r!='strict-identity-fit'];assert not remaining
 report=data('private-browser-v1','staged-browser.json');views=[v for v in report['views']if 'time'in v]
 assert report['passed']and not report['errors']and len(views)==4
 assert {(v['width'],v['time'])for v in views}=={(w,t)for w in [1280,390]for t in ['15:00','22:00']}
 for v in views:assert v['sourceSHA256']==SHA and v['originalTriangles']==10049 and v['fullyFramed']and v['pick']==v['collision']==UID and v['fallbackFaces']==0 and v['suppressed'][PODIUM]['suppressed']
 failure=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failure)==1 and failure[0]['fallbackRetained']and failure[0]['suppressedBasicsRestored']=={PODIUM:True}
 prior=HERE/'local'/folder('private-browser-v1').name;cat=read(prior/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['sha256']==SHA and cat['rootTranslation']==[-834500,0,816500]
 patch=read(prior/'terrain.json');pub=module('stanford_existing_publisher',HERE.parent/'island-detail-integration/publish.py');parent=read(ROOT/'3d-viewer/city/data/terrain.json');pub.validate_patch(patch,parent);manifest=read(ROOT/'3d-viewer/city/data/manifest.json');pub.check_patch_overlap(patch,parent.get('patches',[])+[read(ROOT/'3d-viewer'/p['url'])for p in manifest['terrainPatches']])
 DOC.mkdir();STAGE.mkdir()
 review={'reviewer':'Codex ROOT','visualAcceptance':True,'imagesActuallyViewed':[ref(folder('private-browser-v1')/v['file'])for v in views],'currentManifest':ref(ROOT/'3d-viewer/city/data/manifest.json'),'stagedBrowser':ref(folder('private-browser-v1')/'staged-browser.json'),'observation':'All four desktop/mobile daytime/night exports inspected. Original whole hotel framed, no duplicate podium. Original facade remains plain; no fabricated windows added. Night visibility reduced with scene lighting, without missing geometry.'};save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 qualification={'uids':[UID],'sourceSHA256ByUid':SOURCES,'currentManifest':review['currentManifest'],'rawPolicyReasons':raw,'remainingPolicyReasons':remaining,'identityReconciliation':ref(folder('combined-source-review-v1')/'ROOT-SOURCE-REVIEW.json'),'exactLegacyIdentifierEqualityClaimed':False,'sourceGeometryChanges':0,'sourcePoseChanges':0,'fullFourModeFoundation':True,'basicNeighbours':13,'touchingNativeActors':0,'privateStageQualified':True,'publication':False};save(DOC/'qualification.json',qualification)
 entry.update(label='InterContinental Grand Stanford Hong Kong',sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,originalSourceKey='50fc7bc071df80beda9ae82ed346a2cc010eeddd1eb42b345f0c983e347c5451/B365201779201063C0',sourceIdentityReview=qualification['identityReconciliation'],sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Original combined tower/podium at unchanged source pose and 1x scale. Full source coverage, ground contact and affected-neighbour checks passed; explicit source identity review retains historical identifier mismatch.')
 dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(prior/entry['asset'],dest);assert ref(dest)['sha256']==SHA
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 terrain=STAGE/'government-native-stanford-original-v1-20261015.json';shutil.copyfile(prior/'terrain.json',terrain)
 t={'source':str(terrain.relative_to(ROOT)),'sha256':ref(terrain)['sha256'],'destination':'city/data/'+terrain.name,'resolution':5,'area':'Grand Stanford original-source terrain'};destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':'Grand Stanford unchanged combined original','catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':destination}],'topLevelTerrainPatches':[t]})
 config=read(prior/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[t]);save(STAGE/'browser-config.json',config)
 pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for q in refs.values():check(q)
 module('freeze_stanford_stage',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-unchanged-combined-hotel-stage-v1',[Path(__file__),HERE/'acceptance-policy.py',*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*')if p.is_file()]],{'uids':[UID],'privateStageQualified':True,'publisherDryRunPassed':True,'fullAcceptance':False})
 print('Qualified single original source; dry run passed.',flush=True)
if __name__=='__main__':main()
