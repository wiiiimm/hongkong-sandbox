"""Nominate exact exposed original surface fragments; no terrain change/approval."""
from pathlib import Path
from fractions import Fraction
from functools import lru_cache
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_surface_inset import plane,lower_region,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-runtime-buried-coverage-v2-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v2-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 selection=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';row=next(x for x in read(selection)['rows']if x['uid']=='landsd/281463:0');raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=decode_original_world_triangles(raw)
 groundpath=HERE/'local'/SRC.name/'runtime-geometry.json.gz';ground=np.asarray(read(groundpath)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3)
 points=np.concatenate([t,t.mean(1)[:,None,:]],axis=1);gp=shapely.polygons(ground[:,:,[0,2]]);validground=shapely.area(gp)>1e-10
 helper=module('lai_remaining_samples',HERE/'xl-final-script-pass.py');heights=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground[validground],shapely.STRtree(gp[validground])).reshape(-1,4)
 assert np.isfinite(heights).all();buried=((points[:,:,1]-heights)<-.5).all(1);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);upward=cross[:,1]>.25*np.linalg.norm(cross,axis=1)
 foundationpath=BASE/'government-xl-lai-chi-kok-four-mode-foundations-v2-20261019/281463:0-original.json';f=read(foundationpath)['foundation'];assert int(buried.sum())==f['fullyBuriedTriangles'] and int((buried&upward).sum())==f['fullyBuriedUpwardTriangles'];refs.append(foundationpath)
 nonvertical=np.abs(cross[:,1])>1e-10
 wanted=np.flatnonzero(buried&nonvertical).tolist()
 save(DOC/'remaining-buried-faces.json.gz',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],upwardFaceIds=np.flatnonzero(buried&upward).tolist(),nonverticalFaceIds=wanted,allBuriedFaceIds=np.flatnonzero(buried).tolist(),vertices=t[buried].tolist(),groundGaps=(points[:,:,1]-heights)[buried].tolist()))
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
  rows.append(dict(originalFace=i,upward=bool(upward[i]),sourceProjectedAreaM2=float(p.area),exposedProjectedAreaM2=float(exposed.area),higherSourceCoveredAreaM2=float(p.intersection(covered).area),fragmentRange=[start,len(out)],nearCoplanarOtherFaceIds=ambiguous))
 result=np.asarray(out);assert len(result)>0 and np.isfinite(result).all();ps=shapely.polygons(result[:,:,[0,2]]);union=shapely.union_all(ps);excess=float(shapely.area(ps).sum()-union.area)
 summary=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],nominatedOriginalFaces=len(wanted),fullyHiddenFaces=sum(x['exposedProjectedAreaM2']<=1e-10 for x in rows),exposedFaces=sum(x['exposedProjectedAreaM2']>1e-10 for x in rows),fragments=len(result),projectedAreaM2=float(union.area),projectedOverlapM2=excess,exactPlaneResolvedFaces=sum(bool(x['nearCoplanarOtherFaceIds'])for x in rows),sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,qualification='Exact-plane fragments of all remaining nonvertical buried original faces after private inset, clipped only by higher original source surfaces. Near-coplanar equality resolved with exact rational planes from original coordinates; equal nominated regions have one deterministic owner. Diagnostic only; terrain continuity, support and retained neighbours remain unapproved.')
 groundpolys=shapely.polygons(ground[:,:,[0,2]]);gv=shapely.area(groundpolys)>1e-10;gt=ground[gv];gpolys=groundpolys[gv];gtree=shapely.STRtree(gpolys);checks=[]
 for i,fragment in enumerate(result):
  p=ps[i];covered=[];maxgap=-float('inf');high=[]
  for j in gtree.query(p,predicate='intersects'):
   overlap=p.intersection(gpolys[j])
   if overlap.area<=1e-10:continue
   covered.append(overlap);d=plane(gt[j])-plane(fragment);xy=shapely.get_coordinates(overlap);gap=xy@d[:2]+d[2];maxgap=max(maxgap,float(gap.max()))
   if gap.max()>.5:high.append(dict(terrainFace=int(j),maxTerrainAboveSourceM=float(gap.max()),overlapAreaM2=float(overlap.area)))
  missing=float(p.difference(shapely.union_all(covered)).area)
  checks.append(dict(fragment=i,sourceFace=lineage[i],upward=bool(upward[lineage[i]]),areaM2=float(p.area),uncoveredAreaM2=missing,maxTerrainAboveSourceM=maxgap if np.isfinite(maxgap)else None,overHalfMetrePairs=high))
 summary.update(remainingBuriedFaces=int(buried.sum()),projectedVerticalBuriedFaces=int((buried&~nonvertical).sum()),upwardExposedFragments=sum(x['upward']for x in checks),exposedFragmentsAboveHalfMetre=sum(bool(x['overHalfMetrePairs'])for x in checks),exposedUncoveredAreaM2=sum(x['uncoveredAreaM2']for x in checks))
 save(DOC/'exposed-terrain-checks.json',dict(summary=summary,checks=checks,projectedVerticalBuriedFaceIds=np.flatnonzero(buried&~nonvertical).tolist()))
 save(DOC/'surface-nomination.json.gz',dict(summary=summary,triangles=result.tolist(),sourceFaceIndices=lineage,rows=rows));save(DOC/'summary.json',summary)
 terrainpath=ROOT/'3d-viewer/city/data/government-native-273000-0.json';terrain=read(terrainpath);g=terrain['meta']['georef'];rect=shapely.box(g['bE']-834500,816500-g['bN'],g['bE']-834500+(terrain['w']-1)*g['aE'],816500-g['bN']-(terrain['h']-1)*g['aN']);save(DOC/'retained-intersection.json',dict(retainedTerrainPath=str(terrainpath.relative_to(ROOT)),retainedTerrainSHA256=digest(terrainpath.read_bytes()),nominationIntersectionM2=float(union.intersection(rect).area),retainedSurfaceMustRemainValidated=True));refs.append(terrainpath)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('lai_exposed_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-exposed-original-surface-nomination',refs,dict(uids=[row['uid']],summary=summary,installationApproved=False));print(summary,flush=True)
if __name__=='__main__':main()
