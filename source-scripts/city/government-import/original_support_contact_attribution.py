"""Compute exact contacts for saved unresolved original-source support witnesses.
Reusable source-only diagnostic. No geometry edits or installation approval.
"""
import argparse,uuid
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','capture','checks','uid','support']:p.add_argument('--'+k,required=True)
 a=p.parse_args();out=BASE/a.batch;assert not out.exists();refs=[Path(__file__)];cached={}
 def take(batch,path):
  if batch not in cached:cached[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==cached[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime=take(a.capture,HERE/'local'/a.capture/'runtime-geometry.json.gz');selection=take(a.capture,BASE/a.capture/'selection.json.gz')
 source=next(r for r in runtime['rows']if r['uid']==a.uid);support=next(r for r in runtime['rows']if r['uid']==a.support)
 for item in [source,support]:
  row=next(r for r in selection['rows']if r['uid']==item['uid']);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==item['sourceSHA256'];refs.append(asset)
 reports=take(a.checks,BASE/a.checks/'support-checks.json.gz');report=next(r for r in reports['rows']if r['uid']==a.uid)
 assert report['supportUid']==a.support and report['sourceSHA256']==source['sourceSHA256'] and report['supportSHA256']==support['sourceSHA256']
 failures=report['interface']['unresolved'];assert failures
 def triangles(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 tri=triangles(source);podium=triangles(support);lo,hi=tri.min(1),tri.max(1);targets=[]
 for witness in failures:
  point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));ids=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001];assert ids
  targets.append(dict(witness=witness,incidentFaces=ids))
 edges=defaultdict(list);adj=defaultdict(set)
 for i,face in enumerate(tri):
  for x,y in [(0,1),(1,2),(2,0)]:
   edge=tuple(sorted((tuple(face[x]),tuple(face[y]))))
   if edge[0]!=edge[1]:edges[edge].append(i)
 for ids in edges.values():
  for i in ids:adj[i].update(ids)
 reached={i for t in targets for i in t['incidentFaces']};queue=deque(reached)
 while queue:
  i=queue.popleft()
  for j in adj[i]-reached:reached.add(j);queue.append(j)
 claim=reservations.claim(a.batch+'-'+str(uuid.uuid4()),['immutable-source-proof:'+a.batch],batch=a.batch,ttl=21600);assert claim['ok'];lease=claim['reservation']
 try:
  save(HERE/'local'/a.batch/'reservation.json',lease)
  print(dict(uid=a.uid,witnesses=len(targets),incidentComponentFaces=len(reached),supportFaces=len(podium)),flush=True)
  proof=exact_finite_contacts(tri,sorted(reached),podium,list(range(len(podium))))
  for target in targets:target['positiveContacts']=[c for c in proof['contacts']if c['sourceFaceA']in target['incidentFaces'] and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
  result=dict(uids=[a.uid,a.support],uid=a.uid,supportUid=a.support,sourceSHA256=source['sourceSHA256'],supportSHA256=support['sourceSHA256'],sourceWorldSHA256=digest(tri.tobytes()),supportWorldSHA256=digest(podium.tobytes()),unresolvedWitnesses=len(targets),incidentComponentFaces=len(reached),finiteIncidentContacts=sum(bool(t['positiveContacts'])for t in targets),installationApproved=False,sourceGeometryChanges=0)
  save(out/'contacts.json.gz',dict(**result,targets=targets,proof=proof));save(out/'summary.json',result);assert reservations.owns(lease)
  refs.extend(HERE/n for n in ['exact_original_finite_triangle_contacts_20261010.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
  module('support_contact_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-support-contact-attribution',list(dict.fromkeys(refs)),result);print(result,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
