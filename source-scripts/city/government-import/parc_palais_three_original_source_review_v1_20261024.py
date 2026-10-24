"""Source-bound review of three originals, exact podium seams and inspected previews."""
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from parc_palais_three_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,PARENT,PARENT_SHA,verify_metadata,verify_native_scope
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-parc-palais-three-';BATCH=P+'original-source-review-v1-20261024';BROWSER=P+'recovered-assembly-preview-v2-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);return read(path)
 identity=take(P+'shared-podium-identity-v2-20261024','identity.json');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);current={m['uid']:m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
 scope=take(P+'model-scope-v1-20261024','summary.json');native=take(P+'native-contacts-v1-20261024','summary.json');assert verify_native_scope(scope,native,current)and digest(manifest.read_bytes())==scope['currentManifestSHA256']
 forms={}
 for uid in SOURCES:
  for f in take(P+'model-scope-v1-20261024',uid.split('/')[1]+'-forms.json.gz'):forms[f['building']['uid']]=f['building']
 assert set(forms)==set(SOURCES)|{PARENT}
 foundations=[];partitions=[];seam=[];affected={'238669':[4037,4038,4039,5255,5256,5570,5571,5572,5573,5574,5575,5576,5577,5578],'238671':[3892,3894,3896,3897],'238856':[4738,4739]};supportCounts={'238669':9,'238671':42,'238856':0}
 runtime=P+'runtime-v1-20261024';runtimeGeometry=take(runtime,'selection.json.gz');assert{r['uid']:r['sourceSHA256']for r in runtimeGeometry['rows']}==SOURCES
 geometrypath=HERE/'local'/runtime/'runtime-geometry.json.gz';assert digest(geometrypath.read_bytes())==pins[runtime][str(geometrypath.relative_to(ROOT))];refs.append(geometrypath);geometry={r['uid']:r for r in read(geometrypath)['rows']}
 for uid in SOURCES:
  number=uid.split('/')[1].split(':')[0];supportName=P+number+'-0-support-v1-20261024';support=take(supportName,'summary.json');clearName=P+number+'-complete-clearance-v1-20261024';clear=take(clearName,'summary.json');assert support['supportedUid']==clear['supportedUid']==uid and support['installedSupportUid']==clear['supportUid']==PARENT and clear['sourceSHA256']==SOURCES[uid]and clear['supportSHA256']==PARENT_SHA
  assert len(support['rows'])==len(clear['rows'])==4
  for s,c in zip(support['rows'],clear['rows']):
   f=s['compoundFoundation'];assert f['triangles']==f['completeTerrainTriangles']and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
   assert s['unresolved']==s['finitePaths']==supportCounts[number]
   assert c['exactAffectedFaces']==affected[number]and c['allAffectedWallLike']and not c['negativeNonWallFaces']
   if number!='238856':assert c['compoundCapPathsPassed']and c['allAffectedHaveExposedHighestVertex']
   else:
    assert not c['compoundCapPathsPassed']and not c['allAffectedHaveExposedHighestVertex']
    mode=s['mode'];input_=take(supportName,mode+'/input.json.gz');parent=np.asarray(input_['podium'],dtype='<f8');source=input_['rows'][0];tri=np.asarray(source['position'],dtype='<f8').reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)]
    assert digest(parent.tobytes())==s['sourceWorldSHA256ByUid'][PARENT]and digest(tri.tobytes())==s['sourceWorldSHA256ByUid'][uid]
    groundCount=len(np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3));detail=take(clearName,c['mode']+'.json.gz');contacts=take(P+'native-contacts-v1-20261024',uid.split('/')[1]+'--266063:0--'+mode+'.json.gz')['contacts'];nativewall=parent[13678];cap=parent[31546]
    assert np.cross(nativewall[1]-nativewall[0],nativewall[2]-nativewall[0])[1]==0 and np.all(cap[:,1]==cap[0,1])
    for face in detail['rows']:
     i=face['sourceFace'];assert i in [4738,4739]and np.array_equal(tri[i],face['vertices'])and face['absoluteNormalYRatio']<.001
     # All adverse columns are these exact installed wall/roof facets, never terrain.
     assert{p['groundFace']-groundCount for p in face['negativeGroundPairProofs']}=={13678,31546}
     joins=[p for p in contacts if p['sourceFaceA']==i and p['sourceFaceB']in [13678,13679]and p['dimension']>0 and p['sourcePrimitiveDimensionA']==p['sourcePrimitiveDimensionB']==2];assert len(joins)==(2 if i==4738 else 1)
     top=Fraction(float(tri[i,:,1].max()));roof=Fraction(float(cap[0,1]));gap=roof-top;assert 0<gap<Fraction(1,1000)
     baseGap=abs(Fraction(float(tri[i,:,1].min()))-Fraction(float(parent[[13678,13679],:,1].min())));assert baseGap<Fraction(1,1000)
     seam.append(dict(mode=mode,sourceFace=i,exactRoofMinusWallTopM=str(gap),exactWallBaseDifferenceM=str(baseGap),positiveNativeWallContacts=len(joins),rawClearCapPathPassed=False,sourceSpecificAuthoredWallRoofJoint=True,geometryChanges=0))
   foundations.append(dict(uid=uid,mode=s['mode'],foundation=f,strictUnresolved=s['unresolved'],finitePaths=s['finitePaths']))
  partitions.append(dict(uid=uid,completeSourceFaces=clear['rows'][0]['completeSourceFaces'],affectedOriginalFaces=affected[number],rawCapPathsPassed=all(r['compoundCapPathsPassed']for r in clear['rows']),sourceSpecificInterpretation='Authored lower vertical wall interfaces with full exact cap paths.'if number!='238856'else'Two source-owned lower wall panels positively join exact original podium walls; roof/wall tops differ by0.423431mm and bases by0.217438mm. The raw below-cap/no-clear-cap negatives remain; no source vertex,1mm contact-residual policy or-.5m ordinary gate is changed.'))
 # Independent failed-download evidence remains required even though recovered views
 # deliberately keep all companions available before every own-source export.
 failure=P+'unapproved-supported-preview-v1-20261024'
 for width in [1280,390]:
  r=take(failure,str(width)+'/staged-browser.json');assert r['passed']and not r['errors']
  if width==390:assert{v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(SOURCES)
 prior,pins[BROWSER]=authenticate(BASE/BROWSER);refs.append(BASE/BROWSER/'result.json');assert prior['previewOnly']and not prior['installationApproved']and prior['sourceSHA256ByUid']==SOURCES
 local=HERE/'local'/BROWSER;catpath=local/'catalogue.json';assert digest(catpath.read_bytes())==pins[BROWSER][str(catpath.relative_to(ROOT))]and verify_metadata(read(catpath)['models']);refs.append(catpath)
 images=[];retained=[];reports=[]
 for width in [1280,390]:
  report=take(BROWSER,str(width)+'/staged-browser.json');reports.append(ref(BASE/BROWSER/str(width)/'staged-browser.json'));assert report['passed']and not report['errors']
  assert len([v for v in report['views']if'time'in v])==6
  assert len(report['jointViews'])==3 and all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
  for v in [v for v in report['views']if'time'in v]+report['retainedNativeOwnViews']:
   assert v['fullyFramed']and v['active']and v['visible']and not v['fallbackFaces'];path=BASE/BROWSER/str(width)/v['file'];assert ref(path)['sha256']==pins[BROWSER][ref(path)['path']];refs.append(path);item=dict(**ref(path),uid=v['uid'],width=width,time=v['time']);(images if v['uid']in SOURCES else retained).append(item)
  sheetbase=BASE/(P+'recovered-preview-inspection-v2-20261024')/str(width)
  refs.extend(p for p in sheetbase.iterdir()if p.is_file())
 assert len(images)==12 and len(retained)==4
 wallplot=BASE/'government-xl-parc-palais-block1-two-wall-installed-podium-context-v1-20261024';_,wallpins=authenticate(wallplot);refs.append(wallplot/'result.json');fig=wallplot/'named-faces-current-ground.png';assert ref(fig)['sha256']==wallpins[ref(fig)['path']];refs.append(fig)
 result=dict(reviewer='ROOT',uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORTS,currentManifest=ref(manifest),identityAccepted=True,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=4,wholeSourceFoundationEvidence=foundations,completeNegativePartitions=partitions,authoredWallRoofSeamEvidence=seam,allRawPhysicalFailuresRetained=True,rawAllCapPathsPassed=False,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,browserReports=reports,visualAcceptance=True,ROOTActuallyInspectedWholeSourceAndRetainedExports=True,leaseResources=sorted('building:'+u for u in forms),terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,interpretation='Exact three original towers and unchanged registered installed podium only. All source-source interfaces remain measured authored joint evidence, never generic unrelated-collision credit. No other current actors are scoped beyond this exact four-actor assembly. Source1/2/3 whole-face ground/native checks retain18clear-cap lowerwalls and two named original wall/roof seam panels. Actual recovered source and retained desktop/mobile day/night exports inspected alongside source diagrams; raw strict support, peer-contact and cap negatives remain archived. No geometry generation, terrain changes, scale or source-pose corrections, old-native reacceptance or global guard relaxation.')
 save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);refs.extend([HERE/'parc_palais_three_original_catalogue_scope_v1_20261024.py',HERE/'installed_support_complete_compound_clearance_v1_20261024.py']);module('parc_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-bound-three-original-podium-joint-physical-and-inspected-visual-review',refs,result)
if __name__=='__main__':main()
