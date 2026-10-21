"""DRAFT nonpublishing scripted ALTERED renderer terrain candidate.
Genuine merged authentic source-plane core + bounded10mL1 compute band + exact clipped current.
All strict rational current outer seam criteria remain unchanged.
ROOT full-read before numerical execution; supervised canonical reservation required.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,subprocess,time,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_source_core_ten_metre_transition_domain_v1_20261011 import domain
from exact_compute_transition_mesh_v1_20261011 import faces,project,nominate
B=ROOT/'docs/astra-city/government-import';MERGED=B/'government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v1-20261011';AUTH=B/'government-xl-mongkok-stadium240332-complete-original-authentic-tin-finite-v1-20261011';DOC=B/'government-xl-mongkok-stadium240332-ten-metre-merged-core-transition-candidate-v1-20261011';METHOD=B/'government-xl-mongkok-stadium240332-ten-metre-merged-core-transition-method-v1-20261011/METHOD.md';JS=HERE/'mongkok_stadium240332_ten_metre_transition_actual_ground_v1_20261011.mjs';ATTR=HERE/'mongkok_stadium240332_transition_candidate_actual_native_attributes_v1_20261011.mjs';PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [strings(v)for v in x]
 return x
def outward(q,lower):
 q=F(q);v=float(q)
 if(lower and F(v)>q)or(not lower and F(v)<q):v=float(np.nextafter(v,-np.inf if lower else np.inf))
 assert (F(v)<=q if lower else F(v)>=q);return v
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(sorted(uids),)).fetchall()
def main():
 start_time=time.monotonic();assert not DOC.exists();r=read(AUTH/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 auth=read(AUTH/'diagnostic.json.gz');assert auth['completeOriginalSourceFaces']==15456 and auth['genuineOriginalBodies']==14 and len(auth['zeroOriginalFaces'])==15 and not auth['ordinaryFailingFaces']and not auth['coverageFailingFaces'];assert auth['completeOriginalWorldSHA256']=='9cb0fd4ea699487958ff12aea7370ac8a872b0ccc5a791da2eb2687d63f5330c';assert auth['source']['sha256']=='896138f962db178400870c74c41d5eae3a2ba99e0c978fad49790956c0a50bdd'
 merged_result=read(MERGED/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(merged_result['jobId'],)).fetchone()==('complete',merged_result)
 for e in merged_result['evidenceRefs']:assert ref(ROOT/e['path'])==e
 merged=read(MERGED/'diagnostic.json.gz');assert merged['mergedCoreProvenanceAndProjectionQualified']and merged['completeActualPatchClosedRectangleFootprintProved']and not merged['allUncoveredProtectedPatchProjectedPolygons']and merged['completeProtectedPatchFacets']==16297 and merged['completeSourceTINFacets']==109339;assert merged['completeMergedOriginalAtomicTopology']['projectedTopologyQualified']
 sourcefile=HERE/'local'/MERGED.name/'merged-authentic-whole-source-facets.json.gz';s=read(sourcefile);assert s['completeOriginalSheetFacets']==109339 and all(ref(ROOT/e['path'])==e for e in s['sourceFiles']);core=np.asarray(s['completeSelectedOriginalFacets'],dtype='<f8');assert core.ndim==3 and core.shape[1:]==(3,3)and len(core)==merged['completeMergedWholeOriginalSourceFacets']>=640 and digest(core.tobytes())==s['completeSelectedOriginalSHA256'];oldsource=read(HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz');assert set(oldsource['completeSelectedFacetIds'])<=set(s['completeSelectedOriginalSheetFacetIds'])and s['completeOriginalSheetSHA256']==oldsource['completeOriginalSheetSHA256']and s['sourceETag']==oldsource['sourceETag']and s['sourceRevision']==oldsource['sourceRevision']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';current=ref(manifest);assert current['sha256']==PIN;refs=[ref(p)for p in [Path(__file__),JS,ATTR,METHOD,AUTH/'result.json',AUTH/'diagnostic.json.gz',MERGED/'result.json',MERGED/'diagnostic.json.gz',HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz',sourcefile,ROOT/auth['source']['path'],manifest,HERE/'exact_source_core_ten_metre_transition_domain_v1_20261011.py',HERE/'test_exact_source_core_ten_metre_transition_domain_v1_20261011.py',HERE/'exact_compute_transition_mesh_v1_20261011.py',HERE/'test_exact_compute_transition_mesh_v1_20261011.py',ROOT/'source-scripts/city/government-import/DIRECT-IMPORT-POLICY.md']]+s['sourceFiles'];failure=None;d=None;mesh=None;runtime_usable=False;runtime=None
 try:d=domain([project(f)for f in faces(core)])
 except AssertionError as e:failure=dict(stage='authentic-core-ten-metre-domain',reason=str(e))
 if d is None:
  assert ref(manifest)==current and all(ref(ROOT/e['path'])==e for e in refs)
  save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,terrainCandidateApproved=False,sourceGeometryChanges=0,liveTerrainChanges=0,exactFailure=failure,evidenceRefs=refs));return
 bounds=d['exactWholeDomainXZBounds'];rounded=[outward(v,i<2)for i,v in enumerate(bounds)];save(DOC/'exact-domain.json.gz',strings(d))
 spec=importlib.util.spec_from_file_location('stadium_clipped_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);forms=m.load_forms(rounded);form_rows=[dict(building=f,tile=t)for f,_,t in forms];refs.extend(ref(ROOT/'3d-viewer'/t)for _,_,t in forms);native=[]
 for catalogue in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/catalogue;refs.append(ref(p))
  for e in read(p)['models']:
   a,z=e['worldBounds']
   if e['uid']=='landsd/240527:0'or not(z[0]<rounded[0]or a[0]>rounded[2]or z[2]<rounded[1]or a[2]>rounded[3]):
    asset=p.parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];refs.append(ref(asset));native.append(dict(catalogue=ref(p),entry=e,actualAsset=ref(asset),protectionDischarged=False))
 assert any(e['entry']['uid']=='landsd/240527:0'for e in native);uids={'landsd/240332:0','landsd/240527:0'}|{f['uid']for f,_,_ in forms}|{e['entry']['uid']for e in native};before=state(uids);refs.extend([ref(DOC/'exact-domain.json.gz'),ref(HERE/'xl-final-script-pass.py')]);save(DOC/'current-inputs.json.gz',dict(uid='landsd/240332:0',currentManifest=current,exactDomainXZBounds=strings(bounds),completeOutwardRoundedDomainXZBounds=rounded,evidenceRefs=refs));groundfile=DOC/'complete-current-ground.json.gz';subprocess.run(['node',str(JS),str((DOC/'current-inputs.json.gz').relative_to(ROOT)),str(groundfile.relative_to(ROOT))],cwd=ROOT,check=True);g=read(groundfile);assert g['startEndAllInputsVerified']and g['completeOutsideNeighbourBroadphase'];ground=np.asarray([e['actualTriangle']for e in g['completeClosedDomainAABBActualGroundFacets']],dtype='<f8').reshape(-1,3,3)
 try:mesh=nominate(core,ground,d)
 except AssertionError as e:failure=dict(stage='exact-current-outer-generated-mesh-and-float32',reason=str(e),exactFailureContext=strings(getattr(e,'evidence',None)),failureMayStopAtFirstSpecificCounterexample=True)
 refs.extend([ref(DOC/'current-inputs.json.gz'),ref(groundfile)]);refs.extend(dict(path=p,sha256=h)for p,h in g['inputHashes'].items());assert ref(manifest)==current and state(uids)==before and all(ref(ROOT/e['path'])==e for e in refs)
 if mesh is not None:
  save(DOC/'raw-geometric-nomination.json.gz',strings(mesh));refs.append(ref(DOC/'raw-geometric-nomination.json.gz'));literal=np.asarray(mesh['exactSourceCoreAndGeneratedBandFacets']+mesh['exactClippedRetainedCurrentFacets'],dtype='<f8').reshape(-1,3,3);positions=literal.reshape(-1);indices=np.arange(len(positions)//3,dtype='<u4');attribute_input=DOC/'literal-native-attribute-inputs.json.gz';save(attribute_input,dict(uid='landsd/240332:0',currentManifest=current,completeLiteralCandidateFacets=len(literal),literalNativeMesh=dict(position=positions.tolist(),index=indices.tolist()),expectedPositionAttributeSHA256=digest(positions.astype('<f4').tobytes()),expectedIndexAttributeSHA256=digest(indices.tobytes()),evidenceRefs=refs));attribute_output=DOC/'actual-native-attributes.json.gz'
  with(DOC/'native-attribute-process.stdout.log').open('w')as out,(DOC/'native-attribute-process.stderr.log').open('w')as err:child=subprocess.run(['node',str(ATTR),str(attribute_input.relative_to(ROOT)),str(attribute_output.relative_to(ROOT))],cwd=ROOT,stdout=out,stderr=err)
  refs.extend(ref(p)for p in [attribute_input,DOC/'native-attribute-process.stdout.log',DOC/'native-attribute-process.stderr.log'])
  if child.returncode:failure=dict(stage='literal-production-native-attribute-capture',exitCode=child.returncode)
  else:
   runtime=read(attribute_output);assert runtime['startEndAllInputsVerified'];refs.append(ref(attribute_output));refs.extend(dict(path=p,sha256=h)for p,h in runtime['inputHashes'].items());runtime_usable=runtime['allFacesHeightIndexed']and runtime['missingCentroidSamples']==0
   if not runtime_usable:failure=dict(stage='literal-production-native-height-index',allExcludedCandidateFaces=runtime['allExcludedHeightIndexCandidateFaces'],missingCentroidSamples=runtime['missingCentroidSamples'])
  if runtime_usable:save(DOC/'nonpublishing-terrain-candidate.json.gz',strings(mesh));refs.append(ref(DOC/'nonpublishing-terrain-candidate.json.gz'))
 assert ref(manifest)==current and state(uids)==before and all(ref(ROOT/e['path'])==e for e in refs)
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=mesh is not None and runtime_usable,rawGeometryNominationCreated=mesh is not None,actualProductionNativeHeightIndexUsable=runtime_usable,terrainCandidateApproved=False,candidateTerrainGeometryIsScriptedAlteredRendererTerrain=True,originalSourceGeometryChanges=0,liveTerrainChanges=0,currentManifest=current,completeAuthenticCoreFaces=len(core),completePriorStadiumAuthenticCoreFaces=640,completeProtectedPatchPriorFacets=16297,mergedAuthenticSourceCoreProvenance=ref(MERGED/'diagnostic.json.gz'),completeAuthenticSheetFaces=109339,completeComputeBandConvexPieces=len(d['computeBandPolygons']),completeGlobalProductionFacetsTraversed=g['completeGlobalActualFacetsTraversed'],completeRelevantCurrentGroundFaces=len(ground),metric='10mL1; Euclidean distance<=10m',exactDomainXZBounds=strings(bounds),allAffectedCurrentForms=form_rows,allAffectedInstalledNativeEntries=native,allProtectedReviewUIDs=sorted(uids),protectedReviewStateUnchanged=True,exactFailure=failure,fullOriginalLiteralLeftBalancedSourceAndActorRegressionsDischarged=False,genuineAll14BodyGroundOrMountedRolesDischarged=False,fullWaterMaskAndRuntimeGatesDischarged=False,sourceGeometryAndPoseByteIdentical=True,allRaw783CurrentFailuresAndAllPriorSeamPinchBranchNegativesPreserved=True,evidenceRefs=list({(e['path'],e['sha256']):e for e in refs}.values()),elapsedSeconds=time.monotonic()-start_time,qualification='Nonpublishing exact scripted renderer terrain nomination only. Complete merged authentic nativeTIN core covers the independently proven whole15456original source and complete existing protected240527 patch footprint; every original core plane remains exact while polygon winding is normalized for geometry analysis and renderer triangulation differs. Band is explicitly compute generated from genuine source-boundary10mL1 offsets and deterministic inverse-squared-distance source/current anchors; no building geometry/pose edit, source height snap or manufactured walls. Complete current globalterrain traversal, currentouter finite plane anchors, source/generated internal and actualFloat32 seams/overlaps are checked for nomination. Clipped outside-current pieces preserve original exact planes before ordinaryFloat32 casting; every actualFloat32 plane residual is retained, not waived. Literal productionmakeTerrain attributes and nativeTerrainSurface complete index/centroid census are independently captured; excluded tiny facets or missing samples prevent a usable candidate, without deleting them. All protected actor fullsource/allfour streams/body/grade/support/foreign/native/water/runtime and stage/live checks remain pending; no installation or role/identity acceptance.'))
 print(json.dumps(dict(candidateCreated=mesh is not None and runtime_usable,rawGeometryNominationCreated=mesh is not None,exactFailure=failure,core=len(core),bandPieces=len(d['computeBandPolygons']),currentGround=len(ground),affectedForms=len(forms),protectedNative=len(native),elapsedSeconds=time.monotonic()-start_time,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
