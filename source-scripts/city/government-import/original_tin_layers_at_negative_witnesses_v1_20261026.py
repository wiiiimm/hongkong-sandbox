"""Inspect original terrain at every exact negative-column witness; no selection or approval."""
import argparse
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def interval_at(face,point):
    vertices=[[F(float(v))for v in r]for r in face];x,z=point;a,b,c=vertices
    det=(a[0]-c[0])*(b[2]-c[2])-(b[0]-c[0])*(a[2]-c[2])
    if det:
        u=((x-c[0])*(b[2]-c[2])-(b[0]-c[0])*(z-c[2]))/det
        v=((a[0]-c[0])*(z-c[2])-(x-c[0])*(a[2]-c[2]))/det
        if min(u,v,1-u-v)<0:return None
        y=u*a[1]+v*b[1]+(1-u-v)*c[1];return y,y
    heights=[]
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):
        if a[0]==b[0]and a[2]==b[2]:
            if(x,z)==(a[0],a[2]):heights.extend([a[1],b[1]])
            continue
        t=(x-a[0])/(b[0]-a[0])if a[0]!=b[0]else(z-a[2])/(b[2]-a[2])
        if 0<=t<=1 and a[0]+t*(b[0]-a[0])==x and a[2]+t*(b[2]-a[2])==z:heights.append(a[1]+t*(b[1]-a[1]))
    return(min(heights),max(heights))if heights else None


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','clearance','terrain-check','uid']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    low=take(a.clearance,base/a.clearance/'summary.json');checked=next(r for r in take(a.terrain_check,base/a.terrain_check/'summary.json')['rows']if r['uid']==a.uid);assert low['sourceSHA256']==checked['sourceSHA256']
    witnesses={};modes=['original','literal','left','balanced']
    for mode in modes:
        data=take(a.clearance,base/a.clearance/(mode+'.json.gz'));rows=[];seen=set()
        for r in data['rows']:
            for pair in r['negativeGroundPairProofs']:
                for v in pair['proof']['allExactBasicFeasibleColumnVertices']:
                    if F(v['exactGapM'])>=F(-1,2):continue
                    key=(r['sourceFace'],tuple(v['exactSourcePoint']),tuple(v['exactGroundPoint']))
                    if key in seen:continue
                    seen.add(key);rows.append(dict(sourceFace=r['sourceFace'],sourcePoint=v['exactSourcePoint'],currentGroundPoint=v['exactGroundPoint'],currentGapM=v['exactGapM']))
        assert {r['sourceFace']for r in rows}=={r['sourceFace']for r in data['rows']};witnesses[mode]=rows
    xz=np.asarray([[float(F(r['sourcePoint'][i]))for i in [0,2]]for rows in witnesses.values()for r in rows]);lo=xz.min(0)-1e-7;hi=xz.max(0)+1e-7
    decoder=module('negative_witness_original_terrain',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local'/a.batch;faces=[];origins=[]
    for name in checked['sourceTerrainPaths']:
        path=ROOT/name;meta=take(a.terrain_check,path)
        for member in meta.get('buffers',[]):
            p=path.parent/member['uri'];assert digest(p.read_bytes())==pins[a.terrain_check][str(p.relative_to(ROOT))];refs.append(p)
        tri=decoder.terrain_triangles(path);keep=(tri[:,:,0].max(1)>=lo[0])&(tri[:,:,0].min(1)<=hi[0])&(tri[:,:,2].max(1)>=lo[1])&(tri[:,:,2].min(1)<=hi[1])&(np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0)
        for i in np.flatnonzero(keep):faces.append(tri[i]);origins.append(dict(path=name,sourceFace=int(i)))
    faces=np.asarray(faces);tree=shapely.STRtree(shapely.polygons(faces[:,:,[0,2]]));summary=[];cache={}
    for mode,rows in witnesses.items():
        for r in rows:
            p=tuple(F(v)for v in r['sourcePoint']);key=(p[0],p[2])
            if key not in cache:
                layers=[]
                for i in tree.query(shapely.Point(float(p[0]),float(p[2])).buffer(1e-7)):
                    interval=interval_at(faces[i],key)
                    if interval is not None:
                        area=shapely.Polygon(faces[i][:,[0,2]]).area;layers.append(dict(**origins[i],exactHeightInterval=list(map(str,interval)),usableNonverticalSurface=area>1e-10))
                cache[key]=layers
            r['originalTerrainLayers']=cache[key];heights=[F(q['exactHeightInterval'][0])for q in cache[key]if q['usableNonverticalSurface']];r['someOriginalSurfaceNotAboveSourceByHalfMetre']=any(y<=p[1]+F(1,2)for y in heights);r['originalNonverticalHeightRangeM']=[float(min(heights)),float(max(heights))]if heights else None
        save(out/(mode+'.json.gz'),dict(rows=rows));summary.append(dict(mode=mode,negativeWitnesses=len(rows),sourceFaces=len({r['sourceFace']for r in rows}),witnessesWithOriginalSurface=sum(r['originalNonverticalHeightRangeM']is not None for r in rows),witnessesWithSomeLowerOriginalSurface=sum(r['someOriginalSurfaceNotAboveSourceByHalfMetre']for r in rows),facesWithoutAnyLowerOriginalSurface=sorted({r['sourceFace']for r in rows if not r['someOriginalSurfaceNotAboveSourceByHalfMetre']})))
    result=dict(uids=[a.uid],sourceSHA256=low['sourceSHA256'],rows=summary,sourceTerrainTrianglesConsidered=len(faces),sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every exact negative feasible-column endpoint inspected against all nominated original terrain triangles. Exact rational containment/height intervals, including vertical source faces. Query buffer is nomination only. A lower layer does not establish ground identity, support or acceptance; no terrain surface selected or model edited.')
    save(out/'summary.json',result);refs.append(HERE/'xl-second-pass.py');module('negative_witness_original_layers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-negative-source-witness-original-terrain-layer-context',refs,result);print(summary,flush=True)

if __name__=='__main__':main()
