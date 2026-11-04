"""Qualify three unchanged Opus originals, retaining scoped raw diagnostics."""
from pathlib import Path
import copy,shutil,sys
from shapely.geometry import MultiPoint,Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-opus-'
BATCH=PREFIX+'qualified-stage-v1-20261017';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
PODIUM='landsd/248432:0';TOWER='landsd/322573:0';COMPANION='landsd/319559:0'
SOURCES={PODIUM:'413249980adc12dffbe589ec5db87a66075682c71e134b0e21a74d228d85f72e',TOWER:'e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764',COMPANION:'ae3e7059569519540c4136e2296a107e5c1f6da7d2895ed2ca56881f6bee3e17'}
NAMES=['basic-ground-capture-v2','basic-finite-v1','current-native-scope-v2','stable-assembly-identity-v1','source-support-review-v1','original-patch-roles-v1','assembly-original-patch-v1','original-group-v1','loader-validation-v1','original-group-browser-v1']
PREVIOUS=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json'
def folder(n):return BASE/(PREFIX+n+'-20261017')
def data(n,f):return read(folder(n)/f)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify():
 refs={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in NAMES:
   p=folder(n)/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']+[ref(p)]:assert q['path']not in refs or refs[q['path']]==q;refs[q['path']]=q
 for q in refs.values():assert ref(ROOT/q['path'])==q
 return refs

def main():
 assert not DOC.exists()and not STAGE.exists();refs=verify()
 finite=data('basic-finite-v1','summary.json');assert finite['all2ActorsComplete']and finite['noIntroducedFailures']and len(finite['rows'])==2
 assert all(not r['introducedUnproved']and not r['afterUncovered']for r in finite['rows'])
 capture=data('basic-ground-capture-v2','capture-report.json.gz');assert capture['strictExteriorUnchanged']and capture['startEndAllInputsVerified']and capture['basicActors']==2
 native=data('current-native-scope-v2','scope.json');assert native['allCurrentActorsNominated']and native['currentCatalogueFormSourceAndModuleBytesUnchanged']and native['currentNativeActors']==6668 and not native['touchingNativeUids']
 full=data('assembly-original-patch-v1','summary.json');assert full['originalFaces']==13557 and full['fourWorldGeometryByteIdentical']and not full['currentUncovered']and len(full['ordinaryFailures'])==131
 identity=data('stable-assembly-identity-v1','ROOT-SOURCE-REVIEW.json');support=data('source-support-review-v1','ROOT-SUPPORT-REVIEW.json');roles=data('original-patch-roles-v1','ROOT-SOURCE-REVIEW.json')
 assert identity['sourceIdentityRelationshipAccepted']and {r['uid']:r['sourceSHA256']for r in identity['measurements']}==SOURCES
 assert support['sourceSpecificSupportAccepted']and support['sourceSHA256ByUid']==SOURCES and support['requiredOriginalPodiumUid']==PODIUM and set(support['dependentUids'])=={TOWER,COMPANION}
 assert roles['sourceRoleInterpretationAccepted']and roles['sourceSHA256']==SOURCES[PODIUM]and roles['foundation']['fullyBuriedUpwardTriangles']==0
 assert roles['groundSHA256']==support['groundSHA256']and roles['worldSHA256']==support['worldSHA256']
 metrics=copy.deepcopy(data('original-group-v1','metrics.json'));selection=data('original-group-v1','selection.json.gz')['rows'];r=next(r for r in selection if r['uid']==COMPANION)
 # Restore the missing diagnostic fields using the converter's same convex-hull formula,
 # against this exact viewer footprint (not a current service ObjectID substitute).
 asset=ROOT/r['candidate']['path'];assert ref(asset)['sha256']==SOURCES[COMPANION]
 tri=decode_original_world_triangles(asset.read_bytes());hull=MultiPoint(tri[:,:,[0,2]].reshape(-1,2)).convex_hull;b=r['source']['building'];shape=Polygon(b['rings'][0],b['rings'][1:])
 diagnostic=dict(overlap=hull.intersection(shape).area/max(.001,min(hull.area,shape.area)),centroidDistance=hull.centroid.distance(shape.centroid))
 companion=next(m for m in metrics['rows']if m['uid']==COMPANION);assert companion['identity']=={};companion['identity']=diagnostic
 policy=module('opus_policy',HERE/'acceptance-policy.py');raw={};remaining={}
 expected={PODIUM:{'terrain-intersects-source-over-0.5m','strict-identity-fit'},TOWER:{'ground-contact-unresolved'},COMPANION:{'ground-contact-unresolved','strict-identity-fit'}}
 for m in metrics['rows']:
  u=m['uid'];raw[u]=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[u]),m,metrics['profiles']['mobile']);assert set(raw[u])==expected[u],(u,raw[u]);remaining[u]=[]
 # Only these enumerated warnings resolve through exact source-role/support/identity
 # reviews above. No thresholds, generic policy, source facets or transforms change.
 loader=data('loader-validation-v1','validation.json');assert len(loader['results'])==3 and all(r['outcome']=='runtime-accepted-placement-unreviewed'for r in loader['results'])
 report=data('original-group-browser-v1','staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==12 and len(report['jointViews'])==6
 for v in views:assert v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]and not v['fallbackFaces']
 for j in report['jointViews']:assert {m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==1 and failed[0]['fallbackRetained']and failed[0]['dependentFallbacks']=={TOWER:{'active':False},COMPANION:{'active':False}}
 review=data('original-group-browser-v1','ROOT-IMAGE-INSPECTION.json');assert review['reviewer']=='Codex ROOT'and review['sourceGeometryAppearanceAccepted']and len(review['reviewedImages'])==4
 for q in review['reviewedImages']:assert ref(ROOT/q['path'])==q
 prior=HERE/'local'/folder('original-group-browser-v1').name;cat=read(prior/'catalogue.json');assert {e['uid']:e['sha256']for e in cat['models']}==SOURCES
 previous=read(PREVIOUS);assert previous['manifestSHA256']==ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256'];fixed={r['uid']:r for r in previous['rows']if r['uid']in SOURCES}
 assert fixed and all(not r['installedVerified']and r['indexedSourceSHA256']==SOURCES[u]for u,r in fixed.items())
 DOC.mkdir();STAGE.mkdir();save(DOC/'completed-policy-metrics.json',metrics)
 qualification=dict(sourceSHA256ByUid=SOURCES,currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),privateStageQualified=True,rawPolicyReasons=raw,remainingPolicyReasons=remaining,sourceIdentityReview=ref(folder('stable-assembly-identity-v1')/'ROOT-SOURCE-REVIEW.json'),sourceSupportReview=ref(folder('source-support-review-v1')/'ROOT-SUPPORT-REVIEW.json'),foundation=ref(folder('original-patch-roles-v1')/'ROOT-SOURCE-REVIEW.json'),fullFinite=ref(folder('assembly-original-patch-v1')/'summary.json'),companionMissingDiagnosticFieldsRecomputed=diagnostic,completeBasicNeighbours=2,completeCurrentNativeActors=6668,touchingNativeActors=0,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False)
 save(DOC/'qualification.json',qualification);save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 for e in cat['models']:
  u=e['uid'];assert e['proceduralWindows']is False and not e.get('suppressesBuildingUids');assert e['supportDependencies']==([]if u==PODIUM else[dict(uid=PODIUM,state='candidate',csuid='3599414486P20120215',sha256=SOURCES[PODIUM])])
  e.update(label=e.get('label')or ('Opus Hong Kong podium'if u==PODIUM else 'Opus Hong Kong original companion'if u==COMPANION else 'Opus Hong Kong'),sourceIdentityReviewed=True,identityReviewApproved=True,placementReviewed=True,publicationApproved=True,sourceIdentityReview=qualification['sourceIdentityReview'],sourceFunctionalApplicability=ref(DOC/'qualification.json'),aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,placementReview='Unchanged originals at source pose and 1x scale. Exact stable-primary assembly identity, original wall/podium support and lower-skin interpretation; complete terrain, retained neighbours and staged desktop/mobile checks. Raw diagnostics retained in qualification.')
  if u in fixed:e['originalSourceKey']=fixed[u]['sourceKey']
  dest=STAGE/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(prior/e['asset'],dest);assert ref(dest)['sha256']==e['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));shutil.copyfile(prior/'source-forms.json',STAGE/'source-forms.json')
 config=read(prior/'browser-config.json');t=dict(config['terrain'][0]);assert not t.get('replaces');terrain=STAGE/'opus-original-terrain.json';shutil.copyfile(ROOT/t['source'],terrain);t.update(source=str(terrain.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',area='Opus original terrain');assert ref(terrain)['sha256']==t['sha256']
 destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',dict(areas=[dict(area='Opus Hong Kong original assembly',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[t]));config.update(stage=str(STAGE.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[t]);save(STAGE/'browser-config.json',config)
 pub=module('opus_stage_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();assert not read(pub.DOC/'publication-plan.json')['published']
 for q in refs.values():assert ref(ROOT/q['path'])==q
 paths=[Path(__file__),HERE/'acceptance-policy.py',PREVIOUS,folder('original-group-browser-v1')/'ROOT-IMAGE-INSPECTION.json',*[ROOT/p for p in refs],*[p for p in STAGE.rglob('*')if p.is_file()],HERE.parent/'island-detail-integration/publish.py']
 out=module('opus_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-three-original-opus-private-stage-v1',paths,dict(uids=list(SOURCES),privateStageQualified=True,publisherDryRunPassed=True,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],publisherDryRunPassed=True,fixedXLUids=list(fixed)),flush=True)
if __name__=='__main__':main()
