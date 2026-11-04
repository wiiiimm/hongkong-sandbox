"""Apply the existing original-TIN/return weights to exact vertical parent facets.

Exact scalar partitions and 3D edge interpolation precede the same vertex blend
used by nonvertical facets. Zero-area mapped facets have explicit collapse proofs.
"""
from fractions import Fraction as F
import numpy as np
import shapely
from affine_terrain_blend_v1 import evaluate


def clip_interval(polygon,axis,low,high):
    values=[[F(float(v))for v in p]for p in polygon]
    for bound,sign in [(low,1),(high,-1)]:
        result=[]
        for a,b in zip(values,values[1:]+values[:1]):
            va=(a[axis]-bound)*sign;vb=(b[axis]-bound)*sign
            if va>=0:result.append(a)
            if (va<0)!=(vb<0):
                t=va/(va-vb);result.append([a[k]+t*(b[k]-a[k])for k in range(3)])
        values=result
        if not values:break
    return values


def interval(polygon,line,low,high):
    # x = X0*t+X1, z = Z0*t+Z1.
    points=[tuple(F(float(v))for v in p[:2])for p in polygon.exterior.coords[:-1]]
    signed=sum(a[0]*b[1]-a[1]*b[0]for a,b in zip(points,points[1:]+points[:1]));assert signed
    sign=1 if signed>0 else -1;x0,x1,z0,z1=line
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dz=b[0]-a[0],b[1]-a[1];slope=sign*(dx*z0-dz*x0);offset=sign*(dx*(z1-a[1])-dz*(x1-a[0]))
        if not slope:
            if offset<0:return None
        elif slope>0:low=max(low,-offset/slope)
        else:high=min(high,-offset/slope)
        if low>=high:return None
    return low,high


def area_ty(points,axis):
    return abs(sum(a[axis]*b[1]-a[1]*b[axis]for a,b in zip(points,points[1:]+points[:1])))/2 if points else F(0)


class Transition:
    def __init__(self,polygons,planes,sectors):
        self.polygons=np.asarray(polygons,dtype=object);self.planes=[tuple(F(float(v))for v in p)for p in planes];self.tree=shapely.STRtree(self.polygons);self.sectors=[]
        for region,weight in sectors:
            for triangle in shapely.get_parts(shapely.constrained_delaunay_triangles(region)):
                if triangle.geom_type=='Polygon'and triangle.area>0:self.sectors.append((triangle,weight))
        self.sector_tree=shapely.STRtree([p for p,_ in self.sectors])

    def transform(self,face):
        face=np.asarray(face,float);assert face.shape==(3,3)and np.isfinite(face).all()
        n=np.cross(face[1]-face[0],face[2]-face[0]);assert n[1]==0 and np.linalg.norm(n)>0
        exact=[[F(float(v))for v in p]for p in face];axis=0 if np.ptp(face[:,0])>=np.ptp(face[:,2])else 2;low=min(p[axis]for p in exact);high=max(p[axis]for p in exact);assert low<high
        first=min(exact,key=lambda p:p[axis]);last=max(exact,key=lambda p:p[axis]);other=2 if axis==0 else 0;slope=(last[other]-first[other])/(high-low);offset=first[other]-slope*low
        assert all(p[other]==slope*p[axis]+offset for p in exact),'Parent must be exactly vertical in its represented coordinates'
        line=(F(1),F(0),slope,offset)if axis==0 else(slope,offset,F(1),F(0));query=shapely.LineString([face[np.argmin(face[:,axis])][[0,2]],face[np.argmax(face[:,axis])][[0,2]]])
        sources=[];regions=[];events={low,high}
        for i in self.tree.query(query):
            bounds=interval(self.polygons[i],line,low,high)
            if bounds:sources.append((int(i),*bounds));events.update(bounds)
        if not sources:return [face],dict(changed=False,fullyCollapsed=False)
        for i in self.sector_tree.query(query):
            bounds=interval(self.sectors[i][0],line,low,high)
            if bounds:regions.append((int(i),*bounds));events.update(bounds)
        # Include all represented height crossings before choosing the upper source.
        for left,(i,a,b)in enumerate(sources):
            pi=self.planes[i]
            for j,c,d in sources[left+1:]:
                lo,hi=max(a,c),min(b,d)
                if lo>=hi:continue
                delta=[pi[k]-self.planes[j][k]for k in range(3)];m=delta[0]*line[0]+delta[1]*line[2];q=delta[0]*line[1]+delta[1]*line[3]+delta[2]
                if m and lo<-q/m<hi:events.add(-q/m)
        events=sorted(events);output=[];partition_area=F(0);changed=False;collapsed=0;pieces=0;used_sources=set();used_sectors=set()
        for a,b in zip(events,events[1:]):
            poly=clip_interval(face,axis,a,b);part_area=area_ty(poly,axis)
            if not part_area:continue
            partition_area+=part_area;mid=(a+b)/2;available=[i for i,lo,hi in sources if lo<mid<hi];mapped=np.asarray([[float(v)for v in p]for p in poly])
            if available:
                x,z=line[0]*mid+line[1],line[2]*mid+line[3];i=max(available,key=lambda j:(self.planes[j][0]*x+self.planes[j][1]*z+self.planes[j][2],-j));choices=[j for j,lo,hi in regions if lo<mid<hi];assert choices,'Original-TIN interval lacks its return sector';weights=[]
                for j in choices:
                    w=self.sectors[j][1];weights.append(0. if w is None else float(evaluate(np.asarray([[float(x),float(z)]]),w)[0]))
                assert max(weights)-min(weights)<=1e-12,'Shared affine return weights disagree'
                used_sources.add(i);used_sectors.update(choices)
                chosen=min(choices,key=lambda j:(self.sectors[j][1]is not None,j));w=self.sectors[chosen][1];weight=np.zeros(len(mapped))if w is None else evaluate(mapped[:,[0,2]],w);plane=np.asarray([float(v)for v in self.planes[i]]);height=mapped[:,[0,2]]@plane[:2]+plane[2];mapped[:,1]=height*(1-weight)+mapped[:,1]*weight;changed=True
            pieces+=1
            for k in range(1,len(mapped)-1):
                tri=mapped[[0,k,k+1]]
                if np.linalg.norm(np.cross(tri[1]-tri[0],tri[2]-tri[0]))==0:collapsed+=1
                else:output.append(tri)
        assert partition_area==area_ty(exact,axis),'Exact vertical-parent partition lost or duplicated surface'
        if not changed:return [face],dict(changed=False,fullyCollapsed=False)
        return output,dict(changed=True,fullyCollapsed=not output,exactInputTYArea=str(partition_area),originalSourceFaceIdsUsed=sorted(used_sources),returnSectorIds=sorted(used_sectors),exactPartitionTYAreaPreserved=True,scalarIntervals=len(events)-1,pieces=pieces,zeroAreaMappedTriangles=collapsed,policy='Every parent point is partitioned before the same source/return vertex blend; only represented zero-area mapped triangles omitted. No source building edit or threshold change.')
