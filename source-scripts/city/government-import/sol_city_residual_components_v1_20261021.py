"""Classify residual source contact paths without changing acceptance limits."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-residual-components-v1-20261021';DOC=BASE/BATCH
S=BASE/'government-xl-sol-city-original-support-20261006';C=BASE/'government-xl-sol-city-original-contacts-v1-20261021';P=BASE/'government-xl-sol-city-original-paths-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for d in [S,C,P]:
  r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
def take(d,p):
 assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
sources={r['uid']:r for r in take(S,S/'support-inputs.json')['sources']};summary=[]
for uid in ['landsd/273080:0','landsd/260034:0']:
 key=uid.split('/')[1];paths=take(P,P/'original'/(key+'.json.gz'));contacts=take(C,C/'original'/(key+'.json.gz'));row=sources[uid];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['candidate']['entry']['sha256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert digest(tri.tobytes())==paths['sourceWorldSHA256'];edges=defaultdict(list);adj=defaultdict(set)
 for i,f in enumerate(tri):
  for a,b in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(f[a]),tuple(f[b]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for ids in edges.values():
  for i in ids:adj[i].update(ids)
 contactFaces={c['sourceFaceA']for c in contacts['proof']['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0};out=[]
 for r in paths['rows']:
  if r['verifiedPath']:continue
  seen=set(r['incidentFaces']);queue=deque(seen)
  while queue:
   i=queue.popleft()
   for j in adj[i]-seen:seen.add(j);queue.append(j)
  hits=seen&contactFaces
  out.append(dict(witness=r['witness'],incidentFaces=r['incidentFaces'],connectedFaces=len(seen),connectedPositiveContactFaces=sorted(hits),reason='connected-contact-without-endpoint-bounded-path'if hits else'no-positive-contact-in-edge-connected-source-component'))
 save(DOC/(key+'.json'),dict(uid=uid,rows=out,installationApproved=False));counts={reason:sum(r['reason']==reason for r in out)for reason in sorted({r['reason']for r in out})};summary.append(dict(uid=uid,residual=len(out),reasons=counts))
save(DOC/'summary.json',dict(rows=summary,installationApproved=False));refs.append(HERE/'exact_packed_world_geometry_20261009.py')
module('sol_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-residual-source-component-classification',refs,dict(uids=list(sources),rows=summary,installationApproved=False));print(summary,flush=True)
