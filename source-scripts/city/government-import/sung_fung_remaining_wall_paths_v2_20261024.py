"""Exact shared-edge/coplanar continuation of three remaining low podium walls."""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-three-low-wall-paths-v2-20261024';out=base/batch;assert not out.exists();runtime='government-xl-next-repairs-sung-fung-courtyard-pair-runtime-v1-20261024';attributes='government-xl-next-repairs-sung-fung-original-podium-current-prephysical-v1-20261024-attributes';context='government-xl-next-repairs-sung-fung-courtyard-pair-buried-context-v1-20261024';refs=[Path(__file__)];pins={}
    for n in [runtime,attributes,context]:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
    def take(n,p):
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    uid='landsd/45779:0';row=next(r for r in take(runtime,base/runtime/'selection.json.gz')['rows']if r['uid']==uid);g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']==uid);attr=next(r for r in take(attributes,base/attributes/'attributes.json.gz')['rows']if r['uid']==uid);ctx=take(context,base/context/'45779:0.json');assert [f['faceIndex']for f in ctx['buriedFaces']]==[1308,1309,1310]and not any(f['upward']for f in ctx['buriedFaces'])
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']==ctx['sourceSHA256'];refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{n:np.asarray(attr[k]).reshape(-1,3)[ix]for n,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]});ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);maxy=F(float(ground[:,:,1].max()));results=[]
    for name,tri in modes.items():
        assert len(tri)==row['triangles'];edges=defaultdict(list);normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);nonrender={i for i,t in enumerate(tri)if exact_nonrendering(t)}
        for i,t in enumerate(tri):
            if i in nonrender:continue
            v=[tuple(p)for p in t]
            for a,b in zip(v,v[1:]+v[:1]):
                if a!=b:edges[tuple(sorted((a,b)))].append(i)
        adj=defaultdict(set)
        for ids in edges.values():
            for i in ids:adj[i].update(j for j in ids if j!=i)
        partial={}
        def exact_neighbours(i):
            if i not in partial:
                proof=exact_finite_contacts(tri,[i],tri,list(range(len(tri))))
                assert proof['allPairsExamined']
                partial[i]=[c for c in proof['contacts']if c['sourceFaceB']!=i and c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
            return adj[i]|{c['sourceFaceB']for c in partial[i]}
        paths=[]
        for start in [1308,1309,1310]:
            p,q,r=[[F(float(v))for v in point]for point in tri[start]];u=[q[k]-p[k]for k in range(3)];v=[r[k]-p[k]for k in range(3)];normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
            def coplanar(i):return all(sum(normal[k]*(F(float(point[k]))-p[k])for k in range(3))==0 for point in tri[i])
            todo=deque([start]);parent={start:None};end=None
            while todo:
                i=todo.popleft()
                if i!=start and normals[i,1]>.2*lengths[i]and min(F(float(y))for y in tri[i,:,1])>maxy:end=i;break
                for j in sorted(exact_neighbours(i)):
                    if j not in parent and (coplanar(j)or(normals[j,1]>.2*lengths[j]and min(F(float(y))for y in tri[j,:,1])>maxy)):
                        parent[j]=i;todo.append(j)
            path=[]
            if end is not None:
                k=end
                while k is not None:path.append(k);k=parent[k]
                path.reverse()
            paths.append(dict(sourceFace=start,qualified=bool(path),exactCoplanarWallPathToStrictClearUpwardCap=path,visitedFaces=sorted(parent),capGlobalExactClearanceLowerBoundM=str(min(F(float(y))for y in tri[end,:,1])-maxy)if end is not None else None))
        record=dict(exactPositivePartialContactWitnesses={str(i):v for i,v in partial.items()},mode=name,sourceWorldSHA256=digest(tri.tobytes()),completeSourceFaces=len(tri),groundSHA256=digest(ground.tobytes()),paths=paths,allThreeQualified=all(p['qualified']for p in paths));save(out/(name+'.json'),record);results.append(record);print(dict(mode=name,qualified=record['allThreeQualified'],paths=[p['exactCoplanarWallPathToStrictClearUpwardCap']for p in paths]),flush=True)
    result=dict(uids=[uid],rows=results,installationApproved=False,physicalAcceptance=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Positive paths require exact positive-dimensional finite full or partial surface contacts and same-plane continuation through unchanged source faces, terminating at an upward source cap strictly above every current ground vertex. Connectivity/clearance diagnostic only, not architectural function, footing/root or whole-model acceptance.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']);module('sung_wall_path_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'three-low-original-podium-wall-exact-continuation-diagnostic',refs,result)


if __name__=='__main__':main()
