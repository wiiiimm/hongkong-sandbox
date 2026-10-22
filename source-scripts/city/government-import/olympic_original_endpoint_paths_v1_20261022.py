"""Finite original shared-edge paths bounded by actual source/grade endpoints."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-original-endpoint-paths-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();prior=BASE/'government-xl-olympic-station-raised-rim-contacts-v1-20261022';_,pins=authenticate(prior);cp=prior/'contacts.json.gz';assert digest(cp.read_bytes())==pins[str(cp.relative_to(ROOT))];contacts=read(cp);runtime=BASE/'government-xl-olympic-station-band-runtime-v1-20261022';_,rpins=authenticate(runtime);gp=HERE/'local'/runtime.name/'runtime-geometry.json.gz';assert digest(gp.read_bytes())==rpins[str(gp.relative_to(ROOT))];g=read(gp)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];edges=defaultdict(list);adj=defaultdict(dict);normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);valid=np.any(normal!=0,axis=1)
 for i,face in enumerate(t):
  if not valid[i]:continue
  for a,b in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[a]),tuple(face[b]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for edge,ids in edges.items():
  for a in ids:
   for b in ids:
    if a!=b:adj[a][b]=edge
 anchors={r['positiveIncidentContact']['sourceFace']:r['positiveIncidentContact']for r in contacts['rows']if r['positiveIncidentContact']};assert anchors;rows=[]
 for item in contacts['rows']:
  witness=item['witness'];start=np.asarray(witness['point']);found=None
  for terminal,contact in anchors.items():
   end=np.asarray(contact['contactPoint']);ceiling=float(max(start[1],end[1]));queue=deque(witness['originalIncidentFaces']);previous={i:None for i in queue if valid[i]};queue=deque(previous)
   while queue and terminal not in previous:
    a=queue.popleft()
    for b,edge in adj[a].items():
     if b not in previous and min(q[1]for q in edge)<=ceiling:previous[b]=a;queue.append(b)
   if terminal not in previous:continue
   ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();points=[start]
   for a,b in zip(ids,ids[1:]):
    x,y=map(np.asarray,adj[a][b]);x=x.copy();y=y.copy()
    if max(x[1],y[1])>ceiling:
     cut=x+(y-x)*((ceiling-x[1])/(y[1]-x[1]))
     if x[1]>ceiling:x=cut
     else:y=cut
    points.append((x+y)/2)
   points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
   if max(errors)>.001:continue
   height=float(max(p[1]for p in points));assert height<=ceiling+1e-9;found=dict(faces=ids,continuousPath=[p.tolist()for p in points],maximumResidualM=max(errors),endpointHeightCeilingM=ceiling,maximumPathHeightM=height,withinEndpointHeight=True,positiveDimensionalOriginalEdgesOnly=True,groundContact=contact);break
  rows.append(dict(witness=witness,verifiedPath=found));print(dict(sample=witness['sampleIndex'],pathFaces=len(found['faces'])if found else None),flush=True)
 result=dict(uids=['landsd/81242:0'],sourceSHA256=g['sourceSHA256'],sourceWorldSHA256=digest(t.tobytes()),raisedRimWarnings=len(rows),boundedFinitePaths=sum(r['verifiedPath']is not None for r in rows),unresolvedSamples=[r['witness']['sampleIndex']for r in rows if r['verifiedPath']is None],rows=rows,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,qualification='Actual original finite shared-edge source paths to positive-dimensional source/terrain contacts. Existing1mm point residual and own endpoint-height ceiling checks retained; no vertex-only or zero-face bridges, structural-role or publication approval.')
 save(doc/'paths.json.gz',result);save(doc/'summary.json',{k:v for k,v in result.items()if k!='rows'});refs=[Path(__file__),prior/'result.json',cp,runtime/'result.json',gp,HERE/'pool_incident_wall_contacts_v1_20261017.py'];module('olympic_endpoint_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-own-endpoint-height-original-source-grade-paths',refs,{k:v for k,v in result.items()if k!='rows'})
if __name__=='__main__':main()
