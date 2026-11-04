"""Exact-source ROOT functional review and private dependency migration; no publication."""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-reviewed-private-stage-v1-20261015';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
OLD=HERE/'accepted/government-xl-citywalk-source-20261004';UID='landsd/134332:0';TOWERS=['landsd/215992:0','landsd/216991:0','landsd/218019:0','landsd/218095:0','landsd/218258:0'];MANIFEST='90c8f904bf574d23c2c50a2b228313f053ac7cb6f93ad9006b106b366bddbca7'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==MANIFEST
 folders=['government-xl-citywalk-current294-face-descriptors-v1-20261015','government-xl-citywalk-cap-podium-coverage-v1-20261015','government-xl-citywalk-candidate-foundation-v1-20261015','government-xl-citywalk-current-neighbours-v1-20261015','government-xl-citywalk-current-runtime-checks-v1-20261015','government-xl-citywalk-ocean-pride-current-support-v1-20261015'];paths=[Path(__file__)];pins={}
 for folder in folders:
  d=BASE/folder;r=read(d/'result.json');paths.append(d/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;paths.append(ROOT/p)
 descriptors=read(BASE/folders[0]/'descriptors.json.gz');assert [r['uid']for r in descriptors['rows']]==TOWERS and sum(r['savedPoints']for r in descriptors['rows'])==294 and sum(len(r['faces'])for r in descriptors['rows'])==461
 foundations=read(BASE/folders[2]/'foundation.json')['rows'];assert len(foundations)==4
 for r in foundations:
  f=r['foundation'];assert f['completeTerrainTriangles']==f['triangles']==41277 and f['fullyBuriedTriangles']==0
 runtime=read(BASE/folders[4]/'policy.json');assert runtime['remainingReasons']==[]
 nativepath=BASE/folders[3]/'native/native-neighbour-checks.json';native=read(nativepath);assert len(native['rows'])==9 and all(r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['rows']);assert not read(BASE/folders[3]/'summary.json')['basicFailures']
 for r in native['rows']:
  if r['uid']in TOWERS:assert r['support']['supportFraction']==1 and len(r['unresolvedSupportDependencies'])==1 and r['unresolvedSupportDependencies'][0]['uid']==UID
 rawpath=BASE/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue/tower-support.json';raw=read(rawpath);assert [r['uid']for r in raw['rows']]==TOWERS and sum(len(r['interfaceProof']['unresolved'])for r in raw['rows'])==294;paths.append(rawpath)
 browserdir=BASE/'government-xl-citywalk-current-private-browser-v3-20261015';report=read(browserdir/'staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==4 and len(report['retainedNativeOwnViews'])==36
 for v in views:assert v['fullyFramed']and v['selectionClosed']and v['fallbackFaces']==0 and v['sourceSHA256']=='b2d26e9f7a3b033877cd8c2aa6e6c363fec2cdcc2c09af8b06a1e3f583ad17df'and all(o==1 for o in v['materialOpacities'])
 for v in report['retainedNativeOwnViews']:assert v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0
 images=[browserdir/v['file']for v in views]+[BASE/'government-xl-citywalk-incident-band-display-v1-20261015'/n for n in ['all-461-facets-opposing-views.png','three-complete-caps.png']]+[BASE/'government-xl-citywalk-saved294-combined-junction-review-v1-20261015/combined-junction-context-2160x1800.png'];paths.extend(images);paths.extend(p for p in browserdir.rglob('*')if p.is_file());paths.extend(p for p in (BASE/'government-xl-citywalk-incident-band-display-v1-20261015').rglob('*')if p.is_file())
 DOC.mkdir();STAGE.mkdir();cat=read(OLD/'catalogue.json');assert len(cat['models'])==1;m=cat['models'][0];assert m['uid']==UID and m['sha256']=='b2d26e9f7a3b033877cd8c2aa6e6c363fec2cdcc2c09af8b06a1e3f583ad17df'
 decision=dict(status='approved-for-integration',reviewer='Codex ROOT',reviewType='exact-original-source-functional-applicability',sourceFunctionalDispositionAccepted=True,scope=dict(target=UID,targetSHA256=m['sha256'],towerSources=[dict(uid=r['uid'],sha256=r['sourceSHA256'])for r in descriptors['rows']],manifestSHA256=MANIFEST),rawStrictInterfaces=ref(rawpath),raw294FailuresRemainNumericallyFailed=True,strictInterfacePassed=False,exactSamplerAttribution=ref(BASE/folders[0]/'descriptors.json.gz'),imagesActuallyInspected=[ref(p)for p in images],interpretation='The 294 samples lie on original lower facade junctions entering the authored podium. The complete461 incident facets include vertical and near-vertical wall bands, a preserved degenerate facet, and three thin horizontal closure caps at the lower band. Their original roof-projected coverage and opposing context views identify embedded lower facade/cap junctions, not294 independent support feet or exposed buried floor slabs. This specific original assembly is accepted at its fixed source placement; no contact tolerance is increased and raw strict results remain false.',horizontalCapsRetained=[dict(uid=TOWERS[0],faces=[2691,3173]),dict(uid=TOWERS[1],faces=[2815])],projectionFloat64ResidualsNotPromotedToExactCertificate=True,noIndependentFootingOrEngineeringCertificate=True,noGeometryOrPlacementChanges=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publication=False,installationApproved=False)
 save(DOC/'ROOT-functional-review.json',decision)
 save(DOC/'terrain-regression-disposition.json',dict(raw=ref(nativepath),allNineIntroducedBurialCountsZero=True,ordinaryFormsChecked=292,ordinaryFailures=0,visionCityFiveResolvedOnlyByExactFunctionalReview=ref(DOC/'ROOT-functional-review.json'),oceanPride=dict(uid='landsd/162512:0',supportUid='landsd/175935:0',currentStrictPair=ref(BASE/folders[-1]/'result.json'),strictUnresolved=22,sourcePairUnchangedByTerrain=True,podiumNativeRegressionPassed=next(r['passed']for r in native['rows']if r['uid']=='landsd/175935:0'),sourceSupportReapproved=False,publicationFlagUntouched=True,reason='Existing tower and original podium bytes, transforms and source-to-source query are unchanged. Candidate ground remains below the tower and adds no buried faces; podium passes full native regression. The current pair issue is retained, not introduced or resolved by Citywalk terrain.')))
 # Only dependency metadata changes on the five existing towers. Preserve assets and all other fields.
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');changes=[];catalogues=[];replacements=[]
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;c=read(p);modified=copy.deepcopy(c);touched=[]
  for e in modified['models']:
   if e['uid']not in TOWERS:continue
   original=copy.deepcopy(e['supportDependencies']);updated=copy.deepcopy(original)
   for dep in updated:
    if dep['uid']==UID:assert dep['state']=='surveyed-footprint-fallback'and dep['csuid']==m['buildingCSUID'];dep.update(state='installed',sha256=m['sha256'])
   changes.append(dict(uid=e['uid'],catalogue=str(p.relative_to(ROOT)),modelSHA256=e['sha256'],modelId=e['modelId'],buildingCSUID=e['buildingCSUID'],oldSupportDependencies=original,supportDependencies=updated));e['supportDependencies']=updated;touched.append(e['uid'])
  if touched:
   out=STAGE/f'dependency-catalogue-{len(catalogues)}.json';save(out,modified);replacements.append(dict(url=url,source=str(out.relative_to(ROOT))));catalogues.append(dict(source=str(p.relative_to(ROOT)),url=url,oldSHA256=digest(p.read_bytes()),models=touched));paths.append(p)
 assert sorted(c['uid']for c in changes)==TOWERS
 save(DOC/'dependency-review.json',dict(contactReport=str(rawpath.relative_to(ROOT)),contactReportSHA256=digest(rawpath.read_bytes()),sourceFunctionalReview=ref(DOC/'ROOT-functional-review.json'),catalogues=catalogues,changes=changes,requiresNewNativeUids=[UID],rawStrictFailuresPreserved=True))
 m.update(proceduralWindows=False,placementReviewed=True,publicationApproved=True,sourceIdentityReviewed=True,identityReviewApproved=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,placementReview='Unchanged original Citywalk at fixed source placement. Current full foundation, runtime and whole-parent neighbours verified; exact source-functional review retains294 raw tower lower-facade junction failures without changing tolerances.');cat['area']='Citywalk original government source';save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(STAGE/'source-forms.json',read(OLD/'source-forms.json'));asset=STAGE/m['asset'];asset.parent.mkdir(parents=True);shutil.copyfile(OLD/m['asset'],asset);assert digest(asset.read_bytes())==m['sha256']
 candidate=read(BASE/folders[2]/'plan.json')['terrainOverride'];patch=read(ROOT/candidate['path']);terrainfile=STAGE/'government-native-citywalk-reviewed-20261015.json';shutil.copyfile(ROOT/candidate['path'],terrainfile);assert digest(terrainfile.read_bytes())==candidate['sha256'];retained=['landsd/305615:0','landsd/273839:0'];assert all(next(r['passed']for r in native['rows']if r['uid']==u)for u in retained)
 save(DOC/'native-replacement-review.json',dict(status='approved-for-integration',supersededURL=candidate['replaces']['url'],supersededSHA256=candidate['replaces']['sha256'],replacementSHA256=candidate['sha256'],sourceGeometryChanged=False,aiCalls=0,modelGeometryChanges=0,retainedUids=retained,replacementTargetUids=patch['meta']['targetUids'],fullMeshCheck=ref(nativepath),completeNineActorDisposition=ref(DOC/'terrain-regression-disposition.json')))
 terrain=dict(source=str(terrainfile.relative_to(ROOT)),sha256=candidate['sha256'],destination='city/data/'+terrainfile.name,resolution=patch['cell'],area=cat['area'],replaces={**candidate['replaces'],'retainedUids':retained},nativeReview=ref(DOC/'native-replacement-review.json'));destination='city/data/official-models/'+BATCH+'/catalogue.json'
 dep=ref(DOC/'dependency-review.json');dep['visualApproval']=ref(DOC/'ROOT-functional-review.json');save(STAGE/'plan.json',dict(areas=[dict(area=cat['area'],catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[terrain],dependencyReviews=[dep]))
 cfg=read(browserdir/'browser-config.json');cfg.update(stage=str(STAGE.relative_to(ROOT))+'/',catalogueURL=destination,terrain=[terrain],catalogueReplacements=replacements,doc=str(DOC.relative_to(ROOT))+'/browser/');save(STAGE/'browser-config.json',cfg)
 paths.extend(p for p in STAGE.rglob('*')if p.is_file());save(DOC/'stage.json',dict(private=True,publication=False,installed=False,plan=ref(STAGE/'plan.json'),sourceFunctionalReview=ref(DOC/'ROOT-functional-review.json'),dependencyCount=5,nextStep='Guarded publisher dry run, fresh staged browser with dependency metadata, then guarded live publication and exact installed ledger readback.'))
 module('citywalk_private_stage_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-reviewed-private-stage-v1',paths,dict(uids=[UID,*TOWERS],sourceFunctionalDispositionAccepted=True,fullAcceptance=False,publication=False,newlyInstalled=0))
 print('Private stage ready; no live files changed',flush=True)
if __name__=='__main__':main()
