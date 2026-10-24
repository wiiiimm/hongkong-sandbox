"""Bounded exact wall-path/contact investigation; no installation acceptance."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-podium-rim-contacts-v2-20261020';DOC=BASE/BATCH;UID='landsd/285642:0'
assert not DOC.exists();refs=[Path(__file__)];SRC=BASE/'government-xl-china-ferry-podium-rim-v1-20261020';receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
refs.append(SRC/'result.json')
def consume(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
PRIOR=BASE/'government-xl-china-ferry-podium-rim-contacts-v1-20261020';pr=read(PRIOR/'result.json')
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pr['jobId'],)).fetchone()==('complete',pr)
refs.append(PRIOR/'result.json');prior_pins={e['path']:e['sha256']for e in pr['evidenceRefs']}
data=consume(HERE/'local'/SRC.name/'input.json.gz');rim=consume(SRC/'rim.json');summary=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 t,s=np.asarray(data['worlds'][mode],dtype='<f8'),np.asarray(data['ground'],dtype='<f8');r=dict(sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(s.tobytes()))
 bad=next(x for x in rim['rows']if x['mode']==mode)['proof']['failed'];assert len(bad)==61
 affected=[dict(position=x['position'],incidentFaces=x['incidentFaces'])for x in bad]
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
 support=s;pp=PRIOR/(mode+'.json.gz');assert digest(pp.read_bytes())==prior_pins[str(pp.relative_to(ROOT))];refs.append(pp);saved=read(pp);assert saved['sourceWorldSHA256']==r['sourceWorldSHA256'] and saved['supportWorldSHA256']==r['supportWorldSHA256'];assert saved['faceIdsExamined']==sorted(dist);proof=saved['proof']
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
  start=np.asarray(a['position']);candidates=[]
  ordered=sorted(positive,key=lambda c:np.linalg.norm(np.array([[float(Fraction(v))for v in q]for q in c['exactPoints']]).mean(0)-start))
  for contact in ordered:
   endpoint=np.array([[float(Fraction(v))for v in q]for q in contact['exactPoints']]).mean(0);ceiling=max(start[1],endpoint[1]);root=contact['sourceFaceA'];parent={root:None};queue=deque([root]);found=None
   while queue:
    face=queue.popleft()
    if face in a['incidentFaces']:found=face;break
    for other in sorted(adj[face]&set(dist)):
     if other in parent:continue
     edge=set(map(tuple,t[face]))&set(map(tuple,t[other]))
     if len(edge)!=2 or min(q[1]for q in edge)>ceiling:continue
     parent[other]=face;queue.append(other)
   if found is not None:
    path=[found]
    while parent[path[-1]]is not None:path.append(parent[path[-1]])
    candidates=[(path,contact)];break
  path,contact=candidates[0]if candidates else([],None)
  paths.append(dict(**a,hasPositiveContactPath=bool(path),faces=path,pathBounds=[t[path].min((0,1)).tolist(),t[path].max((0,1)).tolist()]if path else None,contactRows=[contact]if contact else[]))
 save(DOC/(mode+'.json.gz'),dict(uid=UID,mode=mode,sourceWorldSHA256=r['sourceWorldSHA256'],supportWorldSHA256=r['supportWorldSHA256'],drawnGroundOnly=True,boundedSearchHops=12,faceIdsExamined=sorted(dist),proof=proof,paths=paths,installationApproved=False))
 row=dict(mode=mode,facesExamined=len(dist),pairsTested=proof['trianglePairsTested'],contactRows=len(contacts),positiveContactRows=len(positive),targets=len(paths),pathsFound=sum(p['hasPositiveContactPath']for p in paths),contactSchema=sorted(contacts[0])if contacts else []);summary.append(row);print(row,flush=True)
save(DOC/'summary.json',dict(uid=UID,rows=summary,qualification='Source-only diagnostic through original faces including undersides to exact positive-dimensional drawn ground intersections; canonical eligibility unchanged. No endpoint-height claim, architectural role or physical acceptance. No paths beyond twelve edges examined; misses are not proof of non-installability.',installationApproved=False))
refs.extend(HERE/n for n in ['exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
module('parkview5_lower_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-lower-wall-finite-contact-search',list(dict.fromkeys(refs)),dict(uids=[UID],rows=summary,installationApproved=False,geometryChanges=0))
