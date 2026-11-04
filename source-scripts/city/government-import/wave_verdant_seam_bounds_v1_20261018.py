"""Certify complete flagged low-rim edges against unchanged compound surfaces; diagnostic only."""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-remaining-interfaces-v1-20261018';ASSEMBLY=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';BATCH='government-xl-wave-verdant-seam-bounds-v1-20261018';DOC=BASE/BATCH;UIDS=['landsd/301562:0','landsd/195000:0']
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 summary=[];cache={}
 for mode in ['original','literal','left','balanced']:
  data=read(ASSEMBLY/mode/'input.json.gz');surface=np.asarray(data['podium']);lo=surface.min(1);hi=surface.max(1);tree=cKDTree(surface.mean(1));nearest_cache={}
  def nearest(p):
   key=tuple(p)
   if key in nearest_cache:return nearest_cache[key]
   ids=np.atleast_1d(tree.query(p,k=min(8,len(surface)))[1]);best=min((float(np.linalg.norm(closest(p,surface[i])-p)),int(i))for i in ids)
   lower=np.linalg.norm(np.maximum(np.maximum(lo-p,p-hi),0),axis=1)
   for i in np.flatnonzero(lower<=best[0]+1e-12):
    d=float(np.linalg.norm(closest(p,surface[i])-p))
    if d<best[0]:best=(d,int(i))
   nearest_cache[key]=best;return best
  for row in read(PRIOR/'interfaces.json.gz')['rows']:
   if row['mode']!=mode or row['uid']not in UIDS:continue
   g=next(x for x in data['rows']if x['uid']==row['uid']);t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];bottom=t[:,:,1].min();edges={};point_refs=[]
   for f in row['unresolved']:
    p=np.asarray(f['position']);point_refs.append(dict(position=p.tolist(),distanceM=nearest(p)[0],supportFace=nearest(p)[1]))
    for face in f['sourceFaces']:
     tri=t[face['faceIndex']]
     for i in range(3):
      a,b=tri[i],tri[(i+1)%3];d=b-a
      if max(a[1],b[1])>bottom+.35 or d@d==0:continue
      q=a+np.clip((p-a)@d/(d@d),0,1)*d
      if np.linalg.norm(q-p)<=.001:edges[tuple(sorted((tuple(a),tuple(b))))]=[a,b]
   assert edges;results=[]
   for edge,(a,b)in edges.items():
    intervals=[(a,b,0)];leaves=[];failed=[]
    while intervals:
     x,y,depth=intervals.pop();mid=(x+y)/2;distance,face=nearest(mid);bound=distance+float(np.linalg.norm(y-x))/2
     if bound<=.1:leaves.append(dict(a=x.tolist(),b=y.tolist(),midpointDistanceM=distance,upperBoundM=bound,supportFace=face));continue
     if distance>.1 or depth>=18:failed.append(dict(a=x.tolist(),b=y.tolist(),midpointDistanceM=distance,upperBoundM=bound,supportFace=face,depth=depth));continue
     intervals.extend([(x,mid,depth+1),(mid,y,depth+1)])
    results.append(dict(edge=[list(v)for v in edge],certifiedWithinPointOneM=not failed,leaves=leaves,failed=failed))
   out=dict(mode=mode,uid=row['uid'],unresolvedPoints=point_refs,edges=results,allFlaggedEdgesCertified=all(e['certifiedWithinPointOneM']for e in results),qualification='Complete edge distance bound uses the 1-Lipschitz distance to the finite union of unchanged compound triangles. 0.1m is a diagnostic bound only; no vertical support limit or model geometry is changed. All selected edges and failed bounds retained.')
   save(DOC/(mode+'-'+row['uid'].split('/')[1]+'.json.gz'),out);s=dict(mode=mode,uid=row['uid'],edges=len(results),certified=sum(e['certifiedWithinPointOneM']for e in results),maxUnresolvedPointDistanceM=max(x['distanceM']for x in point_refs),allFlaggedEdgesCertified=out['allFlaggedEdgesCertified']);summary.append(s);print(s,flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,newlyInstalled=0));refs=[Path(__file__),PRIOR/'result.json',HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/p for p in pins]];out=module('wave_seam_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-verdant-complete-flagged-rim-edge-distance-bounds-v1',refs,dict(uids=UIDS,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
