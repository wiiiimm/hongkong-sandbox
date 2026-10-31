"""DRAFT nonpublishing faithful original multisurface+3joins+10mL1 renderer terrain.
ROOT FULLREAD before execution. No acceptance/publication/geometry edits.
"""
from pathlib import Path
from fractions import Fraction as F
import json,argparse,importlib.util,subprocess,time,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,decoded,encoded
from exact_faithful_multisurface_transition_domain_v2_20261011 import domain,closed_pairs
from exact_faithful_multisurface_transition_mesh_v1_20261011 import nominate
from exact_compute_transition_mesh_v1_20261011 import faces,project
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection
from exact_original_projection_coverage_v2_20261010 import signed_area
B=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-mongkok-stadium240332-';NAME=PREFIX+'faithful-multisurface-transition-candidate-v2-20261011';DOC=B/NAME;LOCAL=HERE/'local'/NAME;METHOD=B/(NAME+'-method')/'METHOD.md';PRIOR=B/(PREFIX+'complete-bounded-source3d-atoms-three-join-integration-v1-20261011');LOCUS=B/(PREFIX+'complete-source3d-boundary-cycles-open-join-core-locus-v1-20261011');OLD=B/(PREFIX+'actual-native-union-authentic-core-inventory-v2-20261011');FRINGE=B/(PREFIX+'adjacent15c-complete-fringe-coverage-crosssheet-seams-v1-20261011');JS=HERE/'mongkok_stadium240332_faithful_multisurface_current_ground_and_parent_routing_v1_20261011.mjs';ATTR=HERE/'mongkok_stadium240332_faithful_multisurface_candidate_actual_native_attributes_v1_20261011.mjs';UIDS=['landsd/240332:0','landsd/240527:0']
def persist(p,value):
 if p.exists():assert read(p)==value,"Changed existing phase output"
 else:save(p,value)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(folder):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 return r
def state(uids):
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(sorted(uids),)).fetchall()
def outward(v,lower):
 q=F(v);v=float(q)
 if lower and F(v)>q or not lower and F(v)<q:v=float(np.nextafter(v,-np.inf if lower else np.inf))
 assert F(v)<=q if lower else F(v)>=q
 return v
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--expected-manifest',required=True);args=ap.parse_args();assert len(args.expected_manifest)==64;assert not(DOC/"diagnostic.json.gz").exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';current=ref(manifest);assert current['sha256']==args.expected_manifest
 folders=[PRIOR,LOCUS,OLD,FRINGE];receipts=[verify(p)for p in folders];d=decoded(read(PRIOR/'diagnostic.json.gz'));locus=decoded(read(LOCUS/'diagnostic.json.gz'));assert locus['summary']['completeIntegratedFaces']==14801 and locus['summary']['completeDirectedCycles']==3 and locus['summary']['componentsWithBoundaryDegreeFailures']==0;assert d['summary']['generatedOpenBoundaryAtoms']==1 and d['summary']['generatedProperOriginalSurfaceCrossings']==0 and d['summary']['generatedPositiveUnnominatedSourceContacts']==0
 op=HERE/'local'/OLD.name/'actual-union-authentic-whole-source-facets.json.gz';fp=HERE/'local'/FRINGE.name/'complete-original15c-sheet-world.json.gz';o,f=read(op),read(fp);a=np.asarray(o['completeSelectedOriginalFacets'],dtype='<f8');b=np.asarray(f['allWholeOriginalSheetFacets'],dtype='<f8');assert digest(a.tobytes())==o['completeSelectedOriginalSHA256']and digest(b.tobytes())==f['completeOriginalSheetWorldSHA256'];mapping={j:i for i,j in enumerate(o['completeSelectedOriginalSheetFacetIds'])};core=np.asarray([a[mapping[i]]if sheet=='14D'else b[i]for sheet,i in d['completeOriginalSourceFacetBindings']],dtype='<f8');assert core.shape==(14798,3,3)and digest(core.tobytes())==d['completeRetainedOriginal3DSourceSHA256'];joins=d['allOrientedGeneratedNominations'];assert len(joins)==3;polys=[project(t)for t in faces(core)]
 code=['exact_faithful_multisurface_transition_domain_v2_20261011.py','test_exact_faithful_multisurface_transition_domain_equivalence_v2_20261011.py','exact_faithful_multisurface_transition_domain_v1_20261011.py','test_exact_faithful_multisurface_transition_domain_v1_20261011.py','exact_faithful_multisurface_transition_mesh_v1_20261011.py','test_exact_faithful_multisurface_transition_mesh_v1_20261011.py','test_faithful_multisurface_literal_native_runtime_v1_20261011.mjs','exact_resumable_projected_inventory_v1_20261011.py','exact_compute_transition_mesh_v1_20261011.py','exact_cross_set_projected_source_coverage_v1_20261011.py'];refs=[ref(p)for p in[Path(__file__),METHOD,METHOD.with_name("method.json"),op,fp]+[HERE/p for p in code]]+[ref(p/q)for p in folders for q in['result.json','diagnostic.json.gz']]+o['sourceFiles']+f['sourceFiles'];source_refs=list(refs)
 def source_fence():assert all(ref(ROOT/e['path'])==e for e in source_refs)
 cp=Checkpoints(LOCAL/'immutable-source-domain-checkpoints',polys,source_refs,source_fence);failure=None;nomination=None;runtime=None;g=None;all_uids=set(UIDS);before=state(all_uids)
 try:dom=domain(polys,cp)
 except AssertionError as e:failure=dict(stage='scratch-projected-source-union-and-ten-metre-domain',reason=str(e),context=getattr(e,'evidence',None));dom=None
 if dom is not None:
  persist(DOC/'exact-source-bound-domain.json.gz',encoded(dom));refs.append(ref(DOC/'exact-source-bound-domain.json.gz'));bounds=dom['exactWholeDomainXZBounds'];rounded=[outward(q,i<2)for i,q in enumerate(bounds)];refs.extend([current,ref(JS),ref(ATTR)]);persist(DOC/'current-inputs.json.gz',dict(uid=UIDS[0],currentManifest=current,completeOutwardRoundedDomainXZBounds=rounded,evidenceRefs=refs));groundpath=DOC/'complete-current-ground-and-parent-routing.json.gz';
  if not groundpath.exists():subprocess.run(['node',str(JS),str((DOC/'current-inputs.json.gz').relative_to(ROOT)),str(groundpath.relative_to(ROOT))],cwd=ROOT,check=True)
  g=read(groundpath);assert all(ref(ROOT/p)['sha256']==h for p,h in g['inputHashes'].items());assert g['startEndAllInputsVerified']and g['restoredParentCapturedByRemovingOnlyProtectedTerrainLayer'];refs.extend([ref(DOC/'current-inputs.json.gz'),ref(groundpath)]);refs.extend(dict(path=p,sha256=h)for p,h in g['inputHashes'].items());maskbounds=g['completeCoarseRoutingWorldBounds'];spec=importlib.util.spec_from_file_location('forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);forms=m.load_forms(maskbounds);refs.append(ref(HERE/'xl-final-script-pass.py'));form_rows=[dict(building=p,tile=t)for p,_,t in forms];refs.extend(ref(ROOT/'3d-viewer'/t)for _,_,t in forms);native=[]
  for cat in read(manifest)['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/cat;refs.append(ref(p))
   for e in read(p)['models']:
    a,z=e['worldBounds']
    if e['uid']==UIDS[1]or not(z[0]<maskbounds[0]or a[0]>maskbounds[2]or z[2]<maskbounds[1]or a[2]>maskbounds[3]):
     asset=p.parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];refs.append(ref(asset));native.append(dict(catalogue=ref(p),entry=e,asset=ref(asset),protectionDischarged=False))
  assert any(e['entry']['uid']==UIDS[1]for e in native);assert state(UIDS)==before;all_uids.update(p['uid']for p,_,_ in forms);all_uids.update(e['entry']['uid']for e in native);before=state(all_uids)
  # Only coarse parent routing and exact protected terrain layer may be replaced.
  protected=[q['meshOrdinal']for q in g['completeGlobalActualMeshes']if q['completeFacets']==16297 and q['actualPositionAttributeSHA256']=='4a318ade67bad09734b2a87c610d432dc81021530a0ce130e3c901de2c33df95'];assert len(protected)==1
  others=[r for r in g['completeClosedDomainAABBActualGroundFacets']if r['meshOrdinal']not in[0,protected[0]]];otherfaces=faces(np.asarray([r['actualTriangle']for r in others],dtype='<f8').reshape(-1,3,3))if others else[];otherpolys=[project(t)for t in otherfaces];domainpolys=dom['scratchOriginalProjectionUnionCells']+dom['computeBandPolygons'];pairs=closed_pairs(domainpolys,otherpolys);overlap=[]
  for i,j in pairs:
   area=signed_area(intersection(domainpolys[i],otherpolys[j]))
   if area:overlap.append(dict(domainPiece=i,retainedProductionFacet=others[j],exactAreaM2=area))
  persist(DOC/'retained-other-terrain-layer-overlap.json.gz',encoded(overlap));refs.append(ref(DOC/'retained-other-terrain-layer-overlap.json.gz'))
  if overlap:failure=dict(stage='retained-other-terrain-layer-protection',overlapCount=len(overlap),noOtherLayerRemovalAuthorized=True)
  else:
   parent=np.asarray([r['actualTriangle']for r in g['completeRestoredOriginalParentFacetsInsideRoutingMask']],dtype='<f8').reshape(-1,3,3)
   def current_fence():assert ref(manifest)==current and all(ref(ROOT/e['path'])==e for e in refs)
   cp=Checkpoints(LOCAL/'fresh-current-candidate-checkpoints',[core.tolist(),joins,parent.tolist()],refs,current_fence)
   try:nomination=nominate(core,joins,parent,dom,cp)
   except AssertionError as e:failure=dict(stage='exact-source-band-parent-and-Float32-nomination',reason=str(e),context=getattr(e,'evidence',None))
   if nomination is not None:
    persist(DOC/'raw-faithful-surface-nomination.json.gz',encoded(nomination));refs.append(ref(DOC/'raw-faithful-surface-nomination.json.gz'));literal=np.asarray(nomination['allExactLiteralCandidateFacets'],dtype='<f8');positions=literal.reshape(-1);indices=np.arange(len(positions)//3,dtype='<u4');inp=DOC/'literal-native-attribute-inputs.json.gz';out=DOC/'actual-native-attributes.json.gz';persist(inp,dict(uid=UIDS[0],currentManifest=current,completeLiteralCandidateFacets=len(literal),literalNativeMesh=dict(position=positions.tolist(),index=indices.tolist()),expectedPositionAttributeSHA256=digest(positions.astype('<f4').tobytes()),evidenceRefs=refs));
    if not out.exists():subprocess.run(['node',str(ATTR),str(inp.relative_to(ROOT)),str(out.relative_to(ROOT))],cwd=ROOT,check=True)
    runtime=read(out);assert all(ref(ROOT/p)['sha256']==h for p,h in runtime['inputHashes'].items());refs.extend([ref(inp),ref(out)]);refs.extend(dict(path=p,sha256=h)for p,h in runtime['inputHashes'].items());assert runtime['startEndAllInputsVerified']and runtime['completeRenderedAndIndexedRolesAccounted'];assert runtime['completeActualDrawnCandidateFacets']==len(literal)
    if runtime['allExcludedNonzeroProjectedFaces']or runtime['missingCentroidSamples']:failure=dict(stage='actual-runtime-nonvertical-height-coverage',allExcludedNonzeroProjectedFaces=runtime['allExcludedNonzeroProjectedFaces'],missingCentroidSamples=runtime['missingCentroidSamples'])
    else:
     terrain=read(ROOT/'3d-viewer/city/data/terrain.json');patch=dict(w=terrain['w'],h=terrain['h'],meta=terrain['meta'],vegetation=terrain['vegetation'],coarseCells=g['proposedCoarseRoutingCells'],nativeMesh=dict(position=positions.tolist(),index=indices.tolist()),sourceOnly=True,terrainCandidateApproved=False,scriptedComputeTerrain=True);persist(DOC/'nonpublishing-faithful-terrain-patch.json.gz',patch);refs.append(ref(DOC/'nonpublishing-faithful-terrain-patch.json.gz'))
 assert state(all_uids)==before and ref(manifest)==current and all(ref(ROOT/e['path'])==e for e in refs);assert all(verify(p)==r for p,r in zip(folders,receipts));refs.extend(ref(p)for p in LOCAL.rglob('*')if p.is_file()and not p.name.endswith('.tmp'));persist(DOC/'diagnostic.json.gz',encoded(dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=(DOC/'nonpublishing-faithful-terrain-patch.json.gz').exists(),terrainCandidateApproved=False,originalSourceGeometryChanges=0,liveTerrainChanges=0,completeUnchangedOriginalFaces=14798,completeUnchangedGeneratedJoins=3,completeOriginalWorldSHA256=digest(core.tobytes()),rawOriginal91CrossingsAndAllProjected49437NegativesPreserved=True,originalAndGeneratedOpenBoundaryAtomsPreserved=True,currentManifest=current,allAffectedCurrentForms=form_rows if g else[],allAffectedNativeEntries=native if g else[],allProtectedReviewUIDs=sorted(all_uids),protectedReviewStateUnchanged=True,exactFailure=failure,allFullFourStreamActorGroundRootWaterRuntimeRegressionsDischarged=False,evidenceRefs=refs,qualification='Faithful ORIGINAL multisurface renderer terrain plus three separately nominated source-bound vertical joins and compute-labelled source-bound10mL1 band. Scratch disjoint projected union masks do not replace/delete/refit any original3D face; drawing topology retains all14798originals+3joins, including the known interior openatom and91sourcecrossings. Existing MAX finite native walking sampler and intentional vertical height-index exclusions are bound independently, no stronger invented all-render-faces-height-indexed/watertight predicate. All newly introduced band seams require exact finite original/current3D and productionFloat32 equality; rawsource failures remain separate. Only protected240527 TERRAIN layer and rootcoarse routing are nominated for replacement, installed building bytes/pose unchanged. Complete source/current actor/foreign/native/grade/support/water/road and full staged/live runtime gates remain mandatory before any approval. No publication/state edits.')));print(json.dumps(dict(candidateCreated=(DOC/'nonpublishing-faithful-terrain-patch.json.gz').exists(),exactFailure=str(failure),sourceOnly=True,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
