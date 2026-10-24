"""Compare exact source terrain with retained parent terrain; never invent elevations."""
import importlib.util,shutil
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
spec=importlib.util.spec_from_file_location('continuation',HERE/'sol-continuation-20261003.py');continuation=importlib.util.module_from_spec(spec);spec.loader.exec_module(continuation)
module=continuation.module
final=module('continuation_final','xl-final-script-pass.py');patches=module('continuation_patches','native_patch_resolution.py')
BASE,DOC,LOCAL=continuation.BASE,continuation.DOC,continuation.LOCAL
SITES=[('yoho','landsd/273672:0','yoho-mall-ii-terrain-diagnostic-20260927'),('citywalk','landsd/134332:0','citywalk-terrain-diagnostic-20260925'),('festival','landsd/91827:0','festival-pair-rescue-diagnostic-20261002')]
def run():
 continuation.owns();reports=[]
 parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path);sampler=final.s.resolution.terrain.fine.DemSampler(parent,rendered=True);sampler.parent_height_floor=1.2
 for name,uid,old_name in SITES:
  old=BASE/old_name;row=next(r for r in read(old/'selection.json.gz')['rows'] if r['uid']==uid);entry=row['candidate']['entry'];assert digest(Path(row['candidate']['path']).read_bytes())==entry['sha256']
  final.s.LOCAL=LOCAL/name;asset=final.s.LOCAL/'assets'/(entry['sha256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset)
  model=final.s.glb_triangles({**row['native']['model'],'sourceSHA256':entry['sha256'],'modelId':entry['modelId'],'native':row['native']})
  result=read(old/'result.json');patch_path=ROOT/result['patchPath'];assert digest(patch_path.read_bytes())==result['patchSHA256'];patch=read(patch_path);native=patches._faces(patch)
  lo,hi=model.min(axis=(0,1)),model.max(axis=(0,1));extent=shapely.box(lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2);original=np.asarray(patches.grid_surface_faces(sampler,extent))
  points=np.concatenate([model,model.mean(axis=1)[:,None,:]],axis=1);gaps=[]
  for terrain in (original,native):
   polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
   heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain[valid],shapely.STRtree(polys[valid])).reshape(-1,4);assert np.isfinite(heights).all();gaps.append(points[:,:,1]-heights)
  cross=np.cross(model[:,1]-model[:,0],model[:,2]-model[:,0]);up=cross[:,1]>.25*np.linalg.norm(cross,axis=1);old_buried,new_buried=[(g<-.5).all(axis=1) for g in gaps];unavoidable=(np.maximum(*gaps)<-.5).all(axis=1)
  rescuable=new_buried&~old_buried&up
  partial_rescue=(gaps[1]<-.5).any(axis=1)&(gaps[0]>=-.5).all(axis=1)
  if name=='citywalk':rescuable=partial_rescue
  if name=='festival':rescuable=(gaps[1]<-.5).any(axis=1)
  building=row['source']['building'];foot=shapely.Polygon(building['rings'][0],building['rings'][1:])
  report={'uid':uid,'sourceSHA256':entry['sha256'],'parent':continuation.ref(parent_path),'nativePatch':continuation.ref(patch_path),'nativeBuriedUpwardTriangles':int((new_buried&up).sum()),'parentBuriedUpwardTriangles':int((old_buried&up).sum()),'buriedUpwardEvenWithPointwiseLowerSurface':int((unavoidable&up).sum()),'minimumParentGapM':float(gaps[0].min()),'minimumNativeGapM':float(gaps[1].min()),'samplesBuriedUnderBothSurfaces':int((np.maximum(*gaps)<-.5).sum()),'rescuableByParent':int(rescuable.sum()),'failedSourceFaces':[{'index':int(i),'vertices':model[i].tolist(),'parentGapsM':gaps[0][i].tolist(),'nativeGapsM':gaps[1][i].tolist(),'parentRescuable':bool(rescuable[i])} for i in np.flatnonzero(new_buried&up)],'publication':False,'aiCalls':0,'modelGeometryChanges':0}
  if rescuable.any():
   rescue=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in model[rescuable]]).buffer(.01,join_style='mitre');bounds=patches._patch_bounds(patch)
   lower_proof=None
   if name=='festival':rescue,lower_proof=patches.lower_parent_projection(patch,bounds,rescue,sampler)
   repair=patches.preserve_parent_under_projection(patch,bounds,rescue,sampler);candidate=LOCAL/name/'diagnostic-parent-rescue.json';save(candidate,patch)
   proof=final.foundation_context(model,patches._faces(patch),foot)
   terrain=patches._faces(patch);polys=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
   heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),terrain[valid],shapely.STRtree(polys[valid])).reshape(-1,4);remaining=points[:,:,1]-heights;face,sample=np.unravel_index(np.argmin(remaining),remaining.shape);proof['worstSample']={'sourceFace':int(face),'sampleIndex':int(sample),'position':points[face,sample].tolist(),'parentGapM':float(gaps[0][face,sample]),'nativeGapM':float(gaps[1][face,sample]),'candidateGapM':float(remaining[face,sample])}
   report['diagnosticParentRescue']={'preservation':repair,'lowerParentSelection':lower_proof,'candidatePatch':continuation.ref(candidate),'foundation':proof,'strictFoundationAccepted':proof['completeTerrainTriangles']==proof['triangles'] and proof['fullyBuriedUpwardTriangles']==0 and proof['fullyBuriedAreaFraction']<=.001}
  save(DOC/(name+'-terrain-options.json'),report);reports.append(report)
  print({k:report[k] for k in ('uid','nativeBuriedUpwardTriangles','buriedUpwardEvenWithPointwiseLowerSurface','rescuableByParent')},flush=True)
 save(DOC/'terrain-options.json',{'rows':reports,'qualification':'Pointwise lower surface is a diagnostic bound only. Derived candidates retain unchanged parent faces only under exact rescuable source-face projections; all runtime, coverage, neighbour and browser gates remain required.','aiCalls':0,'modelGeometryChanges':0,'publication':False})
from pathlib import Path
if __name__=='__main__':run()
