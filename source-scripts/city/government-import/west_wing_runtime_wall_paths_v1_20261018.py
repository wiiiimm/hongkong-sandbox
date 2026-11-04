"""Diagnose complete vertical wall paths from source rims to actual rendered candidate terrain."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-runtime-wall-paths-v1-20261018';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-west-wing-runtime-support-v2-20261018'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={r['path']:r['sha256'] for r in receipt['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path;refs.append(ROOT/path)
 geometry=read(PRIOR/'input.json.gz');ground=np.asarray(geometry['terrain'],dtype='<f8')
 sources={r['uid']:r['sourceSHA256'] for r in read(BASE/'government-xl-west-wing-group-four-world-v1-20261018/selection.json.gz')['rows']}
 a,b,c=ground[:,0],ground[:,1],ground[:,2];v0=b[:,[0,2]]-a[:,[0,2]];v1=c[:,[0,2]]-a[:,[0,2]];det=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0];nz=det!=0;out=[]
 for row in read(PRIOR/'checks.json.gz')['rows']:
  tri=np.asarray(geometry['worlds'][row['mode']][row['uid']],dtype='<f8')
  for failure in row['unresolved']:
   assert failure['reason']=='support-above-rim';p=np.asarray(failure['position']);q=p[[0,2]]-a[:,[0,2]];u=np.full(len(ground),np.nan);v=u.copy();u[nz]=(q[nz,0]*v1[nz,1]-q[nz,1]*v1[nz,0])/det[nz];v[nz]=(v0[nz,0]*q[nz,1]-v0[nz,1]*q[nz,0])/det[nz];ids=np.flatnonzero(nz&(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9));hits=[]
   for i in ids:
    y=float(a[i,1]+u[i]*(b[i,1]-a[i,1])+v[i]*(c[i,1]-a[i,1]));hits.append(dict(face=int(i),height=y))
   assert hits;h=max(h['height'] for h in hits);assert abs((p[1]-h)-failure['gap'])<1e-5;path=LineString([(0,float(p[1])),(0,h)]);intervals=[];faces=[]
   for f in failure['originalSourceFaces']:
    t=tri[f['faceIndex']];assert np.array_equal(t,np.asarray(f['vertices']));n=np.cross(t[1]-t[0],t[2]-t[0]);norm=np.linalg.norm(n)
    if norm==0 or n[1]!=0:continue
    if abs(np.dot(n,p-t[0]))/norm>1e-7:continue
    axis=0 if np.ptp(t[:,0])>=np.ptp(t[:,2]) else 2
    polygon=Polygon(t[:,[axis,1]]);line=LineString([(p[axis],p[1]),(p[axis],h)]);intersection=polygon.intersection(line)
    if intersection.is_empty:continue
    parts=list(intersection.geoms) if hasattr(intersection,'geoms') else [intersection]
    for part in parts:
     ys=[q[1] for q in part.coords]
     if max(ys)>min(ys):intervals.append(LineString([(0,min(ys)),(0,max(ys))]));faces.append(f['faceIndex'])
   coverage=unary_union(intervals) if intervals else LineString();gapLength=path.difference(coverage).length;withinTolerance=path.difference(coverage.buffer(1e-8)).is_empty
   out.append(dict(uid=row['uid'],mode=row['mode'],sourceSHA256=sources[row['uid']],originalFailure=failure,groundHits=hits,groundContact=[float(p[0]),h,float(p[2])],verticalPathLengthM=h-float(p[1]),sourceFaceIds=sorted(set(faces)),exactUncoveredPathLengthM=gapLength,wholePathCoveredWithinNumericalTolerance=withinTolerance,numericalToleranceM=1e-8))
 assert len(out)==sum(len(r['unresolved'])for r in read(PRIOR/'checks.json.gz')['rows'])
 save(DOC/'paths.json',dict(rows=out,covered=sum(r['wholePathCoveredWithinNumericalTolerance'] for r in out),samples=len(out),diagnosticOnly=True,physicalAccepted=False,sourceGeometryChanges=0,qualification='Actual ground intersection and whole vertical path through exact incident original vertical faces; no new contact geometry, no rim threshold relaxation. Source-role and full runtime acceptance remain separate.'))
 result=module('west_embedded_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-all-mode-runtime-embedded-wall-paths-v1',refs,dict(uids=sorted({r['uid'] for r in out}),samples=len(out),covered=sum(r['wholePathCoveredWithinNumericalTolerance'] for r in out),diagnosticOnly=True,physicalAccepted=False));print(result['jobId'],flush=True)
if __name__=='__main__':main()
