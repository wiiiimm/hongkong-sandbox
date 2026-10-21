"""Verify scoped facade witness routes, finite band feet and original host contact paths."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from pool_incident_wall_contacts_v1_20261017 import closest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-tower3a-attachment-paths-v1-20261021';DOC=BASE/BATCH
FOUND=BASE/'government-xl-tko-complete-foundations-v2-20261021';BAND=BASE/'government-xl-tko-tower3a-connected-edge-band-v1-20261021';ROLE=BASE/'government-xl-tko-tower3a-facade-role-v1-20261021';CONTACT=BASE/'government-xl-tko-complete-contacts-v1-20261021'
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def rational(p):return tuple(F(float(x))for x in p)
def foot(point,face):
 a,b,c=map(rational,face);u,v=sub(b,a),sub(c,a);w=sub(point,a);aa,ab,bb=dot(u,u),dot(u,v),dot(v,v);det=aa*bb-ab*ab;assert det>0
 beta=(dot(w,u)*bb-dot(w,v)*ab)/det;gamma=(dot(w,v)*aa-dot(w,u)*ab)/det
 assert beta>=0 and gamma>=0 and beta+gamma<=1
 q=tuple(a[i]+beta*u[i]+gamma*v[i]for i in range(3));d=dot(sub(q,point),sub(q,point));assert d<=F(.1)**2
 return q,d

def chain(start,ids,end,tri,adj):
 points=[np.asarray(start,float)]
 for a,b in zip(ids,ids[1:]):points.append(np.asarray(min(adj[a][b],key=lambda p:p[1]),float))
 points.append(np.asarray(end,float));errors=[float(np.linalg.norm(closest(q,tri[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
 assert errors and max(errors)<=.001
 return dict(faces=ids,points=[p.tolist()for p in points],maximumResidualM=max(errors))

def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={};used={};summary=[]
 for d in [FOUND,BAND,ROLE,CONTACT]:
  _,bound=authenticate(d);pins[d]=bound;refs.append(d/'result.json')
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 role=take(ROLE,ROLE/'role-review.json');assert role['roleInterpretationAccepted'] and role['uid']=='landsd/32024:0'
 for mode in ['original','literal','leftF32','balancedF32']:
  inp=take(FOUND,FOUND/mode/'32024:0/input.json.gz');r=inp['rows'][0];tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];podium=np.asarray(inp['podium']).reshape(-1,3,3)
  band=take(BAND,BAND/(mode+'.json.gz'));connected=take(BAND,BAND/(mode+'-host-connectivity.json'));contact=take(CONTACT,CONTACT/mode/'32024:0.json.gz')
  sha=digest(tri.tobytes());assert sha==band['sourceWorldSHA256']==connected['sourceWorldSHA256']==contact['sourceWorldSHA256']==role['witnesses'][mode]['sourceWorldSHA256'];assert digest(podium.tobytes())==contact['podiumWorldSHA256']
  allowed=set(role['exactFaceIds']);assert allowed==set(band['excludedFaceIds']);hostids=band['hostFaceIds'];assert hostids==connected['hostFaces'];parents={int(k):v for k,v in connected['parents'].items()}
  edges=defaultdict(list);adj=defaultdict(dict)
  for f,t in enumerate(tri):
   if np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))==0:continue
   for a,b in [(0,1),(1,2),(2,0)]:
    e=tuple(sorted((tuple(t[a]),tuple(t[b]))))
    if e[0]!=e[1]:edges[e].append(f)
  for e,ids in edges.items():
   for a in ids:
    for b in ids:
     if a!=b:adj[a][b]=e
  options=[]
  for bi,item in enumerate(band['rows']):
   assert item['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'];edge=item['sourceEdge'];ends=list(map(rational,edge));sourcefaces=[f for f in edges[tuple(map(tuple,edge))]if f in allowed];assert len(sourcefaces)==1
   for record in item['proof']['allFiniteOriginalFacetIntervals']:
    if not record['entireIntervalWithinFixedBand']:continue
    lo,hi=map(F,record['exactProjectedFootCoverageInterval']);parameter=(lo+hi)/2;point=tuple(ends[0][k]+parameter*(ends[1][k]-ends[0][k])for k in range(3));host=hostids[record['originalSurfaceFace']];q,d=foot(point,tri[host]);options.append((float(point[1]),bi,sourcefaces[0],point,host,q,d,parameter))
  options.sort(key=lambda x:x[0]);positive=defaultdict(list)
  for c in contact['proof']['contacts']:
   if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0:positive[c['sourceFaceA']].append(c)
  rows=[]
  for witness in role['witnesses'][mode]['rows']:
   starts=witness['incidentFaces'];assert set(starts)<=allowed;previous={f:None for f in starts};queue=deque(starts)
   while queue:
    f=queue.popleft()
    for n in sorted(adj[f]):
     if n in allowed and n not in previous:previous[n]=f;queue.append(n)
   choice=next((o for o in options if o[2]in previous),None);assert choice is not None
   _,bi,terminal,point,host,q,d,parameter=choice;ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();sourcepath=chain(witness['witness']['position'],ids,[float(x)for x in point],tri,adj)
   hostpath=[host]
   while parents[hostpath[-1]] is not None:hostpath.append(parents[hostpath[-1]])
   assert len(hostpath)==len(set(hostpath));seed=hostpath[-1];assert seed in connected['sourceContactSeeds']and positive[seed]
   c=positive[seed][0];points=[[F(x)for x in p]for p in c['exactPoints']];end=[sum(p[k]for p in points)/len(points)for k in range(3)]
   route=chain([float(x)for x in q],hostpath,[float(x)for x in end],tri,adj)
   rows.append(dict(witness=witness,sourcePath=sourcepath,boundaryRecordIndex=bi,exactBoundaryParameter=str(parameter),exactBoundaryPoint=list(map(str,point)),hostFace=host,exactFiniteHostFoot=list(map(str,q)),exactAttachmentSquaredDistanceM2=str(d),hostPath=route,terminalPositiveContact=c,attachmentVerified=True,structuralRootCredit=False))
  assert len(rows)==14;save(DOC/(mode+'.json.gz'),dict(uid=role['uid'],sourceWorldSHA256=sha,podiumWorldSHA256=digest(podium.tobytes()),rows=rows,installationApproved=False));summary.append(dict(mode=mode,witnesses=14,attachmentVerified=14));print(summary[-1],flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=[role['uid']],rows=summary,sourceGeometryChanges=0,installationApproved=False,qualification='Only role-reviewed projecting facade witnesses: continuous finite original-face routes to fully certified original boundary edges, exact finite host foot within unchanged 0.1m band, and nondegenerate original host path to positive finite podium contact. Not a structural root; whole-assembly acceptance remains separate.')
 save(DOC/'summary.json',result);module('tko_attachment_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'scoped-original-facade-witness-attachment-routes',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
