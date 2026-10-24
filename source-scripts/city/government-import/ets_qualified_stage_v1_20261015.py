"""Qualify the unchanged station podium and retained regional terrain children."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-qualified-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
UID='landsd/323703:0';SHA='4f483e0d26cd40ba3bf93c6edd1e8485e5d11c2d7cde3cd9243651f0505784ea'
FOLDERS=['bounded-gap-infill-v4','basic-ground-capture-v1','basic-finite-v1','native-parent-scope-v1','native-ground-capture-v1','native-finite-v1','four-world-ground-v1','current-loader-validation-v1','current-placement-metrics-v1','private-browser-v2','original-source-review-v1']
def folder(n):return BASE/('government-xl-ets-'+n+'-20261015')
def data(n,f):return read(folder(n)/f)
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def verify_inputs():
 refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for n in FOLDERS:
   d=folder(n);r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(d/'result.json')]:
    assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():assert ref(ROOT/q['path'])==q
 return refs

def main():
 assert not DOC.exists()and not STAGE.exists();refs=verify_inputs()
 identity=data('original-source-review-v1','ROOT-SOURCE-REVIEW.json');assert identity['identityAccepted']and identity['sourceSHA256']==SHA and identity['primaryUID']==UID and not identity['policyExceptions']and not identity['exactLegacyGeoRefClaimed']
 ground=data('four-world-ground-v1','summary.json');assert len(ground['rows'])==4 and ground['allFourModesCovered']and ground['allFourModesUnburied']
 for r in ground['rows']:assert not r['continuousBelowHalfMetreFaces']and not r['exactUncoveredFaces']and r['foundation']['completeTerrainTriangles']==r['foundation']['triangles']==10610 and r['foundation']['fullyBuriedTriangles']==0
 basic=data('basic-finite-v1','summary.json');assert basic['all9ActorsComplete']and basic['noIntroducedFailures']and len(basic['rows'])==9
 assert all(not r['introducedUnproved']and not r['afterUncovered']for r in basic['rows'])
 assert data('native-parent-scope-v1','result.json')['touchingNativeUids']==['landsd/159863:0']
 native=data('native-finite-v1','summary.json');assert native['uid']=='landsd/159863:0'and native['noIntroducedFailures']and len(native['rows'])==4
 assert all(r['completeFaces']==32225 and not r['introducedUnproved']and not r['introducedUncovered']for r in native['rows'])
 assert data('native-ground-capture-v1','result.json')['strictExteriorUnchanged']
 report=data('private-browser-v2','staged-browser.json');views=[v for v in report['views']if 'time'in v];assert report['passed']and not report['errors']and len(views)==4
 assert {(v['width'],v['time'])for v in views}=={(w,t)for w in [1280,390]for t in ['15:00','22:00']}
 for v in views:assert v['sourceSHA256']==SHA and v['originalTriangles']==10610 and v['fullyFramed']and v['pick']==v['collision']==UID and v['fallbackFaces']==0
 failure=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failure)==1 and failure[0]['fallbackRetained']
 prior=HERE/'local'/folder('private-browser-v2').name;cat=read(prior/'catalogue.json');assert len(cat['models'])==1;entry=cat['models'][0];assert entry['sha256']==SHA and cat['rootTranslation']==[-834500,0,816500]
 terrainref=data('current-loader-validation-v1','terrain-candidates.json')[0];patch=read(prior/'terrain.json');old=read(ROOT/'3d-viewer'/terrainref['replaces']['url']);assert patch['patches'][:-1]==old['patches'] and {k:v for k,v in patch.items()if k!='patches'}=={k:v for k,v in old.items()if k!='patches'}
 DOC.mkdir();STAGE.mkdir()
 save(DOC/'ROOT-IMAGE-INSPECTION.json',{'reviewer':'Codex ROOT','visualAcceptance':True,'imagesActuallyViewed':[ref(folder('private-browser-v2')/v['file'])for v in views],'observation':'All four high-angle desktop/mobile day/night images inspected. Full original podium and curved platform visible; no fabricated window skin. Night contrast follows scene lighting. Earlier oblique mobile captures retained but not used for approval because foreground buildings obscured the platform. No neighbouring buildings hidden or suppressed.'})
 qualification={'uids':[UID],'sourceSHA256ByUid':{UID:SHA},'currentManifest':ref(ROOT/'3d-viewer/city/data/manifest.json'),'rawPolicyReasons':[],'remainingPolicyReasons':[],'identityReconciliation':ref(folder('original-source-review-v1')/'ROOT-SOURCE-REVIEW.json'),'sourceGeometryChanges':0,'sourcePoseChanges':0,'basicNeighbours':9,'touchingNativeActors':1,'privateStageQualified':True,'publication':False};save(DOC/'qualification.json',qualification)
 source=next(r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if r['modelId']==entry['modelId'])
 entry.update(label='East Tsim Sha Tsui Station podium / Middle Road Playground',sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,originalSourceKey=source['sourceKey'],sourceIdentityReview=qualification['identityReconciliation'],sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Original station podium at unchanged source pose and 1x scale. Existing identity-fit, contact, four-mode complete source and neighbour checks pass. Regional terrain grid and all prior children preserved.')
 dest=STAGE/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(prior/entry['asset'],dest);assert ref(dest)['sha256']==SHA
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 terrain=STAGE/'government-regional-ets-original-v1-20261015.json';shutil.copyfile(prior/'terrain.json',terrain)
 t={'source':str(terrain.relative_to(ROOT)),'sha256':ref(terrain)['sha256'],'destination':'city/data/'+terrain.name,'resolution':patch['cell'],'area':'Regional terrain retaining all children plus East Tsim Sha Tsui original','replaces':terrainref['replaces']};destination='city/data/official-models/'+BATCH+'/catalogue.json'
 save(STAGE/'plan.json',{'areas':[{'area':'East Tsim Sha Tsui unchanged original','catalogue':str((STAGE/'catalogue.json').relative_to(ROOT)),'destination':destination}],'topLevelTerrainPatches':[t]})
 config=read(prior/'browser-config.json');config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[t]);save(STAGE/'browser-config.json',config)
 pub=module('ets_existing_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for q in refs.values():assert ref(ROOT/q['path'])==q
 module('freeze_ets_stage',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-unchanged-station-stage-v1',[Path(__file__),HERE/'acceptance-policy.py',*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*')if p.is_file()]],{'uids':[UID],'privateStageQualified':True,'publisherDryRunPassed':True,'fullAcceptance':False})
 print('Qualified single station original; dry run passed.',flush=True)
if __name__=='__main__':main()
