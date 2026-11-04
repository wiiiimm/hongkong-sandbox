"""Complete actual retained BASIC contacts with all four unchanged original coordinate modes."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex227942-retained-contacts-v1-20261018';DOC=BASE/BATCH;UID='landsd/227942:0'
def main():
 assert not DOC.exists();names=['government-xl-apex227942-four-world-v2-20261018','government-xl-apex227942-exterior-capture-v1-20261018'];pins={};refs=[Path(__file__)]
 for name in names:
  p=BASE/name/'result.json';r=read(p)
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(p)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 cap=BASE/names[0];worlds=read(cap/'world-triangles.json.gz');attrs=read(cap/'attributes.json.gz')['rows'][0];source=read(cap/'input.json.gz')['rows'][0];bounds={'original':np.asarray(packed_world_bounds((ROOT/source['path']).read_bytes())['originalWholeSourceBounds'])}
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
  p=np.asarray(attrs[key]).reshape(-1,3);bounds[mode]=np.array([p.min(0),p.max(0)])
 basic=read(BASE/names[1]/'basic-actors.json.gz')['rows'];assert len(basic)==4;cache={};rows=[]
 for mode,values in worlds.items():
  t=np.asarray(values[UID],dtype='<f8');b=bounds[mode]
  for actor in basic:
   p=np.asarray(actor['position'],dtype='<f8').reshape(-1,3);q=np.array([p.min(0),p.max(0)]);foreign=p[np.asarray(actor['index']).reshape(-1,3)];disjoint=bool(np.any(b[1]<q[0])or np.any(q[1]<b[0]));row=dict(mode=mode,uid=UID,foreignUid=actor['uid'],sourceWholeUnusedBounds=b.tolist(),foreignWholeUnusedBounds=q.tolist(),completeBoundsDisjoint=disjoint,sourceFaces=len(t),foreignFaces=len(foreign))
   if not disjoint:
    key=digest(t.tobytes())+'-'+digest(foreign.tobytes())
    if key not in cache:
     proof=exact_finite_contacts(t,list(range(len(t))),foreign,list(range(len(foreign))));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0;path=DOC/'pairs'/(key+'.json.gz');save(path,proof);cache[key]=dict(proofPath=str(path.relative_to(ROOT)),finiteContacts=len(proof['contacts']),trianglePairsTested=proof['trianglePairsTested'])
    row.update(cache[key],solidContainmentNotCertified=True)
   rows.append(row);print({k:row[k]for k in ['mode','foreignUid','completeBoundsDisjoint']},flush=True)
 save(DOC/'contacts.json.gz',dict(rows=rows,fullAcceptance=False));summary=dict(actorModePairs=len(rows),boundsDisjoint=sum(r['completeBoundsDisjoint']for r in rows),contactPairs=sum(r.get('finiteContacts',0)>0 for r in rows),fullAcceptance=False);save(DOC/'summary.json',summary)
 refs.extend(HERE/p for p in ['exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_packed_world_bounds_v3_20261010.py']);out=module('apex_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-four-world-complete-retained-basic-contacts-v1',list(set(refs)),dict(uids=[UID]+[a['uid']for a in basic],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
