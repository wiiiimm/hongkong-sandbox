"""Attribute newly failing rim locations to complete source and terrain faces."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from rendered_patch_sampler import RenderedPatchSampler
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-rim-layer-attribution-v1-20261019'
DOC=BASE/BATCH
def main():
    assert not DOC.exists();refs=[Path(__file__),HERE/'rendered_patch_sampler.py',HERE/'native_patch_resolution.py'];pins={}
    prior=BASE/'government-xl-lai-chi-kok-platform-rim-compare-v1-20261019'
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [prior,BASE/'government-xl-lai-chi-kok-eight-runtime-v1-20261019']:
            r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    runtime=read(HERE/'local/government-xl-lai-chi-kok-eight-runtime-v1-20261019/runtime-geometry.json.gz')['rows']
    g=next(r for r in runtime if r['uid']=='landsd/281463:0')
    p=np.asarray(g['position']).reshape(-1,3);index=np.asarray(g['index']).reshape(-1,3)
    source=p[index];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
    retainedpath=ROOT/'3d-viewer/city/data/government-native-273000-0.json'
    assert str(retainedpath.relative_to(ROOT)) in pins
    retained=repair._faces(read(retainedpath))
    layers={}
    for name,t in [('platform',source),('drawnTerrain',ground),('retained273000',retained)]:
        polygons=shapely.polygons(t[:,:,[0,2]]);valid=np.flatnonzero(shapely.area(polygons)>1e-10)
        layers[name]=(t,valid,shapely.STRtree(polygons[valid]))
    rows=[];affected=set();unique={}
    for s in read(prior/'comparison.json')['samples']:
        if (s['candidateGap']<-.5 or s['candidateGap']>1) and -.5<=s['originalGap']<=1:
            unique.setdefault(tuple(s['point']),[]).append(s['origin'])
    for point,origins in unique.items():
        x,y,z=point;hits={}
        for name,(t,ids,tree) in layers.items():
            values=[]
            for j in tree.query(shapely.Point(x,z),predicate='intersects'):
                i=int(ids[j]);height=RenderedPatchSampler.height(t[i],x,z)
                values.append(dict(faceId=i,height=float(height),abovePoint=float(height-y),vertices=t[i].tolist()))
            hits[name]=sorted(values,key=lambda r:r['height'],reverse=True)
        incident=set()
        for origin in origins:
            if 'vertex' in origin:incident.update(np.flatnonzero((index==origin['vertex']).any(1)).tolist())
            else:incident.add(origin['face'])
        affected.update(incident)
        rows.append(dict(point=point,origins=origins,incidentSourceFaces=sorted(incident),layers=hits))
    save(DOC/'attribution.json',dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],rows=rows,completeIncidentFaces=[dict(faceId=i,vertices=source[i].tolist())for i in sorted(affected)],installationApproved=False))
    summary=dict(uid=g['uid'],uniquePoints=len(rows),incidentSourceFaces=sorted(affected),points=[dict(point=r['point'],topHeights={k:v[0]['height']if v else None for k,v in r['layers'].items()})for r in rows],installationApproved=False)
    save(DOC/'summary.json',summary)
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    module('rim_layer_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'platform-rim-complete-source-and-terrain-layer-attribution',list(dict.fromkeys(refs)),dict(uids=[g['uid']],summary=summary,installationApproved=False))
    print(summary,flush=True)
if __name__=='__main__':main()
