"""Private expanded Whampoa grid with a bounded derived terrain child; no publication."""
from pathlib import Path
import copy,traceback
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from china_merchants_finite_inset_v4_20261021 import plane,lift
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import grid_surface_faces
from float32_coverage import approve_roundoff,geometry_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-private-wrapper-v3-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/118230:0'
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(name,p):
 _,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
cn='government-xl-harbourfront-tower-drawn-ground-v1-20261021';cap=take(cn,HERE/'local'/cn/'drawn-ground.json.gz')
for p,h in cap['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pins[p]=h;refs.append(ROOT/p)
root=read(ROOT/'3d-viewer/city/data/terrain.json');manifest=read(ROOT/'3d-viewer/city/data/manifest.json');url='city/data/terrain-whampoa-estates.json';old=read(ROOT/'3d-viewer'/url);assert not old.get('patches') and not old.get('nativeMesh')
builder=module('harbourfront_wrapper_builder',HERE/'resolve-pass-indexed-parent-clipping.py');cells=[536,418,541,426];bounds=builder.extent(cells,root);assert bounds==cap['bounds']
# No other top-level replacement may overlap this complete root-cell extent.
for e in manifest['terrainPatches']:
 if e['url']==url:continue
 p=read(ROOT/'3d-viewer'/e['url']);assert shapely.box(*builder.extent(p['coarseCells'],root)).intersection(shapely.box(*bounds)).area==0,e['url']
previous='government-xl-harbourfront-tower-private-wrapper-v1-20261021';parent=take(previous,HERE/'local'/previous/'expanded-parent.json');retained=old['w']*old['h'];w=parent['w'];h=parent['h']
for rr in range(old['h']):
 for cc in range(old['w']):
  for k in ['elev','renderedElev','vegetation']:assert parent[k][rr*w+cc]==old[k][rr*old['w']+cc]
builder.validate_patch(parent,root)
pre=LOCAL/'expanded-parent.json';save(pre,parent)
sn='government-xl-next-twenty-current-terrain-v6-20261021';row=next(r for r in take(sn,BASE/sn/'selection.json.gz')['rows']if r['uid']==UID);ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap);pins[str(ap.relative_to(ROOT))]=row['sourceSHA256'];tri=decode_original_world_triangles(ap.read_bytes())
core=shapely.union_all(shapely.polygons(tri[:,:,[0,2]])).buffer(1,join_style=2);outer=core.buffer(8,join_style=2);floor=float(tri[:,:,1].min());domain=[3282.5,-1787.5,3372.5,-1667.5];rect=shapely.box(*domain);assert rect.covers(outer)
scope='government-xl-harbourfront-tower-current-scope-v1-20261021';forms=take(scope,BASE/scope/'form-obligations.json.gz');hotel=next(f for f in forms if f['uid']=='landsd/145750:0');protected=shapely.Polygon(hotel['rings'][0],hotel['rings'][1:]).buffer(.25,join_style=2);guard=protected.buffer(1,join_style=2);sourceProjection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));assert sourceProjection.disjoint(guard)
save(DOC/'protected-neighbour.json',dict(uid=hotel['uid'],sourceDistanceM=sourceProjection.distance(protected),protectedWKT=protected.wkt,guardWKT=guard.wkt,preserveOriginalTerrainWithinProtectedPolygon=True))
allfaces=np.asarray(cap['position']).reshape(-1,3,3);keep=(allfaces[:,:,0].max(1)>=domain[0])&(allfaces[:,:,0].min(1)<=domain[2])&(allfaces[:,:,2].max(1)>=domain[1])&(allfaces[:,:,2].min(1)<=domain[3]);output=[];lineage=[]
for i in np.flatnonzero(keep):
 face=allfaces[i];poly=shapely.Polygon(face[:,[0,2]])
 if poly.area<=1e-10:
  if rect.covers(poly):output.append(face);lineage.append(int(i))
  else:assert poly.disjoint(rect),'Boundary-crossing vertical needs exact 3D clipping'
  continue
 clipped=poly.intersection(rect)
 if clipped.area<=1e-10:continue
 coeff=plane(face)
 regions=[clipped.intersection(core),clipped.intersection(outer).difference(core),clipped.difference(outer)]
 regions=[q for r in regions for q in [r.intersection(protected),r.intersection(guard).difference(protected),r.difference(guard)]if q.area>1e-10]
 for part in regions:
  if part.area<=1e-10:continue
  for f in ([face.copy()]if part.equals(poly)else lift(part,coeff)):
   for v in f:
    point=shapely.Point(v[[0,2]]);weight=min(max(0.,1-point.distance(core)/8),min(1.,point.distance(protected)));v[1]=min(v[1],v[1]+weight*(floor-v[1]))
   output.append(f);lineage.append(int(i))
faces=np.asarray(output);assert len(faces)<=25000
childcells=[int(domain[0]-bounds[0]),int(domain[1]-bounds[1]),int(domain[2]-bounds[0]),int(domain[3]-bounds[1])]
ps=builder.terrain.fine.DemSampler(parent,rendered=True);seed=np.asarray(grid_surface_faces(ps,rect));child=builder.make_patch(dict(uids=[UID],cells=childcells),parent,seed,[],parent_url=str(pre.relative_to(ROOT/'3d-viewer')) if pre.is_relative_to(ROOT/'3d-viewer') else str(pre.relative_to(ROOT)),parent_sha256=digest(pre.read_bytes()),allow_native_below_clamp=True)
child['nativeMesh']['position']=faces.reshape(-1).tolist();child['nativeMesh']['index']=list(range(len(faces)*3));policy='Derived private terrain floor at immutable original minimum Y, 1m collar and 8m return, preserving the hotel footprint plus 0.25m with a 1m guard transition to actual current rendered planes. No building geometry edits.';child['nativeMesh']['source'].update(policy=policy);child['meta']['source']['policy']=policy
before=geometry_sha(child);error=None
try:
 from native_patch_resolution import projected_context
 _,polygons,missing,_=projected_context(child,domain);difference=shapely.union_all(polygons).symmetric_difference(rect).area
 save(DOC/'coverage-measurement.json',dict(float32SymmetricDifferenceAreaM2=difference))
 if difference>0:save(DOC/'numerical-coverage.json',approve_roundoff(child,domain))
 overlap=module('harbourfront_wrapper_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC;overlap.overlap_proof(child,[Path(__file__),HERE/'local'/cn/'drawn-ground.json.gz'])
 builder.validate_patch(child,parent);assert geometry_sha(child)==before
except Exception as exc:error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
parent['patches']=[child]
if error is None:
 try:builder.validate_patch(parent,root)
 except Exception as exc:error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(DOC/'validation-failure.json',error)
out=LOCAL/'candidate-wrapper.json';save(out,parent);save(DOC/'lineage.json.gz',dict(capturedFaceIds=lineage,domain=domain))
save(DOC/'terrain-candidates.json',[dict(path=str(out.relative_to(ROOT)),sha256=digest(out.read_bytes()),uids=[UID],bounds=bounds,triangles=len(faces),replaces=dict(url=url,sha256=pins['3d-viewer/'+url],retainedUids=old['meta'].get('targetUids',[])))])
summary=dict(uids=[UID],terrainValidationPassed=error is None,error=error,rootCells=cells,completeParentBounds=bounds,childBounds=domain,retainedGridNodes=retained,allOriginalGridValuesUnchanged=True,childTriangles=len(faces),sourceGeometryChanges=0,installationApproved=False,qualification='Private expanded Whampoa grid retains every original node. New exterior grid samples the root DEM. Native child uses actual rendered terrain planes. Full current actor/packed bounds, exterior equivalence, physical/runtime/neighbour and browser checks remain required.')
save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
refs.extend([pre,out,HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'china_merchants_finite_inset_v4_20261021.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py'])
r=module('harbourfront_wrapper_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-expanded-whampoa-native-child-validation',refs,summary);print(dict(jobId=r['jobId'],**summary),flush=True)
