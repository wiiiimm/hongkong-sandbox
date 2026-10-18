"""Exact distance to original faces with verified lower contact paths; no seam edits."""
from pathlib import Path
import math,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-residual-all-source-layers-v1-20261018';BATCH='government-xl-olympian-two-residual-verified-face-distance-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 meshes={s['uid']:np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)]for s in read(PRIOR/'inputs.json.gz')['sources']}
 known={}
 for name in ['government-xl-olympian-two-source-face-paths-v4-20261018','government-xl-olympian-two-residual-surface-paths-v1-20261018']:
  for row in read(BASE/name/'paths.json.gz')['rows']:
   for d in row['details']:
    w=d['witness']
    if w:
     for face in w['faces']:known.setdefault(row['uid'],set()).add(face)
 exact={r['uid']:{tuple(x['position']):x['exactStartFaces']for x in r['details']}for r in read(BASE/'government-xl-olympian-two-exact-start-faces-v1-20261018/exact-start-faces.json.gz')['rows']};results=[]
 for row in read(PRIOR/'layers.json.gz')['rows']:
  uid=row['uid'];p=np.asarray(row['position']);tri=meshes[uid];ids=np.asarray(sorted(known[uid]));candidates=tri[ids];lo=candidates.min(1);hi=candidates.max(1);delta=np.maximum(np.maximum(lo-p,p-hi),0);bounds=np.linalg.norm(delta,axis=1);best=math.inf;winner=None;tested=0
  for j in np.argsort(bounds):
   # Float bounding boxes only prune well-separated faces; final distance uses exact input rationals.
   if bounds[j]>best+1e-8:break
   d=math.sqrt(float(squared_distance(p,candidates[j])));tested+=1
   if d<best:best=d;winner=int(ids[j])
  starts=exact[uid][tuple(row['position'])];entry=dict(uid=uid,position=row['position'],exactStartFaces=starts,startFaceVertices={str(f):tri[f].tolist()for f in starts},nearestVerifiedPathFace=winner,nearestVerifiedPathFaceVertices=tri[winner].tolist(),distanceToVerifiedPathFaceM=best,candidateFaces=len(ids),exactFaceTests=tested,contactLayerFound=row['hasContactLayer'],supportApproved=False)
  results.append(entry);print(dict(uid=uid,distanceM=best,face=winner,tests=tested),flush=True)
 save(DOC/'distances.json',dict(rows=results,fullAcceptance=False,qualification='Distance to complete original faces occurring on previously verified paths, not to the height-clipped path itself. Nearness does not prove a continuous path or support. No welding, snapping, edits or acceptance changes.'))
 refs.extend(ROOT/p for p in pins);refs.append(HERE/'exact_point_triangle_distance_20261018.py')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('olympian_residual_distance_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-residual-original-verified-face-distance-v1',list(set(refs)),dict(uids=sorted({x['uid']for x in results}),points=len(results),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
