"""Complete original podium nearest-surface diagnostic; no acceptance or edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fu-tor-loy-'
BATCH=PREFIX+'nearest-interfaces-v1-20261017';DOC=BASE/BATCH

def nearest(p,tri):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];u=b-a;v=c-a;n=np.cross(u,v);nn=np.einsum('ij,ij->i',n,n)
 q=p-n*np.divide(np.einsum('ij,ij->i',p-a,n),nn,out=np.zeros(len(tri)),where=nn>0)[:,None]
 uu=np.einsum('ij,ij->i',u,u);vv=np.einsum('ij,ij->i',v,v);uv=np.einsum('ij,ij->i',u,v);d=q-a;du=np.einsum('ij,ij->i',d,u);dv=np.einsum('ij,ij->i',d,v);det=uu*vv-uv*uv
 s=np.divide(du*vv-dv*uv,det,out=np.full(len(tri),np.nan),where=det>0);t=np.divide(dv*uu-du*uv,det,out=np.full(len(tri),np.nan),where=det>0)
 ds=np.sum((q-p)**2,axis=1);ds[~((s>=0)&(t>=0)&(s+t<=1)&(nn>0))]=np.inf
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;den=np.sum(e*e,axis=1);k=np.clip(np.divide(np.sum((p-x)*e,axis=1),den,out=np.zeros(len(tri)),where=den>0),0,1);z=x+k[:,None]*e;dd=np.sum((z-p)**2,axis=1);mask=dd<ds;q[mask]=z[mask];ds[mask]=dd[mask]
 i=int(np.argmin(ds));return i,q[i],float(np.sqrt(ds[i]))

def main():
 assert not DOC.exists()
 tri=np.array([[[0.,0,0],[1,0,0],[0,0,1]]]);assert np.allclose(nearest(np.array([.2,2,.2]),tri)[1],[.2,0,.2]);assert np.allclose(nearest(np.array([2.,0,0]),tri)[1],[1,0,0])
 paths=[BASE/(PREFIX+'original-interfaces-v1-20261016')/'support-checks.json.gz',HERE/'local'/(PREFIX+'original-group-v1-20261016')/'runtime-geometry.json.gz'];refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['original-interfaces-v1','original-group-v1']:
   f=BASE/(PREFIX+name+'-20261016')/'result.json';r=read(f);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f)
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 # This source-only analysis consumes the exact saved geometry and interface files;
 # it makes no fresh terrain/current-manifest/browser acceptance claim.
 for p in paths:assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p)
 geo=read(paths[1])['rows'];triangles={g['uid']:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in geo};support=triangles['landsd/228219:0'];output=[]
 for row in read(paths[0])['rows']:
  details=[];tower=triangles[row['uid']]
  for f in row['unresolved']:
   p=np.asarray(f['position']);i,q,dist=nearest(p,support);incident=[v['faceIndex'] for v in f['originalSourceFaces']];normal=np.cross(support[i,1]-support[i,0],support[i,2]-support[i,0]);length=np.linalg.norm(normal)
   on_source=nearest(q,tower[incident])[2] if incident else None
   details.append(dict(position=f['position'],originalReason=f['reason'],originalVerticalGapM=f['gap'],nearestPodiumFace=i,nearestPosition=q.tolist(),nearestDistanceM=dist,podiumNormal=(normal/length).tolist()if length else None,incidentTowerDistanceM=on_source,withinExistingHalfMetreNomination=dist<=.5,exactSurfaceContact=dist<=.001))
  summary=dict(uid=row['uid'],failedSamples=len(details),exactSurfaceContacts=sum(x['exactSurfaceContact']for x in details),withinHalfMetre=sum(x['withinExistingHalfMetreNomination']for x in details),fartherThanHalfMetre=sum(x['nearestDistanceM']>.5 for x in details),maximumNearestDistanceM=max(x['nearestDistanceM']for x in details))
  output.append(dict(**summary,rows=details));print(summary,flush=True)
 DOC.mkdir();save(DOC/'nearest-surfaces.json.gz',dict(rows=output,fullAcceptance=False,qualification='Global nearest point over every original podium triangle. Half-metre is nomination only, not support approval. Historical exact source coordinates; no current-world/terrain acceptance.'))
 save(DOC/'summary.json',dict(rows=[{k:v for k,v in r.items()if k!='rows'}for r in output],newlyInstalled=0,fullAcceptance=False))
 r=module('fu_nearest_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-nearest-interface-diagnostic-v1',refs,dict(uids=['landsd/228219:0']+[r['uid']for r in output],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId']),flush=True)
if __name__=='__main__':main()
