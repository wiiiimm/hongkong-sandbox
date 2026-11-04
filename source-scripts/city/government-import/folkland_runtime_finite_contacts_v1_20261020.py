"""Exact finite contact search in all captured Folkland render representations."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-runtime-finite-contacts-v1-20261020';DOC=BASE/BATCH;UID='landsd/264677:0';POD='landsd/225387:0'
CAP=BASE/'government-xl-folkland-pair-runtime-capture-v1-20261020';SUP=BASE/'government-xl-folkland-four-mode-support-v1-20261020'
assert not DOC.exists();refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for d in [CAP,SUP]:
  r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def consume(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
capture=consume(CAP/'attributes.json.gz');assert capture['startEndAllInputsVerified'];summary=[]
for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
 worlds={x['uid']:np.asarray(x[field],dtype='<f8').reshape(-1,3)[np.asarray(x['completeOriginalIndex']).reshape(-1,3)]for x in capture['rows']}
 t,s=worlds[UID],worlds[POD];r=dict(sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(s.tobytes()));affected=[]
 bad=consume(SUP/mode/'support.json.gz')['rows'][0]['proof']['unresolved'];assert len(bad)==31
 lo,hi=t.min(1),t.max(1)
 for x in bad:
  point=np.asarray(x['position']);possible=np.flatnonzero(np.all(lo<=point+1e-6,axis=1)&np.all(hi>=point-1e-6,axis=1));ids=[int(i)for i in possible if np.linalg.norm(closest(point,t[i])-point)<=1e-6];assert ids
  affected.append(dict(position=x['position'],incidentFaces=ids))
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normals,axis=1);ny=np.divide(normals[:,1],length,out=np.zeros(len(t)),where=length>0);eligible=set(np.flatnonzero((length>0)).tolist());edges=defaultdict(list);adj={i:set()for i in eligible}
 for i in sorted(eligible):
  for a,b in zip(t[i],np.roll(t[i],-1,axis=0)):
   if not np.array_equal(a,b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for ids in edges.values():
  for i in ids:adj[i].update(j for j in ids if j!=i)
 seeds={f for x in affected for f in x['incidentFaces']if f in eligible};dist={i:0 for i in seeds};todo=deque(sorted(seeds))
 while todo:
  i=todo.popleft()
  if dist[i]==12:continue
  for j in sorted(adj.get(i,())):
   if j not in dist:dist[j]=dist[i]+1;todo.append(j)
 support=s;proof=exact_finite_contacts(t,sorted(dist),support,list(range(len(support))))
 contacts=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2]
 # Inspect contact_measure's dimension field explicitly; zero-dimensional contacts
 # are never promoted to a support route.
 positive=[c for c in contacts if c.get('dimension',-1)>0]
 roots={c['sourceFaceA']for c in positive};prev={i:None for i in roots};todo=deque(sorted(roots))
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]&set(dist)):
   if j not in prev:prev[j]=i;todo.append(j)
 paths=[]
 for a in affected:
  candidates=[]
  for f in a['incidentFaces']:
   if f not in prev:continue
   path=[f]
   while prev[path[-1]]is not None:path.append(prev[path[-1]])
   candidates.append(path)
  path=min(candidates,key=lambda p:(len(p),p))if candidates else []
  paths.append(dict(**a,hasPositiveContactPath=bool(path),faces=path,pathBounds=[t[path].min((0,1)).tolist(),t[path].max((0,1)).tolist()]if path else None,contactRows=[c for c in positive if path and c['sourceFaceA']==path[-1]]))
 save(DOC/(mode+'.json.gz'),dict(uid=UID,mode=mode,sourceWorldSHA256=r['sourceWorldSHA256'],supportWorldSHA256=r['supportWorldSHA256'],originalPodiumOnly=True,boundedSearchHops=12,faceIdsExamined=sorted(dist),proof=proof,paths=paths,installationApproved=False))
 row=dict(mode=mode,facesExamined=len(dist),pairsTested=proof['trianglePairsTested'],contactRows=len(contacts),positiveContactRows=len(positive),targets=len(paths),pathsFound=sum(p['hasPositiveContactPath']for p in paths),contactSchema=sorted(contacts[0])if contacts else []);summary.append(row);print(row,flush=True)
save(DOC/'summary.json',dict(uid=UID,rows=summary,qualification='Source-only diagnostic through original faces including undersides to exact positive-dimensional original podium intersections; canonical eligibility unchanged. No endpoint-height claim, architectural role or physical acceptance. No paths beyond twelve edges examined; misses are not proof of non-installability.',installationApproved=False))
refs.extend(HERE/n for n in ['exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
module('parkview5_lower_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-lower-wall-finite-contact-search',list(dict.fromkeys(refs)),dict(uids=[UID,POD],rows=summary,installationApproved=False,geometryChanges=0))
