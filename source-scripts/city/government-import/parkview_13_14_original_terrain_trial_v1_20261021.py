"""Diagnostic complete foundations against original government terrain; no publication."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-13-14-original-terrain-trial-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-parkview-13-14-current-runtime-v2-20261021';REC=BASE/'government-xl-parkview-14-companion-projection-v2-20261021'
assert not DOC.exists();refs=[Path(__file__)];_,pins=authenticate(CAP);_,rpins=authenticate(REC)
def take(p,pins):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
selected=take(CAP/'selection.json.gz',pins);runtime=take(HERE/'local'/CAP.name/'runtime-geometry.json.gz',pins);recovery=take(REC/'source-recovery.json',rpins);refs.extend([CAP/'result.json',REC/'result.json'])
loader=module('parkview_original_tin_loader',HERE/'xl-second-pass.py');loader.LOCAL=LOCAL;ground=[]
for name in recovery['terrainPaths']:
 p=ROOT/name;take(p,rpins)
 for side in p.parent.iterdir():
  if side.is_file():assert digest(side.read_bytes())==rpins[str(side.relative_to(ROOT))];refs.append(side)
 ground.append(loader.terrain_triangles(p))
ground=np.concatenate(ground);geometry={r['uid']:r for r in runtime['rows']};world={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for u,g in geometry.items()};final=module('parkview_original_tin_foundation',HERE/'xl-final-script-pass.py');out=[]
for r in selected['rows']:
 uid=r['uid']
 if uid=='landsd/254491:0':continue
 tri=world[uid];lo,hi=tri.min((0,1)),tri.max((0,1));glo,ghi=ground.min(1),ground.max(1);near=ground[(ghi[:,0]>=lo[0]-2)&(glo[:,0]<=hi[0]+2)&(ghi[:,2]>=lo[2]-2)&(glo[:,2]<=hi[2]+2)];assert len(near)>0
 b=r['source']['building'];foot=Polygon(b['rings'][0],b['rings'][1:])
 for label,support in [('original-terrain',near),('original-terrain-and-podium',np.concatenate([near,world['landsd/254491:0']]))]:
  f=final.foundation_context(tri,support,foot);save(DOC/(uid.split('/')[1]+'-'+label+'.json'),dict(uid=uid,sourceSHA256=r['sourceSHA256'],foundation=f,installationApproved=False));row=dict(uid=uid,support=label,buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles'],complete=f['completeTerrainTriangles'],originalTerrainFaces=len(near));out.append(row);print(row,flush=True)
refs.extend([HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);module('parkview_original_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-terrain-complete-foundation-diagnostic',refs,dict(uids=['landsd/253980:0','landsd/255260:0'],rows=out,installationApproved=False,productionChanges=0,nextStep='Only evaluate a terrain replacement if the original surface resolves the failures; source containment and support paths remain separate.'))
