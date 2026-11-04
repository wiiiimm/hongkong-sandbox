"""Recompute finite original wall contacts in all captured renderer representations."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-heya-aqua-render-contacts-v1-20261020';DOC=BASE/BATCH
SUP=BASE/'government-xl-heya-aqua-current-support-v3-20261020';REN=BASE/'government-xl-heya-aqua-render-foundations-v1-20261020';ADJ=BASE/'government-xl-heya-aqua-wall-adjacency-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_original_finite_triangle_contacts_20261010.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [SUP,REN,ADJ]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 targets=take(SUP/'finite-contacts.json.gz')['targets'];cap=take(REN/'attributes.json.gz')['rows'];adj=take(ADJ/'adjacency.json');ids=sorted({i for x in targets for i in x['incidentFaces']}|{i for x in adj['paths']for route in x['routes']for i in route['faces']});out=[]
 for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  tri={r['uid']:np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in cap};tower=tri['landsd/184287:0'];podium=tri['landsd/184285:0'];proof=exact_finite_contacts(tower,ids,podium,list(range(len(podium))))
  positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2];contacted={c['sourceFaceA']for c in positive};routes=[]
  for x in adj['paths']:
   for route in x['routes']:
    faces=route['faces'];shared=[]
    for a,b in zip(faces,faces[1:]):
     common=set(map(tuple,tower[a]))&set(map(tuple,tower[b]));assert len(common)>=2
     shared.append([list(p)for p in sorted(common)])
    routes.append(dict(faces=faces,sharedVertices=shared,lastFaceContacts=faces[-1]in contacted))
  witnesses=[dict(position=x['witness']['position'],incidentFaces=x['incidentFaces'],positiveContacts=[c for c in positive if c['sourceFaceA']in x['incidentFaces']])for x in targets]
  save(DOC/(mode+'-contacts.json.gz'),dict(proof=proof,witnesses=witnesses,adjacentRoutes=routes));row=dict(mode=mode,witnesses=len(witnesses),withPositiveIncidentContact=sum(bool(x['positiveContacts'])for x in witnesses),adjacentRoutes=routes);out.append(row);print(row,flush=True)
 result=dict(uids=['landsd/184287:0','landsd/184285:0'],rows=out,installationApproved=False,diagnosticOnly=True)
 save(DOC/'summary.json',result)
 for p in refs:
  key=str(p.relative_to(ROOT))
  if key in pins:assert digest(p.read_bytes())==pins[key]
 module('heya_render_contacts_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-wall-contacts-and-exact-shared-edges-renderer-modes',refs,result)
if __name__=='__main__':main()
