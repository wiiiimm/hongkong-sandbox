"""Private hotel-core terrain joined to unchanged parent exterior, away from all BASIC actors."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,Point,box
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-local-terrain-join-v4-20261015';DOC=BASE/BATCH
CAP=BASE/'government-xl-stanford-basic-ground-capture-v1-20261015';PREV=BASE/'government-xl-stanford-upper-runtime-candidate-v2-20261015'
def split_vertical(face,region):
 projection=shapely.MultiPoint(face[:,[0,2]]).convex_hull
 clipped=projection.intersection(region)
 if clipped.is_empty:return []
 if projection.geom_type=='Point':return [face.tolist()] if region.covers(projection)else []
 axis=0 if np.ptp(face[:,0])>=np.ptp(face[:,2])else 2
 output=[]
 for part in shapely.get_parts(clipped):
  if part.geom_type not in ('LineString','LinearRing') or part.length==0:continue
  coords=np.asarray(part.coords);k=0 if axis==0 else 1;lo,hi=coords[:,k].min(),coords[:,k].max();poly=[v.copy()for v in face]
  for bound,sign in [(lo,1),(hi,-1)]:
   result=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    da,db=sign*(a[axis]-bound),sign*(b[axis]-bound)
    if da>=0:result.append(a)
    if (da<0 and db>0)or(da>0 and db<0):result.append(a+(b-a)*(da/(da-db)))
   poly=result
   if not poly:break
  for j in range(1,len(poly)-1):output.append([poly[0].tolist(),poly[j].tolist(),poly[j+1].tolist()])
 return output

def main():
 assert not DOC.exists();DOC.mkdir();refs=[Path(__file__)];
 for folder in [CAP,PREV,BASE/'government-xl-stanford-native-parent-scope-v1-20261015']:
  r=read(folder/'result.json');refs.append(folder/'result.json')
  for q in r['evidenceRefs']:
   p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 assert not read(BASE/'government-xl-stanford-native-parent-scope-v1-20261015/scope.json.gz')['touchingNativeUids']
 helper=module('stanford_join_geometry',HERE/'primrose_private_terrain_join_v1_20261015.py');refs.append(HERE/'primrose_private_terrain_join_v1_20261015.py')
 source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']=='B365201779201063C0');asset=ROOT/source['asset']['path'];refs.append(asset);assert digest(asset.read_bytes())==source['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());p=shapely.polygons(t[:,:,[0,2]]);whole=shapely.union_all(p[shapely.area(p)>1e-10]);inner=whole.buffer(.1,join_style='mitre');outer=whole.buffer(.8,join_style='mitre');inp=read(CAP/'input.json.gz');domain=box(*inp['domain']);assert domain.contains(outer)
 separation=[]
 for a in read(CAP/'basic-actors.json.gz')['rows']:
  t=np.asarray(a['position']).reshape(-1,3)[np.asarray(a['index']).reshape(-1,3)];p=shapely.polygons(t[:,:,[0,2]]);region=shapely.union_all(p[shapely.area(p)>1e-10]);assert outer.disjoint(region),a['uid'];separation.append({'uid':a['uid'],'distanceM':whole.distance(region)})
 before=np.asarray(read(CAP/'before-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);after=np.asarray(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);out=[];lineage=[]
 def emit(region,face,kind,idx,other=None,j=None):
  for poly in helper.pieces(region):
   points=[]
   for x,z in list(poly.exterior.coords)[:3]:
    y=helper.height(face,x,z)
    if other is not None:
     q=Point(x,z);di=q.distance(inner);do=q.distance(outer.boundary);assert di+do>0;alpha=do/(di+do);y=alpha*y+(1-alpha)*helper.height(other,x,z)
    points.append([x,y,z])
   out.append(points);lineage.append({'kind':kind,'face':idx,'parentFace':j})
 for kind,faces,region in [('hotel-core',after,inner),('current-parent',before,domain.difference(outer))]:
  for i,f in enumerate(faces):
   poly=Polygon(f[:,[0,2]])
   if poly.area==0:
    for part in split_vertical(f,region):out.append(part);lineage.append({'kind':kind+'-vertical-split','face':i})
   else:emit(poly.intersection(region),f,kind,i)
 band=outer.difference(inner);bp=shapely.polygons(before[:,:,[0,2]]);tree=shapely.STRtree(bp)
 for i,f in enumerate(after):
  p=Polygon(f[:,[0,2]])
  if p.area==0:
   projection=shapely.MultiPoint(f[:,[0,2]]).convex_hull
   for j in tree.query(projection,predicate='intersects'):
    if bp[j].area<=1e-10:continue
    for vertices in split_vertical(f,band.intersection(bp[j])):
     joined=[]
     for x,y,z in vertices:
      q=Point(x,z);di=q.distance(inner);do=q.distance(outer.boundary);assert di+do>0;alpha=do/(di+do);joined.append([x,alpha*y+(1-alpha)*helper.height(before[j],x,z),z])
     out.append(joined);lineage.append({'kind':'transition-vertical-split','face':i,'parentFace':int(j)})
   continue
  part=p.intersection(band)
  if part.is_empty:continue
  for j in tree.query(part,predicate='intersects'):
   if bp[j].area>1e-10:emit(part.intersection(bp[j]),f,'transition',i,before[j],int(j))
 patch=read(PREV/'private-patch.json.gz');patch['id']=BATCH;patch['nativeMesh']['position']=np.asarray(out).reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(out)*3));p=shapely.polygons(np.asarray(out,dtype='<f4').astype(float)[:,:,[0,2]]);valid=shapely.area(p)>1e-10;union=shapely.union_all(p[valid]);gap=float(union.symmetric_difference(domain).area);excess=float(shapely.area(p[valid]).sum()-union.area);assert gap<.25 and excess<.25
 src=patch['nativeMesh']['source'];src['numericalCoverageGap']['measuredAreaM2']=gap;src['numericalProjectionOverlap']['measuredAreaM2']=excess;src['privateHotelJoin']={'innerPaddingM':.1,'outerPaddingM':.8,'separateBasicActors':len(separation),'sourceGeometryChanges':0,'sourceSHA256':source['sourceSHA256'],'policy':'Private hotel-core repair with interpolated narrow band; actual parent exterior retained. Current acceptance pending.'}
 resolution=module('stanford_join_validation',HERE/'resolve-pass.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';refs.extend([parentpath,HERE/'resolve-pass.py'])
 try:resolution.validate_patch(patch,read(parentpath));validation={'passed':True}
 except (AssertionError,ValueError)as e:validation={'passed':False,'error':str(e)}
 save(DOC/'private-patch.json.gz',patch);save(DOC/'construction.json.gz',{'lineage':lineage,'separation':separation,'innerGeoJSON':shapely.to_geojson(inner),'outerGeoJSON':shapely.to_geojson(outer),'sourceSHA256':source['sourceSHA256']});summary={'triangles':len(out),'gapM2':gap,'excessM2':excess,'validation':validation,'basicActorsOutsideJoin':len(separation),'sourceGeometryChanges':0,'fullAcceptance':False};save(DOC/'summary.json',summary)
 module('freeze_stanford_join',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-hotel-core-current-parent-exterior-join-v4',refs,{'uids':['landsd/305584:0','landsd/335875:0'],'summary':summary,'fullAcceptance':False});print(summary,flush=True)
if __name__=='__main__':main()
