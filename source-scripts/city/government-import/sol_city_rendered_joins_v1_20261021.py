"""Recheck nominated exact source joins in actual renderer coordinates."""
from pathlib import Path
import sys,json,uuid,subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-sol-city-rendered-joins-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-sol-city-five-foundations-v1-20261021'
JOINS={k:[BASE/('government-xl-sol-city-'+kind+'-v'+str(v)+'-20261021') for v in [1,2]] for k,kind in [('251569:0','additional-tower-joins'),('268424:0','additional-tower-joins'),('260034:0','component-joins'),('273080:0','component-joins')]}
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)];pins={};used={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in dict.fromkeys([CAP]+[d for ds in JOINS.values() for d in ds]):
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(d/'result.json');pins[d]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 summary=[];cache={}
 for key,dirs in JOINS.items():
  pairs=set()
  for d in dirs:
   old=take(d,d/(key+'-joins.json.gz'))
   for component in old['components']:
    for c in component['outsidePositiveContacts']:
     assert c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2
     pairs.add(tuple(sorted([c['sourceFaceA'],c['sourceFaceB']])))
  pairs=sorted(pairs)
  for mode in ['literal','leftF32','balancedF32']:
   inp=take(CAP,CAP/mode/key/'input.json.gz');r=inp['rows'][0];assert r['uid']=='landsd/'+key
   tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];sha=digest(tri.tobytes());cachekey=(sha,tuple(pairs))
   if cachekey in cache:
    records=cache[cachekey]
   else:
    records=[]
    for n,(a,b) in enumerate(pairs):
     proof=exact_finite_contacts(tri,[a],tri,[b]);positive=[c for c in proof['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
     records.append(dict(sourceFaces=[a,b],positiveContacts=positive,proof=proof))
     if n%250==0:print(dict(uid=r['uid'],mode=mode,checked=n,total=len(pairs)),flush=True);assert reservations.owns(lease)
    cache[cachekey]=records
   save(DOC/mode/(key+'.json.gz'),dict(uid=r['uid'],sourceWorldSHA256=sha,records=records,installationApproved=False))
   item=dict(uid=r['uid'],mode=mode,nominatedPairs=len(pairs),positivePairs=sum(bool(r['positiveContacts']) for r in records));summary.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(HERE/n for n in ['exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
 result=dict(uids=['landsd/'+k for k in JOINS],rows=summary,installationApproved=False,sourceGeometryChanges=0)
 save(DOC/'summary.json',result)
 module('sol_rendered_join_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-rendered-nominated-intercomponent-joins',list(dict.fromkeys(refs)),result)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
