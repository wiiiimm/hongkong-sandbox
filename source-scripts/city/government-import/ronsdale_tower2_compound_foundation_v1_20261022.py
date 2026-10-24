"""Check the complete unchanged tower against the repaired terrain and original podium."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-tower2-compound-foundation-v1-20261022';DOC=BASE/BATCH
UID='landsd/256702:0';POD='landsd/233771:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap='government-xl-remaining-forty-assembly-runtime-v1-20261021';runtime=take(cap,HERE/'local'/cap/'runtime-geometry.json.gz');selection=take(cap,BASE/cap/'selection.json.gz');geometries={r['uid']:r for r in runtime['rows']if r['uid']in [UID,POD]};assert len(geometries)==2
 current='government-xl-ronsdale-inset-runtime-v2-20261022';new=take(current,HERE/'local'/current/'runtime-geometry.json.gz')['rows'][0];assert new['uid']==POD
 def tri(g):return np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert np.array_equal(tri(new),tri(geometries[POD]))
 for uid in [UID,POD]:
  row=next(r for r in selection['rows']if r['uid']==uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==geometries[uid]['sourceSHA256'];refs.append(asset)
 ground=np.asarray(new['drawnGroundGeometry']).reshape(-1,3,3);building=next(r for r in selection['rows']if r['uid']==UID)['source']['building'];f=module('ronsdale_compound_foundation',HERE/'xl-final-script-pass.py').foundation_context(tri(geometries[UID]),np.concatenate([ground,tri(new)]),Polygon(building['rings'][0],building['rings'][1:]))
 result=dict(uids=[UID,POD],uid=UID,supportUid=POD,sourceWorldSHA256=digest(tri(geometries[UID]).tobytes()),supportWorldSHA256=digest(tri(new).tobytes()),foundation=f,sourceGeometryChanges=0,installationApproved=False);save(DOC/'foundation.json',result);refs.append(HERE/'xl-final-script-pass.py');module('ronsdale_compound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-repaired-ground-and-original-podium-foundation',refs,result);print({k:v for k,v in f.items()if k!='components'},flush=True)
if __name__=='__main__':main()
