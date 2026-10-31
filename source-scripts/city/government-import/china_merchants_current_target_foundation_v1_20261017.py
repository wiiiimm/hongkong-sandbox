"""Fresh production target capture and complete original foundation; no publication."""
from pathlib import Path
import subprocess,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-current-target-foundation-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=BASE/'government-xl-retained-group-central-wrapper-20261009-264206-0';SOURCE=HERE/'local'/OLD.name;WRAP=BASE/'government-xl-china-merchants-current-wrapper-v1-20261015'
def main():
 assert not DOC.exists()and not LOCAL.exists();manifestp=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifestp.read_bytes());selection=read(OLD/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']=='landsd/264206:0';selection['manifestSHA256']=manifestsha
 require_remaining(BASE/'government-xl-citic-original-installed-v1-20261017/full-xl-current-count.json',row['uid'],row['sourceSHA256'])
 forms=read(SOURCE/'source-forms.json')
 for uid,r in forms.items():
  p=ROOT/'3d-viewer'/r['tile'];assert digest(p.read_bytes())==r['tileSHA256'];assert next(b for b in read(p)['buildings']if b['uid']==uid)==r['building']
 claim=reservations.claim('china-current-target-'+str(uuid.uuid4()),['building:landsd/264206:0'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir();save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',read(WRAP/'terrain-candidates.json'))
  tool=HERE/'acceptance-metrics-retained-group-parent.mjs';cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(SOURCE.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
  with(DOC/'worker.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=600)
  assert p.returncode==0
  rt=read(LOCAL/'runtime-geometry.json.gz');geo=rt['rows'][0];assert geo['sourceSHA256']==row['sourceSHA256'];tri=np.asarray(geo['position']).reshape(-1,3)[np.asarray(geo['index']).reshape(-1,3)];ground=np.asarray(geo['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];f=module('china_current_target_foundation',HERE/'xl-final-script-pass.py');foundation=f.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',dict(uid=row['uid'],sourceSHA256=geo['sourceSHA256'],foundation=foundation,fullAcceptance=False))
  paths=[Path(__file__),OLD/'selection.json.gz',WRAP/'result.json',LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py']
  for path,h in rt['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;paths.append(ROOT/path)
  assert digest(manifestp.read_bytes())==manifestsha
  module('china_current_target_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-original-production-foundation-v1',paths,dict(uids=[row['uid']],foundation=foundation,fullAcceptance=False))
  print({k:foundation[k]for k in ['triangles','fullyBuriedTriangles','fullyBuriedUpwardTriangles','fullyBuriedAreaFraction']},flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
