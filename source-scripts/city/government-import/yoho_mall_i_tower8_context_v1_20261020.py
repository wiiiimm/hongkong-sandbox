"""Complete Tower 8 contact/component context; no engineering or acceptance inference."""
from pathlib import Path
from collections import defaultdict
import json,sys,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-tower8-context-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;REC=BASE/'government-xl-yoho-mall-i-tower-recovery-v1-20261020';CAP=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020';CONTACT=BASE/'government-xl-yoho-mall-i-tower-contacts-v1-20261020';UID='landsd/294858:0'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [REC,CAP,CONTACT]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];refs.append(p);used[k]=pins[d][k];return read(p)
 r=next(r for r in take(REC,REC/'recovery.json')['rows']if r['uid']==UID);m=take(CAP,CAP/'selection.json.gz')['rows'][0];ap=ROOT/r['assetPath'];mp=ROOT/m['candidate']['path'];assert digest(ap.read_bytes())==r['sourceSHA256']and digest(mp.read_bytes())==m['sourceSHA256'];refs.extend([ap,mp]);t=decode_original_world_triangles(ap.read_bytes());p=decode_original_world_triangles(mp.read_bytes());prior=take(CONTACT,CONTACT/'294858:0.json.gz');flagged={i for target in prior['targets']for i in target['incidentFaces']}
 parent=list(range(len(t)));vertices={}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,face in enumerate(t):
  for vertex in face:
   key=tuple(vertex)
   if key in vertices:parent[root(i)]=root(vertices[key])
   else:vertices[key]=i
 groups=defaultdict(list)
 for i in range(len(t)):groups[root(i)].append(i)
 print(dict(sourceFaces=len(t),exactVertexComponents=len(groups),flaggedFaces=sorted(flagged)),flush=True)
 proof=exact_finite_contacts(t,list(range(len(t))),p,list(range(len(p))));positive=[c for c in proof['contacts']if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0];contactfaces={c['sourceFaceA']for c in positive};rows=[]
 for ids in sorted(groups.values(),key=lambda ids:(-len(ids),ids[0])):
  tri=t[ids];rows.append(dict(faceIds=ids,faces=len(ids),worldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],flaggedFaces=sorted(set(ids)&flagged),positiveContactFaces=sorted(set(ids)&contactfaces)))
 save(DOC/'contacts.json.gz',proof);save(DOC/'components.json.gz',dict(rows=rows,definition='Exact shared source vertex components; not structural units or approval requirements.'))
 summary=dict(uids=[UID,'landsd/189427:0'],sourceSHA256=r['sourceSHA256'],completeSourceFaces=len(t),components=len(rows),positiveFiniteContacts=len(positive),componentsWithFlaggedSamples=[x for x in rows if x['flaggedFaces']],installationApproved=False,geometryChanges=0)
 save(DOC/'summary.json',summary)
 for path,h in used.items():assert digest((ROOT/path).read_bytes())==h
 assert reservations.owns(lease);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
 module('yoho_tower8_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-tower8-component-contact-context',list(dict.fromkeys(refs)),summary)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
