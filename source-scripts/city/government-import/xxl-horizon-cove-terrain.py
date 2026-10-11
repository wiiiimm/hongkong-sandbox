"""Build Horizon Cove's bounded original-government terrain patch; no AI or model edits."""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
import native_patch_resolution as patch_resolution
ROOT,HERE=s.ROOT,s.HERE
DOC=s.DOC/'fourth-pass/horizon-cove';LOCAL=s.LOCAL/'fourth-pass-horizon-cove';UID='landsd/283473:0';TOWER='landsd/282761:0'
read,save,h,rel=s.read,s.save,s.h,s.rel

def main():
 original=next(r for r in read(s.BASE/'selection.json.gz')['rows'] if r['modelId']=='B353741083402063C0')
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');world=original['native']['model']['worldBounds'];cells=s.resolution.rectangle_for(world,parent);bounds=s.resolution.extent(cells,parent)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
 assert not any(s.resolution.terrain.overlap(cells,read(ROOT/'3d-viewer'/p['url'])['coarseCells']) for p in manifest['terrainPatches'])
 fragments=[];used=[]
 for source in read(s.DOC/'recovery.json')['sheets']+read(s.DOC/'adjacent-terrain-results.json')['sources']:
  found=[]
  for path in source['terrainPaths']:
   triangles=s.context.triangles(ROOT/path);near=triangles[(triangles[:,:,0].max(1)>=bounds[0])&(triangles[:,:,0].min(1)<=bounds[2])&(triangles[:,:,2].max(1)>=bounds[1])&(triangles[:,:,2].min(1)<=bounds[3])]
   if len(near):found.append(near)
  if found:
   fragments.extend(found);proof=source['source'];folder=s.LOCAL/'sheets'/source['sheet']/'terrain';used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':rel(folder/e['name']),'sha256':e['sha256']} for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]})
 assert fragments
 lo,hi=world;native=np.concatenate(fragments);model=s.glb_triangles(original);projection=shapely.union_all(shapely.polygons(model[:,:,[0,2]]));native_polygons=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(native_polygons)>1e-10;native=native[valid];native_polygons=native_polygons[valid]
 step=5;w=round((bounds[2]-bounds[0])/step)+1;hh=round((bounds[3]-bounds[1])/step)+1;grid=np.array([[bounds[0]+col*step,bounds[1]+row*step] for row in range(hh) for col in range(w)])
 source_heights=s.context.shared.samples(grid,native,shapely.STRtree(native_polygons));rendered=s.resolution.terrain.fine.DemSampler(parent,rendered=True);raw=s.resolution.terrain.fine.DemSampler(parent);parent_heights=np.array([rendered.ground(x,z) for x,z in grid]);raw_heights=np.array([raw.ground(x,z) for x,z in grid])
 core=[lo[0]-1,lo[2]-1,hi[0]+1,hi[2]+1];inside=shapely.covers(projection.buffer(1),shapely.points(grid));alphas=[];heights=[];elev=[];water=[]
 for i,((x,z),source_height,parent_height,raw_height,is_inside) in enumerate(zip(grid,source_heights,parent_heights,raw_heights,inside)):
  alpha=max(0,min(1,min(x-core[0],core[2]-x,z-core[1],core[3]-z)/10)) if np.isfinite(source_height) else 0
  if raw_height<=0 and not is_inside:alpha=0
  height=float(source_height*alpha+parent_height*(1-alpha)) if alpha else float(parent_height);alphas.append(alpha);heights.append(height)
  if raw_height<=0 and not is_inside:elev.append(0);water.append(i)
  else:elev.append(height)
 pg=parent['meta']['georef'];cell=pg['aE'];vegetation=[]
 for x,z in grid:
  col=min(parent['w']-1,max(0,round((x+834500-pg['bE'])/cell)));row=min(parent['h']-1,max(0,round((z-816500+pg['bN'])/cell)));vegetation.append(parent['vegetation'][row*parent['w']+col])
 positions=np.column_stack([grid[:,0],np.asarray(heights),grid[:,1]]);index=[]
 for row in range(hh-1):
  for col in range(w-1):
   q=row*w+col;index.extend([q,q+1,q+w,q+1,q+w+1,q+w])
 source_meta={'provider':'Lands Department/HKSAR','crs':'EPSG:2326','verticalDatum':'HKPD','nativeSources':used,'policy':'Deterministic five-metre samples of the recovered original government TIN in the model core with a ten-metre parent-terrain boundary blend. Source building geometry and elevations remain unchanged.','parentWaterMask':{'preservedGridPoints':len(water),'indexes':water},'sourceSampledGridPoints':int(np.isfinite(source_heights).sum()),'maximumSourceWeight':float(max(alphas))}
 patch={'id':'government-native-283473-0','w':w,'h':hh,'cell':step,'elev':elev,'renderedElev':heights,'vegetation':vegetation,'coarseCells':cells,'meta':{'georef':{'aE':step,'aN':-step,'bE':bounds[0]+834500,'bN':816500-bounds[1],'W':w,'H':hh},'parentTerrain':'city/data/terrain.json','parentSha256':h(ROOT/'3d-viewer/city/data/terrain.json'),'targetUids':[UID,TOWER],'source':source_meta},'nativeMesh':{'position':positions.reshape(-1).tolist(),'index':index,'source':{'verticalDatum':'HKPD','verticalScale':1,'policy':'Five-metre deterministic original-TIN samples with exact parent boundary joins; no AI or building geometry changes.'}}}
 s.resolution.validate_patch(patch,parent);assert len(index)//3<25000
 patch_path=LOCAL/(patch['id']+'.json');save(patch_path,patch);entry={'path':rel(patch_path),'sha256':h(patch_path),'uids':[UID,TOWER],'bounds':bounds,'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[entry])
 region=box(*bounds);live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
  for building in json.loads(raw)['buildings']:
   if Polygon(building['rings'][0],building['rings'][1:]).intersects(region):
    neighbours.append({'building':building,'patchIndexes':[0],'existingNative':building['uid'] in live or bool(building.get('modelGeometry'))});touched=True
  if touched:hashes[rel(path)]=s.digest(raw)
 save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':[UID,TOWER],'patches':[entry]})
 s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
 report=read(DOC/'neighbour-checks.json');save(DOC/'terrain-result.json',{'uid':UID,'cells':cells,'bounds':bounds,'patch':entry,'sourceSheets':[x['sheet'] for x in used],'neighbours':len(neighbours),'blockedBy':report['patches'][0]['blockedBy'],'aiCalls':0,'modelGeometryChanges':0,'publication':False})
 print(json.dumps(read(DOC/'terrain-result.json')))
if __name__=='__main__':main()
