"""Resolve conservative whole-edge failures via exact subdivision or exact gap witnesses."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
from langham_rim_gap_witness_v1_20261017 import d2
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-conflict-edge-bands-v1-20261017'
BATCH='government-xl-aqua272788-unproved-edges-resolution-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 rt=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';g=next(g for g in read(rt)['rows']if g['uid']=='landsd/193086:0');tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(tri)==22735
 lo,hi=tri.min(1),tri.max(1);rows=[]
 for edge in read(PRIOR/'edges.json.gz')['rows']:
  if edge['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']:continue
  line=np.array(edge['segment']);a,b=[tuple(F(float(v))for v in p)for p in line];probes=[]
  for k in range(33):
   t=F(k,32);p=tuple(a[j]+(b[j]-a[j])*t for j in range(3));i,q,dist=nearest(np.array([float(v)for v in p]),tri);probes.append(dict(parameter=str(t),exactCoordinates=[str(v)for v in p],nearestFace=i,distanceM=dist))
  worst=max(probes,key=lambda p:p['distanceM']);out=dict(face=edge['face'],edge=edge['edge'],probes=probes)
  if worst['distanceM']>.1:
   point=tuple(F(v)for v in worst['exactCoordinates']);limit=F(.1)**2;excluded=0;checks=[]
   for i,t in enumerate(tri):
    bound=sum(max(F(float(lo[i,j]))-point[j],point[j]-F(float(hi[i,j])),F(0))**2 for j in range(3))
    if bound>limit:excluded+=1;continue
    dist=d2(point,[tuple(F(float(v))for v in p)for p in t]);checks.append(dict(face=i,squaredDistanceM2=str(dist),outsideBand=dist>limit))
   assert excluded+len(checks)==len(tri) and all(q['outsideBand']for q in checks)
   out.update(provedGap=True,exactWitness=worst,exactBoundsExcluded=excluded,exactChecks=checks)
  else:
   partitions=[]
   for n in [8,32]:
    pieces=[]
    for k in range(n):
     exact=[tuple(a[j]+(b[j]-a[j])*F(t,n)for j in range(3))for t in [k,k+1]];segment=np.array([[float(v)for v in p]for p in exact]);assert all(F(float(segment[i,j]))==exact[i][j]for i in range(2)for j in range(3))
     pieces.append(dict(parameterInterval=[str(F(k,n)),str(F(k+1,n))],proof=verify(segment,tri)))
    passed=all(p['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in pieces);partitions.append(dict(subdivisions=n,complete=passed,pieces=pieces))
    if passed:break
   out.update(provedGap=False,completeEdgeCertified=passed,partitions=partitions)
  rows.append(out);print(dict(face=out['face'],edge=out['edge'],provedGap=out['provedGap'],complete=out.get('completeEdgeCertified'),maxProbeDistanceM=worst['distanceM']),flush=True)
 save(DOC/'resolution.json.gz',dict(rows=rows,fixedBandM=.1,wholeModelAccepted=False,geometryChanges=0))
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/e['path']for e in r['evidenceRefs']],HERE/'langham_rim_gap_witness_v1_20261017.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py']
 result=module('aqua_unproved_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-unproved-original-edges-exact-resolution-v1',refs,dict(uids=['landsd/272788:0'],edges=len(rows),provedGapEdges=sum(x['provedGap']for x in rows),additionalCertifiedEdges=sum(x.get('completeEdgeCertified',False)for x in rows),fullAcceptance=False,nextStep='Retain exact physical failure and inspect source role at resolved edge locations; no geometry change or tolerance waiver.'))
 print(result['jobId'],flush=True)
if __name__=='__main__':main()
