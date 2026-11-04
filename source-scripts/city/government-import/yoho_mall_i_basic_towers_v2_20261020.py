"""Complete current BASIC towers against actual mall podium and proposed terrain."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-basic-towers-v2-20261020';DOC=BASE/BATCH
CAP=BASE/'government-xl-yoho-mall-i-private-runtime-v3-20261020';NEIGH=BASE/'government-xl-yoho-mall-i-neighbours-v2-20261020';PATCH=BASE/'government-xl-yoho-mall-i-private-terrain-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};consumed={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,NEIGH,PATCH]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(d,p):
  k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[d][k];consumed[k]=pins[d][k];refs.append(p);return read(p)
 checks=take(NEIGH,NEIGH/'neighbour-checks.json');uids=[r['uid']for r in checks['rows']if 'increased-neighbour-ground-gap'in r['reasons']];assert len(uids)==7
 mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(NEIGH,mp);inputs=[];hashes={};native={e['uid']for u in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/u)['models']};assert not native.intersection(uids)
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in uids:inputs.append(dict(building=b,tile=str(p.relative_to(ROOT))));hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 assert len(inputs)==7
 save(DOC/'basic-input.json',dict(manifestSHA256=digest(mp.read_bytes()),currentInputHashes=hashes,rows=inputs))
 tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(tool),str((DOC/'basic-input.json').relative_to(ROOT)),str((DOC/'basic-geometry.json').relative_to(ROOT))],cwd=ROOT,check=True);refs.append(tool)
 take(PATCH,PATCH/'terrain-candidates.json');save(DOC/'input.json',dict(basicGeometry=str((DOC/'basic-geometry.json').relative_to(ROOT)),patches=str((PATCH/'terrain-candidates.json').relative_to(ROOT))))
 groundtool=HERE/'yoho_mall_i_basic_ground_v1_20261020.mjs';subprocess.run(['node',str(groundtool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);refs.append(groundtool)
 runtime=take(CAP,HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];podium=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];capture=read(DOC/'ground.json.gz')
 save(DOC/'input.json.gz',dict(rows=capture['rows'],podium=podium.tolist()));supporttool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(supporttool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);support=read(DOC/'support.json.gz');refs.append(supporttool)
 final=module('yoho_basic_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in capture['rows']:
  tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);b=r['currentBuilding'];f=final.foundation_context(tri,np.concatenate([ground,podium]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);proof=next(x['proof']for x in support['rows']if x['uid']==r['uid']);summary.append(dict(uid=r['uid'],supportPassed=proof['passed'],samples=proof['samples'],unresolved=len(proof['unresolved']),foundation={k:v for k,v in f.items()if k!='components'}))
 for report in [capture,support]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in consumed.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'xl-final-script-pass.py');result=dict(uids=uids,rows=summary,installationApproved=False,productionChanges=0);save(DOC/'summary.json',result)
 module('yoho_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-basic-tower-original-podium-and-terrain-checks',list(dict.fromkeys(refs)),result);print(summary,flush=True)
if __name__=='__main__':main()
