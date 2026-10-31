"""Classify residual source contact paths without changing acceptance limits."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-residual-component-joins-v1-20261021';DOC=BASE/BATCH
S=BASE/'government-xl-tko-complete-foundations-v2-20261021';C=BASE/'government-xl-tko-complete-contacts-v1-20261021';P=BASE/'government-xl-tko-complete-paths-v1-20261021'
import sys,json,uuid,subprocess
from run import reservations
LOCAL=HERE/'local'/BATCH
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [S,C,P]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  assert digest(p.read_bytes())==pins[d][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 sources={'landsd/32024:0':{}};summary=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  uid='landsd/32024:0'
  key=uid.split('/')[1];paths=take(P,P/mode/(key+'.json.gz'));contacts=take(C,C/mode/(key+'.json.gz'));inp=take(S,S/mode/key/'input.json.gz');mesh=inp['rows'][0];tri=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];assert digest(tri.tobytes())==paths['sourceWorldSHA256'];edges=defaultdict(list);adj=defaultdict(set)
  for i,f in enumerate(tri):
   for a,b in [(0,1),(1,2),(2,0)]:
    edge=tuple(sorted((tuple(f[a]),tuple(f[b]))))
    if edge[0]!=edge[1]:edges[edge].append(i)
  for ids in edges.values():
   for i in ids:adj[i].update(ids)
  componentProofs={};contactFaces={c['sourceFaceA']for c in contacts['proof']['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0};out=[]
  for r in paths['rows']:
   if r['verifiedPath']:continue
   seen=set(r['incidentFaces']);queue=deque(seen)
   while queue:
    i=queue.popleft()
    for j in adj[i]-seen:seen.add(j);queue.append(j)
   hits=seen&contactFaces;signature=tuple(sorted(seen))
   if signature not in componentProofs:
    outside=sorted(set(range(len(tri)))-seen);proof=exact_finite_contacts(tri,list(signature),tri,outside)
    positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
    record=dict(componentFaces=list(signature),outsidePositiveContacts=positive,proof=proof);componentProofs[signature]=record
    print(dict(uid=uid,componentFaces=len(seen),outsidePositiveContacts=len(positive),tested=proof['trianglePairsTested']),flush=True)
   record=componentProofs[signature]
   out.append(dict(witness=r['witness'],incidentFaces=r['incidentFaces'],componentFaces=list(signature),connectedPositiveContactFaces=sorted(hits),outsidePositiveContactCount=len(record['outsidePositiveContacts']),reason='finite-face-joins-to-other-source-components'if record['outsidePositiveContacts']else'no-positive-face-join-to-any-other-source-face'))
  save(DOC/mode/(key+'-joins.json.gz'),dict(uid=uid,sourceWorldSHA256=digest(tri.tobytes()),components=list(componentProofs.values()),installationApproved=False))
  save(DOC/mode/(key+'.json'),dict(uid=uid,rows=out,installationApproved=False));counts={reason:sum(r['reason']==reason for r in out)for reason in sorted({r['reason']for r in out})};summary.append(dict(mode=mode,uid=uid,residual=len(out),reasons=counts))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False));refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
 module('sol_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-intercomponent-finite-joins',refs,dict(uids=list(sources),rows=summary,installationApproved=False));print(summary,flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
