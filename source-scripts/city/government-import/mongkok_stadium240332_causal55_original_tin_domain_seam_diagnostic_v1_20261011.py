"""DRAFT bounded causal55 current facets/source TIN/complete actual neighbours; NO candidate.
Strict original 3D seams only, preserving actual negative coverage/heights/domain errors.
"""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,json,subprocess,time,uuid,numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_source_planar_domain_recovery_seams_v1_20261011 import recover,projected,oriented
from exact_original_projection_coverage_v2_20261010 import clip,signed_area
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-stadium240332-causal55-original-tin-domain-seam-diagnostic-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;CAP=B/'government-xl-mongkok-stadium240332-complete-current-ground-capture-v1-20261011';FINITE=B/'government-xl-mongkok-stadium240332-complete-current-finite-ground-diagnostic-v1-20261011';AUTH=B/'government-xl-mongkok-stadium240332-complete-original-authentic-tin-finite-v1-20261011';METHOD=B/'government-xl-mongkok-stadium240332-bounded-original-tin-recovery-method-v1-20261011';JS=HERE/'mongkok_stadium240332_causal_domain_actual_ground_provenance_v1_20261011.mjs';PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x
def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[ref(p)for p in [Path(__file__),JS,METHOD/'METHOD.md',METHOD/'method.json']]
 for folder in [CAP,FINITE,AUTH]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.append(ref(folder/'result.json'))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==PIN;d=read(FINITE/'diagnostic.json.gz');ids=set()
 for p in d['allDistinctWholeSourceFiniteProofs'].values():
  assert p['completeFacetsAccounted']==15456
  for i in p['ordinaryFailingSourceFaces']:
   for r in p['allWholeOriginalFacetProofs'][i]['refinedCompleteFinitePairs']:
    if r['proof']['exactClosedHorizontalProjectionsMeet']and F(r['proof']['exactMinimumFiniteColumnGapM'])< -F(1,2):ids.add(r['originalGroundFace'])
 ids=sorted(ids);assert ids==read(METHOD/'method.json')['initialCausalCapturedGroundFacetIds']and len(ids)==55;runtime=HERE/'local'/CAP.name/'runtime-geometry.json.gz';refs.extend(ref(p)for p in [runtime,CAP/'capture-scope.json',FINITE/'diagnostic.json.gz',AUTH/'diagnostic.json.gz',manifest]);save(DOC/'actual-domain-inputs.json.gz',dict(uid='landsd/240332:0',currentManifest=start,runtime=ref(runtime),causalCapturedFacetIds=ids,evidenceRefs=refs));claim=reservations.claim('stadium-causal55-'+str(uuid.uuid4()),['building:landsd/240332:0','building:landsd/240527:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
 try:
  output=DOC/'complete-domain-actual-ground-provenance.json.gz';subprocess.run(['node',str(JS),str((DOC/'actual-domain-inputs.json.gz').relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,check=True);pulse();g=read(output);assert g['startEndAllInputsVerified']and g['all55UniqueOriginalGlobalProvenance'];actual=g['completeClosedDomainAABBActualGroundFacets'];domains=np.asarray([next(r['actualTriangle']for r in actual if r['causalCapturedFacetId']==i)for i in ids],float).reshape(-1,3,3);retained_rows=[r for r in actual if r['causalCapturedFacetId']is None];retained=np.asarray([r['actualTriangle']for r in retained_rows],float).reshape(-1,3,3);assert len(domains)==55;refs.extend(ref(p)for p in [DOC/'actual-domain-inputs.json.gz',output]);refs.extend(dict(path=p,sha256=h)for p,h in g['inputHashes'].items())
  groundfile=HERE/'local'/AUTH.name/'complete-original-tin-covering-whole-facets.json.gz';prior=read(groundfile);gltf=ROOT/next(r['path']for r in prior['sourceFiles']if r['path'].endswith('.gltf'));assert all(ref(ROOT/r['path'])==r for r in prior['sourceFiles']);spec=importlib.util.spec_from_file_location('stadium_causal_tin_decoder',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=LOCAL;whole=decoder.terrain_triangles(gltf);assert len(whole)==109339 and digest(whole.tobytes())==prior['completeOriginalSheetSHA256'];lo,hi=domains[:,:,[0,2]].min((0,1)),domains[:,:,[0,2]].max((0,1));xz=whole[:,:,[0,2]];sid=np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1));source=whole[sid];assert len(source);refs.extend([ref(groundfile),*prior['sourceFiles']]);overlaps=[];polys=[oriented(projected(f))for f in domains]
  for i,a in enumerate(polys):
   assert signed_area(a)>0
   for j in range(i+1,len(polys)):
    poly=a
    for u,v in zip(polys[j],polys[j][1:]+polys[j][:1]):poly=clip(poly,u,v,True)
    area=abs(signed_area(poly))
    if area:overlaps.append(dict(causalDomainIndices=[i,j],capturedFacetIds=[ids[i],ids[j]],exactPositiveProjectedOverlapM2=str(area)))
   pulse()
  proof=None;domain_error=None
  if not overlaps:
   try:proof=recover(domains,source,retained)
   except AssertionError as e:domain_error=str(e)
  for p in sorted((LOCAL/'terrain-repairs').rglob('*'))if(LOCAL/'terrain-repairs').exists()else []:
   if p.is_file():refs.append(ref(p))
  # A complete affected-form inventory is context, not a current physical clearance proof.
  spec=importlib.util.spec_from_file_location('stadium_causal_forms',HERE/'xl-final-script-pass.py');forms_loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(forms_loader);forms=forms_loader.load_forms([float(lo[0]-1),float(lo[1]-1),float(hi[0]+1),float(hi[1]+1)]);form_rows=[dict(building=f,tile=t)for f,_,t in forms];refs.extend(ref(ROOT/'3d-viewer'/t)for _,_,t in forms);native=[]
  for cat in read(manifest)['officialModelCatalogues']:
   path=ROOT/'3d-viewer'/cat;refs.append(ref(path))
   for e in read(path)['models']:
    a,z=e['worldBounds']
    if e['uid']=='landsd/240527:0'or not(z[0]<lo[0]or a[0]>hi[0]or z[2]<lo[1]or a[2]>hi[1]):native.append(dict(catalogue=ref(path),entry=e,completeOriginalSourceAndCurrentProtectionStillRequired=True))
  assert any(r['entry']['uid']=='landsd/240527:0'for r in native);refs.extend(ref(HERE/(n+'.py'))for n in ['xl-second-pass','xl-final-script-pass','exact_source_planar_domain_recovery_seams_v1_20261011','test_exact_source_planar_domain_recovery_seams_v1_20261011','exact_original_projection_coverage_v2_20261010']);assert ref(manifest)==start and all(ref(ROOT/r['path'])==r for r in refs);assert reservations.heartbeat(lease)['ok'];save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',currentManifest=start,sourceOnly=True,currentAcceptance=False,installationApproved=False,terrainProposalCreated=False,sourceGeometryChanges=0,liveTerrainChanges=0,all55CausalCapturedFacetIds=ids,all55ActualWholeDomainFacets=domains.tolist(),completeCurrentOutsideNeighbourFaces=len(retained),completeRelevantOriginalTINFacets=len(source),completeOriginalTINFacetIds=sid.tolist(),completeOriginalTINWorldSHA256=digest(whole.tobytes()),completePositiveProjectedDomainOverlaps=overlaps,domainGuardRejection=domain_error,exactSourcePlanarSeamProof=strings(proof),allAffectedCurrentFormContext=form_rows,allAffectedInstalledNativeEntryContext=native,actualFloat32CandidateReplayed=False,internalSourcePieceSeamsProved=False,fullActorRegressionsDischarged=False,evidenceRefs=list({(r['path'],r['sha256']):r for r in refs}.values()),qualification='Bounded actual causal55whole-facet source-planar seam feasibility only. Exact original-current seam/domain negatives preserved; no candidate is emitted even if external kernel passes. All source-piece internal incidence/3D/F32 seams and full affected actor original/body/F32/ground/support protections remain mandatory. Installed240527 is explicit protected actor, not availability-only native credit. No sourceheight snap/wall/pose edit/arbitrary domain expansion.'));print(json.dumps(dict(causalFacets=55,retainedFacets=len(retained),sourceFacets=len(source),positiveDomainOverlaps=len(overlaps),domainError=domain_error,externalSeamCompatible=None if proof is None else proof['seamCompatible'],heightIncompatibilities=None if proof is None else sum(not r['heightCompatible']for r in proof['allExact3DSeamProofs']),currentAcceptance=False)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
