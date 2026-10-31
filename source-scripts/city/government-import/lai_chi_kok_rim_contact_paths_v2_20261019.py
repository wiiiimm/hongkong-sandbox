"""Every raw rim failure traced through unchanged original edges to exact support."""
from pathlib import Path
from collections import defaultdict,deque
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-rim-contact-paths-v2-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v2-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json',HERE/'exact_original_shell_intersections_20261009.py',HERE/'support-contact.mjs'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p);pins[p]=e['sha256']
 tool=HERE/'lai_chi_kok_rim_lineage_v2_20261019.mjs';subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool)],cwd=ROOT,check=True);refs.append(tool)
 data=read(SRC/'input.json.gz');support=np.asarray(data['podium']);lo=support.min(1);hi=support.max(1);normal=np.cross(support[:,1]-support[:,0],support[:,2]-support[:,0]);validsupport=np.any(normal!=0,axis=1);support_cache={};lineage={r['uid']:r for r in read(DOC/'lineage.json')['rows']};summary=[]
 for row in data['rows']:
  uid=row['uid'];tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.any(normal!=0,axis=1);edges=defaultdict(list);adj={int(i):set()for i in np.flatnonzero(valid)}
  for i in adj:
   for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
    if not np.array_equal(a,b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
  for fs in edges.values():
   for i in fs:adj[i].update(j for j in fs if j!=i)
  cache={};tests=0
  def contact(i):
   nonlocal tests
   if i not in cache:
    t=tri[i];candidates=np.flatnonzero(validsupport&np.all(hi>=t.min(0),axis=1)&np.all(lo<=t.max(0),axis=1));rf=rational_face(t);hit=None
    for v in candidates:
     j=int(v)
     if j not in support_cache:support_cache[j]=rational_face(support[j])
     points=intersection_points(rf,support_cache[j]);tests+=1
     if len(points)>1:hit=dict(sourceFace=i,supportFace=j,points=[[float(v)for v in p]for p in sorted(points)]);break
    cache[i]=hit
   return cache[i]
  rows=[]
  for sample in lineage[uid]['samples']:
   starts=sorted({g['face']for g in sample['generators']if g['face']in adj});prev={i:None for i in starts};queue=deque(starts);hit=None;end=None
   while queue:
    i=queue.popleft();hit=contact(i)
    if hit:end=i;break
    for j in sorted(adj[i]):
     if j not in prev:prev[j]=i;queue.append(j)
   path=[]
   if end is not None:
    path=[end]
    while prev[path[-1]]is not None:path.append(prev[path[-1]])
    path.reverse()
   rows.append(dict(**sample,originalSourcePath=path,finiteSupportContact=hit,visitedOriginalFaces=len(prev),hasContact=hit is not None))
  s=dict(uid=uid,samples=len(rows),withOriginalPathToSupport=sum(r['hasContact']for r in rows),maximumPathFaces=max([len(r['originalSourcePath'])for r in rows],default=0),exactFacetPairTests=tests,collapsedSupportFacesExcluded=int((~validsupport).sum()),rawStrictContacts=lineage[uid]['rawStrictContacts']);summary.append(s);save(DOC/(uid.split('/')[1]+'.json'),dict(summary=s,rows=rows));print(s,flush=True)
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False,qualification='Exact original shared-edge connectivity and positive-dimensional support contacts from all raw failed sample generators. Connectivity does not assert zero gap at each sample or replace source-role, visible exposure and browser acceptance.'))
 module('rim_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-original-component-rim-failures-exact-contact-paths',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in data['rows']],rows=summary,installationApproved=False))
if __name__=='__main__':main()
