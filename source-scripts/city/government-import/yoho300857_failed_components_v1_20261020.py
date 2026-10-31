"""Exact source components containing three flagged facets, without acceptance."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from source_closed_components import components
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-failed-components-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-buried-faces-v1-20261020';CAP=BASE/'government-xl-yoho300857-private-terrain-capture-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),SRC/'result.json',HERE/'source_closed_components.py']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);summary=[]
for g in read(p)['rows']:
 uid=g['uid'];f=SRC/(uid.split('/')[1]+'.json');assert digest(f.read_bytes())==pins[str(f.relative_to(ROOT))];refs.append(f);flags={x['faceId']for x in read(f)['rows']};t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];cs=[c for c in components(t)['components']if flags.intersection(c['faceIndices'])]
 out=[]
 for c in cs:
  ids=c['faceIndices'];v=t[ids];n=np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]);length=np.linalg.norm(n,axis=1);norm=np.divide(n,length[:,None],out=np.zeros_like(n),where=length[:,None]>0)
  out.append(dict(topology=c,flaggedFaces=sorted(flags.intersection(ids)),bounds=[v.min((0,1)).tolist(),v.max((0,1)).tolist()],faces=[dict(faceId=i,vertices=t[i].tolist(),normal=norm[j].tolist())for j,i in enumerate(ids)]))
 save(DOC/(uid.split('/')[1]+'.json.gz'),dict(uid=uid,sourceWorldSHA256=digest(t.astype('<f8').tobytes()),components=out,installationApproved=False));summary.append(dict(uid=uid,components=[dict(faces=len(x['faces']),flags=x['flaggedFaces'],bounds=x['bounds'])for x in out]));print(summary[-1],flush=True)
module('yoho_failed_components_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-flagged-source-components',refs,dict(uids=[x['uid']for x in summary],rows=summary,installationApproved=False))
