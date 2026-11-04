"""Measure original inclined-wall contact at existing 1mm tolerance; diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-incident-wall-contacts-v1-20261017';DOC=BASE/BATCH

def closest(p,t):
 a,b,c=t;u=b-a;v=c-a;n=np.cross(u,v);nn=n@n;candidates=[]
 if nn:
  q=p-n*((p-a)@n)/nn;uv=np.linalg.lstsq(np.column_stack((u,v)),q-a,rcond=None)[0]
  if min(uv)>=-1e-10 and uv.sum()<=1+1e-10:candidates.append(q)
 for x,y in [(a,b),(b,c),(c,a)]:
  e=y-x;den=e@e;candidates.append(x+np.clip((p-x)@e/den,0,1)*e if den else x)
 return min(candidates,key=lambda q:np.linalg.norm(p-q))

def main():
 assert np.allclose(closest(np.array([.2,2.,.2]),np.array([[0.,0,0],[1,0,0],[0,0,1]])),[.2,0,.2])
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for name in ['original-group-v1','original-interfaces-v1']:
  p=BASE/('government-xl-sham-shui-po-pool-'+name+'-20261016')/'result.json';r=read(p)
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(p)
  for q in r['evidenceRefs']:
   assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 path=HERE/'local/government-xl-sham-shui-po-pool-original-group-v1-20261016/runtime-geometry.json.gz';geo=read(path)['rows'];tri={g['uid']:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in geo};support=tri['landsd/265480:0'];output=[]
 a=support[:,0];u=support[:,1]-a;v=support[:,2]-a;det=u[:,0]*v[:,2]-u[:,2]*v[:,0];valid=np.abs(det)>1e-12
 failures=read(BASE/'government-xl-sham-shui-po-pool-original-interfaces-v1-20261016/support-checks.json.gz')['rows'][0]['unresolved']
 for f in failures:
  p=np.array(f['position']);deck=p.copy();deck[1]-=f['gap'];rows=[]
  for face in f['originalSourceFaces']:
   t=tri['landsd/271043:0'][face['faceIndex']];q=closest(deck,t);delta=q-a
   s=np.divide(delta[:,0]*v[:,2]-delta[:,2]*v[:,0],det,out=np.full_like(det,np.nan),where=valid);z=np.divide(u[:,0]*delta[:,2]-u[:,2]*delta[:,0],det,out=np.full_like(det,np.nan),where=valid)
   ids=np.flatnonzero(valid&(s>=-1e-8)&(z>=-1e-8)&(s+z<=1+1e-8));heights=a[ids,1]+s[ids]*u[ids,1]+z[ids]*v[ids,1];gaps=q[1]-heights
   hits=[dict(faceIndex=int(i),height=float(h),gapM=float(g)) for i,h,g in zip(ids,heights,gaps) if abs(g)<=.001]
   rows.append(dict(sourceFace=face['faceIndex'],normal=face['normal'],originalStartDistanceM=float(np.linalg.norm(closest(p,t)-p)),contact=q.tolist(),embeddingHeightM=float(q[1]-p[1]),horizontalTravelM=float(np.linalg.norm((q-p)[[0,2]])),supportContacts=hits,nearestSupportGapM=float(gaps[np.argmin(abs(gaps))]) if len(gaps) else None))
  output.append(dict(position=f['position'],candidates=rows,hasIncidentContact=any(r['supportContacts'] and 0<=r['embeddingHeightM']<=.5 and r['originalStartDistanceM']<=.001 for r in rows)))
 DOC.mkdir();save(DOC/'contacts.json',dict(rows=output,diagnosticOnly=True,fullAcceptance=False,qualification='Same original incident triangle, measured source displacement, support contact within existing 1mm threshold. No wall-type or whole-interface acceptance inferred.'))
 refs.append(path);r=module('pool_incident_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'inclined-original-incident-wall-contact-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0'],fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=r['jobId'],contacts=sum(r['hasIncidentContact'] for r in output),total=len(output)),flush=True)
if __name__=='__main__':main()
