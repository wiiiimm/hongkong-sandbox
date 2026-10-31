"""Exact finite original intersections for all residual lower-face paths; no approval."""
from pathlib import Path
import math,numpy as np
from fractions import Fraction as F
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_local_coplanar_paths_v3_20261017 import segment
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-source-face-paths-v4-20261018';INPUT=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';EXACT=BASE/'government-xl-olympian-two-exact-start-faces-v1-20261018';BATCH='government-xl-olympian-two-residual-surface-paths-v1-20261018';DOC=BASE/BATCH

def distance(p,t):
 d=float(np.linalg.norm(closest(p,t)-p))
 return math.sqrt(float(squared_distance(p,t)))if d>1e-8 else d

def verify(tri,path,faces):
 assert len(path)==len(faces)+1
 return max(distance(p,tri[f])for n,f in enumerate(faces)for p in path[n:n+2])

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 inputs=read(INPUT/'geometry-inputs.json.gz');meshes={s['uid']:np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)]for s in inputs['rows']};exact={r['uid']:{tuple(x['position']):x['exactStartFaces']for x in r['details']}for r in read(EXACT/'exact-start-faces.json.gz')['rows']};outputs=[]
 for row in read(PRIOR/'paths.json.gz')['rows']:
  uid=row['uid'];tri=meshes[uid];known={};solved={};pending=[];errors=[]
  for d in row['details']:
   w=d['witness']
   if not w:pending.append(d);continue
   error=verify(tri,np.asarray(w['continuousLowPath']),w['faces']);assert error<=1e-8,(uid,d['position'],error);errors.append(error)
   for i,f in enumerate(w['faces']):known.setdefault(f,dict(faces=w['faces'][i:],points=w['continuousLowPath'][i+1:],contact=w['contact'],ceiling=w['contactRegionCeiling']))
  for d in pending:
   p=np.asarray(d['position']);choices=[]
   for i in exact[uid][tuple(d['position'])]:
    a=tri[i]
    for j,tail in known.items():
     b=tri[j];ceiling=tail['ceiling']
     if not np.all(a.max(0)>=b.min(0))or not np.all(b.max(0)>=a.min(0)):continue
     cut=segment(a,b,p)
     if cut is None or min(cut[:,1])>ceiling:continue
     if max(cut[:,1])>ceiling:
      t=(ceiling-cut[0,1])/(cut[1,1]-cut[0,1]);q=cut[0]+t*(cut[1]-cut[0]);cut=cut.copy();cut[0 if cut[0,1]>ceiling else 1]=q
     if np.linalg.norm(cut[1]-cut[0])<=1e-6:continue
     delta=cut[1]-cut[0];q=cut[0]+np.clip((p-cut[0])@delta/(delta@delta),0,1)*delta;path=[p,q,*map(np.asarray,tail['points'])];faces=[i,*tail['faces']];error=verify(tri,path,faces)
     if error>1e-8:continue
     choices.append(dict(kind='finite-original-face-intersection',faces=faces,path=[v.tolist()for v in path],contact=tail['contact'],ceiling=ceiling,maximumFaceResidualM=error,pathLengthM=sum(float(np.linalg.norm(b-a))for a,b in zip(path,path[1:]))))
   if choices:solved[tuple(d['position'])]=min(choices,key=lambda w:w['pathLengthM'])
  changed=True
  while changed:
   changed=False
   for d in pending:
    pos=tuple(d['position'])
    if pos in solved:continue
    p=np.asarray(pos);choices=[]
    for endpoint,tail in solved.items():
     q=np.asarray(endpoint)
     for f in exact[uid][pos]:
      if distance(q,tri[f])>1e-8:continue
      path=[p,*map(np.asarray,tail['path'])];faces=[f,*tail['faces']];error=verify(tri,path,faces)
      if error>1e-8:continue
      choices.append(dict(kind='same-original-face-to-verified-endpoint',faces=faces,path=[v.tolist()for v in path],contact=tail['contact'],ceiling=tail['ceiling'],maximumFaceResidualM=error,pathLengthM=sum(float(np.linalg.norm(b-a))for a,b in zip(path,path[1:]))))
    if choices:solved[pos]=min(choices,key=lambda w:w['pathLengthM']);changed=True
  details=[dict(position=d['position'],witness=solved.get(tuple(d['position'])))for d in pending]
  for w in solved.values():assert max(p[1]for p in w['path'])<=w['ceiling']+1e-9 and -.1<=w['contact']['gap']<=1
  summary=dict(uid=uid,initialVerifiedPaths=len(errors),residuals=len(pending),resolvedFinitePaths=len(solved),unresolved=len(pending)-len(solved),maximumInitialPathResidualM=max(errors,default=0));outputs.append(dict(**summary,details=details));print(summary,flush=True)
 save(DOC/'paths.json.gz',dict(rows=outputs,fullAcceptance=False,sourceSpecificInterfaceInterpretationAccepted=False,qualification='All accepted geometric paths independently verify finite source-triangle membership within1e-8m; numerical ambiguity uses exact rational point/triangle distance. Original canonical warnings remain. No geometry or policy changes.'))
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]]+[HERE/n for n in ['wave_local_coplanar_paths_v3_20261017.py','wave_incident_side_intersections_v1_20261017.py','pool_incident_wall_contacts_v1_20261017.py','exact_point_triangle_distance_20261018.py']]
 out=module('olympian_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-all-residual-exact-original-low-face-connections-v1',list(set(refs)),dict(uids=[x['uid']for x in outputs],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
