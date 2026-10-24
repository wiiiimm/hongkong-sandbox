"""Capture actual rendered private terrain and untouched original model."""
from pathlib import Path
import subprocess,json,sys,uuid
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-pier8-current-runtime-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];pins={}
 def take(name,p):
  r,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
 sn='government-xl-next-twenty-current-terrain-v6-20261021';selection=take(sn,BASE/sn/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']=='landsd/213352:0');selection['rows']=[row];manifestp=ROOT/'3d-viewer/city/data/manifest.json';selection['manifestSHA256']=digest(manifestp.read_bytes());refs.append(manifestp)
 form=row['source'];tp=ROOT/'3d-viewer'/form['tile'];assert digest(tp.read_bytes())==form['tileSHA256'];assert next(b for b in read(tp)['buildings']if b['uid']==row['uid'])==form['building'];refs.append(tp);ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap)
 cn='government-xl-central-piers-private-wrapper-v2-20261021';summary=take(cn,BASE/cn/'summary.json');assert summary['terrainValidationPassed'];candidates=take(cn,BASE/cn/'terrain-candidates.json')
 for c in candidates:assert digest((ROOT/c['path']).read_bytes())==c['sha256']
 assetcopy=LOCAL/row['candidate']['entry']['asset'];assetcopy.parent.mkdir(parents=True,exist_ok=True);assetcopy.write_bytes(ap.read_bytes());assert digest(assetcopy.read_bytes())==row['sourceSHA256'];refs.append(assetcopy)
 save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',candidates);save(LOCAL/'source-forms.json',{row['uid']:form})
 tool=HERE/'acceptance-metrics-retained-group-parent.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(DOC/'worker.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 assert p.returncode==0;rt=read(LOCAL/'runtime-geometry.json.gz');metrics=read(DOC/'metrics.json');assert len(rt['rows'])==1 and not metrics['rows'][0].get('error');g=rt['rows'][0];assert g['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
 helper=module('china_actual_foundation',HERE/'xl-final-script-pass.py');b=form['building'];foundation=helper.foundation_context(tri,ground,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 assert digest(manifestp.read_bytes())==selection['manifestSHA256'] and reservations.owns(lease)
 refs.extend([LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py']);result=dict(uids=[row['uid']],metrics=metrics['rows'],foundation={k:v for k,v in foundation.items()if k!='components'},sourceGeometryChanges=0,installationApproved=False)
 r=module('china_actual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-private-wrapper-rendered-original-foundation',list(dict.fromkeys(refs)),result);print(dict(jobId=r['jobId'],**result),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/213352:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
