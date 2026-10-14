"""UNEXECUTED saved GEOS overlap/own-plane attribution; never approval."""
from fractions import Fraction as F
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from upton_inherited_overlap_boundary_v1_20261012 import plane,height

def measurement(raw,domain):
    raw=np.asarray(raw,dtype='<f8');assert raw.ndim==3 and raw.shape[1:]==(3,3)and np.isfinite(raw).all()
    polygons=[Polygon(q[:,[0,2]])for q in raw];ids=[i for i,p in enumerate(polygons)if p.area>1e-10]
    eligible=[polygons[i]for i in ids];extent=box(*domain);union=unary_union(eligible);tolerance=max(.001,extent.area*1e-7)
    return polygons,ids,dict(completeNativeFacets=len(raw),projectedValidatorEligibleFacets=len(ids),allOtherDrawnFaceIDs=[i for i,p in enumerate(polygons)if p.area<=1e-10],
        rectangleAreaM2=extent.area,measuredMissingInsideM2=extent.difference(union).area,measuredOutsideM2=union.difference(extent).area,
        measuredSymmetricCoverageDifferenceM2=union.symmetric_difference(extent).area,nativeProjectedExcessM2=sum(p.area for p in eligible)-union.area,
        unchangedValidatorToleranceM2=tolerance,sameValidatorPolygonAdmissionAndUnionOperations=True,GEOSMeasurementNotExactFractionWholeUnion=True,noOverlapApproval=True)

def rational_plane(points):
    return plane([tuple(F(v)for v in p)for p in points])

def pair_record(i,j,region,raw,descriptors,sources,packed_plane_cache=None):
    assert i<j and region.area>0
    d=[descriptors[i],descriptors[j]];s=[sources[q['sourcePlaneKey']]for q in d]
    vertices=[]
    def collect(g):
        if g.geom_type=='Polygon':vertices.extend(g.exterior.coords);[vertices.extend(r.coords)for r in g.interiors]
        else:
            assert g.geom_type in['MultiPolygon','GeometryCollection']
            for part in g.geoms:
                if part.area>0:collect(part)
    collect(region);xz=sorted(set((F(float(x)),F(float(z)))for x,z in vertices));assert xz
    cache={}if packed_plane_cache is None else packed_plane_cache
    for k in [i,j]:
        if k not in cache:cache[k]=plane(raw[k])
    packed=[cache[k]for k in [i,j]];ideal=[q['exactOwnPlane']for q in s];assert all(q is not None for q in packed)
    def ranges(h):
        values=[height(h,p)for p in xz];return [str(min(values)),str(max(values))]
    same=ideal[0]is not None and ideal[0]==ideal[1]
    group='old-old'if j<147096 else'old-append'if i<147096 else'append-append'
    return dict(leftFace=i,rightFace=j,group=group,leftSource=descriptors[i],rightSource=descriptors[j],measuredPositiveAreaM2=region.area,measuredBoundsXZ=list(region.bounds),
        measuredIntersectionVerticesXZ=[[str(x),str(z)]for x,z in xz],packedAffineHeightRangesAtMeasuredVertices=[ranges(q)for q in packed],
        exactPackedSignedLeftMinusRightAtMeasuredVertices=ranges(tuple(a-b for a,b in zip(*packed))),
        idealOwnPlaneRangesAtMeasuredVertices=[ranges(q)if q is not None else None for q in ideal],sameAuthenticatedIdealPlane=same,
        sameSavedSourceIdentity=d[0]['sourcePlaneKey']==d[1]['sourcePlaneKey'],differentSourceKinds=s[0]['kind']!=s[1]['kind'],
        exactArithmeticAtGEOSBinary64VerticesNotExactContinuousIntersectionProof=True,sourcePlaneExtrapolationNotOriginalFootprintInheritance=True,
        notProductionMAXOrRayAgreement=True,noOldApprovalTransfer=True,physicalAccepted=False)

def parent_edge_rows(patch,parent,domain):
    # Same Float32 cast, all POSITION slots including unused, edge tolerance
    # and parent binary64 evaluation as validate_native_mesh. No new gate.
    positions=np.asarray(patch['nativeMesh']['position'],dtype=np.float32).astype('<f8').reshape(-1,3)
    pg=parent['meta']['georef'];w,h=parent['w'],parent['h'];rows=[]
    def sample(x,z):
        c=(x+834500-pg['bE'])/pg['aE'];r=(816500-z-pg['bN'])/pg['aN'];i=max(0,min(w-2,int(np.floor(c))));j=max(0,min(h-2,int(np.floor(r))));u=c-i;v=r-j
        def at(k):
            rendered=parent.get('renderedElev',[]);a=rendered[k]if rendered else None
            return a if a is not None else max(1.2,parent['elev'][k])if parent['elev'][k]>0 else-4
        a,b,d,e=map(at,[j*w+i,j*w+i+1,(j+1)*w+i,(j+1)*w+i+1])
        return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
    for slot,(x,y,z)in enumerate(positions):
        x,y,z=map(float,(x,y,z))
        if min(abs(x-domain[0]),abs(x-domain[2]),abs(z-domain[1]),abs(z-domain[3]))<.002:
            v=sample(x,z);rows.append(dict(positionSlot=slot,x=x,y=y,z=z,parentHeight=v,absoluteGap=abs(y-v)))
    return dict(completePositionSlotsIncludingUnused=len(positions),allActualValidatorEdgeVertices=rows,maxGapM=max((q['absoluteGap']for q in rows),default=None),unchangedExistingLimitM=.01,
        existingValidatorEdgeEvaluationDiagnosticOnly=True,noSamplerWholeSurfaceOrApprovalClaim=True)
