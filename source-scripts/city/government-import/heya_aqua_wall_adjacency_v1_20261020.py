"""Record exact original edge adjacency to already measured contact faces; diagnostic only."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-heya-aqua-current-support-v3-20261020';BATCH='government-xl-heya-aqua-wall-adjacency-v1-20261020';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 source=next(x for x in take(PRIOR/'support-inputs.json')['sources']if x['uid']=='landsd/184287:0');path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256'];refs.append(path);tri=decode_original_world_triangles(path.read_bytes());contacts=take(PRIOR/'finite-contacts.json.gz')['targets'];unresolved=[x for x in contacts if not x['positiveContacts']];assert len(unresolved)==1
 proven={c['sourceFaceA']:c for x in contacts for c in x['positiveContacts']};edges=defaultdict(list)
 for i,t in enumerate(tri):
  for a,b in [(0,1),(1,2),(2,0)]:
   key=tuple(sorted((tuple(t[a]),tuple(t[b]))))
   if key[0]!=key[1]:edges[key].append(i)
 adjacent=defaultdict(dict)
 for edge,faces in edges.items():
  for a in faces:
   for b in faces:
    if a!=b:adjacent[a][b]=edge
 paths=[]
 for start in unresolved[0]['incidentFaces']:
  q=deque([(start,[start])]);seen={start};found=[]
  while q:
   face,route=q.popleft()
   if face in proven:
    found.append(dict(faces=route,sharedEdges=[adjacent[a][b]for a,b in zip(route,route[1:])],positiveContact=proven[face]));
    if len(found)>=4:break
   if len(route)>=4:continue
   for nxt in adjacent[face]:
    if nxt not in seen:seen.add(nxt);q.append((nxt,route+[nxt]))
  paths.append(dict(sourceFace=start,vertices=tri[start].tolist(),routes=found))
 result=dict(uids=[source['uid']],sourceSHA256=source['sourceSHA256'],witness=unresolved[0]['witness'],paths=paths,diagnosticOnly=True,installationApproved=False,qualification='Exact shared nonzero source edges link the flagged wall triangle to previously measured positive finite podium contacts. This records authored wall continuity, not structural engineering approval or a relaxed strict interface.')
 save(DOC/'adjacency.json',result)
 module('heya_adjacency_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-wall-exact-shared-edge-contact-context',refs,result)
 print([(p['sourceFace'],[r['faces']for r in p['routes']])for p in paths],flush=True)
if __name__=='__main__':main()
