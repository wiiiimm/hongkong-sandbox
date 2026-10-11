"""Immutable causal vertex-star/unique-primary-grade inventory; no solver/mesh."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected
from exact_original_projection_coverage_v2_20261010 import signed_area
B=ROOT/'docs/astra-city/government-import';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';FIXED=B/'government-xl-parkview-block16-fixed-boundary-two-parent-vertex-feasibility-v1-20261011';ATTR=B/'government-xl-parkview-block16-complete-cap-retained-obligations-v1-20261011';PHYSICAL=B/'government-xl-parkview-block16-fresh-current-physical-capture-v1-20261011';DOC=B/'government-xl-parkview-block16-causal-negative-corner-vertex-star-inventory-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();fixed=read(FIXED/'diagnostic.json.gz');assert fixed['eligibleSharedInternalVertexVariables']==0 and fixed['fixedBoundaryTwoParentStencilFeasible']is False
 refs=[ref(p)for p in [Path(__file__),INSTALLED,FIXED/'diagnostic.json.gz',FIXED/'result.json',AUTH/'diagnostic.json.gz',AUTH/'result.json',ATTR/'diagnostic.json.gz',ATTR/'result.json',PHYSICAL/'neighbour-checks.json',PHYSICAL/'native-neighbour-checks.json',PHYSICAL/'result.json',HERE/'pending-context.py',HERE/'native_patch_resolution.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];current=_faces(read(INSTALLED));assert len(current)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];assert digest(terrain.tobytes())=='740580e8f1bd38cddc48b956f5ca161de7fcebac2852d887d02ad60c1178cff5'
 attribution=read(ATTR/'diagnostic.json.gz');foreign=read(PHYSICAL/'neighbour-checks.json')['rows'];native=read(PHYSICAL/'native-neighbour-checks.json')['rows'];assert len(foreign)==23 and len(native)==7
 active=set()
 for r in fixed['exactFixedConstraintViolations']:
  for p,w in zip(r['groundVertexXYZ'],r['exactGroundWeights']):
   if F(w)>0:active.add(tuple(F(float(v))for v in p))
 rows=[];tinXZ=terrain[:,:,[0,2]]
 for v in fixed['completeDomainVertexCensus']:
  p=tuple(F(x)for x in v['exactOriginalXYZ'])
  if p not in active:continue
  point=np.asarray(list(map(float,p)));inc=v['completeCurrentFacetVertexIncidences'];actual=np.argwhere(np.all(current==point,axis=2)).tolist();assert [list(x)for x in inc]==actual,'Complete frozen94794 vertex incidence must match actual current bytes';ids=sorted({int(fi)for fi,k in inc});links=[];edges=defaultdict(list);adj=defaultdict(set);incoming=defaultdict(int);outgoing=defaultdict(int)
  for fi,k in inc:
   face=current[fi];assert np.array_equal(face[k],point);a,b=[tuple(F(float(x))for x in face[j])for j in [(k+1)%3,(k+2)%3]];links.append(dict(currentFacet=fi,fromXYZ=[str(x)for x in a],toXYZ=[str(x)for x in b]));adj[a].add(b);adj[b].add(a);outgoing[a]+=1;incoming[b]+=1
   keys=[tuple(F(float(x))for x in q)for q in face]
   for a1,b1 in zip(keys,keys[1:]+keys[:1]):edges[tuple(sorted((a1,b1)))].append((fi,a1,b1))
  seen=set();todo=[next(iter(adj))]if adj else []
  while todo:
   a=todo.pop()
   if a in seen:continue
   seen.add(a);todo.extend(adj[a]-seen)
  radial=[rs for e,rs in edges.items()if p in e];boundary=[e for e,rs in edges.items()if len(rs)==1];closed=bool(adj and len(seen)==len(adj)and all(len(adj[q])==2 and incoming[q]==outgoing[q]==1 for q in adj)and all(len(rs)==2 and rs[0][1:]==tuple(reversed(rs[1][1:]))for rs in radial)and all(len(rs)<=2 for rs in edges.values())and all(p not in e for e in boundary)and all(signed_area(projected(current[fi]))!=0 for fi in ids))
  candidates=np.flatnonzero(np.all(tinXZ.max(1)>=point[[0,2]],axis=1)&np.all(tinXZ.min(1)<=point[[0,2]],axis=1)).tolist();assert len(candidates)<=128,'Complete bounded point-column candidates; no truncation';pointFace=np.repeat(point[None,:],3,axis=0);pairs=[];heights=set()
  for fi in candidates:
   proof=column(terrain[fi],pointFace);pairs.append(dict(originalTINFacet=fi,exactPointColumn=proof))
   heights.update(F(w['exactSourcePoint'][1])for w in proof['allExactBasicFeasibleColumnVertices'])
  unique=len(heights)==1;grade=next(iter(heights))if unique else None;bound=unique and grade<=p[1];known=[];unknown=[]
  for fi in ids:
   matches=[r for r in attribution['allCurrentCapPairAttributions']if fi in r['exactInstalledNativeFacetMatches']]
   if matches:known.append(dict(currentFacet=fi,priorFullFacetPreservationOverlapEvidence=[dict(originalGroundFace=r['originalGroundFace'],overlaps=r['fullGroundFacetPreservationOverlaps'])for r in matches]))
   else:unknown.append(fi)
  rows.append(dict(originalExactXYZ=[str(x)for x in p],negativeConstraintCorner=True,completeCurrentVertexIncidences=actual,completeCausalVertexStarFacetIDs=ids,completeDirectedLinkIncidences=links,starClosedSingleOrientedNondegenerateFan=closed,outerBoundaryEdges=[[[str(x)for x in q]for q in e]for e in boundary],outerBoundaryVertexMustRemainFixed=True,completeOriginalTINPointAABBCandidates=candidates,completeFiniteOriginalTINPointColumnPairs=pairs,allExactPrimaryGradeHeightsM=sorted(str(x)for x in heights),uniqueRecordedGrade=unique,sourceEvidencedDownwardYInterval=[str(grade),str(p[1])]if bound else None,maximumSourceBoundedDownwardDeltaM=str(p[1]-grade)if bound else None,topologyAndUniqueGradeEligibleContextOnly=closed and bound,priorFullFacetPreservationOverlapContext=known,starFacetsWithoutPriorCapAttribution=unknown,protectiveQualifiedSourceSupportConstraintsComplete=False,sourceOnlyNoVariableNomination=True))
 assert len(rows)==len(active)
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,solverInvoked=False,meshCreated=False,terrainProposalAssetCreated=False,hypotheticalAlteredTerrainNotOriginalTIN=True,terrainChanges=0,originalSourceGeometryChanges=0,completeOriginalTINWorldSHA256=digest(terrain.tobytes()),causalNegativeCornerRows=rows,protectedCurrentForeignUIDs=[r['uid']for r in foreign],protectedCurrentNativeUIDs=[r['uid']for r in native],completeProtectiveSourceSupportConstraintsAvailable=False,evidenceRefs=refs,qualification='Complete exactcurrentXYZ vertex stars causally selected by positive weights in prior exact negativeconstraints, not arbitrary rectangle or scene expansion. Closed fan/unique primary pointgrade yield eligibility CONTEXT only, not sourcepermission/solver/domain approval. Gradebounds use complete pointcolumn candidates/all exactsourceheights, never unrelated minheight or convenient cap. Every affected retained17/native/foreign qualified support/source predicate must be identified and fixed/protected before a nonzero solve. Existing whole-source/nativetopology and F32 seam obligations remain. No unchangedTIN claim, candidate or mesh.'))
 print(json.dumps(dict(negativeCorners=len(rows),closedSingleOrientedStars=sum(r['starClosedSingleOrientedNondegenerateFan']for r in rows),uniquePrimaryGrades=sum(r['uniqueRecordedGrade']for r in rows),topologyGradeEligibleContext=sum(r['topologyAndUniqueGradeEligibleContextOnly']for r in rows),protectiveConstraintsComplete=False,solverInvoked=False,meshCreated=False)),flush=True)
if __name__=='__main__':main()
