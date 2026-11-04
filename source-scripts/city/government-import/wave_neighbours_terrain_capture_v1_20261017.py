"""Measure six unchanged companions against the private Wave terrain candidate."""
import json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-neighbours-terrain-capture-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
REC=BASE/'government-xl-wave-neighbours-original-recovery-v1-20261017';TERR=BASE/'government-xl-wave275510-assembly-terrain-candidate-v1-20261017'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);refs=[Path(__file__)];pins={}
 for d in [REC,TERR]:
  r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 selection=read(REC/'selection.json.gz');rows=selection['rows'];assert len(rows)==6
 for r in rows:
  src=ROOT/r['candidate']['path'];raw=src.read_bytes();assert digest(raw)==r['sourceSHA256'];dest=LOCAL/'assets'/src.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);r['candidate']['path']=str(dest.relative_to(ROOT));r['candidate']['entry']['asset']='assets/'+dest.name;refs.append(dest)
 save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',read(TERR/'terrain-candidates.json'))
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 rt=read(LOCAL/'runtime-geometry.json.gz');final=module('wave_companion_foundations',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  g=next(g for g in rt['rows']if g['uid']==r['uid']);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);summary.append(dict(uid=r['uid'],complete=f['completeTerrainTriangles']==f['triangles'],buried=f['fullyBuriedTriangles']));print(summary[-1],flush=True);assert reservations.owns(lease)
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 refs.extend([LOCAL/'runtime-geometry.json.gz',HERE/'acceptance-metrics-multi-retained.mjs',HERE/'xl-final-script-pass.py']);save(DOC/'summary.json',dict(foundations=summary,installationApproved=False))
 out=module('wave_companion_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-companion-runtime-terrain-foundations-v1',list(set(refs)),dict(uids=[r['uid']for r in rows],summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();uids=[r['uid']for r in read(REC/'selection.json.gz')['rows']];claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
