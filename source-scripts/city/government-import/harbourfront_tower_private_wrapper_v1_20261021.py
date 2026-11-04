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
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-tower-private-wrapper-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/118230:0'
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
parent=copy.deepcopy(old);w=351;h=561;assert old['w']==281 and old['h']==491
parent.update(w=w,h=h,coarseCells=cells,elev=[],renderedElev=[],vegetation=[])
parent['meta']['georef'].update(W=w,H=h);parent['meta']['targetUids']=sorted(set(parent['meta'].get('targetUids',[]))|{UID})
rawsampler=builder.terrain.fine.DemSampler(root);sampler=builder.terrain.fine.DemSampler(root,rendered=True);g=root['meta']['georef'];retained=0
for r in range(h):
 for c in range(w):
  if r<old['h'] and c<old['w']:
   i=r*old['w']+c
   for k in ['elev','renderedElev','vegetation']:parent[k].append(old[k][i])
   retained+=1
  else:
   x=bounds[0]+c;z=bounds[1]+r;parent['elev'].append(rawsampler.ground(x,z));parent['renderedElev'].append(sampler.ground(x,z))
   ci=round((x+834500-g['bE'])/g['aE']);ri=round((z-816500+g['bN'])/g['aE']);parent['vegetation'].append(root['vegetation'][ri*root['w']+ci])
assert retained==old['w']*old['h'];builder.validate_patch(parent,root)
pre=LOCAL/'expanded-parent.json';save(pre,parent)
sn='government-xl-next-twenty-current-terrain-v6-20261021';row=next(r for r in take(sn,BASE/sn/'selection.json.gz')['rows']if r['uid']==UID);ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap);pins[str(ap.relative_to(ROOT))]=row['sourceSHA256'];tri=decode_original_world_triangles(ap.read_bytes())
core=shapely.union_all(shapely.polygons(tri[:,:,[0,2]])).buffer(2,join_style=2);outer=core.buffer(8,join_style=2);floor=float(tri[:,:,1].min());domain=[3282.5,-1787.5,3372.5,-1667.5];rect=shapely.box(*domain);assert rect.covers(outer)
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
 for part in [clipped.intersection(core),clipped.intersection(outer).difference(core),clipped.difference(outer)]:
  if part.area<=1e-10:continue
  for f in ([face.copy()]if part.equals(poly)else lift(part,coeff)):
   for v in f:
    weight=max(0.,1-shapely.Point(v[[0,2]]).distance(core)/8);v[1]=min(v[1],v[1]+weight*(floor-v[1]))
   output.append(f);lineage.append(int(i))
faces=np.asarray(output);assert len(faces)<=25000
childcells=[int(domain[0]-bounds[0]),int(domain[1]-bounds[1]),int(domain[2]-bounds[0]),int(domain[3]-bounds[1])]
ps=builder.terrain.fine.DemSampler(parent,rendered=True);seed=np.asarray(grid_surface_faces(ps,rect));child=builder.make_patch(dict(uids=[UID],cells=childcells),parent,seed,[],parent_url=str(pre.relative_to(ROOT/'3d-viewer')) if pre.is_relative_to(ROOT/'3d-viewer') else str(pre.relative_to(ROOT)),parent_sha256=digest(pre.read_bytes()),allow_native_below_clamp=True)
child['nativeMesh']['position']=faces.reshape(-1).tolist();child['nativeMesh']['index']=list(range(len(faces)*3));policy='Derived private terrain floor at immutable original minimum Y, 2m collar and 8m return to actual current rendered planes. No building geometry edits.';child['nativeMesh']['source'].update(policy=policy);child['meta']['source']['policy']=policy
before=geometry_sha(child);error=None
try:
 save(DOC/'numerical-coverage.json',approve_roundoff(child,domain))
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
