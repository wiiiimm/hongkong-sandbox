"""Whole projected cap coverage by higher original podium facets; no mesh edits."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,connect,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
CAP=BASE/'government-xl-citywalk-horizontal-caps-context-v1-20261015'
POD=BASE/'government-xl-citywalk-saved294-source-layer-attribution-v1-20261014'
BATCH='government-xl-citywalk-cap-podium-coverage-v1-20261015'
DOC=BASE/BATCH

def above(poly,y):
    out=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        inside=a[1]>=y; other=b[1]>=y
        if inside: out.append(a)
        if inside!=other: out.append(a+(b-a)*((y-a[1])/(b[1]-a[1])))
    return out

def main():
    paths=[Path(__file__),CAP/'caps.json',POD/'input.json.gz']
    for folder in [CAP,POD]:
        receipt=read(folder/'result.json');paths.append(folder/'result.json')
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    caps=read(CAP/'caps.json')['rows'];packet=read(POD/'input.json.gz');rows=[]
    for world in packet['sourceWorlds']:
        triangles=np.asarray(world['position'],dtype=float).reshape(-1,3,3)
        lo=triangles.min(axis=1);hi=triangles.max(axis=1)
        for cap in caps:
            v=np.asarray(cap['vertices']);origin=v[0,[0,2]];poly=Polygon(v[:,[0,2]]-origin);y=v[0,1]
            candidates=np.flatnonzero((hi[:,0]>=v[:,0].min())&(lo[:,0]<=v[:,0].max())&(hi[:,2]>=v[:,2].min())&(lo[:,2]<=v[:,2].max())&(hi[:,1]>y))
            covers=[];hits=[]
            for face_id in candidates:
                tri=triangles[face_id];cut=above(list(tri),y)
                if len(cut)<3: continue
                patch=Polygon(np.asarray(cut)[:,[0,2]]-origin)
                if patch.area==0: continue
                intersection=poly.intersection(patch)
                if intersection.area==0: continue
                covers.append(intersection)
                hits.append(dict(podiumFaceID=int(face_id),projectedOverlapM2=intersection.area,podiumVertexHeightRange=tri[:,1].tolist(),capHeight=float(y)))
            union=unary_union(covers);uncovered=poly.difference(union)
            rows.append(dict(uid=cap['uid'],originalFaceID=cap['originalFaceID'],podiumWorld=world['label'],towerRepresentation='actual production descriptor vertices held fixed; not a four-world tower proof',capProjectedAreaM2=poly.area,coveredAreaM2=poly.intersection(union).area,uncoveredAreaM2=uncovered.area,uncoveredWKT=uncovered.wkt,overlyingPodiumFaces=hits,sourceRoleApproved=False))
    DOC.mkdir();save(DOC/'coverage.json',dict(rows=rows,numericMethod='Float64 Shapely polygon intersection/union after exact height-plane clipping in Float64; no epsilon snapping or acceptance tolerance',acceptance=False,nextStep='Inspect cap coverage and original facade junctions together; roof projection is not an occlusion or collision certificate.'))
    module('cap_cover_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'whole-original-cap-podium-projection-v1',paths,dict(uids=['landsd/134332:0'],fullAcceptance=False,capWorldPairs=len(rows),nextStep='Use complete cap overlap instead of cap area to interpret original junction; retain independent physical/runtime checks.'))
    print([{k:r[k]for k in ['uid','originalFaceID','podiumWorld','capProjectedAreaM2','uncoveredAreaM2']}for r in rows])
if __name__=='__main__': main()
