"""Complete original/literal/explicit-Float32 compound foundations, no acceptance waiver."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-eight-foundations-v4-20261019';DOC=BASE/BATCH;PAIR=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019';ATTR=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';POD='landsd/281463:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];worlds={'original':{}}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PAIR,ATTR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(ATTR/'selection.json.gz')['rows'];assert len(rows)==8
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(raw)
 capture=read(ATTR/'attributes.json.gz');assert capture['startEndAllInputsVerified']
 for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in capture['rows']}
 runtime=read(HERE/'local'/PAIR.name/'runtime-geometry.json.gz')['rows'];ground=np.unique(np.concatenate([np.asarray(r['drawnGroundGeometry']).reshape(-1,9)for r in runtime]),axis=0).reshape(-1,3,3);final=module('pacifica_foundation',HERE/'xl-final-script-pass.py');out=[]
 for mode,world in worlds.items():
  for r in rows:
   uid=r['uid'];tri=world[uid];assert len(tri)==r['triangles'];support=ground if uid==POD else np.concatenate([ground,world[POD]]);b=r['source']['building'];f=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==len(tri)and f['fullyBuriedAreaFraction']==0 and f['fullyBuriedUpwardTriangles']==0
   evidence=dict(uid=uid,sourceSHA256=r['sourceSHA256'],mode=mode,wholeWorldSHA256=digest(np.asarray(tri,dtype='<f8').tobytes()),foundation=f,strictFoundationAccepted=strict,installationApproved=False)
   if f['fullyBuriedTriangles']:
    lo,hi=tri.min((0,1)),tri.max((0,1));native=support[(support[:,:,0].max(1)>=lo[0]-1)&(support[:,:,0].min(1)<=hi[0]+1)&(support[:,:,2].max(1)>=lo[2]-1)&(support[:,:,2].min(1)<=hi[2]+1)];poly=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(poly)>1e-10;native,poly=native[valid],poly[valid];points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(poly)).reshape(-1,4);gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1));assert len(ids)==f['fullyBuriedTriangles'];evidence['buriedFaces']=[dict(faceId=int(i),vertices=tri[i].tolist(),gaps=gaps[i].tolist())for i in ids]
   save(DOC/(uid.split('/')[1]+'-'+mode+'.json'),evidence);summary=dict(uid=uid,mode=mode,passed=strict,buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles'],complete=f['completeTerrainTriangles']);out.append(summary);print(summary,flush=True)
 save(DOC/'summary.json',dict(rows=out,installationApproved=False,sourceGeometryChanges=0))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('pacifica_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-eight-original-four-world-foundations',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=out,installationApproved=False))
if __name__=='__main__':main()
