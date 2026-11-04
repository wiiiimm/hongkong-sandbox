"""Private combined pier terrain, preserving actual current drawn planes outside repairs."""
from pathlib import Path
import numpy as np, shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from china_merchants_finite_inset_v4_20261021 import plane,lift
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-combined-ground-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,p):
 _,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
n='government-xl-central-piers-drawn-parent-v1-20261021';data=take(n,HERE/'local'/n/'drawn-ground.json.gz')
for p,h in data['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h;refs.append(ROOT/p)
rectangle=shapely.box(*data['bounds']);baseline=np.asarray(data['position']).reshape(-1,3,3)
n='government-xl-next-twenty-current-terrain-v6-20261021';selection=take(n,BASE/n/'selection.json.gz')['rows'];models=[];cores=[]
for uid in ['landsd/213352:0','landsd/285475:0']:
 row=next(r for r in selection if r['uid']==uid);p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];pins[str(p.relative_to(ROOT))]=row['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());core=shapely.union_all(shapely.polygons(tri[:,:,[0,2]])).buffer(2,join_style=2);outer=core.buffer(8,join_style=2);assert rectangle.covers(outer);cores.append((core,outer,float(tri[:,:,1].min())));models.append((row,tri))
# Complete only material omissions that the existing renderer intentionally skips.
from native_patch_resolution import grid_surface_faces
sc='government-xl-central-piers-current-scope-v1-20261021';scope=take(sc,BASE/sc/'scope.json');wp=ROOT/'3d-viewer'/scope['replacedWrapper']['url'];parent=take(sc,wp)
builder=module('piers_zero_cell_sampler',HERE/'resolve-pass-indexed-parent-clipping.py');sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
union=shapely.union_all(shapely.polygons(baseline[:,:,[0,2]]));missing=rectangle.difference(union);material=shapely.union_all([p for p in shapely.get_parts(missing) if p.area>1e-5])
fill=np.asarray(grid_surface_faces(sampler,material));assert len(fill)>0;assert np.all(fill[:,:,1]==-4),'Omitted region is not exclusively existing minus-four metre water fallback'
protected=shapely.union_all([shapely.union_all(shapely.polygons(t[:,:,[0,2]])) for _,t in models]);assert material.intersection(protected).area<1e-6
save(DOC/'omitted-water-cells.json',dict(areaM2=material.area,triangles=len(fill),heightM=-4,protectedSourceOverlapM2=material.intersection(protected).area,qualification='Existing rendered-height fallback only; not surveyed seabed. Original rendered terrain retained elsewhere.'))
baseline=np.concatenate([baseline,fill]);output=[];lineage=[];verticals=0
for i,face in enumerate(baseline):
 poly=shapely.Polygon(face[:,[0,2]])
 if poly.area<=1e-10:
  # Keep rendered verticals explicitly; subsequent checks must account for them.
  if rectangle.covers(poly):output.append(face);lineage.append(i);verticals+=1
  else:assert poly.disjoint(rectangle),'Boundary-crossing vertical needs exact 3D clipping'
  continue
 pieces=[poly.intersection(rectangle)]
 for core,outer,floor in cores:
  pieces=[q for p in pieces for q in (p.intersection(core),p.intersection(outer).difference(core),p.difference(outer)) if q.area>1e-10]
 coeff=plane(face)
 for p in pieces:
  for f in ([face.copy()] if p.equals(poly) else lift(p,coeff)):
   for v in f:
    y=float(v[1]);point=shapely.Point(v[[0,2]])
    for core,outer,floor in cores:
     weight=max(0.,1-point.distance(core)/8);v[1]=min(v[1],y+weight*(floor-y))
   output.append(f);lineage.append(i)
output=np.asarray(output);assert np.isfinite(output).all();save(LOCAL/'bounded-terrain.json.gz',dict(triangles=output.tolist(),notPublishable=True));save(DOC/'lineage.json.gz',dict(parentFaces=lineage,retainedVerticals=verticals))
helper=module('piers_combined_foundation',HERE/'xl-final-script-pass.py');rows=[]
for row,tri in models:
 b=row['source']['building'];f=helper.foundation_context(tri,output,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(row['uid'].split('/')[1]+'-foundation.json'),f);r=dict(uid=row['uid'],foundation={k:v for k,v in f.items() if k!='components'});rows.append(r);print(r,flush=True)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
refs.append(LOCAL/'bounded-terrain.json.gz');refs.extend(HERE/n for n in ['china_merchants_finite_inset_v4_20261021.py','native_patch_resolution.py','exact_packed_world_geometry_20261009.py','xl-final-script-pass.py'])
summary=dict(uids=[r['uid'] for r in rows],rows=rows,terrainFaces=len(output),bounds=data['bounds'],sourceGeometryChanges=0,installationApproved=False,qualification='Private derived terrain floors with two metre collars and eight metre transitions using actual current rendered terrain planes. Vertical faces retained explicitly. Coverage, seams, installed neighbours and visual acceptance remain pending.')
save(DOC/'summary.json',summary);r=module('combined_piers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'combined-private-current-renderer-pier-ground',refs,summary);print(r['jobId'],flush=True)
