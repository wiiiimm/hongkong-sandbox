"""Named exact-source Yoho original-pair review; no publication or geometry edits."""
import argparse,copy,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from retained_native_nonregression_v1_20261023 import terrain_decision
from yoho_original_pair_contract_v1_20261102 import SOURCES,SUPPORTS,GROUND_OWNERS,FACES,MODES,TERRAIN_SHA,OLD_TERRAIN_SHA,verify_models,verify_targets,verify_atomic,verify_authored_junction
P='government-xl-yoho-mall-ii273672-';BASE=ROOT/'docs/astra-city/government-import'
EXPECTED_FOREIGN={'landsd/2869:0':118,'landsd/2924:0':165,'landsd/2939:0':165,'landsd/3006:0':127,'landsd/3007:0':68,'landsd/5892:0':52,'landsd/49041:0':0,'landsd/112487:0':48,'landsd/127231:0':747,'landsd/300868:0':0,'landsd/329088:0':0,'landsd/329089:0':0,'landsd/335513:0':0}

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--inspection',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args();batch=P+'final-original-review-v1-20261102';out=BASE/batch;lp=HERE/'local'/batch/'reservation.json';assert not out.exists()
 resources=read(BASE/(P+'cached-tin-v1-20261102-command.json'))['resources']
 if not a.owned:
  assert not lp.parent.exists();c=reservations.claim('yoho-exact-pair-review-'+str(uuid.uuid4()),resources,batch=batch,ttl=3600);assert c['ok'],c
  return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--inspection',a.inspection,'--owned'])
 lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),HERE/'yoho_original_pair_contract_v1_20261102.py',HERE/'retained_native_nonregression_v1_20261023.py'];pins={}
 def take(name,file='summary.json',local=False):
  if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
  path=(HERE/'local'/name if local else BASE/name)/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 def summary(suffix):return take(P+suffix)
 runtime=P+'two-originals-v2-20261102-runtime';attrs=P+'two-originals-v2-20261102-attributes';browser=P+'two-originals-private-preview-v3-20261102'
 selection=take(runtime,'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256'];refs.append(manifest)
 current={}
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for m in read(path)['models']:assert m['uid']not in current;current[m['uid']]=m
 assert len(current)==7092 and not set(SOURCES)&set(current)
 for row in selection['rows']:
  path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==SOURCES[row['uid']];refs.append(path)
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert [b for b in read(tile)['buildings']if b['uid']==row['uid']]==[row['source']['building']];refs.append(tile)
 identity=summary('two-originals-v2-20261102-identity');assert len(identity['rows'])==2 and {r['uid']for r in identity['rows']}==set(SOURCES)and all(r['passed']and not r['reasons']for r in identity['rows'])
 metrics=take(runtime,'metrics.json');assert len(metrics['rows'])==2
 for r in metrics['rows']:
  assert r['sourceSHA256']==SOURCES[r['uid']]and r['sourcePreserved']and r['missingTerrain']==r['missingDrawnTerrain']['count']==r['samplerDisagreement']['count']==0 and r['maxSamplerDelta']<=.004
 for key in ['geometryBytes','residentBytes','triangles','drawCalls']:assert sum(r['budget'][key]for r in metrics['rows'])<=metrics['profiles']['mobile'][key]
 strict=summary('two-originals-v2-20261102-support');roots=summary('original-rooftop-roots-v1-20261102-paths');census=summary('rooftop-compound-face-census-v1-20261102-faces');pairs=summary('original-rooftop-pair-context-v1-20261102');assert verify_authored_junction(strict,roots,census,pairs)
 for mode in MODES:
  detail=take(P+'rooftop-compound-face-census-v1-20261102-faces',mode+'.json');assert len(detail['faces'])==1;face=detail['faces'][0];assert face['sourceFace']==10 and abs(face['signedNormalYRatio'])<=.25 and 10<face['areaM2']<11
  take(P+'original-rooftop-roots-v1-20261102-paths',mode+'.json.gz')
  take(P+'two-originals-v2-20261102-support',mode+'/input.json.gz')
  pair=next(r for r in pairs['rows']if r['mode']==mode);path=ROOT/pair['rawPath'];raw=take(P+'original-rooftop-pair-context-v1-20261102',path.name);assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
 # Reuse prior exact floor/wall proofs only after complete array equivalence.
 oldruntime=P+'floor-regression-v2-20261102-runtime';oldattrs=P+'floor-regression-v2-20261102-attributes'
 oldg=take(oldruntime,'runtime-geometry.json.gz',True)['rows'];newg=take(runtime,'runtime-geometry.json.gz',True)['rows'];old=next(r for r in oldg if r['uid']=='landsd/273672:0');new=next(r for r in newg if r['uid']=='landsd/273672:0')
 for key in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(old[key]),np.asarray(new[key]))
 olda=next(r for r in take(oldattrs,'attributes.json.gz')['rows']if r['uid']=='landsd/273672:0');newa=next(r for r in take(attrs,'attributes.json.gz')['rows']if r['uid']=='landsd/273672:0')
 for key in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(np.asarray(olda[key]),np.asarray(newa[key]))
 foundation=summary('floor-regression-v2-20261102-foundations');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4 and all(r['triangles']==r['completeTerrainTriangles']==24004 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
 low=summary('ground-context-v2-20261102-clearance');grade=summary('positive-grade-walls-v1-20261102');below=summary('final-below-grade-context-v1-20261102')
 assert all(r['allAffectedWallLike']for r in low['rows'])and len(low['rows'])==4
 assert len(below['rows'])==4 and all(r['negativeFaces']==r['negativeWalls']==742 and not r['negativeNonWallFaces']and not r['downwardGroups']for r in below['rows'])
 assert len(grade['rows'])==4 and all(r['allPositiveFiniteGradeContactsRecomputed']and r['allTopsExceedCompleteLocalGroundUpperBound']and r['minimumExposedMargin']>5 for r in grade['rows'])
 fallback=summary('actual-basic-fallback-support-v1-20261102');assert fallback['currentBasicFallbackSupportPassed']and fallback['rawSupportProof']['samples']==fallback['rawSupportProof']['strictContacts']==126 and not fallback['rawSupportProof']['unresolved']
 models=take(browser,'catalogue.json',True)['models'];assert verify_models(models)
 atomic=take(P+'atomic-lifecycle-v1-20261102','report.json');assert verify_atomic(atomic,models)
 scope=summary('original-neighbour-pair-v1-20261102-scope');assert scope['currentManifestSHA256']==mh and set(scope['uids'])==set(SOURCES)and all(not r['nearbyNativeActors']for r in scope['rows'])
 foreign=[]
 for uid in SOURCES:
  name=P+'original-neighbour-pair-v1-20261102-foreign-'+uid.split('/')[1].split(':')[0];report=take(name);basic=take(name,'basic.json');forms={r['uid']:r['currentBuilding']for r in basic['rows']}
  for path,sha in basic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
  if uid=='landsd/273672:0':assert {r['foreignUid']for r in report['rows']}==set(EXPECTED_FOREIGN)
  else:assert len(report['rows'])==1 and report['rows'][0]['foreignUid']=='landsd/273672:0'
  for pair in report['rows']:
   modes={r['mode']:r for r in pair['modes']};assert len(modes)==5 and set(modes)==MODES|{'before-basic'}
   expected=EXPECTED_FOREIGN[pair['foreignUid']]if uid=='landsd/273672:0' else 33
   assert all(modes[m]['positiveContactPairs']==expected for m in MODES)
   if expected:assert forms[pair['foreignUid']]['parent']=='way/187110731'and modes['before-basic']['positiveContactPairs']>0
   for m in MODES:
    file=uid.split('/')[1]+'--'+pair['foreignUid'].split('/')[1]+'--'+m+'.json.gz';raw=take(name,file);assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
   foreign.append(copy.deepcopy(pair))
 raw=summary('current-checks-v2-20261102-neighbours');assert raw['forms']==259 and len(raw['nativeRows'])==len(raw['requiredNativeUids'])==15 and raw['basicFlags']==[dict(uid='landsd/3007:0',reasons=['increased-neighbour-ground-gap'])]
 qualified=[];contexts=[]
 for row in raw['nativeRows']:
  if row['passed']:qualified.append(copy.deepcopy(row));continue
  assert row['uid']in ['landsd/294858:0','landsd/300857:0'];context=summary('unchanged-native-context-v1-20261102-'+row['uid'].split('/')[1].split(':')[0]);contexts.append(context);qualified.append({**copy.deepcopy(row),**terrain_decision(row,context,current)})
 assert len(contexts)==2 and all(r['passed']for r in qualified)
 patch=summary('current-checks-v2-20261102-binding');assert patch['candidate']['sha256']==TERRAIN_SHA;replacement=patch['candidate']['replaces'];assert replacement['sha256']==OLD_TERRAIN_SHA
 oldpath=ROOT/'3d-viewer'/replacement['url'];newpath=ROOT/patch['candidate']['path'];assert digest(oldpath.read_bytes())==OLD_TERRAIN_SHA and digest(newpath.read_bytes())==TERRAIN_SHA;assert verify_targets(read(oldpath),read(newpath));refs.extend([oldpath,newpath])
 observation_path=(ROOT/a.inspection).resolve();assert observation_path.is_relative_to(BASE);observation=read(observation_path);assert observation['reviewer']=='Codex ROOT'and observation['allDeclaredExportsActuallyInspected']is True;refs.append(observation_path)
 observed={r['path']:r['sha256']for r in observation['imagesActuallyViewed']};assert len(observed)==len(observation['imagesActuallyViewed'])==68
 primary=[];retained=[];reports=[]
 for width in [1280,390]:
  name=str(width)+'/staged-browser.json';report=take(browser,name);assert report['passed']and not report['errors'];views=[v for v in report['views']if'time'in v];assert len(views)==4 and len(report['retainedNativeOwnViews'])==30
  for v in views:
   assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
  for v in views+report['retainedNativeOwnViews']:
   path=BASE/browser/str(width)/v['file'];assert observed[str(path.relative_to(ROOT))]==digest(path.read_bytes());refs.append(path);entry=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=v['uid'],time=v['time'],width=width);(primary if v['uid']in SOURCES else retained).append(entry)
  assert all(v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and v['sourceSHA256']==current[v['uid']]['sha256']for v in report['retainedNativeOwnViews'])
  path=BASE/browser/name;reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
 assert len(primary)==8 and len(retained)==60 and {r['uid']for r in retained}==set(raw['requiredNativeUids'])
 qualified_native={**copy.deepcopy(raw),'basicFlags':[],'rawBasicFlags':copy.deepcopy(raw['basicFlags']),'nativeRows':qualified,'nativeResolved':sorted(raw['requiredNativeUids']),'rawNativeRows':copy.deepcopy(raw['nativeRows']),'coimportRequiredSources':SOURCES,'coimportRequiredAtomicGroup':sorted(SOURCES),'coimportedBasicUid':'landsd/3007:0','legacySupportFailuresReapproved':False,'nonregressionOnly':True,'qualification':'Only for the exact jointly installed atomic original pair. BASIC3007 is replaced by its authenticated original; complete pair fallback is tested and actual BASIC support passes126/126. Raw flags remain. Two old installed support negatives are exact whole-terrain nonregression decisions only.'}
 save(out/'summary.json',qualified_native);save(out/'neighbour-checks.json',take(P+'current-checks-v2-20261102-neighbours','neighbour-checks.json'))
 identity_proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,terrainOwnerUids=sorted(GROUND_OWNERS),supportByUid=SUPPORTS,requiredAtomicGroup=sorted(SOURCES),identityAccepted=True,identityProof=identity_proof,identityProofByUid={u:identity_proof for u in SOURCES},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),completeFourWorldFoundations=True,completeCurrentNeighbourChecks=259,retainedNativeRegression=qualified_native,retainedNativeUids=raw['requiredNativeUids'],installedMetadataChanges=False,exactTerrainReplacement=replacement,terrainCandidate=patch['candidate'],leaseResources=sorted(resources),imagesActuallyViewed=primary,retainedImagesActuallyViewed=retained,browserReports=reports,rawCompoundSupport=strict,canonicalRootPaths=roots,compoundFaceCensus=census,rawOriginalPairContacts=pairs,rawForeignInterfaces=foreign,rawMissingCapWarnings=below['rows'],positiveColumnGradeContext=grade,actualBasicFallbackSupport=fallback,atomicLifecycle=dict(path=str((BASE/(P+'atomic-lifecycle-v1-20261102')/'report.json').relative_to(ROOT)),sha256=digest((BASE/(P+'atomic-lifecycle-v1-20261102')/'report.json').read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,qualification='Exact source-specific original pair acceptance, pending separate guarded publication/live verification. Original wall10 is a near-vertical authored junction wall beneath the maximum overhead podium/walkway envelope, not a buried floor or terrain-placement offset. All34 low-rim witnesses reach six genuine strict anchors through unchanged original edges without rising above endpoint ceilings. Every actual-ground negative is an original wall; complete main foundations have zero wholly buried faces and remaining columns intersect real grade with exposed tops. Preserve the raw maximum-surface and missing-cap negatives. Positive foreign contacts are retained same-parent podium/tower/junction interfaces already present in the BASIC composition; no disjointness, blanket collision waiver, new BASIC support dependency or whole-landmark completeness is claimed. Exact companion3007 replaces its coarse form only with both originals jointly available; independent peer failure/retry, Base/Auto/eviction and126/126actual BASIC fallback contacts pass. All15 installed actors retain geometry/metadata and full terrain-change checks; old support failures are not reaccepted.')
 save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
 module('yoho_exact_final_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'named-exact-original-pair-functional-physical-and-image-review',list(dict.fromkeys(refs)),dict(**qualified_native,sourceReviewAccepted=True,installationApproved=False,publication=False));print(dict(sourceReviewAccepted=True,models=2,retained=15,publication=False),flush=True)
if __name__=='__main__':main()
