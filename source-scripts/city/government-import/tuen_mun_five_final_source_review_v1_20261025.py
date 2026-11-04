"""Bind ROOT's bounded Tuen Mun source review to exact completed evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tuen-mun-five-final-source-review-v1-20261025'
CONFIG=BASE/'government-xl-tuen-mun-five-private-browser-config-v2-20261025.json'
COUNTS={'landsd/290803:0':17607,'landsd/196123:0':383,'landsd/200057:0':26,'landsd/200059:0':103,'landsd/34417:0':97}

def main():
 out=BASE/BATCH;assert not out.exists();config=read(CONFIG);sources=config['sources'];refs=[Path(__file__),CONFIG];pins={};receipts={}
 def take(batch,name='summary.json'):
  if batch not in pins:receipts[batch],pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
  path=BASE/batch/name
  if name=='result.json':assert read(path)==receipts[batch]
  else:assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
  refs.append(path);return read(path)
 selected=take(config['runtime'],'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selected['rows']}==sources
 raw={}
 for row in selected['rows']:
  uid=row['uid'];number=uid.split('/')[1].split(':')[0];assert row['triangles']==COUNTS[uid]
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==sources[uid];refs.append(asset)
  entry=row['candidate']['entry'];assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
  identity=take('government-xl-tuen-mun-five-protected-identity-v1-20261025',number+':0/identity.json')
  assert identity['sourceSHA256']==sources[uid] and identity['originalOwnership']['sourceGraphVerified']
  assert identity['exactCurrentComponentRoute']['qualified'] and identity['freshCurrentIdentity']['exactObjectAndCSUID']
  assert identity['exactWholeCellCoverage']['covered']and identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==COUNTS[uid]
  raw[uid]=identity['reasons']
  foundation=take(f'government-xl-tuen-mun-{number}-protected-seams-foundations-v1-20261025')
  assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
  for r in foundation['rows']:assert r['completeTerrainTriangles']==COUNTS[uid]and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedAreaFraction']<=.001
 primary=take('government-xl-tuen-mun-five-primary-records-v1-20261025');assert not primary['missingRequestedCSUIDs']and primary['footprints']==5
 compound=take('government-xl-tuen-mun-five-compound-projection-v1-20261025');assert compound['sourceSHA256ByUid']==sources and compound['completeOriginalFaces']==18216
 for r in compound['rows']:
  assert r['wholeCellCoveredByOriginalAssembly']and r['wholeCellCoveredByCurrentAssembly']and r['ownCoverageByWholeOriginalAssembly']>.99
  expected={'landsd/195434:0','landsd/246548:0','landsd/290799:0','landsd/290801:0'}if r['uid']=='landsd/290803:0'else({'landsd/246548:0'}if r['uid']=='landsd/196123:0'else set())
  assert set(r['sourceExcessOverlapOutsideCurrentAssemblyByForeignUid'])==expected
 for number in [196123,200057,34417]:
  support=take(f'government-xl-tuen-mun-{number}-current-strict-support-v1-20261025')
  assert support['allFourModesPassed']and support['supportUid']=='landsd/290803:0'and support['supportedUid']==f'landsd/{number}:0'and len(support['rows'])==4
 support=take('government-xl-tuen-mun-200059-current-support-paths-v1-20261025')
 assert support['allUnresolvedHaveFinitePaths']and len(support['rows'])==4
 for r in support['rows']:assert r['targets']==r['verifiedPaths']==7 and r['remaining']==0
 continuous=take('government-xl-tuen-mun-five-protected-seams-continuous-v1-20261025');assert len(continuous['rows'])==5 and all(r['upwardContinuousMinimumGapM']>=-.5 for r in continuous['rows'])
 exact=take('government-xl-tuen-mun-five-protected-seams-exact-coverage-v1-20261025');assert len(exact['rows'])==5 and all(not r['stillUncoveredFaces']for r in exact['rows'])
 ground=take('government-xl-tuen-mun-podium-protected-seams-complete-ground-v1-20261025')
 overhead=take('government-xl-tuen-mun-podium-protected-source-overhead-v1-20261025')
 grade=take('government-xl-tuen-mun-three-exposed-wall-grade-context-v1-20261025')
 downward=take('government-xl-tuen-mun-fifty-downward-nonwall-orientation-v1-20261025')
 for rows in [ground['rows'],overhead['rows'],grade['rows'],downward['rows']]:assert len(rows)==4 and {r['mode']for r in rows}=={'original','literal','left','balanced'}
 for g in ground['rows']:
  mode=g['mode'];o=next(r for r in overhead['rows']if r['mode']==mode);c=next(r for r in grade['rows']if r['mode']==mode);d=next(r for r in downward['rows']if r['mode']==mode)
  assert len(g['negativeNonWallFaces'])==50 and set(g['negativeNonWallFaces'])=={f['sourceFace']for f in d['faces']}
  assert d['allDownward']and all(f['signedNormalYRatio']==-1 for f in d['faces'])
  assert o['uncoveredFaces']==([16325,16326,16328]if mode=='literal'else[])
  assert o['covered']==(84 if mode=='literal'else 82)
  assert c['sourceFaces']==[16325,16326,16328]and c['allFacesHaveExactUpperGroundCrossing']and c['allHighestVerticesExposed']and c['allWallLike']
  assert o['unresolvedWallFaces']==(37 if mode=='literal'else 32)
  assert len(g['exactAffectedFaces'])==183
 obligation=take('government-xl-tuen-mun-native-addition-obligations-v1-20261025')
 assert obligation['additiveObligationsVerified']and obligation['forms']==26
 forms=take('government-xl-tuen-mun-native-addition-obligations-v1-20261025','form-obligations.json.gz')
 regression=take('government-xl-tuen-mun-protected-seams-native-neighbours-v1-20261025')
 assert regression['forms']==26 and not regression['basicFlags']and regression['nativeResolved']==['landsd/229481:0']
 native=regression['nativeRows'];assert len(native)==1 and native[0]['passed']and native[0]['triangles']==31087
 assert native[0]['terrain']['newlyWhollyBuried']==native[0]['terrain']['newlyUpwardWhollyBuried']==0
 retained=obligation['retainedNativeEntries'];assert set(retained)=={'landsd/229481:0'}and retained['landsd/229481:0']['publicationApproved']is False
 patch=take(config['patch']);assert patch['status']=='private-terrain-validator-passed'and patch['terrainTriangles']==6335 and not patch['replacedNativeTerrain']
 assert patch['seamCover']['addedDomainAreaM2']<=.25
 scope=take(config['terrainScope'],'scope.json');assert scope['uids']==['landsd/290803:0']and not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
 inspection=take('government-xl-tuen-mun-five-progress-checkpoint-v1-20261025','remaining-work.json')
 assert inspection['privateVisualInspectionCompleted']and len(inspection['imagesActuallyViewed'])==20 and len(inspection['retainedImagesActuallyViewed'])==4 and len(inspection['sourceDiagramsActuallyViewed'])==10
 assert inspection['sourceSHA256ByUid']==sources
 preview=take(config['batch'],'result.json');assert preview['retainedNativeEntries']==retained
 for report in inspection['browserReports']:
  path=ROOT/report['path'];assert digest(path.read_bytes())==report['sha256']==pins[config['batch']][report['path']];refs.append(path)
  r=read(path);assert r['passed']and not r['errors']
 for image in [*inspection['imagesActuallyViewed'],*inspection['retainedImagesActuallyViewed'],*inspection['sourceDiagramsActuallyViewed']]:
  path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256'];refs.append(path)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==obligation['currentManifestSHA256'];refs.append(manifest)
 resources=sorted([('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain:city/data/terrain.json'])
 result=dict(uids=list(sources),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,supportByUid=config['supportByUid'],retainedNativeUids=list(retained),retainedNativeEntries=retained,retainedNativeRegression=regression,installedMetadataChanges=False,
 reviewer='ROOT',identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),
 sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=26,totalNeighbourForms=26,terrainAffectedForms=26,leaseResources=resources,
 visualAcceptance=True,imagesActuallyViewed=inspection['imagesActuallyViewed'],retainedImagesActuallyViewed=inspection['retainedImagesActuallyViewed'],sourceDiagramsActuallyViewed=inspection['sourceDiagramsActuallyViewed'],browserReports=inspection['browserReports'],originalSourceReviewAccepted=True,
 rawIdentityReasonsRetained=raw,rawPhysicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,
 observations=[
 'The exact five government originals retain their source roots, fixed1x/world pose and full18216faces. ExactObjectID/CSUID/currentcomponent/sourcegraph/wholeGeoRefcells identify these sources, not every civic building inferred from the podium label. The shared civic podium includes roofs, lower closures, walls, accesses and projecting returns. Preserve main16.436m extent and raw foreign projections:70.6165m2TownHall290799,.781138m2Parklane246548,tiny195434/290801; library.04258m2Parklane. No neighbour alias, deletion, suppression or ownership inference.',
 'Library196123 and small200057/34417 pass existing strict four-world podium support. Small200059 has7finite original-facet support paths in all4representations despite raw strict false. Adopt only these4source->290803dependencies. BASIC290801/290804 failed direct support; they retain protected current ground and gain no invented support credit.',
 'All183negative mainfaces are explicitly partitioned:133walllike plus50exact downward basal/underside faces. Original/left/balanced101walls have clear original cap paths; remaining32walls and50undersides have clear same-original overhead. Literal96walls have cap paths;84otherfaces have clear original overhead;3remaining verticalwalls16325/16326/16328 have exact positive-dimensional actual-ground interfaces and exposed own highest vertices. Preserve raw cap/overhead aggregate false; these are ordinary original walls crossing grade, not buried upward roofs. No engineering watertightness/per-componentroot or invented roof path claim. Existing foundationfraction.000342035 passes. No source or terrain excavation to expose downward closures.',
 'Final6335face derived terrain preserves the two unsupported BASIC neighbours original ground and closes Float32 seams under existing2mm/.25m2limits. All18216sourcefaces have complete exact ground coverage and upwardminimum-.081494m passes existing-.5m. All26currentforms and full31087face retainednative229481 pass nonregression; legacy399buried/151upward/min-3.264916m and publicationApproved:false remain unchanged, not reapproved.',
 'ROOTopened all24V1privateexports and rejected small200057partialocclusion; all24V2privateexports and10whole-source diagrams were actually inspected. V2oppositecamera exposes the small rooftop part; original grey/darknight and existingBASIClitwindows retained. This review grants no installation credit: guardedadditivepublication,fresh24liveexports and fulloldasset/521/globalBASIC/native readback remain required.'
 ])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
 module('tuen_mun_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-tuen-mun-source-physical-and-visual-review',list(dict.fromkeys(refs)),result)
 print(dict(sources=len(sources),forms=26,installationApproved=False),flush=True)
if __name__=='__main__':main()
