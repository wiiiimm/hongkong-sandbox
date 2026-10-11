"""DRAFT altered-terrain feasibility with fixed outside topology/XYZ boundary.
No source TIN identity, proposal asset, changed mesh or acceptance claim.
The narrow evidenced two-parent stencil must prove eligible internal vertices
before any height solver. A fixed violated exact finite constraint proves this
stencil infeasible; no artificial height bounds or domain expansion are allowed.
"""
from pathlib import Path
from fractions import Fraction as F
import json
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify as column
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-parkview-block16-fixed-boundary-two-parent-vertex-feasibility-v1-20261011';ATTR=B/'government-xl-parkview-block16-complete-cap-retained-obligations-v1-20261011';FOUR=B/'government-xl-parkview-block16-sampled-foundation-faces-exact-attribution-v1-20261011';GRAPH=B/'government-xl-parkview-block16-complete-original-support-graph-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json';TECHNIQUE=HERE/'xl-terrain-recovery-20261011-hoi-shing-nine-upward-exact-terrain-feasibility-v2.py'
IDS=[94641,94645];SOURCE='b57eab82a53c67a40eb0f94e64215ca5acbd8f4808fb90610c15425aa21c4193';NATIVE='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();assetbase=HERE/'local/government-xl-sustained-131-inputs-20261006/assets';ownedpath=assetbase/(SOURCE+'.glb.gz');nativepath=HERE/'local/government-xl-parkview-block16-fresh-current-carrier-capture-v1-20261011/assets'/(NATIVE+'.glb.gz')
 refs=[ref(p)for p in [Path(__file__),INSTALLED,ownedpath,nativepath,ATTR/'diagnostic.json.gz',ATTR/'result.json',FOUR/'diagnostic.json.gz',FOUR/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',TECHNIQUE,HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py']]
 terrain=_faces(read(INSTALLED));assert len(terrain)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 assert digest(ownedpath.read_bytes())==SOURCE and digest(nativepath.read_bytes())==NATIVE
 owned=decode_original_world_triangles(ownedpath.read_bytes());native=decode_original_world_triangles(nativepath.read_bytes());assert owned.shape==(11351,3,3)and digest(owned.tobytes())==read(GRAPH/'diagnostic.json.gz')['completeOriginalWorldSHA256']=='8fb18cad1beb31c5da4f859c22304ecfac92eb9a1a888992f5766ecc9612f622';assert native.shape==(63133,3,3)and digest(native.tobytes())=='fa5d0001d66a0348acd0596d4ffa39b7c4eda561db093750674f0f15640c6ee0'
 attribution=read(ATTR/'diagnostic.json.gz');four=read(FOUR/'diagnostic.json.gz');assert four['sampledFoundationFailureSourceFaceIDs']==[3798,11277,11281,11282]
 for carrier,nid in zip([25014,25018],IDS):
  r=next(r for r in attribution['allCurrentCapPairAttributions']if r['originalGroundFace']==carrier);assert r['exactInstalledNativeFacetMatches']==[nid]and digest(terrain[nid].tobytes())==r['fullGroundFacetSHA256'];assert [f['uid']for f in r['fullGroundFacetPreservationOverlaps']]==['landsd/256319:0']
 # Bind every exact XYZ vertex incidence across ALL94794 actual current facets.
 # Equal XZ at a differentY does not silently join a second terrain surface.
 incidence=defaultdict(list)
 for fi,face in enumerate(terrain):
  for k,p in enumerate(face):incidence[tuple(float(v)for v in p)].append((fi,k))
 edges=defaultdict(list);domainvertices=set()
 for fi in IDS:
  face=terrain[fi];keys=[tuple(float(v)for v in p)for p in face];assert len(set(keys))==3
  for k,(a,b)in enumerate(zip(keys,keys[1:]+keys[:1])):edges[tuple(sorted((a,b)))].append((fi,k,a,b))
  domainvertices.update(keys)
 assert all(len(v)<=2 for v in edges.values())
 for records in edges.values():
  if len(records)==2:assert records[0][2:]==tuple(reversed(records[1][2:])),'Shared current edge winding conflict'
 boundary=[(e,v)for e,v in edges.items()if len(v)==1];boundaryvertices={p for e,v in boundary for p in e};eligible=[];census=[]
 for p in sorted(domainvertices):
  outside=sorted({fi for fi,k in incidence[p]if fi not in IDS});internal=p not in boundaryvertices and not outside
  if internal:eligible.append(p)
  census.append(dict(exactOriginalXYZ=[str(F(v))for v in p],domainBoundaryVertex=p in boundaryvertices,completeCurrentFacetVertexIncidences=incidence[p],outsideDomainFacetIDs=outside,eligibleSharedInternalVariable=internal,reason='fixed-domain-boundary-or-outside-incidence'if not internal else 'requires-authoritative-unique-grade-bounds-and-full-protective-constraints'))
 # Reviewed stencil only. If topology changes unexpectedly, fail without making
 # up variable bounds or omitting installed17/foreign/native obligations.
 assert len(domainvertices)==4 and len(boundary)==4 and len(edges)-len(boundary)==1
 assert not eligible,'Different stencil has eligible variables; requires separately reviewed source-grade bounds and complete protective constraints before solver'
 rows=[];constraints=[]
 targets=[('native-strict-cap',45867,native[45867],F(0),True)]+[('owned-ordinary-source',fi,owned[fi],-F(1,2),False)for fi in [3798,11277,11281,11282]]
 for role,fid,face,threshold,strict in targets:
  xz=terrain[IDS][:,:,[0,2]];fxz=face[:,[0,2]];candidates=[IDS[i]for i in np.flatnonzero(np.all(xz.max(1)>=fxz.min(0),axis=1)&np.all(xz.min(1)<=fxz.max(0),axis=1))];pairs=[]
  for gi in candidates:
   proof=column(face,terrain[gi]);pairs.append(dict(originalInstalledFacet=gi,exactFinitePair=proof))
   for v in proof['allExactBasicFeasibleColumnVertices']:
    weights=[F(x)for x in v['exactGroundBarycentricWeights']];assert sum(weights)==1;gap=F(v['exactGapM']);valid=gap>threshold if strict else gap>=threshold
    constraints.append(dict(role=role,sourceFace=fid,originalInstalledFacet=gi,groundVertexXYZ=terrain[gi].tolist(),exactGroundWeights=[str(w)for w in weights],originalExactGapM=str(gap),minimumRequiredGapM=str(threshold),strictInequalityRequired=strict,allGroundVerticesFixed=True,eligibleVariableTerms={},exactUnchangedFloat32ReplayGapM=str(gap),fixedConstraintSatisfied=valid,exactColumnVertex=v))
  rows.append(dict(role=role,sourceFace=fid,sourceFacetSHA256=digest(face.tobytes()),completeClosedAABBCandidateDomainFacetIDs=candidates,completeFiniteDomainPairs=pairs))
 violations=[r for r in constraints if not r['fixedConstraintSatisfied']];assert violations,'Cannot infer fixed-stencil infeasibility without an exact violated finite constraint'
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,physicalAccepted=False,terrainProposalAssetCreated=False,changedMeshCreated=False,hypotheticalAlteredTerrainNotOriginalTIN=True,originalSourceGeometryRootPoseChanges=0,terrainChanges=0,domainOriginalInstalledFacets=IDS,completeCurrentTerrainFacets=94794,completeDomainVertexCensus=census,completeDomainBoundaryEdges=len(boundary),genuineInternalDomainEdges=1,eligibleSharedInternalVertexVariables=0,authoritativeBoundsInvented=False,solver=dict(invoked=False,reason='no-eligible-internal-variable-and-exact-fixed-constraint-violations'),allFiveCompleteFiniteDomainInventories=rows,allExactFixedAffineConstraints=constraints,exactFixedConstraintViolations=violations,fixedBoundaryTwoParentStencilFeasible=False,actualHypotheticalFloat32YChanges=0,allOutsideTerrainVerticesAndTopologyRemainExact=True,affected17ForeignNativeGeometryUnchanged=True,newNativeReapproval=False,globalAlteredTerrainFeasibilityExcluded=False,evidenceRefs=refs,qualification='Complete finite cap+four source constraints within narrow two-parent stencil only; not whole11351-source or all-terrain clearance. Zero eligible internal vertices means every current terrain coordinate remains byte-identical, preserving affected17/foreign/native terrain support geometry without reapproval. This topology infeasibility does not exclude a distinct independently evidenced larger vertex-star domain. No arbitrary sourcegrade height/delta cap, candidate, originalTIN or unchanged-surface recovery claim. Source evidence bounds/full protective installed constraints become mandatory before any nonzero solver nomination.'))
 print(json.dumps(dict(domainVertices=len(domainvertices),eligibleInternalVariables=0,exactConstraints=len(constraints),exactFixedViolations=len(violations),fixedBoundaryStencilFeasible=False,meshCreated=False,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
