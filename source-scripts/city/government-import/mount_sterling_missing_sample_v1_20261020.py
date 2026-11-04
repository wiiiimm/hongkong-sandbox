"""Diagnose the exact missing drawn-terrain sample without changing geometry."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-missing-sample-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-mount-sterling-candidate-ground-v2-20261020';GROUND=BASE/'government-xl-mount-sterling-adjoining-ground-v1-20261020'
def main():
    assert not DOC.exists();refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (CAP,GROUND):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    row=next(r for r in take(CAP,HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'] if r['uid']=='landsd/273905:0');missing=take(CAP,CAP/'273905:0.json.gz')['uncoveredFaceIndices'];tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];ground=np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3);original=np.asarray(take(GROUND,HERE/'local'/GROUND.name/'289787:0-ground.json.gz')['completeAdjoiningTerrain']);records=[]
    for face in missing:
        points=np.vstack([tri[face],tri[face].mean(0)])
        for j,p in enumerate(points):
            point=shapely.Point(p[[0,2]]);out=dict(face=face,sample=j,position=p.tolist(),terrain={})
            for name,g in [('drawn',ground),('original',original)]:
                polygons=shapely.polygons(g[:,:,[0,2]]);dist=shapely.distance(polygons,point);nearest=np.argsort(dist)[:5];out['terrain'][name]=dict(coveringFaces=np.flatnonzero(shapely.covers(polygons,point)).tolist(),nearest=[dict(face=int(i),distanceM=float(dist[i]),vertices=g[i].tolist()) for i in nearest])
            records.append(out)
    summary=dict(uids=[row['uid']],rows=records,installationApproved=False,geometryChanges=0);save(DOC/'diagnostic.json',summary);module('mount_sterling_missing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'missing-drawn-sample-original-comparison',refs,summary)
    for r in records:print(dict(face=r['face'],sample=r['sample'],position=r['position'],drawnCoverage=len(r['terrain']['drawn']['coveringFaces']),drawnDistance=r['terrain']['drawn']['nearest'][0]['distanceM'],originalCoverage=len(r['terrain']['original']['coveringFaces'])),flush=True)
if __name__=='__main__':main()
