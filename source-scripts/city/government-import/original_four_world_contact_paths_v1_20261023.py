"""Reapply exact original contact paths independently in all four coordinates.
Preserves every strict-interface negative. No geometry changes or approval.
"""
import argparse
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
BASE=ROOT/'docs/astra-city/government-import'

def paths(t,report):
 targets=report['targets'];assert len(targets)<=1000
 contacts=[c for c in report['proof']['contacts']if c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
 edges=defaultdict(list);adj=defaultdict(dict)
 for i,face in enumerate(t):
  for x,y in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[x]),tuple(face[y]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for edge,ids in edges.items():
  for x in ids:
   for y in ids:
    if x!=y:adj[x][y]=edge
 endpoints=[(c,np.array([[float(Fraction(v))for v in q]for q in c['exactPoints']]).mean(0))for c in sorted(contacts,key=lambda c:-c['maximumSpanM'])]
 rows=[]
 for target in targets:
  start=np.asarray(target['witness']['position']);found=None
  for contact,end in sorted(endpoints,key=lambda pair: pair[0]['sourceFaceA'] not in target['incidentFaces']):
   ceiling=max(start[1],end[1]);terminal=contact['sourceFaceA'];queue=deque(target['incidentFaces']);previous={i:None for i in queue}
   while queue and terminal not in previous:
    x=queue.popleft()
    for y,edge in adj[x].items():
     if y not in previous and min(q[1]for q in edge)<=ceiling:previous[y]=x;queue.append(y)
   if terminal not in previous:continue
   ids=[];at=terminal
   while at is not None:ids.append(at);at=previous[at]
   ids.reverse();points=[start]
   for x,y in zip(ids,ids[1:]):
    low,high=map(np.asarray,adj[x][y]);assert min(low[1],high[1])<=ceiling
    if max(low[1],high[1])>ceiling:
     cut=low+(high-low)*((ceiling-low[1])/(high[1]-low[1]))
     if low[1]>ceiling:low=cut
     else:high=cut
    points.append((low+high)/2)
   points.append(end);errors=[float(np.linalg.norm(closest(q,t[f])-q))for i,f in enumerate(ids)for q in points[i:i+2]]
   if max(errors)>.001:continue
   maximum=float(max(q[1]for q in points));assert maximum<=ceiling+1e-9
   found=dict(faces=ids,continuousPath=[q.tolist()for q in points],maximumResidualM=max(errors),endpointHeightCeilingM=float(ceiling),maximumPathHeightM=maximum,withinEndpointHeight=True,contact=contact);break
  rows.append(dict(witness=target['witness'],incidentFaces=target['incidentFaces'],verifiedPath=found))
 return rows

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','capture','attributes','support-checks','uid','support']:p.add_argument('--'+k,required=True)
 a=p.parse_args();out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cache={}
 def take(batch,path):
  if batch not in cache:cache[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==cache[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.capture,BASE/a.capture/'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
 attr=take(a.attributes,BASE/a.attributes/'attributes.json.gz');assert attr['startEndAllInputsVerified'];attrs={r['uid']:r for r in attr['rows']}
 checks=take(a.support_checks,BASE/a.support_checks/'summary.json');assert checks['supportedUid']==a.uid and checks['supportUid']==a.support
 worlds={}
 for uid in [a.uid,a.support]:
  r=selected[uid];g=attrs[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==g['sourceSHA256'];refs.append(asset)
  worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
   worlds[uid][mode]=np.asarray(g[field],dtype='<f8').reshape(-1,3)[np.asarray(g['completeOriginalIndex']).reshape(-1,3)]
 rows=[]
 for check in checks['rows']:
  mode=check['mode'];t=worlds[a.uid][mode];podium=worlds[a.support][mode]
  assert digest(t.tobytes())==check['sourceWorldSHA256ByUid'][a.uid] and digest(podium.tobytes())==check['sourceWorldSHA256ByUid'][a.support]
  lo,hi=t.min(1),t.max(1);targets=[]
  for witness in check['support']['unresolved']:
   point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
   ids=[int(i)for i in broad if np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0 and np.linalg.norm(closest(point,t[i])-point)<=.001];assert ids
   targets.append(dict(witness=witness,incidentFaces=ids))
  topology=components(t);incident={i for r in targets for i in r['incidentFaces']}
  reached=sorted({i for c in topology['components']if incident.intersection(c['faceIndices']) for i in c['faceIndices']})
  proof=exact_finite_contacts(t,reached,podium,list(range(len(podium)))) if reached else dict(contacts=[])
  report=dict(targets=targets,proof=proof);verified=paths(t,report)
  result=dict(mode=mode,targets=len(targets),verifiedPaths=sum(r['verifiedPath']is not None for r in verified),remaining=sum(r['verifiedPath']is None for r in verified),sourceWorldSHA256=check['sourceWorldSHA256ByUid'][a.uid],supportWorldSHA256=check['sourceWorldSHA256ByUid'][a.support],strictInterfacePassed=check['support']['passed'])
  save(out/(mode+'.json.gz'),dict(**result,rows=verified,exactContacts=proof));rows.append(result);print(result,flush=True)
 result=dict(uids=[a.uid,a.support],rows=rows,allUnresolvedHaveFinitePaths=all(r['remaining']==0 for r in rows),sourceGeometryChanges=0,installationApproved=False,qualification='Source-facet connectivity and exact finite contact endpoints only; strict negatives preserved. No architectural support, collision, secondary-component, identity or publication approval.')
 save(out/'summary.json',result)
 refs += [HERE/n for n in ['pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_packed_world_geometry_20261009.py','source_closed_components.py']]
 module('four_world_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-original-finite-contact-paths',refs,result)
if __name__=='__main__':main()
