"""Full-drawn-mesh incidence is descriptive, never a topology admission gate."""
from fractions import Fraction as F
from collections import defaultdict,deque
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from upton_inherited_overlap_boundary_v1_20261012 import points,sub,dot,sha,interval_clip,union_intervals,segment_to_facets

def cross(a,b):return tuple(a[i]*b[j]-a[j]*b[i]for i,j in [(1,2),(2,0),(0,1)])
def normal_key(n):
 first=next(x for x in n if x);return tuple(x/first for x in n)
def key(face):return tuple(sorted(tuple(float(x)for x in p)for p in face))
def full_draw_attribution(drawn,candidate,candidate_provenance,current,current_lineage):
 """Actual geometry occurrence bijection, without fabricating unique identity."""
 drawn=np.asarray(drawn,dtype='<f8');candidate=np.asarray(candidate,dtype='<f8');current=np.asarray(current,dtype='<f8')
 assert drawn.shape[1:]==candidate.shape[1:]==current.shape[1:]==(3,3)
 assert all(np.isfinite(x).all()for x in [drawn,candidate,current]);assert len(candidate)==len(candidate_provenance)and len(current)==len(current_lineage)
 remaining=defaultdict(deque);alternatives=defaultdict(list);old=defaultdict(list)
 for i,f in enumerate(candidate):remaining[key(f)].append(i);alternatives[key(f)].append(i)
 for i,f in enumerate(current):old[key(f)].append(i)
 out=[];fallback=[]
 for i,f in enumerate(drawn):
  k=key(f);base=dict(actualDrawnFace=i,actualOrderedFaceSHA256=sha(f),allGeometryIdenticalCandidateFaceIDs=alternatives[k],allGeometryIdenticalCurrentGlobalFaceIDs=old[k],preJSONSignedZeroRestorationNotClaimed=True)
  if remaining[k]:
   c=remaining[k].popleft();base.update(kind='candidateOccurrence',candidateFace=c,candidateProvenance=candidate_provenance[c])
  else:
   assert old[k],('Unattributed actual fallback',i)
   base.update(kind='unchangedCurrentFallbackOccurrence',allCurrentSourceIdentityAlternatives=[current_lineage[j]for j in old[k]]);fallback.append(i)
  out.append(base)
 assert not any(remaining.values()),'Candidate occurrence missing from actual draw'
 return dict(rows=out,completeDrawnFaces=len(drawn),completeCandidateOccurrences=len(candidate),completeFallbackOccurrences=len(fallback),fallbackFaceIDs=fallback,geometryMultiplicityPreserved=True,ambiguousIdentityRetained=True)

def prepare(world):
 world=np.asarray(world,dtype='<f8');assert world.ndim==3 and world.shape[1:]==(3,3)and np.isfinite(world).all();rows=[];zeros=[];edges=defaultdict(list)
 for i,face in enumerate(world):
  if exact_nonrendering(face):zeros.append(i);rows.append(None);continue
  p,q,r=points(face,(3,3));u=sub(q,p);v=sub(r,p);uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);det=uu*vv-uv*uv;assert det>0
  rows.append(dict(points=(p,q,r),u=u,v=v,uu=uu,uv=uv,vv=vv,det=det,normal=cross(u,v)))
  for e,(a,b)in enumerate([(p,q),(q,r),(r,p)]):
   assert a!=b;ek=tuple(sorted((a,b)));edges[ek].append(dict(face=i,faceEdge=e,direction=1 if a==ek[0]else-1))
 return dict(world=world,worldSHA256=sha(world),rows=rows,exactDegenerateFaceIDs=zeros,edges=edges)
def broadphase(segment,world,band):
 a=points(segment,(2,3));band=F(band);assert band>=0
 lo=np.nextafter(np.array([float(min(p[k]for p in a)-band)for k in range(3)]),-np.inf);hi=np.nextafter(np.array([float(max(p[k]for p in a)+band)for k in range(3)]),np.inf)
 return np.flatnonzero(((world.max(1)>=lo)&(world.min(1)<=hi)).all(1)).tolist()
def incidence(segment,prepared):
 a,b=points(segment,(2,3));d=sub(b,a);assert dot(d,d)>0,'Collapsed nomination stays uncredited'
 ids=broadphase((a,b),prepared['world'],0);hits=[];zero=[]
 for i in ids:
  f=prepared['rows'][i]
  if f is None:zero.append(i);continue
  p,q,r=f['points'];n=f['normal']
  if dot(n,sub(a,p))or dot(n,d):continue
  ap=sub(a,p);du=dot(d,f['u']);dv=dot(d,f['v']);uc=(dot(ap,f['u'])*f['vv']-dot(ap,f['v'])*f['uv'])/f['det'];us=(du*f['vv']-dv*f['uv'])/f['det'];vc=(dot(ap,f['v'])*f['uu']-dot(ap,f['u'])*f['uv'])/f['det'];vs=(dv*f['uu']-du*f['uv'])/f['det']
  iv=(F(0),F(1))
  for c,s in [(uc,us),(vc,vs),(1-uc-vc,-us-vs)]:iv=interval_clip(iv,c,s)if iv is not None else None
  if iv is None:continue
  hits.append(dict(face=i,iv=iv,bary=((uc,us),(vc,vs),(1-uc-vc,-us-vs)),normal=n,points=(p,q,r)))
 breaks=sorted({F(0),F(1),*[t for q in hits for t in q['iv']]});cells=[]
 for lo,hi in zip(breaks,breaks[1:]):
  mid=(lo+hi)/2;active=[q for q in hits if q['iv'][0]<=mid<=q['iv'][1]];interior=[q['face']for q in active if all(c+s*mid>0 for c,s in q['bary'])];planes=defaultdict(list)
  for q in active:
   nk=normal_key(q['normal']);values=[dot(nk,cross(d,sub(p,a)))for p in q['points']];side=max(values,key=abs);planes[nk].append((q['face'],1 if side>0 else -1 if side<0 else 0))
  two_sided=[n for n,z in planes.items()if {-1,1}<={v for _,v in z}]
  if interior:kind='strictInteriorOfSurvivingFacet'
  elif two_sided:kind='coplanarTwoSidedInternalIncidence'
  elif len(planes)>1:kind='sharedNoncoplanarCreaseIncidence'
  elif active:kind='ordinaryOneSidedExteriorEdgeIncidence'
  else:kind='noExactFacetOnNominalTrace'
  cells.append(dict(exactOpenParameterInterval=list(map(str,(lo,hi))),classification=kind,allActualIncidentFaceIDs=[q['face']for q in active],strictInteriorFaceIDs=interior,allPlaneSideIncidences=[dict(exactUnorientedPlaneNormal=list(map(str,n)),faces=z)for n,z in planes.items()]))
 union=union_intervals([q['iv']for q in hits]);endpoints=[dict(exactParameter=str(t),allActualIncidentFaceIDs=[q['face']for q in hits if q['iv'][0]<=t<=q['iv'][1]])for t in breaks]
 return dict(completeActualDrawnWorldSHA256=prepared['worldSHA256'],safeInclusiveExactTraceCandidateFaceIDs=ids,allDegenerateCandidateFacesRetainedUncredited=zero,allExactClosedFacetIntervals=[dict(actualDrawnFace=q['face'],exactClosedParameterInterval=list(map(str,q['iv'])))for q in hits],completeExactSurfaceCoverage=union==[(F(0),F(1))],completeClosedParameterUnion=[list(map(str,z))for z in union],allOpenIntervalIncidenceClasses=cells,allClosedBreakpointIncidences=endpoints,oneSidedExteriorEdgesAreNormal=True,noTopologyAdmissionGate=True,noRoleRootOrBridgeCredit=True)
def reconcile(segment,prepared):
 a,b=points(segment,(2,3))
 if a==b:return dict(collapsedNominationRetainedUncredited=True,noTopologyAdmissionGate=True)
 exact=incidence((a,b),prepared);ids=broadphase((a,b),prepared['world'],F(.1));world=prepared['world'][ids]
 bounds={name:segment_to_facets((a,b),world,limit)for name,limit in [('distance01MSeparateDiagnostic',F(.01)),('existingAssociation1M',F(.1))]}
 touched=sorted({ids[row['facet']]for result in bounds.values()for row in result['allCompleteIntervalCertificates']});edgeids=[]
 # These are complete exact coordinate-edge incidence records of the actual
 # touched facets. T-junction/partial incidence is already captured by the
 # trace intervals; whole-edge counts alone are never a topology admission gate.
 for ek,rows in prepared['edges'].items():
  if any(row['face']in touched for row in rows):edgeids.append(dict(exactActualEdge=[list(map(str,p))for p in ek],allWholeCoordinateEdgeIncidences=rows))
 return dict(exactNominalTrace=list(map(lambda p:list(map(str,p)),(a,b))),completeActualIncidence=exact,completeActualDistanceCandidateFaceIDs=ids,allSeparateDistanceDiagnostics=bounds,allActualTouchedFacetWholeEdgeIncidences=edgeids,packingDisplacementDoesNotCreatePermanentHold=True,notGlobalWatertightnessCertificate=True,noCandidateEdits=True)
def saved_change_contract(row):
 q=row['completeDrawnUnionIdealAffineMax'];assert q and q['proof']['completeIdealAffineMaxRegionCovered'];p=q['proof'];v=F(p['exactMaximumAbsoluteIdealAffineMaxDifferenceM']);assert v>=0
 return dict(savedCompleteMaxProofVerbatim=q,savedLineageRangesVerbatim=row['exactInheritance'],exactMaximumDifferenceM=str(v),belowExistingSamplerAudit01MContract=v<F(.01),existingContractIsStrictLessThan01=True,exactZeroIsNotAdmissionRequirement=True,noSamplerOrOrdinaryThresholdChanged=True,bitwiseJSHeightEqualityNotClaimed=True,noOverlapApprovalWritten=True)
