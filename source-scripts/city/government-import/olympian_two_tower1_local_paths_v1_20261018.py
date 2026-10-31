"""Test exact finite original surface connections for Tower 1; no acceptance waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from wave_local_coplanar_paths_v3_20261017 import witness
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-nearest-interfaces-v1-20261018';INPUT=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';BATCH='government-xl-olympian-two-tower1-local-paths-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 d=read(INPUT/'geometry-inputs.json.gz');meshes={s['uid']:np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)]for s in d['rows']};support=np.concatenate([meshes[s['uid']]for s in d['rows']if s['uid']not in d['towerUIDs']]);row=next(x for x in read(INPUT/'support-checks.json.gz')['rows']if x['uid']=='landsd/270317:0');details=[dict(wall=witness(meshes[row['uid']],support,f,True),surface=witness(meshes[row['uid']],support,f,False))for f in row['unresolved']]
 summary=dict(uid=row['uid'],failedSamples=len(details),wallConnections=sum(x['wall']['witness']is not None for x in details),surfaceConnections=sum(x['surface']['witness']is not None for x in details),fullAcceptance=False)
 save(DOC/'paths.json.gz',dict(summary=summary,rows=details,qualification='Existing half-metre local finite original intersection diagnostic only. Proximity alone grants no acceptance. Raw strict failures retained.'));print(summary,flush=True)
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]]+[HERE/n for n in ['wave_local_coplanar_paths_v3_20261017.py','wave_incident_side_intersections_v1_20261017.py','pool_local_wall_paths_v1_20261017.py','pool_incident_wall_contacts_v1_20261017.py']]
 out=module('olympian_local_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-tower1-finite-local-original-connections-v1',refs,dict(uids=[row['uid'],'landsd/265851:0','landsd/239351:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
