"""Bounded exact source-face witnesses for the eleven residual compound contacts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from wave_local_coplanar_paths_v3_20261017 import witness
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-full-compound-support-v1-20261017';BATCH='government-xl-wave-verdant-local-contacts-v1-20261017';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(PRIOR/'input.json.gz')['rows'][0];tri=np.array(row['position']).reshape(-1,3)[np.array(row['index']).reshape(-1,3)];source=read(BASE/'government-xl-wave-verdant-podium-original-recovery-v1-20261017/selection.json.gz')['rows'][0];path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256'];support=decode_original_world_triangles(path.read_bytes());norm=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1);snorm=np.linalg.norm(np.cross(support[:,1]-support[:,0],support[:,2]-support[:,0]),axis=1);rows=[]
 for f in read(PRIOR/'support.json.gz')['rows'][0]['proof']['unresolved']:
  p=np.array(f['position']);incident=[dict(faceIndex=int(i))for i in np.flatnonzero(norm>0)if np.linalg.norm(closest(p,tri[i])-p)<=.001];assert incident;f=dict(f,originalSourceFaces=incident);distance,face=min((float(np.linalg.norm(closest(p,support[j])-p)),int(j))for j in np.flatnonzero(snorm>0));rows.append(dict(failure=f,nearestPodiumDistanceM=distance,nearestPodiumFace=face,wall=witness(tri,support,f,True),surface=witness(tri,support,f,False)))
 summary=dict(uid=row['uid'],samples=len(rows),localWallWitnesses=sum(x['wall']['witness']is not None for x in rows),localSurfaceWitnesses=sum(x['surface']['witness']is not None for x in rows),minimumNearestDistanceM=min(x['nearestPodiumDistanceM']for x in rows),maximumNearestDistanceM=max(x['nearestPodiumDistanceM']for x in rows),fullAcceptance=False)
 save(DOC/'paths.json.gz',dict(rows=rows,qualification='Existing half-metre local-ball proof, exact shared edges and finite original contacts. All-surface includes floors and is not wall-only acceptance; raw canonical failures remain.'));save(DOC/'summary.json',summary)
 refs.extend([path]+[HERE/n for n in ['exact_packed_world_geometry_20261009.py','wave_local_coplanar_paths_v3_20261017.py','wave_incident_side_intersections_v1_20261017.py','pool_local_wall_paths_v1_20261017.py','pool_incident_wall_contacts_v1_20261017.py']]);out=module('verdant_local_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verdant-original-local-contact-witnesses-v1',list(set(refs)),dict(uids=[row['uid'],source['uid']],summary=summary,fullAcceptance=False,newlyInstalled=0));print(summary,flush=True);print(out['jobId'],flush=True)
if __name__=='__main__':main()
