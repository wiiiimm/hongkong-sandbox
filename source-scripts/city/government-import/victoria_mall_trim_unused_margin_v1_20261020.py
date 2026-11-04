"""Remove only the unneeded north terrain margin; complete originals stay covered."""
from pathlib import Path
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-trim-unused-margin-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-victoria-mall-candidate-terrain-v2-20261020';SCOPE=BASE/'government-xl-victoria-mall-current-scope-v2-20261020';ATTR=BASE/'government-xl-victoria-mall-actual-render-attributes-v1-20261020';PAIR=BASE/'government-xl-victoria-three-original-checked-20261009'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,SCOPE,ATTR,PAIR]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
def consume(folder,path):
 assert digest(path.read_bytes())==pins[folder.name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
path=HERE/'local'/SRC.name/'candidate-terrain.json';old=consume(SRC,path);scope=consume(SCOPE,SCOPE/'scope.json');capture=consume(ATTR,ATTR/'attributes.json.gz');sources=consume(PAIR,PAIR/'support-inputs.json')['sources']
parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=consume(SCOPE,parentpath);builder=module('victoria_trim_builder',HERE/'resolve-pass-indexed-parent-clipping.py')
assert old['coarseCells']==[504,424,507,428];cells=[504,424,507,427];bounds=builder.extent(cells,parent);assert bounds==[812.5,-1787.5,1022.5,-1577.5]
allbounds=[]
for r in sources:
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset);p=packed_world_bounds(asset.read_bytes());v=next(x for x in capture['rows']if x['uid']==r['uid']);assert v['sourceSHA256']==p['sourceSHA256']
 modes=[p['originalWholeSourceBounds'],v['completeLiteralWorldBounds'],v['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],v['completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
 for lo,hi in modes:assert bounds[0]<lo[0]<=hi[0]<bounds[2] and bounds[1]<lo[2]<=hi[2]<bounds[3],('Complete original outside candidate',r['uid'],lo,hi)
 allbounds.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],completeFourWorldBounds=modes,allPositionVerticesAccounted=p['allOriginalPositionVerticesAccounted']))
face=repair._faces(old);out=[];retained=[];cut=[];removed=[]
for i,t in enumerate(face):
 if np.all(t[:,2]<=bounds[3]):out.append(t);retained.append(i);continue
 if np.all(t[:,2]>bounds[3]):removed.append(i);continue
 cut.append(i);polygon=builder.exact.rect(list(t),bounds)
 for j in range(1,len(polygon)-1):out.append(np.array([polygon[0],polygon[j],polygon[j+1]]))
assert all(face[i,:,2].min()>max(b['completeFourWorldBounds'][m][1][2]for b in allbounds for m in range(4))for i in removed)
# Cut facets may extend south of the clipping line. Their retained sub-polygons
# remain on their exact original planes; verify no source-domain facet is cut.
source_extent=shapely.union_all([shapely.box(lo[0],lo[2],hi[0],hi[2])for b in allbounds for lo,hi in b['completeFourWorldBounds']])
for i in cut:assert shapely.Polygon(face[i][:,[0,2]]).intersection(source_extent).area==0
patch=copy.deepcopy(old);patch['id']='government-native-victoria-trimmed-margin-v1-20261020';patch['coarseCells']=cells
h=round((bounds[3]-bounds[1])/old['cell'])+1;assert h==43
for name in ['elev','renderedElev','vegetation']:patch[name]=patch[name][:h*patch['w']]
patch['h']=h;patch['meta']['georef']['H']=h
tri=np.asarray(out);patch['nativeMesh']['position']=tri.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(len(tri)*3));patch['nativeMesh'].pop('sourceOverlap',None)
patch['nativeMesh']['source']['unusedNorthMarginRemoval']=dict(originalCandidateSHA256=digest(path.read_bytes()),priorCells=old['coarseCells'],cells=cells,policy='Clip only unused north terrain margin on a territory parent-cell boundary. Complete four-mode source bounds stay covered. No building bytes, placement or original protected ground changed.')
newpath=DOC/'candidate-terrain.json';save(newpath,patch);failure=None
try:builder.validate_patch(patch,parent)
except Exception as e:failure=dict(type=type(e).__name__,message=str(e))
inventory=consume(SCOPE,SCOPE/'complete-bounds.json.gz');required=[r['uid']for r in inventory['rows']if not closed_disjoint(r['completeFourWorldBounds'],bounds)]
manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=consume(SCOPE,manifestpath);overlaps=[]
for e in manifest['terrainPatches']:
 p=ROOT/'3d-viewer'/e['url'];d=read(p);b=repair._patch_bounds(d)
 if shapely.box(*bounds).intersection(shapely.box(*b)).area>1e-8:overlaps.append(dict(url=e['url'],bounds=b));refs.append(p)
result=dict(uids=[r['uid']for r in sources],sourceGeometryChanges=0,installationApproved=False,priorFaces=len(face),retainedFaces=len(retained),cutFaces=len(cut),removedFaces=len(removed),newFaces=len(tri),bounds=bounds,sourceBounds=allbounds,requiredNativeUids=required,installedTerrainOverlaps=overlaps,validatorFailure=failure,allCurrentActors=len(inventory['rows']),minimumNorthSourceClearanceM=min(bounds[3]-hi[2]for b in allbounds for lo,hi in b['completeFourWorldBounds']))
save(DOC/'face-account.json',dict(retained=retained,cut=cut,removed=removed));save(DOC/'summary.json',result)
refs.extend([HERE/'resolve-pass-indexed-parent-clipping.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'heritage_saved_native_bounds_binding_v1_20261014.py'])
for p in refs:
 for mapping in pins.values():
  if str(p.relative_to(ROOT))in mapping:assert digest(p.read_bytes())==mapping[str(p.relative_to(ROOT))]
module('victoria_trim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remove-unused-terrain-margin-with-complete-source-coverage',list(dict.fromkeys(refs)),result)
print({k:result[k]for k in ['newFaces','cutFaces','validatorFailure','minimumNorthSourceClearanceM','requiredNativeUids','installedTerrainOverlaps']},flush=True)
