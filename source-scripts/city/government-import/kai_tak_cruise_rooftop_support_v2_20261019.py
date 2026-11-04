"""Actual current BASIC tower meshes against the unchanged Kai Tak Cruise Terminal."""
import subprocess,numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-kai-tak-cruise-rooftop-support-v2-20261019';DOC=BASE/BATCH;CAP=BASE/'government-xl-kai-tak-cruise-expanded-parent-v3-20261019';PRIOR=BASE/'government-xl-kai-tak-cruise-current-neighbours-v1-20261019';UIDS=['landsd/'+str(n)+':0'for n in [92857,92858,92859,92802,92803,92804,92915,92919,92920,92921]]
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';source=read(PRIOR/'neighbour-inputs.json.gz');found={}
 for path,h in source['inputHashes'].items():
  tile=ROOT/path;assert digest(tile.read_bytes())==h
  for form in read(tile)['buildings']:
   if form['uid']in UIDS:
    assert form['uid']not in found;found[form['uid']]=dict(building=form,tile=path)
 assert set(found)==set(UIDS)
 save(DOC/'basic-input.json',dict(manifestSHA256=digest(manifest.read_bytes()),currentInputHashes=source['inputHashes'],rows=[found[u]for u in UIDS]))

 tool=HERE/'xl-one-peking-current-foreign-basic-tower-geometry-v1-20261010.mjs';subprocess.run(['node',str(tool),str((DOC/'basic-input.json').relative_to(ROOT)),str((DOC/'basic-geometry.json').relative_to(ROOT))],cwd=ROOT,check=True)
 capture=read(DOC/'basic-geometry.json');rows=[dict(r,building=r['currentBuilding'])for r in capture['rows']];g=read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];podium=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);save(DOC/'input.json.gz',dict(rows=rows,podium=podium.tolist()))
 supporttool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(supporttool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);proofs=read(DOC/'support.json.gz');final=module('times_compound_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  t=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];b=r['building'];f=final.foundation_context(t,np.concatenate([ground,podium]),Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(r['uid'].split('/')[1]+'-foundation.json'),f);proof=next(p['proof']for p in proofs['rows']if p['uid']==r['uid']);summary.append(dict(uid=r['uid'],supportPassed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved']),foundation={k:v for k,v in f.items()if k!='components'}))
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False));print(summary,flush=True)
 for p,h in {**pins,**proofs['inputHashes'],**capture['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,supporttool,HERE/'xl-final-script-pass.py']);module('times_towers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kai-tak-cruise-retained-rooftop-support',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False))
if __name__=='__main__':main()
