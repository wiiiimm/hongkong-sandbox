"""Capture actual rendered private terrain and untouched original model."""
from pathlib import Path
import subprocess,json,sys,uuid
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-12-15-shared-runtime-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 def take(name,p):
  r,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
 sn='government-xl-parkview-13-14-current-runtime-v2-20261021';selection=take(sn,BASE/sn/'selection.json.gz');selection['rows'].extend(take('government-xl-parkview-12-15-candidate-runtime-v2-20261021',BASE/'government-xl-parkview-12-15-candidate-runtime-v2-20261021/selection.json.gz')['rows']);rows=selection['rows'];assert {r['uid']for r in rows}=={'landsd/253980:0','landsd/255260:0','landsd/254491:0','landsd/255648:0','landsd/255440:0'};manifestp=ROOT/'3d-viewer/city/data/manifest.json';assert selection['manifestSHA256']==digest(manifestp.read_bytes());refs.append(manifestp)
 for row in rows:
  form=row['source'];tp=ROOT/'3d-viewer'/form['tile'];assert digest(tp.read_bytes())==form['tileSHA256'];assert next(b for b in read(tp)['buildings']if b['uid']==row['uid'])==form['building'];refs.append(tp);ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap)
  assetcopy=LOCAL/row['candidate']['entry']['asset'];assetcopy.parent.mkdir(parents=True,exist_ok=True);assetcopy.write_bytes(ap.read_bytes());assert digest(assetcopy.read_bytes())==row['sourceSHA256'];refs.append(assetcopy)
 cn='government-xl-parkview-12-15-private-terrain-v1-20261021';summary=take(cn,BASE/cn/'summary.json');assert summary['terrainValidationPassed'];candidates=take(cn,BASE/cn/'terrain-candidates.json')
 for c in candidates:assert digest((ROOT/c['path']).read_bytes())==c['sha256']
 save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',candidates);save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows})
 tool=HERE/'acceptance-metrics-retained-group-parent.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(DOC/'worker.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 assert p.returncode==0;rt=read(LOCAL/'runtime-geometry.json.gz');metrics=read(DOC/'metrics.json');assert len(rt['rows'])==5 and all(not r.get('error')for r in metrics['rows']);foundations=[]
 helper=module('thei_actual_foundation',HERE/'xl-final-script-pass.py')
 for row in rows:
  g=next(r for r in rt['rows']if r['uid']==row['uid']);assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
  b=row['source']['building'];foundation=helper.foundation_context(tri,ground,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(row['uid'].split('/')[1]+'-foundation.json'),foundation);foundations.append(dict(uid=row['uid'],foundation={k:v for k,v in foundation.items()if k!='components'}))
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 assert digest(manifestp.read_bytes())==selection['manifestSHA256'] and reservations.owns(lease)
 refs.extend([LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py']);result=dict(uids=[r['uid']for r in rows],metrics=metrics['rows'],foundations=foundations,sourceGeometryChanges=0,installationApproved=False)
 r=module('china_actual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-private-wrapper-rendered-original-foundation',list(dict.fromkeys(refs)),result);print(dict(jobId=r['jobId'],**result),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/253980:0','building:landsd/255260:0','building:landsd/254491:0','building:landsd/255648:0','building:landsd/255440:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(p),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
