"""Complete vertex/edge-midpoint/centroid proximity census; no attachment approval."""
from pathlib import Path
import time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';GRAPH=BASE/'government-xl-opus-original-component-graph-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-detached-distance-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(GRAPH/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),GRAPH/'result.json',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py']
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 graph=consume(GRAPH/'graph.json.gz');worlds=consume(WORLD/'world-triangles.json.gz');uids=sorted(worlds['original']);tri=np.concatenate([np.array(worlds['original'][u]) for u in uids]);assert all(np.array_equal(tri,np.concatenate([np.array(w[u]) for u in uids])) for w in worlds.values())
 ids=np.array([i for b in graph['positiveContactReachableFromPodium'] for i in graph['components'][b]['globalFaces']]);support=tri[ids];lo=support.min(axis=1);hi=support.max(axis=1);results=[]
 claim=reservations.claim('opus-distance-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 try:
  for body in graph['unconnectedComponents']:
   faces=graph['components'][body]['globalFaces'];t=tri[faces];p=np.unique(np.concatenate([t.reshape(-1,3),((t+np.roll(t,-1,axis=1))/2).reshape(-1,3),t.mean(axis=1)]),axis=0);details=[]
   for point in p:
    candidates=np.flatnonzero(np.all(hi>=point-.1,axis=1)&np.all(lo<=point+.1,axis=1))
    if len(candidates):i,q,d=nearest(point,support[candidates]);j=int(candidates[i])
    else:d=float('inf')
    if d>.1:j,q,d=nearest(point,support)
    details.append(dict(position=point.tolist(),nearestConnectedFace=int(ids[j]),nearestPosition=q.tolist(),distanceM=d))
    if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(body,len(details),len(p),flush=True)
   results.append(dict(component=body,faces=len(faces),probes=len(p),maximumProbeDistanceM=max(x['distanceM'] for x in details),minimumProbeDistanceM=min(x['distanceM'] for x in details),probesBeyondPointOneMetre=sum(x['distanceM']>.1 for x in details),rows=details));print({k:v for k,v in results[-1].items() if k!='rows'},flush=True)
  DOC.mkdir();save(DOC/'distances.json.gz',dict(rows=results,fullAcceptance=False,qualification='Every unique original vertex, edge midpoint and face centroid compared against all positive-area podium-connected original surfaces. Nearest search is globally exact when distance exceeds 0.1m; within-band candidate search may omit a nearer face outside its cube but still proves the recorded distance bound. Sampling does not certify full-face/boundary attachment. No source edit or bridge/root credit.'))
  summary=dict(rows=[{k:v for k,v in x.items() if k!='rows'} for x in results],fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
  result=module('opus_distance_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-detached-source-proximity-census-v1',refs,dict(uids=uids,**summary));print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
