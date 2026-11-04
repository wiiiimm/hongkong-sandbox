"""Diagnostic original triangle intersections; no support acceptance or geometry edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-sham-shui-po-pool-contact-segments-v1-20261016'
DOC=BASE/BATCH

def segment(a,b):
 n=np.cross(a[1]-a[0],a[2]-a[0]);m=np.cross(b[1]-b[0],b[2]-b[0]);d=np.cross(n,m)
 length=np.linalg.norm(d)
 if length<1e-12*np.linalg.norm(n)*np.linalg.norm(m):return None
 d=d/length
 origin=np.linalg.solve(np.array([n,m,d]),np.array([n@a[0],m@b[0],0.]))
 lo,hi=-np.inf,np.inf
 for tri in [a,b]:
  edges=np.column_stack((tri[1]-tri[0],tri[2]-tri[0]));inverse=np.linalg.pinv(edges)
  uv=inverse@(origin-tri[0]);slope=inverse@d
  values=[uv[0],uv[1],1-uv.sum()];slopes=[slope[0],slope[1],-slope.sum()]
  for v,k in zip(values,slopes):
   if abs(k)<1e-12:
    if v < -1e-9:return None
   elif k>0:lo=max(lo,-v/k)
   else:hi=min(hi,-v/k)
 if lo>hi+1e-8:return None
 return np.array([origin+lo*d,origin+hi*d])

def main():
 # Analytic crossing, disjoint, and parallel cases exercise the actual primitive.
 a=np.array([[0.,0,0],[2,0,0],[0,0,2]])
 b=np.array([[.5,-1,0],[.5,1,0],[.5,0,2]])
 s=segment(a,b);assert s is not None and np.allclose(s[:,0],.5) and np.allclose(s[:,1],0)
 assert segment(a,b+np.array([5,0,0])) is None
 assert segment(a,a+np.array([0,1,0])) is None
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for name in ['original-group-v1','original-interfaces-v1']:
  p=BASE/('government-xl-sham-shui-po-pool-'+name+'-20261016')/'result.json';r=read(p)
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(p)
  for q in r['evidenceRefs']:
   assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 path=HERE/'local/government-xl-sham-shui-po-pool-original-group-v1-20261016/runtime-geometry.json.gz'
 rows=read(path)['rows'];tri={r['uid']:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in rows}
 support=tri['landsd/265480:0'];tower=tri['landsd/271043:0']
 failures=read(BASE/'government-xl-sham-shui-po-pool-original-interfaces-v1-20261016/support-checks.json.gz')['rows'][0]['unresolved'];output=[]
 for f in failures:
  point=np.asarray(f['position']);lo=point-.6;hi=point+.6
  ids=np.flatnonzero(np.all(support.max(axis=1)>=lo,axis=1)&np.all(support.min(axis=1)<=hi,axis=1));hits=[]
  for face in f['originalSourceFaces']:
   source=tower[face['faceIndex']]
   for j in ids:
    line=segment(source,support[j])
    if line is None:continue
    delta=line[1]-line[0];den=delta@delta;t=np.clip((point-line[0])@delta/den,0,1) if den else 0;nearest=line[0]+t*delta
    hits.append(dict(sourceFace=face['faceIndex'],supportFace=int(j),segment=line.tolist(),nearest=nearest.tolist(),distanceM=float(np.linalg.norm(nearest-point)),horizontalDistanceM=float(np.linalg.norm((nearest-point)[[0,2]])),heightAboveRimM=float(nearest[1]-point[1])))
  hits.sort(key=lambda h:h['distanceM']);output.append(dict(position=f['position'],incidentSourceFaces=[q['faceIndex'] for q in f['originalSourceFaces']],supportFacesExamined=len(ids),intersections=hits))
 DOC.mkdir();save(DOC/'contact-segments.json.gz',dict(rows=output,diagnosticOnly=True,numericalEpsilon=1e-8,fullAcceptance=False))
 summary=[dict(position=r['position'],intersections=len(r['intersections']),nearest=r['intersections'][0] if r['intersections'] else None) for r in output];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False,qualification='Intersections of unchanged incident source triangles with original podium triangles. Local candidate range 0.6m; absence is not a global non-contact proof. No acceptance threshold changed.'))
 refs.append(path)
 out=module('pool_segment_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pool-wall-podium-triangle-intersections-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0'],fullAcceptance=False,newlyInstalled=0,originalGeometryChanges=0))
 print(dict(jobId=out['jobId'],failures=len(output),withOriginalIntersection=sum(bool(r['intersections']) for r in output)),flush=True)
if __name__=='__main__':main()
