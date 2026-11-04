"""Bind exact current support witnesses to immutable, previously proven original contacts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sol-city-current-original-contacts-v1-20261021';DOC=BASE/BATCH
CAP=BASE/'government-xl-sol-city-five-foundations-v1-20261021';OLD=BASE/'government-xl-sol-city-original-contacts-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,OLD]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];used[k]=pins[d][k];refs.append(p);return read(p)
 summary=[]
 for key in ['260034:0','273080:0']:
  inp=take(CAP,CAP/'original'/key/'input.json.gz');s=take(CAP,CAP/'original'/key/'support.json.gz')['rows'][0]['proof'];old=take(OLD,OLD/'original'/(key+'.json.gz'));r=inp['rows'][0];tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];podium=np.asarray(inp['podium']).reshape(-1,3,3)
  assert digest(tri.tobytes())==old['sourceWorldSHA256'] and digest(podium.tobytes())==old['podiumWorldSHA256']
  lo,hi=tri.min(1),tri.max(1);targets=[]
  for witness in s['unresolved']:
   point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1));ids=[int(i)for i in broad if np.linalg.norm(np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]))>0 and np.linalg.norm(closest(point,tri[i])-point)<=.001];assert ids
   positive=[c for c in old['proof']['contacts']if c['sourceFaceA']in ids and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and c['dimension']>0];targets.append(dict(witness=witness,incidentFaces=ids,positiveContacts=positive))
  save(DOC/'original'/(key+'.json.gz'),{**old,'targets':targets,'historicalWitnessesRetained':old['targets'],'qualification':'Exact current support samples; only previously proven positive contacts reused after byte-identical source/support array checks. Absence of a nominated contact does not imply no contact exists. Remaining samples require fresh continuous paths.'})
  item=dict(uid=r['uid'],targets=len(targets),positive=sum(bool(t['positiveContacts'])for t in targets));summary.append(item);print(item,flush=True)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'pool_incident_wall_contacts_v1_20261017.py');module('sol_current_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-witness-positive-contact-binding',list(dict.fromkeys(refs)),dict(uids=['landsd/260034:0','landsd/273080:0'],rows=summary,installationApproved=False))
if __name__=='__main__':main()
