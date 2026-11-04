"""Diagnostic accounting; existing ordinary finite kernels remain unchanged.

Measured Float32 projected coverage/overlap uses the actual validator's surface
selection. No overlap policy, tolerance, geometry or approval is written.
"""
from fractions import Fraction as F
import hashlib,json
import numpy as np
import shapely
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha,triangles,closed_face_scope

def candidate_surface(patch,provenance):
 mesh=patch['nativeMesh'];p=np.asarray(mesh['position'],dtype=np.float32).astype('<f8').reshape(-1,3);raw=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3)
 ix=mesh['index'];assert all(type(i)is int and 0<=i<len(p)for i in ix)and len(ix)%3==0 and np.isfinite(p).all()and np.isfinite(raw).all()
 index=np.asarray(ix,dtype=np.int64).reshape(-1,3);assert len(index)==len(provenance)
 for i,r in enumerate(provenance):
  assert r['candidateFace']==i and r['kind']in ['originalTIN','capturedCurrentRing','computedVerticalRuledJoin']and r['rawNominationFaceSHA256']==sha(raw[index[i]])
 assert not mesh.get('sourceOverlap')and not mesh.get('source',{}).get('numericalProjectionOverlap')and not mesh.get('source',{}).get('numericalCoverageGap')
 return p[index]

def verify_drawn_multiset(raw,drawn):
 raw=triangles(raw);drawn=triangles(drawn)
 def key(t):return tuple(sorted(tuple(map(float,p))for p in t))
 from collections import Counter
 need=Counter(map(key,raw));have=Counter(map(key,drawn));assert all(have[k]>=n for k,n in need.items())
 return dict(completeCandidateFacets=len(raw),completeDomainDrawnFacets=len(drawn),candidateMultisetIncludedWithMultiplicity=True,windingIgnoredForThisMultisetOnly=True,noSeamOrCoverageClaim=True)

def measured_projection(patch,provenance,domain,parent):
 faces=candidate_surface(patch,provenance);mesh=patch['nativeMesh'];raw=np.asarray(mesh['position'],dtype='<f8').reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];rawpolys=shapely.polygons(raw[:,:,[0,2]])
 polys=shapely.polygons(faces[:,:,[0,2]]);area=shapely.area(polys);ids=np.flatnonzero(area>1e-10);eligible=polys[ids];union=shapely.union_all(eligible);extent=shapely.box(*domain)
 left,right=shapely.STRtree(eligible).query(eligible,predicate='intersects');pairs=[];samples=[];kinds={}
 for a,b in sorted(zip(left.tolist(),right.tolist())):
  if a>=b:continue
  q=eligible[a].intersection(eligible[b]);i,j=int(ids[a]),int(ids[b]);dimension='area'if q.area>0 else'line'if q.length>0 else'point'
  row=dict(leftFace=i,rightFace=j,leftProvenance=provenance[i],rightProvenance=provenance[j],projectedDimension=dimension,measuredAreaM2=float(q.area),measuredLengthM=float(q.length),rawBinary64NominationMeasuredPairAreaM2=float(rawpolys[i].intersection(rawpolys[j]).area),rawVsFloat32OverlayIsMeasurementNotExactFalsePositiveClaim=True)
  pairkind='|'.join(sorted([provenance[i]['kind'],provenance[j]['kind']]));group=kinds.setdefault(pairkind,dict(areaPairs=0,linePairs=0,pointPairs=0,summedPairwiseAreaM2=0.0));group[dimension+'Pairs']+=1;group['summedPairwiseAreaM2']+=float(q.area)
  if q.area>0:
   pt=q.representative_point();heights=[];rays=[]
   for k in [i,j]:
    A,B,C=faces[k];det=(B[0]-A[0])*(C[2]-A[2])-(B[2]-A[2])*(C[0]-A[0]);assert det!=0
    u=((pt.x-A[0])*(C[2]-A[2])-(pt.y-A[2])*(C[0]-A[0]))/det;v=((B[0]-A[0])*(pt.y-A[2])-(B[2]-A[2])*(pt.x-A[0]))/det
    heights.append(float(A[1]+u*(B[1]-A[1])+v*(C[1]-A[1])));n=np.cross(B-A,C-A);assert n[1]!=0;rays.append(float(A[1]-(n[0]*(pt.x-A[0])+n[2]*(pt.y-A[2]))/n[1]))
   row['representativePointHeightMeasurements']=dict(x=pt.x,z=pt.y,leftHeight=heights[0],rightHeight=heights[1],signedLeftMinusRightM=heights[0]-heights[1],independentLeftPlaneRayHeight=rays[0],independentRightPlaneRayHeight=rays[1],notContinuousHeightOrderingProof=True)
   if q.area>1e-8 and len(samples)<64:samples.append(dict(x=pt.x,z=pt.y,leftFace=i,rightFace=j,highestSamplerHeight=max(heights),highestRayHeight=max(rays),error=abs(max(heights)-max(rays))))
  pairs.append(row)
 pg=parent['meta']['georef'];w=parent['w'];h=parent['h']
 def sample(x,z):
  c=(x+834500-pg['bE'])/pg['aE'];r=(816500-z-pg['bN'])/pg['aN'];i=max(0,min(w-2,int(np.floor(c))));j=max(0,min(h-2,int(np.floor(r))));u=c-i;v=r-j
  def at(k):
   a=parent.get('renderedElev',[]);q=a[k]if a else None;return q if q is not None else max(1.2,parent['elev'][k])if parent['elev'][k]>0 else-4
  a,b,d,e=map(at,[j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1]);return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
 points=faces.reshape(-1,3);edges=[]
 for n,(x,y,z)in enumerate(points):
  if min(abs(x-domain[0]),abs(x-domain[2]),abs(z-domain[1]),abs(z-domain[3]))<.002:
   height=sample(x,z);edges.append(dict(face=n//3,corner=n%3,x=float(x),y=float(y),z=float(z),parentHeight=height,absoluteGap=abs(float(y)-height)))
 serial=(json.dumps(patch,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
 return dict(candidateGeometryCanonicalSHA256=hashlib.sha256(serial).hexdigest(),completeCandidateFaces=len(faces),projectedValidatorEligibleFaces=ids.tolist(),allOtherDrawnFacetsRetainedButNotHeightCoverageFaces=np.flatnonzero(area<=1e-10).tolist(),nativeProjectedExcessM2=float(area[ids].sum()-union.area),symmetricCoverageDifferenceM2=float(union.symmetric_difference(extent).area),missingInsideParentM2=float(extent.difference(union).area),outsideParentM2=float(union.difference(extent).area),validatorToleranceM2=max(.001,extent.area*1e-7),allProjectedIntersectingPairs=pairs,pairsBySavedProvenanceKinds=kinds,pairwiseAreaSumIsNotUnionExcess=True,float32HighestRayAgreement=dict(samples=len(samples),maxError=max((r['error']for r in samples),default=None),rows=samples),parentEdgeVertices=edges,parentEdgeMaximumGap=max((r['absoluteGap']for r in edges),default=None),parentEdgeExistingLimitM=.01,measurementIsNotExactSeamProof=True,noOverlapApprovalGranted=True)

def reuse_key(face,ground):return(sha(face),sha(ground))
def compare_candidate(old,new,within):
 assert old['sourceFaceSHA256']==new['sourceFaceSHA256']
 for r in [old,new]:
  if r['ordinaryBoundProved']:assert r['projectionCovered']and F(r['exactLowerM'])>=-F(1,2)
 return dict(currentOrdinaryProved=old['ordinaryBoundProved'],candidateOrdinaryProved=new['ordinaryBoundProved'],currentClearCandidateUnproved=bool(old['ordinaryBoundProved']and not new['ordinaryBoundProved']),currentUnprovedCandidateClear=bool(not old['ordinaryBoundProved']and new['ordinaryBoundProved']),candidateCoverageUnprovedOutsideCapturedDomainIsExtractionLimit=bool(not new['projectionCovered']and not within),noRootRoleOrAcceptanceCredit=True)
