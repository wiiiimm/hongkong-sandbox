"""Separate terrain and podium burial in unchanged complete runtime towers."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-13-14-burial-attribution-v1-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-parkview-13-14-current-runtime-v2-20261021'
assert not DOC.exists();_,pins=authenticate(CAP);refs=[Path(__file__),CAP/'result.json']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
selected=take(CAP/'selection.json.gz');runtime=take(HERE/'local'/CAP.name/'runtime-geometry.json.gz');geometry={r['uid']:r for r in runtime['rows']};world={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for u,g in geometry.items()};final=module('parkview_burial_attribution',HERE/'xl-final-script-pass.py');rows=[]
for r in selected['rows']:
 u=r['uid']
 if u=='landsd/254491:0':continue
 b=r['source']['building'];foot=Polygon(b['rings'][0],b['rings'][1:]);ground=np.asarray(geometry[u]['drawnGroundGeometry']).reshape(-1,3,3)
 for label,support in [('terrain-only',ground),('podium-only',world['landsd/254491:0'])]:
  f=final.foundation_context(world[u],support,foot);save(DOC/(u.split('/')[1]+'-'+label+'.json'),dict(uid=u,sourceSHA256=r['sourceSHA256'],support=label,foundation=f,installationApproved=False));row=dict(uid=u,support=label,buried=f['fullyBuriedTriangles'],upwardBuried=f['fullyBuriedUpwardTriangles'],buriedAreaM2=f['fullyBuriedAreaM2'],complete=f['completeTerrainTriangles']);rows.append(row);print(row,flush=True)
refs.append(HERE/'xl-final-script-pass.py');module('parkview_burial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-runtime-burial-attribution',refs,dict(uids=['landsd/253980:0','landsd/255260:0'],rows=rows,installationApproved=False,nextStep='Use exact face-role and local terrain evidence to resolve failures; neither support-only nor terrain-only result is full acceptance.'))
