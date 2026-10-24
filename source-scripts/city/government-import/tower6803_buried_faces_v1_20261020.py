"""Attribute exact complete-foundation failures; original-source diagnostic only."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-buried-faces-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-tower6803-current-capture-v1-20261020';FOUND=BASE/'government-xl-tower6803-four-mode-foundations-v1-20261020'
assert not DOC.exists();refs=[Path(__file__),HERE/'xl-final-script-pass.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [CAP,FOUND]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);capture={r['uid']:r for r in read(p)['rows']}
def world(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
worlds={u:world(g)for u,g in capture.items()};final=module('tower6803_face_context',HERE/'xl-final-script-pass.py');summary=[]
def heights(points,native):
 poly=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(poly)>1e-10
 return final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native[valid],shapely.STRtree(poly[valid])).reshape(-1,4)
for uid,pod in [('landsd/6803:0','landsd/15047:0'),('landsd/15047:0',None)]:
 t=worlds[uid];ground=np.asarray(capture[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);support=np.concatenate([ground,worlds[pod]])if pod else ground;points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);h=heights(points,support);gaps=points[:,:,1]-h;ids=np.flatnonzero(np.isfinite(h).all(1)&(gaps<-.5).all(1));n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);up=n[:,1]>.25*np.linalg.norm(n,axis=1)
 fp=FOUND/(uid.split('/')[1]+'-literal.json');assert digest(fp.read_bytes())==pins[str(fp.relative_to(ROOT))];refs.append(fp);f=read(fp)['foundation'];assert len(ids)==f['fullyBuriedTriangles']and sum(up[ids])==f['fullyBuriedUpwardTriangles']
 gh=heights(points[ids],ground);gg=points[ids,:,1]-gh;rows=[]
 for j,i in enumerate(ids):rows.append(dict(faceId=int(i),vertices=t[i].tolist(),upward=bool(up[i]),completeSupportGapsM=gaps[i].tolist(),groundOnlyGapsM=gg[j].tolist(),sampledGroundClear=bool(np.isfinite(gh[j]).all()and (gg[j]>=-.5).all()),belowHigherPodiumOnly=bool(pod and np.isfinite(gh[j]).all()and (gg[j]>=-.5).all())))
 save(DOC/(uid.split('/')[1]+'.json'),dict(uid=uid,sourceWorldSHA256=digest(t.tobytes()),drawnGroundSHA256=digest(ground.tobytes()),supportUid=pod,rows=rows,qualification='Exact literal-runtime canonical failed-face attribution. Ground-only sample classification is not whole-face or physical acceptance.',installationApproved=False))
 s=dict(uid=uid,faces=len(rows),upward=sum(x['upward']for x in rows),faceIds=[x['faceId']for x in rows],belowHigherPodiumOnly=sum(x['belowHigherPodiumOnly']for x in rows));summary.append(s);print(s,flush=True)
module('tower6803_buried_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-failed-face-attribution',list(dict.fromkeys(refs)),dict(uids=list(capture),rows=summary,installationApproved=False))
