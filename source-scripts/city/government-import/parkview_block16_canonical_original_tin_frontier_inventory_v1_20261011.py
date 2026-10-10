"""Source-only complete original TIN shared-edge inventory + bounded frontier.
No terrain candidate, originalheight adjustments, graph acceptance or livewrites.
First deterministic closed whole-source-facet frontier under exact original+F32
full outside-facet interface criterion; not globally minimal terrain recovery.
"""
import importlib.util,json,collections
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_shared_edge_component_census_v2_20261011 import census
from native_patch_resolution import _faces
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-block16-canonical-original-TIN-frontier-inventory-v1-20261011';DOC=B/BATCH;AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';FAILED=B/'government-xl-parkview-block16-two-parent-facet-source-planar-proposal-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def triangle_key(face):return tuple(sorted(tuple(map(float,v))for v in face))
def edge_key(a,b):return tuple(sorted((tuple(map(float,a)),tuple(map(float,b)))))
def main():
 assert not DOC.exists();refs=[ref(p)for p in [Path(__file__),AUTH/'diagnostic.json.gz',AUTH/'result.json',FAILED/'diagnostic.json.gz',FAILED/'result.json',INSTALLED,HERE/'pending-context.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'native_patch_resolution.py']];failed=read(FAILED/'diagnostic.json.gz');assert failed['localTerrainProposalWritten']is False and failed['exactSourcePlanarPreFloat32Proof']['seamCompatible']is False
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];packed=terrain.astype(np.float32).astype('<f8');current=_faces(read(INSTALLED));assert len(current)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 topology=census(terrain,list(range(len(terrain))));render=set(topology['completeRenderableFaceIds']);blocked=set(topology['exactNonrenderingOriginalFaces']);edges=collections.defaultdict(list)
 for i in topology['completeRenderableFaceIds']:
  vv=[tuple(map(float,v))for v in terrain[i]]
  for a,b in zip(vv,vv[1:]+vv[:1]):
   if a==b:continue
   key=edge_key(a,b);edges[key].append((i,1 if a==key[0]else-1))
 inventory=[dict(edge=k,originalFaceIncidences=v)for k,v in sorted(edges.items())];assert digest(json.dumps(inventory,sort_keys=True,separators=(',',':')).encode())==topology['exactNonzeroEdgeInventorySHA256'];save(DOC/'complete-original-TIN-nonzero-edge-inventory.json.gz',inventory)
 currentkeys=collections.defaultdict(list)
 for i,face in enumerate(current):currentkeys[triangle_key(face)].append(i)
 actualmatches={i:currentkeys.get(triangle_key(packed[i]),[])for i in render};complete_current_matches=[dict(originalTINFacet=i,exactWholePackedCurrentNativeFacetMatches=ids)for i,ids in sorted(actualmatches.items())if ids]
 candidateids=failed['completeSourceCandidateOriginalTINIds'];seed=sorted({candidateids[p['source']]for p in failed['exactSourcePlanarPreFloat32Proof']['exactSourcePlanarPieces']});assert seed and set(seed)<=render;selected=set(seed);history=[];last=[];closed=False;budgetExceeded=False;step=0
 while True:
  boundary=[];expand=set()
  activekeys=set()
  for fid in selected:
   vv=[tuple(map(float,v))for v in terrain[fid]]
   activekeys.update(edge_key(a,b)for a,b in zip(vv,vv[1:]+vv[:1])if a!=b)
  for key in sorted(activekeys):
   incidences=edges[key]
   inside=sorted(i for i,_ in incidences if i in selected)
   if not inside:continue
   outside=sorted(i for i,_ in incidences if i not in selected)
   if not outside and len(incidences)>1:continue
   packededge=edge_key(np.asarray(key[0],dtype=np.float32),np.asarray(key[1],dtype=np.float32));collapsed=packededge[0]==packededge[1]
   matches=[dict(originalOutsideTINFacet=i,exactWholeCurrentNativeMatches=actualmatches[i])for i in outside if actualmatches[i]]
   qualified=bool(outside and matches and not collapsed and len(incidences)==2 and len(inside)==1 and incidences[0][1]!=incidences[1][1])
   boundary.append(dict(exactOriginalSourceEdge=key,actualFloat32SourceEdge=packededge,insideOriginalTINFacets=inside,outsideOriginalTINFacets=outside,sourceEdgeIncidences=len(incidences),actualCollapsed=collapsed,exactWholeUnchangedOutsideCurrentFacetMatches=matches,qualifiedSourceContextFrontier=qualified))
   if not qualified:expand.update(outside)
  unresolved=[r for r in boundary if not r['qualifiedSourceContextFrontier']];history.append(dict(step=step,selectedWholeOriginalTINFacetCount=len(selected),boundaryEdges=len(boundary),qualifiedBoundaryEdges=len(boundary)-len(unresolved),newUnqualifiedOutsideOriginalFacets=sorted(expand-selected),terminalUnmatchedOriginalSourceEdges=sum(not r['outsideOriginalTINFacets']for r in unresolved)))
  last=boundary
  if not unresolved:closed=True;break
  if not expand-selected:break
  if len(selected|expand)>2048 or step>=16:budgetExceeded=True;break
  selected.update(expand);step+=1
 source_projection_zero=[]
 for i in sorted(selected):
  face=terrain[i];u,v=face[1]-face[0],face[2]-face[0]
  # This float value is inventory only; zeroProjectedExact needs Fraction in any
  # future recovery kernel. These facets remain full original obligations.
  if u[0]*v[2]-u[2]*v[0]==0:source_projection_zero.append(i)
 bound=np.array(sorted(selected));lo,hi=packed[bound].min((0,1)),packed[bound].max((0,1));xz=current[:,:,[0,2]];cost=np.flatnonzero(np.all(xz.max(1)>=lo[[0,2]],axis=1)&np.all(xz.min(1)<=hi[[0,2]],axis=1)).tolist()
 for r in refs:assert ref(ROOT/r['path'])==r
 out=dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,retentionRemovalApproved=False,nativeReacceptance=False,completeOriginalTINWorldSHA256=digest(terrain.tobytes()),completePackedOriginalTINWorldSHA256=digest(packed.tobytes()),completeOriginalTINTopology=topology,exactWholeOriginalPackedCurrentFacetMatches=complete_current_matches,seedPositiveAreaOriginalTINFacetIDs=seed,deterministicFrontierHistory=history,selectedWholeOriginalTINFacetIDs=sorted(selected),completeSelectedSourceFrontier=last,firstClosedContextFrontier=closed,frontierBudgetExceeded=budgetExceeded,selectedSourceProjectedFloatZeroInventoryOnly=source_projection_zero,wholeOriginalPackedFrontierBounds=[lo.tolist(),hi.tolist()],conservativePotentialAffectedInstalledNativeFacetIDs=cost,evidenceRefs=refs,qualification='Complete original3D nonzero edge census, no point glue. Source+F32 fullfacet outside-edge equality is source context only, not terrain support or physical root. This is first deterministic monotone whole-source-facet closure under strong full-current-outside-facet criterion, not globally optimal/minimal geometry. AABB cost is conservative inventory only; no exact proposed domain or retained17/native/foreign discharge. Future method must bind full internal sourcepiece/F32 edgeincidence/overlap3D seam compatibility, exact projected retained facets/cuts and allsource/current affected17+7native/foreign predicates.')
 save(DOC/'diagnostic.json.gz',out);print(json.dumps(dict(originalFacets=len(terrain),sourceComponents=len(topology['sharedEdgeConnectedComponents']),completeEdges=topology['completeNonzeroEdges'],sourceSeeds=len(seed),selectedOriginalFacets=len(selected),firstClosedContextFrontier=closed,budgetExceeded=budgetExceeded,boundaryEdges=len(last),qualifiedBoundaryEdges=sum(r['qualifiedSourceContextFrontier']for r in last),conservativeAffectedNativeFacetCandidates=len(cost),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
