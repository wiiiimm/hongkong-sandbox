"""Trace the remaining witness across exactly coplanar, edge-connected original faces."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,sub,cross,dot
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-coplanar-contact-v1-20261020';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-heya-aqua-current-support-v3-20261020'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 inputs=take(PRIOR/'support-inputs.json');targets=[x for x in take(PRIOR/'finite-contacts.json.gz')['targets'] if not x['positiveContacts']];assert len(targets)==1
 sources={r['uid']:r for r in inputs['sources']};tri={}
 for uid,r in sources.items():
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['candidate']['entry']['sha256'];refs.append(p);tri[uid]=decode_original_world_triangles(p.read_bytes())
 t=tri['landsd/184287:0'];support=tri['landsd/184285:0'];edgefaces=defaultdict(list)
 for i,face in enumerate(t):
  vertices=[tuple(v) for v in face]
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):
   if a!=b:edgefaces[tuple(sorted((a,b)))].append(i)
 rows=[]
 for target in targets:
  seed=target['incidentFaces'][0];rf=rational_face(t[seed]);normal=cross(sub(rf[1],rf[0]),sub(rf[2],rf[0]));assert any(normal);seen={seed};queue=deque([seed]);links=[]
  while queue:
   i=queue.popleft();v=[tuple(p) for p in t[i]]
   for a,b in zip(v,v[1:]+v[:1]):
    if a==b:continue
    for j in edgefaces[tuple(sorted((a,b)))]:
     if j in seen:continue
     face=rational_face(t[j]);n=cross(sub(face[1],face[0]),sub(face[2],face[0]))
     if any(n) and all(dot(normal,sub(p,rf[0]))==0 for p in face):seen.add(j);queue.append(j);links.append(dict(fromFace=i,toFace=j,sharedEdge=[a,b]))
  proof=exact_finite_contacts(t,sorted(seen),support,list(range(len(support))));contacts=[x for x in proof['contacts'] if x['dimension']>0 and x['sourcePrimitiveDimensionA']==2 and x['sourcePrimitiveDimensionB']==2]
  rows.append(dict(witness=target['witness'],seedFace=seed,exactCoplanarConnectedFaces=sorted(seen),links=links,positiveContacts=contacts,proof=proof,sourceFaces=t[sorted(seen)].tolist()))
 save(DOC/'contact.json.gz',dict(rows=rows,installationApproved=False))
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py'])
 result=dict(uids=list(sources),remainingWitnesses=len(rows),witnessesWithCoplanarConnectedContact=sum(bool(r['positiveContacts']) for r in rows),connectedFaceCounts=[len(r['exactCoplanarConnectedFaces']) for r in rows],sourceGeometryChanges=0,installationApproved=False,qualification='Exact rational coplanarity and shared complete source edges. Source connectivity evidence only; no strict-interface waiver or publication approval.')
 save(DOC/'summary.json',result);module('heya_coplanar_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-witness-exact-coplanar-source-contact',list(dict.fromkeys(refs)),result);print(result,flush=True)
if __name__=='__main__':main()
