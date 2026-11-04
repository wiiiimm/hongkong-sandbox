"""Nominate exact exposed original surface fragments; no terrain change/approval."""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_surface_inset import plane,lower_region,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-exposed-source-nomination-v2-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-sheet-attribution-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 selection=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';row=next(x for x in read(selection)['rows']if x['uid']=='landsd/281463:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw)
 records=read(SRC/'buried-faces.json.gz')['faces'];wanted=[x['faceId']for x in records if x['upward']];assert len(wanted)==1598
 polygons=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ids=np.flatnonzero(valid);tree=shapely.STRtree(polygons[valid]);planes={int(i):plane(t[i])for i in ids};out=[];lineage=[];rows=[]
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
 result=np.asarray(out);assert len(result)>0 and np.isfinite(result).all();ps=shapely.polygons(result[:,:,[0,2]]);union=shapely.union_all(ps);excess=float(shapely.area(ps).sum()-union.area)
 summary=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],nominatedOriginalFaces=len(wanted),fullyHiddenFaces=sum(x['exposedProjectedAreaM2']<=1e-10 for x in rows),exposedFaces=sum(x['exposedProjectedAreaM2']>1e-10 for x in rows),fragments=len(result),projectedAreaM2=float(union.area),projectedOverlapM2=excess,exactPlaneResolvedFaces=sum(bool(x['nearCoplanarOtherFaceIds'])for x in rows),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,qualification='Exact-plane fragments of buried upward original faces, clipped only by higher original source surfaces. Near-coplanar equality resolved with exact rational planes from original coordinates; equal nominated regions have one deterministic owner. Diagnostic only; terrain continuity, support and retained neighbours remain unapproved.')
 save(DOC/'surface-nomination.json.gz',dict(summary=summary,triangles=result.tolist(),sourceFaceIndices=lineage,rows=rows));save(DOC/'summary.json',summary)
 terrainpath=ROOT/'3d-viewer/city/data/government-native-273000-0.json';terrain=read(terrainpath);g=terrain['meta']['georef'];rect=shapely.box(g['bE']-834500,816500-g['bN'],g['bE']-834500+(terrain['w']-1)*g['aE'],816500-g['bN']-(terrain['h']-1)*g['aN']);save(DOC/'retained-intersection.json',dict(retainedTerrainPath=str(terrainpath.relative_to(ROOT)),retainedTerrainSHA256=digest(terrainpath.read_bytes()),nominationIntersectionM2=float(union.intersection(rect).area),retainedSurfaceMustRemainValidated=True));refs.append(terrainpath)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('lai_exposed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-exposed-original-surface-nomination',refs,dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
