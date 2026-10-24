"""Exact finite clearance of four original wall facets above original TIN."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_original_projection_coverage_20261009 import exact_coverage
from exact_original_triangle_pair_column_gap_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-14-exact-wall-ground-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();refs=[Path(__file__)];data={};pins={}
def take(batch,name):
 folder=BASE/batch;_,ps=authenticate(folder);p=folder/name;assert digest(p.read_bytes())==ps[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);pins.update(ps);return read(p)
inputs=take('government-xl-parkview-13-14-four-world-contacts-v1-20261021','input.json.gz')['rows'];recovery=take('government-xl-parkview-14-companion-projection-v2-20261021','source-recovery.json');faces=take('government-xl-parkview-14-four-faces-v1-20261021','faces.json');loader=module('parkview_exact_ground_loader',HERE/'xl-second-pass.py');loader.LOCAL=LOCAL;ground=[]
for path in recovery['terrainPaths']:
 p=ROOT/path
 for q in p.parent.iterdir():
  if q.is_file():assert digest(q.read_bytes())==pins[str(q.relative_to(ROOT))];refs.append(q)
 ground.append(loader.terrain_triangles(p))
ground=np.concatenate(ground);worlds={}
for r in inputs:
 if r['uid']!='landsd/253980:0':continue
 g=r['source'];t=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert digest(t.tobytes())==r['sourceWorldSHA256'];worlds[r['mode']]=t
assert set(worlds)=={'original','literal','explicitLeftF32','explicitBalancedF32'}
original=worlds['original'];assert all(np.array_equal(t,original)for t in worlds.values());rows=[];gxz=ground[:,:,[0,2]]
for row in faces['rows']:
 fid=row['faceId'];face=original[fid];assert np.array_equal(face,np.asarray(row['vertices']));xz=face[:,[0,2]];ids=np.flatnonzero(np.all(gxz.max(1)>=xz.min(0),axis=1)&np.all(gxz.min(1)<=xz.max(0),axis=1));near=ground[ids];coverage=exact_coverage(face,near);assert coverage['exactProjectionCovered'];pairs=[dict(groundFaceId=int(i),proof=verify(face,ground[i]))for i in ids];gaps=[Fraction(p['proof']['exactMinimumFiniteColumnGapM'])for p in pairs if p['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps and min(gaps)>0
 rows.append(dict(faceId=fid,sourceFaceSHA256=digest(face.tobytes()),coverage=coverage,allFiniteColumnPairs=pairs,minimumWholeFaceGroundClearanceM=float(min(gaps))));print(dict(faceId=fid,finitePairs=len(ids),minimumClearance=float(min(gaps))),flush=True)
save(DOC/'proof.json.gz',dict(uid='landsd/253980:0',sourceSHA256=faces['sourceSHA256'],rows=rows,worldRepresentationsIdentical=True,modeWorldSHA256={m:digest(t.tobytes())for m,t in worlds.items()},installationApproved=False,qualification='Exact clearance above unchanged original provider terrain only. A proposed packed replacement must be verified separately; not current terrain acceptance.'))
refs.extend(HERE/n for n in ['xl-second-pass.py','exact_original_projection_coverage_20261009.py','exact_original_triangle_pair_column_gap_20261010.py']);module('parkview_exact_wall_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-wall-original-ground-clearance',refs,dict(uids=['landsd/253980:0'],faces=len(rows),allFourModesIdentical=True,minimumClearanceM=min(r['minimumWholeFaceGroundClearanceM']for r in rows),installationApproved=False))
