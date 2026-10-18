"""Private unchanged Times Square podium and both original towers: runtime and support."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-original-assembly-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;POD=BASE/'government-xl-times-square-private-ground-v2-20261018';TOWERS=BASE/'government-xl-times-square-original-towers-v1-20261018';UID='landsd/233901:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [POD,TOWERS]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(POD/'selection.json.gz')['rows']+read(TOWERS/'selection.json.gz')['rows'];assert len(rows)==3
 identities=[]
 for r in rows:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);r['candidate']['path']=str(target.relative_to(ROOT))
  if r['uid']!=UID:
   context=read(TOWERS/(r['uid'].split('/')[1]+'-context.json'));proof=verify_files(r,context,LOCAL/'identity'/r['uid'].split('/')[1]);save(DOC/(r['uid'].split('/')[1]+'-identity.json'),proof);identities.append(dict(uid=r['uid'],passed=proof['passed'],reasons=proof['reasons']))
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(DOC/'terrain-candidates.json',read(POD/'terrain-candidates.json'))
 command=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(DOC/'worker.log').open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==3 and not any(r.get('error')for r in metrics['rows']);g={r['uid']:r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']};podium=np.asarray(g[UID]['position']).reshape(-1,3)[np.asarray(g[UID]['index']).reshape(-1,3)];supportrows=[dict(uid=r['uid'],position=g[r['uid']]['position'],index=g[r['uid']]['index'],building=r['source']['building'])for r in rows if r['uid']!=UID];save(DOC/'input.json.gz',dict(rows=supportrows,podium=podium.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proofs=read(DOC/'support.json.gz');final=module('times_original_assembly_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  uid=r['uid'];rt=g[uid];tri=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];ground=np.asarray(rt['drawnGroundGeometry']).reshape(-1,3,3);surface=ground if uid==UID else np.concatenate([ground,podium]);b=r['source']['building'];f=final.foundation_context(tri,surface,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.split('/')[1]+'-foundation.json'),f);proof=next((p['proof']for p in proofs['rows']if p['uid']==uid),None);item=dict(uid=uid,foundation={k:v for k,v in f.items()if k!='components'},support=None if proof is None else dict(passed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],wallIntersections=proof['wallIntersections'],unresolved=len(proof['unresolved'])));summary.append(item);print(item,flush=True)
 save(DOC/'summary.json',dict(rows=summary,towerIdentity=identities,installationApproved=False));print('towerIdentity',identities,flush=True)
 for p,h in {**pins,**metrics['inputHashes'],**proofs['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([tool,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'acceptance-metrics-multi-retained.mjs'])
 module('times_original_assembly_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-three-original-runtime-support-foundation',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=summary,towerIdentity=identities,installationApproved=False))
if __name__=='__main__':main()
