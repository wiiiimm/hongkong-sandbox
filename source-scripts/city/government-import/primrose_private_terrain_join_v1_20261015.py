"""Private scripted terrain join; original building bytes and placement untouched.
Retain saved candidate planes inside a padded source projection and current parent
planes outside an outer ring. Overlay both TINs through the transition, then
triangulate and interpolate heights. This produces a new, unapproved terrain.
"""
from pathlib import Path
import copy,importlib.util
import numpy as np
import shapely
from shapely.geometry import Polygon,box,Point
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-primrose-basic-ground-capture-v1-20261015';OLD=BASE/'government-xl-primrose-podium-current-physical-20261007';BATCH='government-xl-primrose-private-terrain-join-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def pieces(region):
 return [p for p in shapely.get_parts(shapely.constrained_delaunay_triangles(region))if p.geom_type=='Polygon'and p.area>1e-10]
def height(face,x,z):
 n=np.cross(face[1]-face[0],face[2]-face[0]);assert abs(n[1])>1e-10
 return float(face[0,1]-(n[0]*(x-face[0,0])+n[2]*(z-face[0,2]))/n[1])
def main():
 assert not DOC.exists()and not LOCAL.exists();receipt=read(CAP/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 source=read(OLD/'selection.json.gz')['rows'][0];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());p=shapely.polygons(tri[:,:,[0,2]]);whole=shapely.union_all(p[shapely.area(p)>1e-10]);current=read(CAP/'basic-actors.json.gz');separation=[]
 for a in current['rows']:
  points=np.asarray(a['position']).reshape(-1,3);t=points[np.asarray(a['index']).reshape(-1,3)];polys=shapely.polygons(t[:,:,[0,2]]);region=shapely.union_all(polys[shapely.area(polys)>1e-10]);overlap=whole.intersection(region).area;distance=whole.distance(region)
  separation.append(dict(uid=a['uid'],intersectionAreaM2=overlap,distanceM=distance,actualProjectionGeoJSON=shapely.to_geojson(region)))
 assert {r['uid']for r in separation if r['intersectionAreaM2']>0}=={'landsd/74566:0','landsd/74568:0'}
 nearest=min(r['distanceM']for r in separation if r['intersectionAreaM2']==0);assert nearest>1
 inner=whole.buffer(.1,join_style='mitre');outer=whole.buffer(.8,join_style='mitre');domain=box(*read(CAP/'input.json.gz')['domain']);assert domain.contains(outer)
 for r in separation:
  if r['intersectionAreaM2']==0:assert outer.disjoint(shapely.from_geojson(r['actualProjectionGeoJSON'])),r['uid']
 band=outer.difference(inner);before=np.asarray(read(CAP/'before-ground.json.gz')['completeRelevantDrawnTriplets'],float).reshape(-1,3,3);after=np.asarray(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)
 output=[];lineage=[];counts={}
 def emit(region,face,kind,idx,other=None,j=None):
  for poly in pieces(region):
   points=[]
   for x,z in list(poly.exterior.coords)[:3]:
    y=height(face,x,z)
    if other is not None:
     p=Point(x,z);di=p.distance(inner);do=p.distance(outer.boundary);den=di+do;assert den>0
     alpha=do/den;y=alpha*y+(1-alpha)*height(other,x,z)
    points.append([x,y,z])
   output.append(points);lineage.append(dict(kind=kind,savedFace=idx,savedParentFace=j));counts[kind]=counts.get(kind,0)+1
 for label,faces,region in [('candidate-core',after,inner),('current-parent',before,domain.difference(outer))]:
  for i,f in enumerate(faces):
   poly=Polygon(f[:,[0,2]])
   if poly.area<=1e-10:
    # Preserve any drawn vertical or degenerate face that intersects this region.
    line=shapely.MultiPoint(f[:,[0,2]]).convex_hull
    if region.intersects(line):
     assert region.covers(line),'Vertical face crosses join boundary; dedicated split required'
     output.append(f.tolist());lineage.append(dict(kind=label+'-vertical',savedFace=i));counts[label+'-vertical']=counts.get(label+'-vertical',0)+1
    continue
   emit(poly.intersection(region),f,label,i)
 bp=shapely.polygons(before[:,:,[0,2]]);tree=shapely.STRtree(bp)
 for i,f in enumerate(after):
  poly=Polygon(f[:,[0,2]])
  if poly.area<=1e-10:continue
  clipped=poly.intersection(band)
  if clipped.is_empty:continue
  for j in tree.query(clipped,predicate='intersects'):
   if bp[j].area>1e-10:emit(clipped.intersection(bp[j]),f,'transition',i,before[j],int(j))
 t=np.asarray(output);projections=shapely.polygons(t[:,:,[0,2]]);coverage=shapely.union_all(projections[shapely.area(projections)>1e-10]);missing=domain.difference(coverage).area;excess=float(shapely.area(projections).sum()-coverage.area)
 assert missing<.01 and excess<.01,(missing,excess)
 original=read(OLD/'terrain-candidates.json')[0];patch=copy.deepcopy(read(ROOT/original['path']));patch['id']=BATCH;patch['nativeMesh']['position']=t.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(t)*3));patch['nativeMesh'].pop('sourceOverlap',None)
 patch['nativeMesh']['source']['privateScriptedJoin']=dict(method='candidate core/current-parent exterior with explicitly new interpolated transition',innerPaddingM=.1,outerPaddingM=.8,sourceGeometryChanges=0,originalCandidate=original,approval=False)
 DOC.mkdir();LOCAL.mkdir();out=LOCAL/'government-native-primrose-private-join.json';save(out,patch)
 save(DOC/'construction.json.gz',dict(sourceSHA256=source['sourceSHA256'],nearestSeparateActualActorM=nearest,separation=separation,innerGeoJSON=shapely.to_geojson(inner),outerGeoJSON=shapely.to_geojson(outer),lineage=lineage,counts=counts,triangles=len(t),projectedMissingM2=missing,projectedExcessM2=excess,sourceGeometryChanges=0,publication=False,installationApproved=False,newTerrainRequiresRuntimePhysicalVisualReview=True))
 candidate={**original,'path':str(out.relative_to(ROOT)),'sha256':digest(out.read_bytes()),'triangles':len(t)};save(DOC/'terrain-candidates.json',[candidate])
 refs=[ROOT/q['path']for q in receipt['evidenceRefs']]+[CAP/'result.json',OLD/'selection.json.gz',asset,Path(__file__),out,HERE/'exact_packed_world_geometry_20261009.py']
 spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'private-scripted-source-core-parent-exterior-terrain-join-v1',refs,dict(uids=['landsd/74569:0','landsd/74570:0','landsd/74573:0'],triangles=len(t),fullAcceptance=False,qualification='New private terrain join; original buildings unchanged. Full actual runtime, physical and visual validation pending.'));print(dict(triangles=len(t),counts=counts,missing=missing,excess=excess),flush=True)
if __name__=='__main__':main()
