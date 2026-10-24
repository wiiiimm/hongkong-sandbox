"""All original Opus positive-area components and exact inter-component contacts."""
from pathlib import Path
import time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from opus_source_role_inventory_v1_20261017 import topology
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-original-component-graph-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(WORLD/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={x['path']:x['sha256'] for x in r['evidenceRefs']};path=WORLD/'world-triangles.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];worlds=read(path);uids=sorted(worlds['original']);alltri={m:np.concatenate([np.array(w[u]) for u in uids]) for m,w in worlds.items()};tri=alltri['original'];assert len(tri)==13557
 bodies=[];zero=[];offset=0;actors=[]
 for uid in uids:
  t=np.array(worlds['original'][uid]);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);ids=np.flatnonzero(np.any(cross!=0,axis=1));zero.extend((offset+np.flatnonzero(np.all(cross==0,axis=1))).tolist());_,parts,_=topology(t[ids]);actors.append(dict(uid=uid,offset=offset,faces=len(t),positiveAreaComponents=len(parts)))
  for part in parts:
   faces=(offset+ids[part]).tolist();z=tri[faces];bodies.append(dict(uid=uid,globalFaces=faces,bounds=[z.min((0,1)).tolist(),z.max((0,1)).tolist()]))
  offset+=len(t)
 members={f:i for i,b in enumerate(bodies) for f in b['globalFaces']};assert len(members)+len(zero)==len(tri) and not set(members)&set(zero)
 lo=np.array([b['bounds'][0] for b in bodies]);hi=np.array([b['bounds'][1] for b in bodies]);pairs=[(a,b) for a in range(len(bodies)) for b in range(a+1,len(bodies)) if np.all(hi[a]>=lo[b]) and np.all(hi[b]>=lo[a])];flo=tri.min(axis=1);fhi=tri.max(axis=1);cache={};contacts=[];pointcontacts=[];tested=0
 claim=reservations.claim('opus-graph-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def exact(i):
  if i not in cache:cache[i]=rational_face(tri[i])
  return cache[i]
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(dict(testedFacePairs=tested,positiveComponentPairs=len(contacts)),flush=True)
 try:
  for a,b in pairs:
   left=bodies[a]['globalFaces'];right=bodies[b]['globalFaces']
   if len(left)>len(right):left,right=right,left
   right=np.array(right);found=None;point=None
   for i in left:
    hits=right[np.all(flo[right]<=fhi[i],axis=1)&np.all(fhi[right]>=flo[i],axis=1)]
    for j in hits:
     j=int(j);tested+=1;p=intersection_points(exact(i),exact(j));pulse()
     if not p:continue
     record=dict(components=[a,b],sourceFaces=[i,j],contact=contact_measure(p))
     if len(p)>1:found=record;break
     if point is None:point=record
    if found:break
   if found:contacts.append(found)
   elif point:pointcontacts.append(point)
  roots={i for i,b in enumerate(bodies) if b['uid']=='landsd/248432:0'};assert len(roots)==1;reached=set(roots)
  while True:
   old=set(reached)
   for x in contacts:
    if set(x['components'])&reached:reached.update(x['components'])
   if old==reached:break
  replay=[]
  for mode,t in alltri.items():
   failed=[]
   for n,x in enumerate(contacts):
    i,j=x['sourceFaces'];p=intersection_points(rational_face(t[i]),rational_face(t[j]));pulse()
    if len(p)<2:failed.append(n)
   replay.append(dict(mode=mode,worldSHA256=digest(t.tobytes()),positiveWitnesses=len(contacts)-len(failed),failedWitnesses=failed))
  out=dict(actors=actors,completeOriginalFaces=len(tri),components=bodies,zeroAreaFacesRetainedUncredited=zero,allComponentPairs=len(bodies)*(len(bodies)-1)//2,boundingCandidates=len(pairs),exactTrianglePairsTested=tested,positiveContacts=contacts,pointOnlyContactsUncredited=pointcontacts,podiumComponentCandidates=sorted(roots),positiveContactReachableFromPodium=sorted(reached),unconnectedComponents=sorted(set(range(len(bodies)))-reached),fourWorldPositiveWitnessReplay=replay,fullAcceptance=False,structuralSupportAccepted=False,newlyInstalled=0,qualification='Complete nonzero-edge components of positive-area source faces; one exact positive-dimensional witness per intersecting component pair. Zero-area and point-only contacts provide no bridge credit. Podium is a nominated graph root only, not independently accepted ground support. Remaining source identity, ground roots, finite clearance, neighbours and browser checks required.')
  DOC.mkdir();save(DOC/'graph.json.gz',out);refs=[Path(__file__),WORLD/'result.json',path,*[HERE/n for n in ['opus_source_role_inventory_v1_20261017.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']]]
  result=module('opus_graph_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-positive-component-contact-graph-v1',refs,dict(uids=uids,componentCount=len(bodies),reachableFromPodium=len(reached),unconnectedComponents=out['unconnectedComponents'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],actors=actors,componentCount=len(bodies),reachableFromPodium=len(reached),unconnectedComponents=out['unconnectedComponents'],replay=replay),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
