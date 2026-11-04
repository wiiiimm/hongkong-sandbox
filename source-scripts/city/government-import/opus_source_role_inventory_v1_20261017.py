"""Complete original face connectivity and exact buried-face neighbourhoods."""
from pathlib import Path
from collections import deque
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';BATCH='government-xl-opus-source-role-inventory-v1-20261017';DOC=BASE/BATCH

def topology(tri):
 edges={};adj=[set() for _ in tri]
 for i,t in enumerate(tri):
  for j in range(3):
   edge=tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3]))))
   if edge[0]==edge[1]:continue
   for k in edges.get(edge,[]):adj[i].add(k);adj[k].add(i)
   edges.setdefault(edge,[]).append(i)
 remaining=set(range(len(tri)));components=[];membership={}
 while remaining:
  seed=min(remaining);remaining.remove(seed);queue=[seed];faces=[]
  while queue:
   i=queue.pop();faces.append(i)
   for j in sorted(adj[i]&remaining):remaining.remove(j);queue.append(j)
  faces.sort();n=len(components)
  for i in faces:membership[i]=n
  components.append(faces)
 assert sum(map(len,components))==len(tri) and len(membership)==len(tri)
 return adj,components,membership

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [WORLD,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');contacts=consume(WORLD/'contacts.json.gz')['rows'];gpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in consume(gpath)['rows']]);polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground=ground[valid];tree=shapely.STRtree(polygons[valid]);f=module('opus_role_foundation',HERE/'xl-final-script-pass.py');rows=[]
 for mode,world in worlds.items():
  for uid,t in world.items():
   tri=np.array(t);adj,components,membership=topology(tri);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(cross,axis=1);normal=np.divide(cross,length[:,None],out=np.zeros_like(cross),where=length[:,None]>0)
   points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1);heights=f.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground,tree).reshape(-1,4);gaps=points[:,:,1]-heights;buried=np.flatnonzero(np.isfinite(heights).all(axis=1)&(gaps<-.5).all(axis=1))
   details=[]
   for i in buried:
    ids=[int(i)]+sorted(adj[i]);details.append(dict(faceIndex=int(i),component=membership[int(i)],componentFaces=len(components[membership[int(i)]]),faces=[dict(faceIndex=j,vertices=tri[j].tolist(),normal=normal[j].tolist(),sampleGapsM=gaps[j].tolist(),areaM2=float(length[j]/2)) for j in ids]))
   anchors={r['sourceFace'] for r in next(x for x in contacts if x['mode']==mode)['rows'] if r['uid']==uid and r['verified']}
   wall=None
   if uid=='landsd/319559:0':
    parents={140:None};queue=deque([140]);end=None
    while queue:
     i=queue.popleft()
     if i in anchors:end=i;break
     for j in sorted(adj[i]):
      if j not in parents:parents[j]=i;queue.append(j)
    chain=[]
    while end is not None:chain.append(end);end=parents[end]
    chain.reverse();wall=dict(faceIndex=140,component=membership[140],componentFaces=len(components[membership[140]]),directAdjacentFaces=sorted(adj[140]),pathToVerifiedContactFace=chain,warning='Connected source topology alone is not complete support acceptance.')
   row=dict(mode=mode,uid=uid,totalFaces=len(tri),components=components,componentCount=len(components),degenerateFaces=np.flatnonzero(length==0).tolist(),buriedFaces=details,wall140=wall);rows.append(row);print(mode,uid,len(components),[int(i) for i in buried],wall,flush=True)
 DOC.mkdir();save(DOC/'inventory.json.gz',dict(rows=rows,fullAcceptance=False,newlyInstalled=0,qualification='All original faces retained and accounted for by exact shared nonzero edges. Buried-face neighbourhood and wall connectivity are source-role investigation evidence, not engineering certification or publication approval.'))
 refs += [HERE/'xl-final-script-pass.py',Path(f.s.context.shared.__file__)]
 out=module('opus_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-source-role-inventory-v1',refs,dict(uids=list(next(iter(worlds.values()))),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId']),flush=True)
if __name__=='__main__':main()
