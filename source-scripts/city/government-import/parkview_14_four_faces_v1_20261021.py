"""Locate all four podium-covered source facets; diagnostic, no acceptance."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-14-four-faces-v1-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-parkview-13-14-current-runtime-v2-20261021'
assert not DOC.exists();_,pins=authenticate(CAP);p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rt={r['uid']:r for r in read(p)['rows']}
def world(r):return np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
tri=world(rt['landsd/253980:0']);pod=world(rt['landsd/254491:0']);polys=shapely.polygons(pod[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;surface=pod[valid];polys=polys[valid];index=shapely.STRtree(polys);final=module('parkview4faces',HERE/'xl-final-script-pass.py');points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),surface,index).reshape(-1,4);gap=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gap<-.5).all(1));assert len(ids)==4
rows=[]
for fid in ids:
 face=tri[fid];lo,hi=face.min(0),face.max(0);near=np.flatnonzero((pod[:,:,0].max(1)>=lo[0]-2)&(pod[:,:,0].min(1)<=hi[0]+2)&(pod[:,:,2].max(1)>=lo[2]-2)&(pod[:,:,2].min(1)<=hi[2]+2)&(pod[:,:,1].max(1)>=lo[1]-2)&(pod[:,:,1].min(1)<=hi[1]+5))
 rows.append(dict(faceId=int(fid),vertices=face.tolist(),sampleGaps=gap[fid].tolist(),nearbyPodiumFaceIds=near.tolist(),normal=np.cross(face[1]-face[0],face[2]-face[0]).tolist()))
save(DOC/'faces.json',dict(uid='landsd/253980:0',sourceSHA256=rt['landsd/253980:0']['sourceSHA256'],podiumSHA256=rt['landsd/254491:0']['sourceSHA256'],rows=rows,installationApproved=False));module('parkview4facesfreeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-podium-covered-face-locations',[Path(__file__),CAP/'result.json',p,HERE/'xl-final-script-pass.py'],dict(uids=['landsd/253980:0'],faceIds=ids.tolist(),installationApproved=False));print(rows,flush=True)
