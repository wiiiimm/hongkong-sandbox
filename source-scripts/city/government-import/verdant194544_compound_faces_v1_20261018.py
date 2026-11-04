"""Four-mode complete original neighbour foundation and actual finite-surface distance evidence."""
from pathlib import Path
import subprocess,numpy as np,shapely
from scipy.spatial import cKDTree
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-verdant194544-four-world-v1-20261018';SEAM=BASE/'government-xl-verdant195000-seam-review-v1-20261018';ASSEMBLY=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';REC=BASE/'government-xl-wave-verdant-194544-original-recovery-v1-20261017';BATCH='government-xl-verdant194544-compound-faces-v1-20261018';DOC=BASE/BATCH;UID='landsd/194544:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SEAM]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 source=read(REC/'selection.json.gz')['rows'][0];b=source['source']['building'];final=module('verdant_neighbour_full_faces',HERE/'xl-final-script-pass.py');summary=[]
 for mode,world in read(CAP/'world-triangles.json.gz').items():
  t=np.asarray(world[UID]);support=np.asarray(read(ASSEMBLY/mode/'input.json.gz')['podium']);foundation=final.foundation_context(t,support,Polygon(b['rings'][0],b['rings'][1:]));d=DOC/mode;save(d/'foundation.json',foundation);save(d/'input.json.gz',dict(rows=[dict(uid=UID,position=t.reshape(-1).tolist(),index=list(range(len(t)*3)))],podium=support.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs'
  with(d/'support.log').open('w')as log:subprocess.run(['node',str(tool),str(d.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  proof=read(d/'support.json.gz')['rows'][0]['proof'];lo=support.min(1);hi=support.max(1);tree=cKDTree(support.mean(1));cache={}
  def nearest(p):
   key=tuple(p)
   if key in cache:return cache[key]
   ids=np.atleast_1d(tree.query(p,k=8)[1]);best=min((float(np.linalg.norm(closest(p,support[i])-p)),int(i))for i in ids);lower=np.linalg.norm(np.maximum(np.maximum(lo-p,p-hi),0),axis=1)
   for i in np.flatnonzero(lower<=best[0]+1e-12):
    value=float(np.linalg.norm(closest(p,support[i])-p))
    if value<best[0]:best=(value,int(i))
   cache[key]=best;return best
  polys=shapely.polygons(support[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),support[valid],shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1));assert len(ids)==foundation['fullyBuriedTriangles'];faces=[]
  for i in ids:
   queue=[(t[i],0)];leaves=[];failed=[]
   while queue:
    tri,depth=queue.pop();centre=tri.mean(0);distance,face=nearest(centre);bound=distance+float(np.linalg.norm(tri-centre,axis=1).max());record=dict(triangle=tri.tolist(),distanceM=distance,upperBoundM=bound,supportFace=face)
    if bound<=.1:leaves.append(record);continue
    if distance>.1 or depth>=14:failed.append(record);continue
    a,c,e=tri;ac=(a+c)/2;ce=(c+e)/2;ea=(e+a)/2;queue.extend((np.asarray(v),depth+1)for v in [[a,ac,ea],[ac,c,ce],[ea,ce,e],[ac,ce,ea]])
   faces.append(dict(sourceFace=int(i),vertices=t[i].tolist(),sampledVerticalGaps=gaps[i].tolist(),wholeFaceWithinPointOneM=not failed,leaves=leaves,failed=failed))
  residual=[dict(**f,nearestDistanceM=nearest(np.asarray(f['position']))[0],nearestSupportFace=nearest(np.asarray(f['position']))[1])for f in proof['unresolved']];save(d/'finite-surface-context.json.gz',dict(faces=faces,unresolved=residual,fullAcceptance=False));s=dict(mode=mode,uid=UID,completeFaces=len(t),buried=len(ids),buriedFacesWithinPointOneM=sum(f['wholeFaceWithinPointOneM']for f in faces),strictContacts=proof['strictContacts'],unresolved=len(residual),maximumResidualDistanceM=max((r['nearestDistanceM']for r in residual),default=0));summary.append(s);print(s,flush=True)
 save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='Raw compound foundation warnings retained. Finite-surface distances do not certify source roles or placement; all subdivision failures retained. No geometry edits.'));refs.extend([tool,HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'xl-final-script-pass.py',*[ROOT/p for p in pins]]);out=module('verdant_neighbour_faces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verdant-neighbour-four-mode-whole-source-compound-face-context-v1',refs,dict(uids=[UID],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
