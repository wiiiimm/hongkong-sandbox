"""Resolve remaining warnings against actual strict grade anchors on the same source."""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction
import heapq,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-original-strict-anchor-paths-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name,local=False):
  folder=BASE/batch;r,p=authenticate(folder);path=(HERE/'local'/batch if local else folder)/name;assert digest(path.read_bytes())==p[str(path.relative_to(ROOT))];refs.extend([folder/'result.json',path]);return read(path)
 paths=take('government-xl-olympic-original-endpoint-paths-v2-20261022','paths.json.gz');ctx=take('government-xl-olympic-station-band-continuous-v1-20261022','81242:0.json.gz');g=take('government-xl-olympic-station-band-runtime-v1-20261022','runtime-geometry.json.gz',True)['rows'][0];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert digest(t.tobytes())==paths['sourceWorldSHA256']==ctx['sourceBinding']['decodedWorldTrianglesSHA256'];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);polys=shapely.polygons(ground[:,:,[0,2]]);validground=shapely.area(polys)>1e-10;ground=ground[validground];polys=polys[validground];tree=shapely.STRtree(polys);sampler=module('strict_anchor_actual_ground',HERE/'xl-final-script-pass.py');normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);valid=np.any(normal!=0,axis=1);anchors={}
 for i,c in enumerate(ctx['faces']):
  anchor=c['minimum']
  if not valid[i]or not c['groundProjectionCovered']or not anchor or not -.1<=anchor['minimumGapM']<=.1:continue
  p=np.asarray(anchor['position']);residual=float(np.linalg.norm(closest(p,t[i])-p))
  if residual>.001:continue
  height=float(sampler.s.context.shared.samples(p[None,[0,2]],ground,tree)[0]);gap=float(p[1]-height)
  if np.isfinite(height)and -.1<=gap<=.1:anchors[i]=dict(sourceFace=i,sourcePoint=p.tolist(),actualGroundHeight=height,actualGap=gap,sourceResidualM=residual,strictBandM=[-.1,.1])
 edges=defaultdict(list);adj=defaultdict(dict)
 for i,face in enumerate(t):
  if not valid[i]:continue
  for a,b in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[a]),tuple(face[b]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for edge,ids in edges.items():
  for a in ids:
   for b in ids:
    if a!=b:adj[a][b]=edge
 joins=take('government-xl-olympic-original-low-component-joins-v1-20261022','finite-contacts.json.gz')
 for c in joins['contacts']:
  a,b=c['sourceFaceA'],c['sourceFaceB']
  if a==b or c['dimension']<=0 or c['sourcePrimitiveDimensionA']!=2 or c['sourcePrimitiveDimensionB']!=2:continue
  points=[tuple(float(Fraction(v))for v in p)for p in c['exactPoints']];low=min(points,key=lambda p:p[1])
  if b not in adj[a]:adj[a][b]=adj[b][a]=(low,low)
 rows=[]
 for target in [r for r in paths['rows']if not r['verifiedPath']]:
  w=target['witness'];start=np.asarray(w['point']);cost={i:float(start[1])for i in w['originalIncidentFaces']if valid[i]};previous={i:None for i in cost};queue=[(v,i)for i,v in cost.items()];heapq.heapify(queue)
  while queue:
   value,a=heapq.heappop(queue)
   if value!=cost[a]:continue
   for b,edge in adj[a].items():
    needed=max(value,min(p[1]for p in edge))
    if needed<cost.get(b,float('inf')):cost[b]=needed;previous[b]=a;heapq.heappush(queue,(needed,b))
  candidates=sorted((i for i in anchors if i in cost and cost[i]<=max(start[1],anchors[i]['sourcePoint'][1])+1e-9),key=lambda i:(max(start[1],anchors[i]['sourcePoint'][1]),abs(anchors[i]['actualGap']),i));found=None
  for terminal in candidates:
   end=np.asarray(anchors[terminal]['sourcePoint']);ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();points=[start]+[np.asarray(min(adj[a][b],key=lambda p:p[1]))for a,b in zip(ids,ids[1:])]+[end];errors=[float(np.linalg.norm(closest(q,t[f])-q))for k,f in enumerate(ids)for q in points[k:k+2]];ceiling=float(max(start[1],end[1]));height=float(max(p[1]for p in points))
   if max(errors)>.001 or height>ceiling+1e-9:continue
   found=dict(faces=ids,continuousPath=[p.tolist()for p in points],strictGradeAnchor=anchors[terminal],maximumResidualM=max(errors),maximumPathHeightM=height,endpointHeightCeilingM=ceiling);break
  reachableAnchors=[i for i in anchors if i in cost];row=dict(witness=w,verifiedPath=found,reachableSourceFaces=len(cost),reachableStrictAnchors=len(reachableAnchors),minimumRequiredHeightToAnyStrictAnchorM=min([cost[i]for i in reachableAnchors],default=None),reachableSourceFaceIds=sorted(cost)if found is None else[]);rows.append(row);print(dict(sample=w['sampleIndex'],pathFaces=len(found['faces'])if found else None,reachable=len(cost),anchors=len(reachableAnchors)),flush=True)
 result=dict(uids=paths['uids'],sourceWorldSHA256=paths['sourceWorldSHA256'],strictOriginalGradeAnchors=len(anchors),remainingTargets=len(rows),newQualifiedPaths=sum(r['verifiedPath']is not None for r in rows),unresolvedSamples=[r['witness']['sampleIndex']for r in rows if not r['verifiedPath']],rows=rows,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,qualification='Exact source interfaces and same-source finite convex paths to independently replayed strict .1m grade anchors. Existing1mm residual and own endpoint-height bounds retained; raw prior failures remain. No facade-role or publication approval.')
 save(doc/'paths.json.gz',result);save(doc/'summary.json',{k:v for k,v in result.items()if k!='rows'});refs.extend([HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'xl-final-script-pass.py']);module('olympic_strict_anchor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-strict-grade-anchor-paths',refs,{k:v for k,v in result.items()if k!='rows'})
if __name__=='__main__':main()
