"""Account for complete CITIC/foreign original contacts, without new admission gates."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,rational_face,segment_has
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-exact-contacts-v1-20261017';DOC=BASE/BATCH;PREV=BASE/'government-xl-citic-neighbour-originals-v1-20261017';LOCAL=HERE/'local'/PREV.name

def boundary(points,face):
 f=rational_face(face)
 return any(all(segment_has(a,b,p) for p in points) for a,b in zip(f,f[1:]+f[:1]))
def main():
 assert not DOC.exists();r=read(PREV/'result.json');refs=[Path(__file__),PREV/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={x['path']:x['sha256'] for x in r['evidenceRefs']}
 def consume(p):
  raw=p.read_bytes();assert digest(raw)==pins[str(p.relative_to(ROOT))];refs.append(p);return raw
 consume(PREV/'source-records.json');rows=read(PREV/'source-records.json')
 podium=decode_original_world_triangles(consume(LOCAL/'assets/a8058e18e0fbdfa4a38b10b9b58a5dea5d62ddf0debf76df1e39198a07969b74.glb.gz'))
 claim=reservations.claim('citic-exact-contacts-'+str(uuid.uuid4()),['building:'+u for u in ['landsd/232579:0']+[x['uid'] for x in rows]],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();out=[]
  for row in rows:
   other=decode_original_world_triangles(consume(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')))
   proof=exact_finite_contacts(podium,list(range(len(podium))),other,list(range(len(other))))
   for x in proof['contacts']:
    points=[tuple(F(v) for v in p) for p in x['exactPoints']]
    x['entireContactOnPodiumTriangleEdge']=boundary(points,podium[x['sourceFaceA']]);x['entireContactOnNeighbourTriangleEdge']=boundary(points,other[x['sourceFaceB']])
   summary=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completePodiumFaces=len(podium),completeNeighbourFaces=len(other),contacts=len(proof['contacts']),contactDimensions=dict(Counter(str(x['dimension']) for x in proof['contacts'])),bothTriangleEdges=sum(x['entireContactOnPodiumTriangleEdge'] and x['entireContactOnNeighbourTriangleEdge'] for x in proof['contacts']))
   out.append(dict(**summary,proof=proof));print(summary,flush=True);assert reservations.heartbeat(lease)['ok']
  save(DOC/'contacts.json.gz',dict(rows=out,installationApproved=False,qualification='Complete original finite-facet contacts. Triangle-edge flags describe triangulation only, not ownership or architectural roles. Source contacts alone are not a rejection guard.'))
  refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
  result=module('citic_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-complete-original-exact-finite-contacts-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/232579:0']+[x['uid'] for x in rows],rows=[{k:v for k,v in x.items() if k!='proof'} for x in out],newlyInstalled=0,installationApproved=False))
  print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
