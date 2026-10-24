"""Nominate exact exposed original surface fragments; no terrain change/approval."""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_surface_inset import plane,lower_region,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-lower-surface-nomination-v1-20261021';DOC=BASE/BATCH
SRC=BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021';CTX=BASE/'government-xl-grandiose-buried-face-context-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,CTX]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,path):
  assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 row=next(r for r in take(SRC,SRC/'selection.json.gz')['rows']if r['uid']=='landsd/246824:0');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(raw)
 records=take(CTX,CTX/'246824:0.json.gz')['buriedFaces'];wanted=[r['faceIndex']for r in records if r['upward']];assert len(wanted)==2
 polygons=shapely.polygons(t[:,:,[0,2]]);valid=(shapely.area(polygons)>1e-10)&np.isin(np.arange(len(t)),wanted);ids=np.flatnonzero(valid);tree=shapely.STRtree(polygons[valid]);planes={int(i):plane(t[i])for i in ids};out=[];lineage=[];rows=[]
 wantedset=set(wanted)
 @lru_cache(None)
 def exact_plane(i):
  a,b,c=[[Fraction.from_float(float(v))for v in p]for p in t[i]]
  u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)]
  n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  assert n[1]
  return (-n[0]/n[1],-n[2]/n[1],a[1]+(n[0]*a[0]+n[2]*a[2])/n[1])
 # Resolve near-coplanar plane equality exactly from original float coordinates.
 # Equal nominated surfaces use deterministic face ownership, without shifts.
 for i in wanted:
  p=polygons[i];cuts=[];ambiguous=[]
  for j0 in tree.query(p,predicate='intersects'):
   j=int(ids[j0])
   if i==j:continue
   q=p.intersection(polygons[j])
   if q.area<=1e-10:continue
   d=planes[j]-planes[i];xy=shapely.get_coordinates(q);delta=xy@d[:2]+d[2]
   if np.max(np.abs(delta))<=1e-8:
    ambiguous.append(j);ai=exact_plane(i);aj=exact_plane(j)
    if ai==aj:
     if j in wantedset and j<i:cuts.append(q)
     continue
    d=np.asarray([float(aj[k]-ai[k])for k in range(3)])
   higher=lower_region(q,d)
   if higher.area>1e-10:cuts.append(higher)
  covered=shapely.union_all(cuts);exposed=p.difference(covered);fragments=lift(exposed,planes[i]);start=len(out);out.extend(fragments);lineage.extend([i]*len(fragments))
  rows.append(dict(originalFace=i,sourceProjectedAreaM2=float(p.area),exposedProjectedAreaM2=float(exposed.area),higherSourceCoveredAreaM2=float(p.intersection(covered).area),fragmentRange=[start,len(out)],nearCoplanarOtherFaceIds=ambiguous))
 result=np.asarray(out).reshape(-1,3,3);assert np.isfinite(result).all();ps=shapely.polygons(result[:,:,[0,2]]);union=shapely.union_all(ps);excess=float(shapely.area(ps).sum()-union.area)
 summary=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],nominatedOriginalFaces=len(wanted),fullyHiddenFaces=sum(x['exposedProjectedAreaM2']<=1e-10 for x in rows),exposedFaces=sum(x['exposedProjectedAreaM2']>1e-10 for x in rows),fragments=len(result),projectedAreaM2=float(union.area),projectedOverlapM2=excess,exactPlaneResolvedFaces=sum(bool(x['nearCoplanarOtherFaceIds'])for x in rows),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,qualification='Exact-plane fragments of buried upward original faces, clipped only by other nominated lower surfaces; private diagnostic hypothesis, not physical acceptance. Near-coplanar equality resolved with exact rational planes from original coordinates; equal nominated regions have one deterministic owner. Diagnostic only; terrain continuity, support and retained neighbours remain unapproved.')
 save(DOC/'surface-nomination.json.gz',dict(summary=summary,triangles=result.tolist(),sourceFaceIndices=lineage,rows=rows));save(DOC/'summary.json',summary)
 refs.extend([HERE/'source_surface_inset.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('kowloon_exposed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'kowloon-park-exact-original-surface-nomination',refs,dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
