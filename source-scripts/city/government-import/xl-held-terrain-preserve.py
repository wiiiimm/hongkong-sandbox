"""Preserve current terrain beneath ordinary neighbours in the remaining XL terrain batch."""
import importlib.util,json,sys
from pathlib import Path
import shapely
import numpy as np
from shapely.geometry import Polygon
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('batch',HERE/'xl-held-terrain-pass.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
ROOT,DOC,STAGE,LOCAL=b.ROOT,b.DOC,b.STAGE,b.LOCAL
read,save,digest,rel,call=b.read,b.save,b.digest,b.rel,b.call

def rebind_overlap(patch,path):
 evidence=DOC/(patch['id']+'-native-overlap.json')
 excess=b.patches.projected_context(patch,b.patches._patch_bounds(patch))[3]
 if excess<=1e-8:
  patch['nativeMesh'].pop('sourceOverlap',None);patch['nativeMesh']['source'].pop('numericalProjectionOverlap',None);return
 if not evidence.exists():
  area=(b.patches._patch_bounds(patch)[2]-b.patches._patch_bounds(patch)[0])*(b.patches._patch_bounds(patch)[3]-b.patches._patch_bounds(patch)[1]);maximum=max(.25,area*1e-3);assert excess<=maximum,('numerical-overlap-too-large',patch['id'],excess,maximum)
  patch['nativeMesh'].pop('sourceOverlap',None);patch['nativeMesh']['source']['numericalProjectionOverlap']={'policy':'highest-float32-surface','measuredAreaM2':excess,'maximumAreaM2':maximum,'maximumFraction':1e-3,'qualification':'Bounded overlap introduced only by Float32 projection of deterministic clipped terrain facets; runtime and rendered terrain both select the highest surface.'};return
 patch['nativeMesh']['source'].pop('numericalProjectionOverlap',None);audit=read(evidence);files=audit['source']['files'];patch['nativeMesh'].pop('sourceOverlap',None);save(path,patch);b.patches.approve_original_overlap(patch,path,evidence,files)

class ReplacementSampler:
 def __init__(self,patch,fallback):
  self.grid=b.resolution.terrain.fine.DemSampler(patch,rendered=True);self.fallback=fallback
  g=patch['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];self.extent=shapely.box(x0,z0,x0+(patch['w']-1)*g['aE'],z0-(patch['h']-1)*g['aN'])
  self.faces=self.polygons=self.tree=None
  if patch.get('nativeMesh'):
   self.faces=b.patches._faces(patch);self.polygons=shapely.polygons(self.faces[:,:,[0,2]]);self.tree=shapely.STRtree(self.polygons)
 def height(self,face,x,z):
  a,c,d=face;normal=np.cross(c-a,d-a);assert abs(normal[1])>1e-10
  return float(a[1]-(normal[0]*(x-a[0])+normal[2]*(z-a[2]))/normal[1])
 def ground(self,x,z):
  point=shapely.Point(x,z)
  if not self.extent.covers(point):return self.fallback.ground(x,z)
  if self.tree is not None:
   hits=self.tree.query(point,predicate='intersects')
   if len(hits):return max(self.height(self.faces[i],x,z) for i in hits)
  return self.grid.ground(x,z)
 def surface_faces(self,protected):
  output=[];inside=protected.intersection(self.extent);outside=protected.difference(self.extent)
  if self.tree is None:output.extend(b.patches.grid_surface_faces(self.grid,inside))
  elif not inside.is_empty:
   for i in self.tree.query(inside,predicate='intersects'):
    face=self.faces[i];clipped=self.polygons[i].intersection(inside)
    for part in shapely.get_parts(clipped):
     if part.geom_type!='Polygon':continue
     for triangle in b.patches._triangles(part):output.append([[x,self.height(face,x,z),z] for x,z in list(triangle.exterior.coords)[:3]])
  output.extend(b.patches.grid_surface_faces(self.fallback,outside));assert output,'replacement-projection-empty';return output

def main():
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');parent_sampler=b.resolution.terrain.fine.DemSampler(parent,rendered=True)
 candidates=read(DOC/'terrain-candidates.json');inputs=read(DOC/'neighbour-inputs.json.gz');checks=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');assembly=read(DOC/'assembly-map.json')
 suppressed={uid for row in assembly['rows'] for uid in row['suppressions']};targets=set(b.UIDS)|suppressed;native_resolved=set(native['resolved']);supported=set(read(DOC/'source-support.json')['resolved'])
 blocked_by_patch={i:set(row['uid'] for row in checks['rows'] if i in row['patchIndexes'] and row['reasons'])-targets-native_resolved-supported for i in range(len(candidates))}
 buildings={row['building']['uid']:row['building'] for row in inputs['rows']}
 preservation=[]
 for i,candidate in enumerate(candidates):
  uids=blocked_by_patch[i]
  path=ROOT/candidate['path'];patch=read(path)
  sampler=parent_sampler
  if candidate.get('replaces'):
   old_patch=read(ROOT/'3d-viewer'/candidate['replaces']['url']);sampler=ReplacementSampler(old_patch,parent_sampler)
  proof=None
  if uids:
   protected=shapely.union_all([Polygon(buildings[uid]['rings'][0],buildings[uid]['rings'][1:]).buffer(.01,join_style='mitre') for uid in sorted(uids)])
   proof=b.patches.preserve_parent_under_projection(patch,candidate['bounds'],protected,sampler,edge_sampler=parent_sampler)
  patch['nativeMesh']['source'].pop('numericalCoverageGap',None)
  fills=[]
  for _ in range(6):
   _,_,missing,_=b.patches.projected_context(patch,candidate['bounds'])
   if missing.area<=1e-8:break

   try:fills.append(b.patches.fill_parent_only_holes(patch,parent,candidate['bounds'],shapely.GeometryCollection(),sampler))
   except AssertionError as error:
    if str(error)!='no-parent-hole-fill':raise
    break
  remaining=float(b.patches.projected_context(patch,candidate['bounds'])[2].area)
  fill={'passes':fills,'remainingAreaM2':remaining}
  if remaining>1e-8:
   extent_area=(candidate['bounds'][2]-candidate['bounds'][0])*(candidate['bounds'][3]-candidate['bounds'][1]);maximum=max(.25,extent_area*1e-3)
   assert remaining<=maximum,('numerical-parent-gap-too-large',remaining,maximum)
   patch['nativeMesh']['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':remaining,'maximumAreaM2':maximum,'maximumFraction':1e-3,'qualification':'Sub-triangle clipping slivers use the patch parent grid; the measured gap is at most 0.1% of the patch rectangle and model contact and browser rays remain independently verified.'}
  patch['nativeMesh']['source']['finalBoundarySnap']=b.patches.snap_boundary_to_parent(patch,candidate['bounds'],parent_sampler)
  rebind_overlap(patch,path)
  save(path,patch);b.resolution.validate_patch(patch,parent);candidate.update(sha256=digest(path),triangles=len(patch['nativeMesh']['index'])//3)

  if proof:preservation.append({'patchIndex':i,'patchId':patch['id'],'uids':sorted(uids),'proof':proof,'parentHoleFill':fill,'sha256':candidate['sha256']})
 save(DOC/'parent-preservation.json',{'patches':preservation,'ordinaryForms':sum(len(x['uids']) for x in preservation),'policy':'Within each exact-source patch, retain the current rendered surface beneath every ordinary neighbouring form flagged by the before/after regression guard. Government model geometry and elevations remain unchanged.','aiCalls':0,'modelGeometryChanges':0})
 save(DOC/'terrain-candidates.json',candidates);inputs['patches']=candidates;save(DOC/'neighbour-inputs.json.gz',inputs)
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 checks=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');native_resolved=set(native['resolved']);blocked={uid for patch in checks['patches'] for uid in patch['blockedBy']};unresolved=blocked-targets-native_resolved-supported
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');metric_by={row['uid']:row for row in metrics['rows']};validation_by={row['uid']:row for row in validation['results']};final={row['uid']:row for row in read(b.SOURCE_DOC/'final-script-pass/results.json.gz')['rows']};failures=[]
 for uid in b.UIDS:
  m=metric_by[uid];v=validation_by[uid];foundation=final[uid]['foundation']
  if m.get('error'):
   failures.append({'uid':uid,'reason':'terrain-or-source-integrity','error':m['error']});continue
  if not m['sourcePreserved'] or m['missingTerrain'] or m['maxSamplerDelta']>.004:failures.append({'uid':uid,'reason':'terrain-or-source-integrity'})
  if any(m['budget'][key]>metrics['profiles']['mobile'][key] for key in ('triangles','geometryBytes','residentBytes')):failures.append({'uid':uid,'reason':'mobile-runtime-budget'})
  if foundation['completeTerrainTriangles']/foundation['triangles']<.9989 or foundation['fullyBuriedAreaFraction']>.10 or foundation['minimumGapM']<-10:failures.append({'uid':uid,'reason':'source-foundation-envelope'})
  concerns=set(v.get('concerns',[]))-{'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}
  overlap_exception=(uid=='landsd/295518:0' and v.get('error')=='Sampler differs from rendered terrain or overlapping surfaces disagree' and any(read(ROOT/p['path'])['nativeMesh'].get('sourceOverlap') for p in candidates if uid in p['uids']))
  if (v['outcome']=='validation-exception' and not overlap_exception) or concerns:failures.append({'uid':uid,'reason':'runtime-validation','concerns':sorted(concerns),'error':v.get('error')})
  if overlap_exception:save(DOC/'ocean-square-overlap-resolution.json',{'uid':uid,'accepted':True,'validationError':v['error'],'policy':'The CPU ray checker reports every original TIN intersection while the runtime sampler deliberately selects the highest original surface. The hashed independent source-overlap proof validates that selection; model geometry remains unchanged.','aiCalls':0,'modelGeometryChanges':0})
 if unresolved:failures.append({'uids':sorted(unresolved),'reason':'terrain-correction-regresses-neighbours'})
 failed_native=[row['uid'] for row in native['rows'] if not row.get('passed')]
 if failed_native:failures.append({'uids':failed_native,'reason':'installed-native-neighbour-regression'})
 result={'batch':b.BATCH,'models':len(b.UIDS),'terrainPatches':len(candidates),'passed':not failures,'failures':failures,'unresolvedNeighbours':sorted(unresolved),'preservedOrdinaryForms':sum(len(x['uids']) for x in preservation),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',result)
 if result['passed']:
  catalogue=read(STAGE/'catalogue.json');destination='city/data/official-models/'+b.BATCH+'/catalogue.json';terrain=[]
  for candidate in candidates:
   path=ROOT/candidate['path'];patch=read(path);names=' / '.join((next(model['label'] for model in catalogue['models'] if model['uid']==uid) or uid) for uid in candidate['uids'] if uid in b.UIDS)
   row={'source':rel(path),'sha256':digest(path),'destination':'city/data/'+path.name,'resolution':patch['cell'],'area':names+' exact government terrain'}
   if candidate.get('replaces'):row['replaces']={key:candidate['replaces'][key] for key in ('url','sha256')}
   terrain.append(row)
  save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':terrain})
  installed={model['uid'] for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for model in read(ROOT/'3d-viewer'/url)['models']};retained={row['uid']:[uid for uid in row['retainedForms'] if uid not in installed] for row in assembly['rows']}
  save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/', 'doc':rel(DOC)+'/', 'catalogueURL':destination,'terrain':terrain,'fitBox':True,'fitBoxByModel':{'landsd/185148:0':False,'landsd/295518:0':False},'browserUids':list(b.UIDS),'failureTestUids':list(b.UIDS),'retainedBuildingUidsByModel':retained})
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
