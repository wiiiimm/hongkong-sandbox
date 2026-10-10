"""Exact current partial-edge/outside-star/T-junction incidence, no solve or mesh."""
import json
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,point,covered
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected,oriented
from exact_original_projection_coverage_v2_20261010 import clip,signed_area,cross
B=ROOT/'docs/astra-city/government-import';STAR=B/'government-xl-parkview-block16-causal-negative-corner-vertex-star-inventory-v1-20261011';DOC=B/'government-xl-parkview-block16-partial-edge-vertex-star-boundary-inventory-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x

def positive_overlap(a,b):
 poly=oriented(projected(a));host=oriented(projected(b))
 if signed_area(poly)==0 or signed_area(host)==0:return False
 for c,d in zip(host,host[1:]+host[:1]):poly=clip(poly,c,d,True)
 return abs(signed_area(poly))>0

def parameter(a,b,p):
 k=next(k for k in range(3)if a[k]!=b[k]);t=(p[k]-a[k])/(b[k]-a[k]);assert all(a[i]+t*(b[i]-a[i])==p[i]for i in range(3));return t

def main():
 assert not DOC.exists();d=read(STAR/'diagnostic.json.gz');assert read(STAR/'result.json')['currentAcceptance']is False
 refs=[ref(p)for p in [Path(__file__),INSTALLED,STAR/'diagnostic.json.gz',STAR/'result.json',HERE/'native_patch_resolution.py',HERE/'exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'test_exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 faces=_faces(read(INSTALLED));assert faces.shape==(94794,3,3)and np.isfinite(faces).all()and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 edges=np.stack([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]],axis=1).reshape(-1,2,3);elo,ehi=edges.min(1),edges.max(1);flo,fhi=faces.min(1),faces.max(1);globalVertexIncidences=defaultdict(list)
 for fi,face in enumerate(faces):
  for k,p in enumerate(face):globalVertexIncidences[point(p)].append((fi,k))
 rows=[];total=0;vertexrecords={}
 def register(p):
  p=point(p);key=tuple(str(x)for x in p)
  if key not in vertexrecords:vertexrecords[key]=dict(exactOriginalXYZ=p,allCurrentExactXYZIndexedFacetIncidences=globalVertexIncidences.get(p,[]))
  return key
 for si,star in enumerate(d['causalNegativeCornerRows']):
  corner=tuple(F(x)for x in star['originalExactXYZ']);p=np.asarray(list(map(float,corner)));ids=set(star['completeCausalVertexStarFacetIDs']);assert sorted({fi for fi,k in globalVertexIncidences[corner]})==sorted(ids)
  cornercandidates=np.flatnonzero(np.all(fhi>=p,axis=1)&np.all(flo<=p,axis=1)).tolist();assert len(cornercandidates)<=256,'Complete bounded corner3DAABB inventory; no truncation';cornerpairs=[]
  for fi in cornercandidates:
   proof=column(faces[fi],np.repeat(p[None,:],3,axis=0));hits=[v for v in proof['allExactBasicFeasibleColumnVertices']if F(v['exactGapM'])==0]
   cornerpairs.append(dict(currentFacet=fi,exactFinitePointColumn=proof,allExactSame3DCornerIncidences=hits,cornerIsActualIndexedVertex=any(q==corner for q in map(point,faces[fi])),pointContextOnlyNoPositiveSeamCredit=True))
  grouped=defaultdict(list)
  for fi in ids:
   vertices=list(map(point,faces[fi]))
   for k,(a,b)in enumerate(zip(vertices,vertices[1:]+vertices[:1])):grouped[tuple(sorted([a,b]))].append((fi,k,a,b))
  unmatched=[v[0]for e,v in grouped.items()if corner in e and len(v)==1];assert len(unmatched)==2
  radial=[]
  for sourcefi,sourcele,a,b in unmatched:
   edge=np.asarray([[float(v)for v in q]for q in [a,b]]);candidateids=np.flatnonzero(np.all(ehi>=edge.min(0),axis=1)&np.all(elo<=edge.max(0),axis=1)).tolist();total+=len(candidateids);assert total<=16384,'Complete bounded8edge full94794 broadphase; no truncation';hits=[];eqs=[];other=point(faces[sourcefi,(sourcele+2)%3]);side=cross((a[0],a[2]),(b[0],b[2]),(other[0],other[2]));assert side!=0
   for eid in candidateids:
    fi,le=divmod(eid,3)
    if fi in ids:continue
    c,g=map(point,edges[eid]);iv=overlap(a,b,c,g)
    if iv is None:continue
    third=point(faces[fi,(le+2)%3]);opposite=side*cross((a[0],a[2]),(b[0],b[2]),(third[0],third[2]))<0
    overlapArea=any(positive_overlap(faces[fi],faces[own])for own in ids);axis=next(k for k in range(3)if b[k]!=a[k]);reverse=(g[axis]-c[axis])*(b[axis]-a[axis])<0;qualified=opposite and reverse and not overlapArea and signed_area(projected(faces[fi]))!=0
    ps=[tuple(a[k]+t*(b[k]-a[k])for k in range(3))for t in iv];u=[parameter(c,g,q)for q in ps];hit=dict(currentFacet=fi,currentLocalEdge=le,sourceExactInterval=iv,hostExactInterval=u,opposingLocalXZSide=opposite,opposingActualEdgeOrientation=reverse,anyPositiveAreaProjectionOverlapWithWholeStar=overlapArea,qualifiedOutsidePositive3DIntervalContext=qualified)
    hits.append(hit)
    if qualified:
     for t,s in zip(iv,u):
      terms=defaultdict(F)
      for q,w in [(a,1-t),(b,t),(c,-(1-s)),(g,-s)]:terms[register(q)]+=w
      terms={q:w for q,w in terms.items()if w};residual=sum(w*F(q[1])for q,w in terms.items());assert residual==0
      eqs.append(dict(currentFacet=fi,sourceParameter=t,hostParameter=s,exactYTerms=[dict(vertexXYZKey=q,weight=w)for q,w in terms.items()],exactOriginalResidualM=residual,weightedSeamEquationOnlyNoVariablePermission=True))
   parts=[h['sourceExactInterval']for h in hits if h['qualifiedOutsidePositive3DIntervalContext']];cuts=sorted({F(0),F(1)}|{v for iv in parts for v in iv});atomic=[]
   for lo,hi in zip(cuts,cuts[1:]):atomic.append(dict(interval=[lo,hi],qualifiedOutsideFacetEdges=[dict(currentFacet=h['currentFacet'],currentLocalEdge=h['currentLocalEdge'])for h in hits if h['qualifiedOutsidePositive3DIntervalContext']and h['sourceExactInterval'][0]<=lo and h['sourceExactInterval'][1]>=hi]))
   radial.append(dict(sourceCurrentFacet=sourcefi,sourceLocalEdge=sourcele,exactSourceEdge=[a,b],completeFullCurrentEdge3DAABBCandidateIDs=candidateids,allOutsidePositive3DEdgeOverlaps=hits,completeQualifiedOutsideIntervalCoverage=covered(parts),completeAtomicIntervals=atomic,exactWeightedSeamConstraints=eqs,sourceBoundaryVertexNotAutomaticallyInternal=True))
  rows.append(dict(star=si,originalNegativeCorner=corner,completeCornerFacet3DAABBCandidateIDs=cornercandidates,allCornerFinitePointIncidences=cornerpairs,unmatchedRadialEdges=radial,wholeTwoRadialBoundariesCoveredByQualifiedOutsideEdges=all(r['completeQualifiedOutsideIntervalCoverage']for r in radial)))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,solverInvoked=False,meshCreated=False,terrainChanges=0,completeGlobalCurrentFacets=94794,completeGlobalCurrentEdges=284382,completeUnmatchedRadialEdges=8,completeCurrentEdge3DAABBCandidatePairs=total,completeInventoryNoTruncation=True,rows=strings(rows),allCoupledOriginalVertexIncidences=strings(list(vertexrecords.values())),completeProtectiveSourceSupportConstraintsAvailable=False,evidenceRefs=refs,qualification='Exact partial-edge/T-junction outside-star incidence and weighted3D seam equations only. Current corner point incidences remain context, not positive contact/root/bridge. Sameheight exact positive collinear outside edge coverage requires opposing local side and actual edge orientation plus zero positive-area projected overlap against every star facet; near/wrongheight/fullpiece overlaps do not qualify. All source/host endpoint vertex incidences bound across full94794 mesh. Complete equations do not nominate an eligible internal variable or grant alteredterrain/domain/17/native/foreign support approval. No candidate, mesh, solver or currentcounts change.'))
 print(json.dumps(dict(radialEdges=8,completeCandidatePairs=total,fullyCoveredRadialEdges=sum(r['completeQualifiedOutsideIntervalCoverage']for row in rows for r in row['unmatchedRadialEdges']),starsBothRadialsCovered=sum(r['wholeTwoRadialBoundariesCoveredByQualifiedOutsideEdges']for r in rows),weightedSeamEquations=sum(len(r['exactWeightedSeamConstraints'])for row in rows for r in row['unmatchedRadialEdges']),solverInvoked=False,meshCreated=False)),flush=True)
if __name__=='__main__':main()
