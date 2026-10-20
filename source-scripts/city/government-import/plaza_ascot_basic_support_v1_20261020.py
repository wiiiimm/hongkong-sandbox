"""Actual current BASIC tower meshes against the unchanged Fu Tor Loy podium."""
import subprocess,numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-basic-support-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020';PRIOR=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020';UIDS=['landsd/251609:0','landsd/251614:0','landsd/251615:0']
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 neighbours=BASE/'government-xl-plaza-ascot-neighbours-v1-20261020';nr=read(neighbours/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(nr['jobId'],)).fetchone()==('complete',nr)
 refs.append(neighbours/'result.json')
 for e in nr['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 report=read(neighbours/'neighbour-checks.json');uids=[r['uid'] for r in report['rows'] if 'increased-neighbour-ground-gap' in r['reasons']]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';inputs=[];hashes={}
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for building in read(p)['buildings']:
   if building['uid'] in uids:
    inputs.append(dict(building=building,tile=str(p.relative_to(ROOT))));hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 assert len(inputs)==len(uids)==31
 save(DOC/'basic-input.json',dict(manifestSHA256=digest(manifest.read_bytes()),currentInputHashes=hashes,rows=inputs))
 tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(tool),str((DOC/'basic-input.json').relative_to(ROOT)),str((DOC/'basic-geometry.json').relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(DOC/'basic-geometry.json');rows=[dict(r,building=r['currentBuilding'])for r in capture['rows']];g=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];podium=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);save(DOC/'input.json.gz',dict(rows=rows,podium=podium.tolist()))
 supporttool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(supporttool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proofs=read(DOC/'support.json.gz');final=module('times_compound_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];b=r['building'];f=final.foundation_context(t,np.concatenate([ground,podium]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);proof=next(p['proof']for p in proofs['rows']if p['uid']==r['uid']);summary.append(dict(uid=r['uid'],supportPassed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved']),foundation={k:v for k,v in f.items()if k!='components'}))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False));print(summary,flush=True)
 for p,h in {**pins,**proofs['inputHashes'],**capture['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,supporttool,HERE/'xl-final-script-pass.py']);module('times_towers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'plaza-ascot-flagged-basic-neighbour-podium-diagnostic',list(dict.fromkeys(refs)),dict(uids=uids,rows=summary,installationApproved=False))
if __name__=='__main__':main()
