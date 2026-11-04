"""Compare the current exact tower with already acquired complete official terrain."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-saved-ground-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(folder,path):
 _,ps=authenticate(BASE/folder);key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==ps[key];pins[key]=ps[key];refs.extend([BASE/folder/'result.json',path]);return read(path)
cn='government-xl-next-twenty-current-terrain-v6-20261021';row=next(r for r in take(cn,BASE/cn/'selection.json.gz')['rows']if r['uid']=='landsd/118230:0')
p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes())
gn='government-xl-next-three-adjoining-ground-v1-20261019';data=take(gn,HERE/'local'/gn/'233227:0-ground.json.gz');ground=np.asarray(data['completeAdjoiningTerrain'],dtype='<f8')
# Closed full-source bounds preserve every intersecting facet; never centroid-crop.
lo=tri.min((0,1));hi=tri.max((0,1));mask=(ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]);local=ground[mask];assert len(local)
b=row['source']['building'];helper=module('harbourfront_saved_ground_foundation',HERE/'xl-final-script-pass.py');f=helper.foundation_context(tri,local,shapely.Polygon(b['rings'][0],b['rings'][1:]))
save(DOC/'foundation.json',f);save(DOC/'selected-ground.json.gz',dict(triangles=local.tolist(),sourceTerrainSHA256=digest(ground.tobytes()),sourceFaceIds=np.flatnonzero(mask).tolist(),sourceSheets=data['sheets']))
result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],sourceGeometryChanges=0,sourceTerrainFaces=len(ground),selectedTerrainFaces=len(local),foundation={k:v for k,v in f.items()if k!='components'},installationApproved=False,qualification='Reuses exact authenticated official terrain bytes; this is a source comparison, not current runtime or publication approval.')
save(DOC/'summary.json',result)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
r=module('harbourfront_saved_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-tower-versus-saved-official-terrain',refs,result);print(dict(jobId=r['jobId'],**result),flush=True)
