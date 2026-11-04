"""Verify finite lower-wall paths to authored contact edges; no acceptance."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-runtime-finite-path-verification-v1-20261020';DOC=BASE/BATCH;SOURCE=BASE/'government-xl-folkland-runtime-finite-contacts-v1-20261020';INPUT=BASE/'government-xl-folkland-pair-runtime-capture-v1-20261020';UID='landsd/264677:0'
assert not DOC.exists();refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [SOURCE,INPUT]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
def consume(d,file):
 p=d/file;assert digest(p.read_bytes())==pins[d.name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
summary=[]
capture=consume(INPUT,'attributes.json.gz')
for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
 worlds={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in capture['rows']}
 proof=consume(SOURCE,mode+'.json.gz');t=np.asarray(worlds[UID],dtype='<f8');assert digest(t.tobytes())==proof['sourceWorldSHA256'];out=[]
 for p in proof['paths']:
  ids=p['faces'];assert ids and p['hasPositiveContactPath'];start=np.asarray(p['position'])if 'position'in p else t[p['faceId']].mean(0)
  contact=max(p['contactRows'],key=lambda c:c['maximumSpanM']);assert contact['dimension']>0
  endpoints=np.array([[float(Fraction(v))for v in q]for q in contact['exactPoints']]);end=endpoints.mean(0);ceiling=max(start[1],end[1]);points=[start];above=False
  for a,b in zip(ids,ids[1:]):
   edge=sorted(set(map(tuple,t[a]))&set(map(tuple,t[b])));assert len(edge)==2;x,y=map(np.asarray,edge)
   if min(x[1],y[1])>ceiling+1e-9:above=True
   if min(x[1],y[1])<=ceiling<max(x[1],y[1]):
    cut=x+(y-x)*((ceiling-x[1])/(y[1]-x[1]))
    if x[1]>ceiling:x=cut
    else:y=cut
   points.append((x+y)/2)
  points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]];normal=np.cross(t[ids,1]-t[ids,0],t[ids,2]-t[ids,0]);ratio=normal[:,1]/np.linalg.norm(normal,axis=1)
  # A deck contact on an original upper edge is distinguished from an arbitrary
  # interior triangle crossing. Check both contact endpoints against all edges.
  edgeDistances=[]
  for q in endpoints:
   ds=[]
   for a,b in zip(t[ids[-1]],np.roll(t[ids[-1]],-1,axis=0)):
    v=b-a;f=np.clip(np.dot(q-a,v)/np.dot(v,v),0,1)if np.dot(v,v)else 0;ds.append(float(np.linalg.norm(q-(a+f*v))))
   edgeDistances.append(min(ds))
  out.append(dict(target=p.get('position',p.get('faceId')),faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),maximumPathHeightM=float(max(q[1]for q in points)),endpointHeightCeilingM=float(ceiling),withinEndpointHeight=bool(not above and max(q[1]for q in points)<=ceiling+1e-9),allSteepWallFaces=bool(np.all(np.abs(ratio)<=.25)),terminalContactOnSourceBoundary=all(d<=.001 for d in edgeDistances),terminalContactBoundaryDistancesM=edgeDistances,terminalContact=contact,finitePathVerified=max(errors)<=.001))
 save(DOC/(mode+'.json'),dict(uid=UID,mode=mode,sourceWorldSHA256=proof['sourceWorldSHA256'],supportWorldSHA256=proof['supportWorldSHA256'],rows=out,installationApproved=False))
 s=dict(mode=mode,targets=len(out),finitePaths=sum(x['finitePathVerified']for x in out),boundedHeightPaths=sum(x['withinEndpointHeight']for x in out),wallOnlyPaths=sum(x['allSteepWallFaces']for x in out),sourceBoundaryContacts=sum(x['terminalContactOnSourceBoundary']for x in out),maximumResidualM=max(x['maximumResidualM']for x in out));summary.append(s);print(s,flush=True)
save(DOC/'summary.json',dict(rows=summary,installationApproved=False,qualification='Finite face-segment and own-contact-height verification only. Boundary contacts are classified separately from interior crossings. No structural or source-role acceptance.'))
module('park5_path_verified_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-lower-wall-path-segment-verification',refs,dict(uids=[UID],rows=summary,installationApproved=False))
