"""Find exact finite incident-source/podium intersections near failed samples; diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-wave-all-original-support-distance-v1-20261017';BATCH='government-xl-wave-incident-side-intersections-v1-20261017';DOC=BASE/BATCH

def segment(a,b):
 n=np.cross(a[1]-a[0],a[2]-a[0]);m=np.cross(b[1]-b[0],b[2]-b[0]);ln=np.linalg.norm(n);lm=np.linalg.norm(m)
 if ln==0 or lm==0:return None
 n=n/ln;m=m/lm;d=np.cross(n,m);length=np.linalg.norm(d)
 if length<1e-10:return None
 d=d/length;x=np.linalg.solve(np.array([n,m,d]),np.array([n@a[0],m@b[0],0.]));lo=-np.inf;hi=np.inf
 for t in [a,b]:
  mat=np.column_stack((t[1]-t[0],t[2]-t[0]));uv=np.linalg.lstsq(mat,np.column_stack((x-t[0],d)),rcond=None)[0];weights=np.array([1-uv[:,0].sum(),*uv[:,0]]);rates=np.array([-uv[:,1].sum(),*uv[:,1]])
  for w,v in zip(weights,rates):
   if abs(v)<1e-12:
    if w< -1e-9:return None
   elif v>0:lo=max(lo,-w/v)
   else:hi=min(hi,-w/v)
 if lo>hi or not np.isfinite([lo,hi]).all():return None
 return np.array([x+lo*d,x+hi*d])
def main():
 assert not DOC.exists();r=read(PREV/'result.json');pins={};refs=[Path(__file__),PREV/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(PREV/'support-inputs.json')['sources'];meshes={s['uid']:decode_original_world_triangles((ROOT/s['candidate']['path']).read_bytes())for s in sources};support=meshes['landsd/301560:0'];sl=support.min(1);sh=support.max(1);output=[]
 for row in read(PREV/'support-checks.json.gz')['rows']:
  tri=meshes[row['uid']];records=[]
  for f in row['unresolved']:
   p=np.array(f['position']);candidate=np.flatnonzero(((sh>=p-.5)&(sl<=p+.5)).all(1));hits=[]
   for face in f['originalSourceFaces']:
    i=face['faceIndex'];t=tri[i]
    for j in candidate:
     edge=segment(t,support[j])
     if edge is None:continue
     d=edge[1]-edge[0];den=d@d;q=edge[0]+np.clip((p-edge[0])@d/den,0,1)*d if den else edge[0];dist=float(np.linalg.norm(q-p))
     if dist<=.5:hits.append(dict(sourceFace=i,supportFace=int(j),segment=edge.tolist(),closest=q.tolist(),distanceM=dist,segmentLengthM=float(np.linalg.norm(d))))
   hits.sort(key=lambda h:h['distanceM']);records.append(dict(position=f['position'],originalFailure=f['reason'],intersections=hits,hasFiniteLocalIntersection=any(h['segmentLengthM']>1e-6 for h in hits)))
  output.append(dict(uid=row['uid'],rows=records,failedSamples=len(records),withFiniteLocalIntersection=sum(x['hasFiniteLocalIntersection']for x in records)));print({k:v for k,v in output[-1].items()if k!='rows'},flush=True)
 save(DOC/'intersections.json.gz',dict(rows=output,fullAcceptance=False,qualification='Exact incident triangle versus complete nearby original podium triangles. Nonparallel finite intersection segments only; coplanar and disconnected cases remain unresolved. Within 0.5m nominates local source evidence only, not acceptance.'))
 out=module('wave_side_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-incident-side-intersection-census-v1',list(set(refs)),dict(uids=[x['uid']for x in output]+['landsd/301560:0'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
