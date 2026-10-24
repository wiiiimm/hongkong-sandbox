"""Exact rational distance witness for the unproved original low edge; no edits."""
from fractions import Fraction as F
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-rim-gap-witness-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-langham-failed-rim-edges-finite-band-v1-20261017';RT=HERE/'local/government-xl-langham-current-pair-v1-20261017/runtime-geometry.json.gz'
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def d2(p,triangle):
 a,b,c=triangle;u=sub(b,a);v=sub(c,a);w=sub(p,a);uu=dot(u,u);vv=dot(v,v);uv=dot(u,v);du=dot(w,u);dv=dot(w,v);det=uu*vv-uv*uv;ds=[]
 if det:
  s=(du*vv-dv*uv)/det;t=(dv*uu-du*uv)/det
  if s>=0 and t>=0 and s+t<=1:
   q=tuple(a[j]+s*u[j]+t*v[j]for j in range(3));ds.append(dot(sub(p,q),sub(p,q)))
 for a,b in [(a,b),(b,c),(c,a)]:
  e=sub(b,a);den=dot(e,e);k=max(F(0),min(F(1),dot(sub(p,a),e)/den))if den else F(0);q=tuple(a[j]+k*e[j]for j in range(3));ds.append(dot(sub(p,q),sub(p,q)))
 return min(ds)
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 unit=[tuple(map(F,p))for p in [(0,0,0),(1,0,0),(0,0,1)]]
 assert d2((F(1,4),F(2),F(1,4)),unit)==4
 assert d2((F(2),F(0),F(0)),unit)==1
 assert d2((F(0),F(1),F(0)),[(F(0),)*3]*3)==1
 edge=next(x for x in read(PRIOR/'edges.json.gz')['rows']if x['incidentSourceFaces']==[13146]);line=np.asarray(edge['segment']);rt=read(RT);g=next(x for x in rt['rows']if x['uid']=='landsd/224399:0');tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(tri)==20260
 probes=[]
 for k in range(33):
  t=F(k,32);exact=tuple(F(float(line[0,j]))+(F(float(line[1,j]))-F(float(line[0,j])))*t for j in range(3));p=np.array([float(x)for x in exact]);i,q,d=nearest(p,tri);probes.append(dict(parameter=str(t),position=p.tolist(),nearestFace=i,distanceM=d,exact=exact))
 worst=max(probes,key=lambda x:x['distanceM']);assert worst['distanceM']>.1,'No sampled negative: use subdivision proof next'
 point=worst.pop('exact');limit=F(.1)**2;lo=tri.min(1);hi=tri.max(1);records=[];excluded=0
 for i,t in enumerate(tri):
  bound=sum(max(F(float(lo[i,j]))-point[j],point[j]-F(float(hi[i,j])),F(0))**2 for j in range(3))
  if bound>limit:excluded+=1;continue
  dist=d2(point,[tuple(F(float(x))for x in p)for p in t]);records.append(dict(face=i,exactSquaredDistanceM2=str(dist),outsideFixedBand=dist>limit))
 assert records and all(x['outsideFixedBand']for x in records);assert excluded+len(records)==len(tri)
 for p in probes:p.pop('exact',None)
 summary=dict(sourceFace=13146,completeSupportFaces=len(tri),exactBoundsExcluded=excluded,exactTriangleChecks=len(records),witness=worst,exactWitnessCoordinates=[str(x)for x in point],exactSquaredBandM2=str(limit),allOriginalSupportFacesOutsideBandAtWitness=True,installationApproved=False,qualification='One exact point on the unchanged original edge is farther than the existing0.1m distance band from every complete installed support triangle. This proves a source-pair gap at this point, not corruption, structural impossibility or absence of other provider sources.')
 save(DOC/'witness.json',dict(summary=summary,exactTriangleDistances=records,diagnosticSampleProbes=probes))
 result=module('langham_gap_witness_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-rational-original-edge-gap-witness-v1',[Path(__file__),RT,PRIOR/'result.json',PRIOR/'edges.json.gz',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py'],dict(uids=['landsd/79318:0'],summary=summary,fullAcceptance=False,nextStep='Retain the demonstrated original pair gap; consider other authenticated source revisions/components or an explicitly justified contact interpretation, not more unchanged band-check retries.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
