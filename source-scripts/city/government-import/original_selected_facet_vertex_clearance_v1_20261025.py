"""Exact vertex clearance of selected original facets against actual compound ground.

A bounded source-role diagnostic, never physical or publication approval.
"""
import argparse
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def height(face,x,z):
    a,b,c=[tuple(F(float(v))for v in p)for p in face]
    x,z=F(float(x)),F(float(z))
    den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
    if not den:return None
    u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
    v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
    w=1-u-v
    return u*a[1]+v*b[1]+w*c[1]if min(u,v,w)>=0 else None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','clearance','uid','support']:p.add_argument('--'+k,required=True)
    p.add_argument('--face',type=int,action='append',required=True);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');source={r['uid']:r for r in selection['rows']}
    geometry={r['uid']:r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    attrs={r['uid']:r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']}
    worlds={};hashes={}
    for uid in [a.uid,a.support]:
        row=source[uid];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==attrs[uid]['sourceSHA256'];refs.append(asset);hashes[uid]=row['sourceSHA256']
        ix=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]=dict(original=decode_original_world_triangles(raw),**{m:np.asarray(attrs[uid][k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    actual=np.asarray(geometry[a.uid]['drawnGroundGeometry']).reshape(-1,3,3);rows=[]
    for mode in ['original','literal','left','balanced']:
        proof=take(a.clearance,base/a.clearance/(mode+'.json.gz'));ground=np.concatenate([actual,worlds[a.support][mode]])
        assert digest(ground.astype('<f8').tobytes())==proof['groundSHA256']
        assert digest(worlds[a.uid][mode].astype('<f8').tobytes())==proof['sourceWorldSHA256']
        by={r['sourceFace']:r for r in proof['rows']};lo=ground[:,:,[0,2]].min(1);hi=ground[:,:,[0,2]].max(1)
        for faceid in a.face:
            face=worlds[a.uid][mode][faceid];assert np.array_equal(face,np.asarray(by[faceid]['vertices']))
            vertices=[]
            for point in face:
                ids=np.flatnonzero(np.all(lo<=point[[0,2]],axis=1)&np.all(hi>=point[[0,2]],axis=1))
                values=[(height(ground[i],point[0],point[2]),int(i))for i in ids];values=[r for r in values if r[0]is not None];assert values
                highest=max(v for v,_ in values);gap=F(float(point[1]))-highest
                vertices.append(dict(point=point.tolist(),exactHighestCompoundHeight=str(highest),exactGapM=str(gap),gapM=float(gap),highestGroundFaces=[i for v,i in values if v==highest]))
            n=np.cross(face[1]-face[0],face[2]-face[0]);rows.append(dict(mode=mode,sourceFace=faceid,normalY=float(n[1]/np.linalg.norm(n)),xzSpanM=np.ptp(face[:,[0,2]],axis=0).tolist(),areaM2=float(np.linalg.norm(n)/2),vertices=vertices,anyVertexAtOrAboveCompound=any(F(v['exactGapM'])>=0 for v in vertices),anyVertexWithinExistingHalfMetreLimit=any(F(v['exactGapM'])>=F(-1,2)for v in vertices)))
    result=dict(uids=[a.uid,a.support],sourceSHA256ByUid=hashes,rows=rows,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,qualification='Every requested exact source facet vertex tested against the highest finite actual-ground/original-podium surface in all four coordinate streams. Projected-vertical terrain gives no height credit. Per-vertex evidence only; raw negative partition, whole-facet and architectural-role checks remain separate.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('selected_vertex_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-selected-original-facet-compound-vertex-clearance',refs,result)
    print([dict(mode=r['mode'],face=r['sourceFace'],gaps=[v['gapM']for v in r['vertices']])for r in rows],flush=True)

if __name__=='__main__':main()
