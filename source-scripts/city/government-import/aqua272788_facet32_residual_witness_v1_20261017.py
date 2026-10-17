"""Test exact interior residual points against every unchanged original podium triangle."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from langham_rim_gap_witness_v1_20261017 import d2
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-facet32-subdivision-v1-20261017';BATCH='government-xl-aqua272788-facet32-residual-witness-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 tree=read(PRIOR/'proof-tree.json.gz');rt=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';g=next(g for g in read(rt)['rows']if g['uid']=='landsd/193086:0');tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];lo,hi=tri.min(1),tri.max(1);probes=[]
 for n in tree['nodes']:
  if n['complete']or n.get('children'):continue
  vertices=[[F(v)for v in p]for p in n['exactVertices']];point=tuple(sum(v[j]for v in vertices)/3 for j in range(3));i,q,dist=nearest(np.array([float(v)for v in point]),tri);probes.append(dict(node=n['id'],exactPoint=[str(v)for v in point],nearestFace=i,distanceM=dist))
 worst=max(probes,key=lambda x:x['distanceM']);point=tuple(F(v)for v in worst['exactPoint']);limit=F(.1)**2;excluded=0;checks=[]
 for i,t in enumerate(tri):
  bound=sum(max(F(float(lo[i,j]))-point[j],point[j]-F(float(hi[i,j])),F(0))**2 for j in range(3))
  if bound>limit:excluded+=1;continue
  dist=d2(point,[tuple(F(float(v))for v in p)for p in t]);checks.append(dict(face=i,squaredDistanceM2=str(dist),outsideBand=dist>limit))
 assert excluded+len(checks)==len(tri);gap=all(x['outsideBand']for x in checks)
 save(DOC/'witness.json',dict(sourceFace=32,probes=probes,exactWitness=worst,exactBoundsExcluded=excluded,exactChecks=checks,completePodiumFaces=len(tri),provedInteriorGap=gap,fixedBandM=.1,sourceGeometryChanges=0,qualification='Exact residual-subtriangle centroid lies on the original facet. Complete podium AABB exclusions and exact finite-triangle distances decide whether this point exceeds 0.1m. No corruption or whole-model disposition inferred.'))
 out=module('aqua_residual_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-exact-interior-residual-distance-witness-v1',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins],HERE/'langham_rim_gap_witness_v1_20261017.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py'],dict(uids=['landsd/272788:0'],sourceFace=32,provedInteriorGap=gap,diagnosticNearestDistanceM=worst['distanceM'],fullAcceptance=False,nextStep='Use proved interior separation or remaining conservative proof gap in the source-junction review; do not equate edge proximity with whole-face acceptance.'))
 print(dict(jobId=out['jobId'],provedGap=gap,distanceM=worst['distanceM']),flush=True)
if __name__=='__main__':main()
