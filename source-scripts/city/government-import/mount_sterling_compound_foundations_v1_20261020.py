"""Full original/literal/Float32 foundations against unchanged podium and ground."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-compound-foundations-v1-20261020'
DOC=BASE/BATCH
ATTR=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
GROUND=BASE/'government-xl-mount-sterling-candidate-ground-v3-20261020'
POD='landsd/289787:0'

def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [ATTR,GROUND]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    rows=take(ATTR,ATTR/'input.json.gz')['rows']
    capture=take(ATTR,ATTR/'attributes.json.gz')
    runtime=take(GROUND,HERE/'local'/GROUND.name/'runtime-geometry.json.gz')['rows']
    ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,9) for r in runtime]),axis=0).reshape(-1,3,3)
    tile=ROOT/'3d-viewer/city/data/tiles/-2_-3.json';refs.append(tile)
    forms={b['uid']:b for b in read(tile)['buildings']}
    worlds={'original':{}}
    for row in rows:
        assert row['building']==forms[row['uid']]
        p=ROOT/row['path'];raw=p.read_bytes();assert digest(raw)==row['entry']['sha256'];refs.append(p)
        worlds['original'][row['uid']]=decode_original_world_triangles(raw)
    for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in capture['rows']}
    final=module('mount_sterling_compound_foundation',HERE/'xl-final-script-pass.py');summary=[]
    for mode,world in worlds.items():
        for row in rows:
            uid=row['uid'];tri=world[uid];assert len(tri)==row['entry']['triangles']
            support=ground if uid==POD else np.concatenate([ground,world[POD]])
            b=forms[uid];f=final.foundation_context(tri,support,shapely.Polygon(b['rings'][0],b['rings'][1:]))
            evidence=dict(uid=uid,mode=mode,sourceSHA256=row['entry']['sha256'],
                          worldSHA256=digest(np.asarray(tri,dtype='<f8').tobytes()),foundation=f,installationApproved=False)
            if f['fullyBuriedTriangles']:
                lo,hi=tri.min((0,1)),tri.max((0,1))
                native=support[(support[:,:,0].max(1)>=lo[0]-1)&(support[:,:,0].min(1)<=hi[0]+1)&(support[:,:,2].max(1)>=lo[2]-1)&(support[:,:,2].min(1)<=hi[2]+1)]
                ps=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(ps)>1e-10;native,ps=native[valid],ps[valid]
                points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1)
                heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(ps)).reshape(-1,4)
                gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1))
                assert len(ids)==f['fullyBuriedTriangles']
                evidence['buriedFaces']=[dict(faceId=int(i),vertices=tri[i].tolist(),gaps=gaps[i].tolist()) for i in ids]
            save(DOC/(uid.split('/')[1]+'-'+mode+'.json.gz'),evidence)
            result=dict(uid=uid,mode=mode,complete=f['completeTerrainTriangles'],triangles=len(tri),
                        buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles'],
                        fullyBuriedAreaFraction=f['fullyBuriedAreaFraction'],
                        passed=f['completeTerrainTriangles']==len(tri) and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0)
            summary.append(result);print(result,flush=True)
    save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0))
    module('mount_sterling_compound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'eight-complete-original-and-render-compound-foundations',list(dict.fromkeys(refs)),
        dict(uids=[r['uid'] for r in rows],rows=summary,installationApproved=False))

if __name__=='__main__':main()
