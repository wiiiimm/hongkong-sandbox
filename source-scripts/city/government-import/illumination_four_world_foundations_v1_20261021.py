"""Check all complete original coordinate representations on the corrected terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-four-world-foundations-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)]
def take(n,p):
 _,pins=authenticate(BASE/n);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
n='government-xl-illumination-four-world-contacts-v1-20261021';worlds=take(n,BASE/n/'input.json.gz')['rows'];contacts=take(n,BASE/n/'contacts.json.gz')['rows'];assert len(worlds)==len(contacts)==4
n='government-xl-illumination-inset-runtime-v2-20261021';runtime=take(n,HERE/'local'/n/'runtime-geometry.json.gz');selection=take(n,BASE/n/'selection.json.gz');geometry={r['uid']:r for r in runtime['rows']};forms={r['uid']:r['source']['building']for r in selection['rows']}
# Bind source arrays to the current loader capture, rather than assuming source
# hashes alone establish an unchanged world transform.
literal=next(r for r in worlds if r['mode']=='literal')
def tri(g):return np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
assert np.array_equal(tri(literal['source']),tri(geometry['landsd/255531:0']))
assert np.array_equal(tri(literal['support']),tri(geometry['landsd/258737:0']))
final=module('illumination_current_four_world_foundation',HERE/'xl-final-script-pass.py');rows=[]
for world,contact in zip(worlds,contacts):
 assert world['mode']==contact['mode'] and contact['sourceWorldSHA256']==world['sourceWorldSHA256'] and contact['supportWorldSHA256']==world['supportWorldSHA256']
 assert contact['rawInterface']['passed'] and contact['canonicalContacts']==contact['samples']==10
 for uid,field in [('landsd/255531:0','source'),('landsd/258737:0','support')]:
  t=tri(world[field]);ground=np.asarray(geometry[uid]['drawnGroundGeometry']).reshape(-1,3,3)
  b=forms[uid];f=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]))
  row=dict(uid=uid,mode=world['mode'],sourceWorldSHA256=digest(t.astype('<f8').tobytes()),foundation=f)
  save(DOC/(uid.split('/')[1]+'-'+world['mode']+'.json'),row)
  summary=dict(uid=uid,mode=world['mode'],**{k:v for k,v in f.items()if k!='components'});rows.append(summary);print(summary,flush=True)
  assert f['completeTerrainTriangles']==f['triangles'] and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0
save(DOC/'summary.json',dict(rows=rows,installationApproved=False))
refs.append(HERE/'xl-final-script-pass.py');module('illumination_four_foundations_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-world-original-foundations',refs,dict(uids=list(forms),rows=rows,installationApproved=False))
