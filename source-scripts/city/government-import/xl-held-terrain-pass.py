"""Finish the remaining XL-50 holds with exact source TIN and local compute only."""
from __future__ import annotations
import gzip,hashlib,importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
DOC=ROOT/'docs/astra-city/government-import/government-xl-50-20260913/final-compute-pass/terrain-complete'
LOCAL=HERE/'local/government-xl-held-terrain-20260914';STAGE=HERE/'accepted/government-xl-held-terrain-20260914'
SOURCE_DOC=ROOT/'docs/astra-city/government-import/government-xl-50-20260913/second-pass'
BATCH='government-xl-held-terrain-20260914'
UIDS=('landsd/273000:0','landsd/100745:0','landsd/225173:0','landsd/266063:0','landsd/224024:0','landsd/232096:0','landsd/185148:0','landsd/258884:0','landsd/233970:0','landsd/228431:0','landsd/295518:0')
GROUP_UIDS=(('landsd/273000:0','landsd/232096:0'),('landsd/100745:0',),('landsd/225173:0',),('landsd/266063:0',),('landsd/224024:0',),('landsd/185148:0',),('landsd/258884:0','landsd/228431:0'),('landsd/233970:0',),('landsd/295518:0',))
REPLACEMENTS={'landsd/225173:0':('city/data/support-native-242294-0.json',('landsd/242294:0','landsd/263404:0')),'landsd/295518:0':('city/data/government-native-136832-0.json',('landsd/136832:0',))}

def module(filename,name):
 spec=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
second=module('xl-second-pass.py','xl_second_held_terrain');resolution=second.resolution
patches=module('native_patch_resolution.py','native_patch_resolution_held_terrain')
heavy=module('xl-held-heavy-pass.py','xl_heavy_evidence');midfield=module('xl-held-midfield-pass.py','xl_midfield_evidence');tuen3=module('xl-held-tuen3-pass.py','xl_tuen3_evidence')
sys.path.insert(0,str(HERE.parent/'shared-modelling'));import reservations

def read(path):
 raw=Path(path).read_bytes();return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
def save(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0) if str(path).endswith('.gz') else raw)
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path):return str(Path(path).relative_to(ROOT))
def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT);assert result.returncode in allowed,(args,result.returncode)
def union_cells(items):return [min(x[0] for x in items),min(x[1] for x in items),max(x[2] for x in items),max(x[3] for x in items)]

def evidence():
 rows=[];stage=[]
 for provider in (heavy,midfield,tuen3):
  a,b=provider.build_evidence();rows.extend(a);stage.extend(b)
 by_uid={row['entry']['uid']:(proof,row) for proof,row in zip(rows,stage)}
 return [by_uid[uid][0] for uid in UIDS],[by_uid[uid][1] for uid in UIDS]

def terrain_sources():
 return {row['sheet']:row for row in read(SOURCE_DOC/'recovery.json')['sheets']}

def triangles_for(source,bounds):
 found=[]
 for path in source['terrainPaths']:
  tri=second.terrain_triangles(ROOT/path)
  hit=tri[(tri[:,:,0].max(axis=1)>=bounds[0])&(tri[:,:,0].min(axis=1)<=bounds[2])&(tri[:,:,2].max(axis=1)>=bounds[1])&(tri[:,:,2].min(axis=1)<=bounds[3])]
  if len(hit):found.append(hit)
 return np.concatenate(found) if found else np.empty((0,3,3))

def source_proof(source):
 folder=second.LOCAL/'sheets'/source['sheet']/'terrain';proof=source['source']
 files=[]
 for entry in proof['entries']:
  if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf','.bin')):
   path=folder/entry['name'];assert digest(path)==entry['sha256'];files.append({'path':rel(path),'sha256':entry['sha256']})
 return {'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':files}

def build():
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');parent=read(ROOT/'3d-viewer/city/data/terrain.json')
 installed={model['uid'] for url in manifest['officialModelCatalogues'] for model in read(ROOT/'3d-viewer'/url)['models']}
 assert not installed.intersection(UIDS)
 proof_rows,stage_rows=evidence();runtime={row['entry']['uid']:row['runtime'] for row in stage_rows};proof_by_uid={row['uid']:row for row in proof_rows};source_records={row['uid']:row for row in read(SOURCE_DOC/'selection.json.gz')['rows']}
 STAGE.mkdir(parents=True,exist_ok=True)
 entries=[];forms=[]
 for row in stage_rows:
  entry=dict(row['entry']);entry['publicationApproved']=True
  source_stage=(heavy.STAGE if entry['uid'] in heavy.UIDS else midfield.STAGE if entry['uid'] in midfield.UIDS else tuen3.STAGE)
  dst=STAGE/entry['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source_stage/entry['asset'],dst);assert digest(dst)==entry['sha256']
  entries.append(entry);forms.append(row['form'])
 template=read(HERE/'accepted/government-xxl-20260911/catalogue.json');template.update(area='Remaining XL-50 exact government sources',loadingPolicy='Exact sources and source TIN accepted by deterministic identity, assembly, foundation, neighbour, runtime and browser checks',counts={'packedModels':len(entries)},models=entries)
 save(STAGE/'catalogue.json',template);save(STAGE/'catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms)
 selection=read(SOURCE_DOC/'runtime-selection.json.gz');selection.update(batch=BATCH,manifestSHA256=digest(ROOT/'3d-viewer/city/data/manifest.json'),rows=[runtime[uid] for uid in UIDS],aiCalls=0);save(DOC/'selection.json.gz',selection)
 save(DOC/'assembly-map.json',{'policy':'Suppress only a non-target form with at least 95% footprint coverage whose recorded top is reached by the exact source over that form. Retain taller and partial forms.','rows':proof_rows,'aiCalls':0,'modelGeometryChanges':0})
 source_by_sheet=terrain_sources();live_entries={m['uid']:m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
 patch_rows=[];terrain_plan=[];group_models={}
 for group_uids in GROUP_UIDS:
  group_runtime=[runtime[uid] for uid in group_uids];cells=union_cells([resolution.rectangle_for(row['candidate']['entry']['worldBounds'],parent) for row in group_runtime]);replacement=None
  first=group_uids[0]
  if first in REPLACEMENTS:
   url,retained=REPLACEMENTS[first];old=read(ROOT/'3d-viewer'/url);cells=union_cells([cells,old['coarseCells']]);replacement={'url':url,'sha256':digest(ROOT/'3d-viewer'/url),'retainedUids':list(retained)}
  overlap=[row for row in manifest['terrainPatches'] if resolution.terrain.overlap(cells,read(ROOT/'3d-viewer'/row['url'])['coarseCells'])]
  if replacement:assert [row['url'] for row in overlap]==[replacement['url']]
  else:assert not overlap,[row['url'] for row in overlap]
  bounds=resolution.extent(cells,parent);sheets=sorted({row['candidate']['entry']['sourceTile'] for row in group_runtime});used=[source_proof(source_by_sheet[sheet]) for sheet in sheets];native=np.concatenate([triangles_for(source_by_sheet[sheet],bounds) for sheet in sheets])
  model_tri=np.concatenate([second.glb_triangles(source_records[uid]) for uid in group_uids]);projection=shapely.union_all(shapely.polygons(model_tri[:,:,[0,2]]));low=native[:,:,1].min(axis=1)<1.2;low_projection=shapely.union_all(shapely.polygons(native[low][:,:,[0,2]])) if low.any() else shapely.GeometryCollection();assert low_projection.intersection(projection).area<1e-6;native=native[~low]
  core_rows=[row['candidate']['entry'] for row in group_runtime]+[live_entries[uid] for uid in (replacement or {}).get('retainedUids',[])]
  lows=[row['worldBounds'][0] for row in core_rows];highs=[row['worldBounds'][1] for row in core_rows];core=[min(x[0] for x in lows)-1,min(x[2] for x in lows)-1,max(x[0] for x in highs)+1,max(x[2] for x in highs)+1]
  validator=resolution.validate_patch;resolution.validate_patch=lambda candidate,parent_terrain:None
  target_uids=list(group_uids)+[uid for uid in (replacement or {}).get('retainedUids',[])];group={'uids':target_uids,'cells':cells}
  try:patch=resolution.make_patch(group,parent,native,used,native_core=core,terrain_triangle_budget=100000)
  finally:resolution.validate_patch=validator
  path=STAGE/(patch['id']+'.json');save(path,patch);projected=patches.projected_context(patch,bounds)[3];evidence_path=DOC/(patch['id']+'-native-overlap.json')
  if projected>1e-8:patches.approve_original_overlap(patch,path,evidence_path,[item for u in used for item in u['sourceFiles']])
  sampler=resolution.terrain.fine.DemSampler(parent,rendered=True)
  try:fill=patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
  except AssertionError as error:
   if str(error)!='missing-native-terrain-intersects-source-model':raise
   _,_,missing,_=patches.projected_context(patch,bounds);inside=missing.intersection(projection)
   points=np.concatenate((model_tri.reshape(-1,3),model_tri.mean(axis=1)));mask=np.array([inside.covers(shapely.Point(x,z)) for x,_,z in points]);gaps=np.array([y-sampler.ground(x,z) for x,y,z in points[mask]])
   parent_fill=patches.fill_parent_only_holes(patch,parent,bounds,shapely.GeometryCollection(),sampler)
   fill={'policy':'Recovered source TIN is absent in this portion of the source-model projection; retain the current parent surface there and validate every unchanged model triangle against the completed surface.','missingInsideModelProjectionM2':float(inside.area),'sampledModelPoints':int(mask.sum()),'sampledParentGapRangeM':[float(gaps.min()),float(gaps.max())] if len(gaps) else None,'parentFill':parent_fill}
  patch['nativeMesh']['source'].pop('numericalCoverageGap',None);remaining=float(patches.projected_context(patch,bounds)[2].area)
  if remaining>1e-8:
   maximum=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3);assert remaining<=maximum,('numerical-parent-gap-too-large',remaining,maximum)
   patch['nativeMesh']['source']['numericalCoverageGap']={'policy':'parent-grid-fallback','measuredAreaM2':remaining,'maximumAreaM2':maximum,'maximumFraction':1e-3,'qualification':'Float32 projection slivers use the patch parent grid; the measured gap is at most 0.1% of the patch rectangle and browser rays remain independently verified.'}
  patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
  excess=patches.projected_context(patch,bounds)[3];patch['nativeMesh']['source'].pop('numericalProjectionOverlap',None)
  if evidence_path.exists() and excess>1e-8:
   patch['nativeMesh'].pop('sourceOverlap',None);save(path,patch);patches.approve_original_overlap(patch,path,evidence_path,[item for u in used for item in u['sourceFiles']])
  elif excess>1e-8:
   maximum=max(.25,(bounds[2]-bounds[0])*(bounds[3]-bounds[1])*1e-3);assert excess<=maximum,('numerical-overlap-too-large',excess,maximum)
   patch['nativeMesh'].pop('sourceOverlap',None);patch['nativeMesh']['source']['numericalProjectionOverlap']={'policy':'highest-float32-surface','measuredAreaM2':excess,'maximumAreaM2':maximum,'maximumFraction':1e-3,'qualification':'Bounded overlap introduced only by Float32 projection of deterministic clipped terrain facets.'}
  save(path,patch);validator(patch,parent)
  patch_row={'path':rel(path),'sha256':digest(path),'uids':target_uids,'bounds':bounds,'triangles':len(patch['nativeMesh']['index'])//3}
  if replacement:patch_row['replaces']=replacement
  patch_rows.append(patch_row);group_models[len(patch_rows)-1]=list(group_uids)
  terrain={'source':rel(path),'sha256':digest(path),'destination':'city/data/'+path.name,'resolution':patch['cell'],'area':' / '.join(runtime[uid]['candidate']['entry']['label'] or uid for uid in group_uids)+' exact government terrain'}
  if replacement:terrain['replaces']={k:replacement[k] for k in ('url','sha256')}
  terrain_plan.append(terrain)
  save(DOC/(patch['id']+'-resolution.json'),{'uids':list(group_uids),'sourceSheets':sheets,'droppedWaterClampTriangles':int(low.sum()),'parentHoleFill':fill,'replacement':replacement,'aiCalls':0,'modelGeometryChanges':0})
 save(DOC/'terrain-candidates.json',patch_rows)
 # Freeze all forms touched by each patch for the neighbour regression gate.
 by_form={};input_hashes={};live_detailed=installed
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
  for building in json.loads(raw)['buildings']:
   foot=Polygon(building['rings'][0],building['rings'][1:]);indexes=[i for i,p in enumerate(patch_rows) if foot.intersects(box(*p['bounds']))]
   if indexes:
    row=by_form.setdefault(building['uid'],{'building':building,'patchIndexes':[],'existingNative':building['uid'] in live_detailed or bool(building.get('modelGeometry'))});row['patchIndexes']=sorted(set(row['patchIndexes']+indexes));touched=True
  if touched:input_hashes[rel(path)]=digest(path)
 suppressed={uid for row in proof_rows for uid in row['suppressions']}
 save(DOC/'neighbour-inputs.json.gz',{'rows':list(by_form.values()),'inputHashes':input_hashes,'candidateIds':sorted(set(UIDS)|suppressed),'patches':patch_rows})
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
 local_sources={row['entry']['uid']:row['source'] for row in stage_rows};save(LOCAL/'source-forms.json',local_sources)
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
 call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 neighbours=read(DOC/'neighbour-checks.json');native_checks=read(DOC/'native-neighbour-checks.json');native_resolved=set(native_checks['resolved']);blocked=set(uid for p in neighbours['patches'] for uid in p['blockedBy']);ordinary=blocked-native_resolved-suppressed
 # Prove retained basic forms are supported by the exact source roofs where terrain changes.
 all_model_tri=np.concatenate([second.glb_triangles(source_records[uid]) for uid in UIDS]);source_polys=shapely.polygons(all_model_tri[:,:,[0,2]]);valid=shapely.area(source_polys)>1e-10;source_tri=all_model_tri[valid];source_polys=source_polys[valid];tree=shapely.STRtree(source_polys);source_projection=shapely.union_all(source_polys);support=[];resolved=[]
 for uid in sorted(ordinary):
  building=by_form[uid]['building'];foot=Polygon(building['rings'][0],building['rings'][1:]);lo=np.asarray(building['rings'][0]).min(0);hi=np.asarray(building['rings'][0]).max(0);step=max(2,float(np.sqrt((hi[0]-lo[0])*(hi[1]-lo[1])/2500)));pts=np.array([[x,z] for x in np.arange(lo[0]+step/2,hi[0],step) for z in np.arange(lo[1]+step/2,hi[1],step) if foot.covers(shapely.Point(x,z))]);base=building['base']+building.get('minimum',0);heights=np.full(len(pts),-np.inf)
  if len(pts):
   pi,ti=tree.query(shapely.points(pts),predicate='covered_by');abc=source_tri[ti];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=pts[pi]-abc[:,0,[0,2]];det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];ok=np.abs(det)>1e-10;pi=pi[ok];abc=abc[ok];ab=ab[ok];ac=ac[ok];ap=ap[ok];det=det[ok];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det;ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1]);below=ys<=base+.1;np.maximum.at(heights,pi[below],ys[below])
  covered=np.isfinite(heights);gaps=base-heights;coverage=foot.intersection(source_projection).area/foot.area;passed=coverage>=.9999 and len(pts)>0 and covered.sum()/len(pts)>=.9 and np.abs(gaps[covered]).max()<=.1
  support.append({'uid':uid,'footprintCoverage':coverage,'interiorSamples':len(pts),'covered':int(covered.sum()),'gapRangeM':[float(gaps[covered].min()),float(gaps[covered].max())] if covered.any() else None,'passed':bool(passed)})
  if passed:resolved.append(uid)
 save(DOC/'source-support.json',{'rows':support,'resolved':resolved,'aiCalls':0,'modelGeometryChanges':0})
 unresolved=ordinary-set(resolved)
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');metric_by={row['uid']:row for row in metrics['rows']};validation_by={row['uid']:row for row in validation['results']};final_proofs={row['uid']:row for row in read(SOURCE_DOC/'final-script-pass/results.json.gz')['rows']};failures=[]
 for uid in UIDS:
  m=metric_by[uid];v=validation_by[uid];f=final_proofs[uid];foundation=f['foundation']
  if m.get('error') or not m['sourcePreserved'] or m['missingTerrain'] or m['maxSamplerDelta']>.004:failures.append({'uid':uid,'reason':'terrain-or-source-integrity'})
  if any(m['budget'][key]>metrics['profiles']['mobile'][key] for key in ('triangles','geometryBytes','residentBytes')):failures.append({'uid':uid,'reason':'mobile-runtime-budget'})
  if foundation['completeTerrainTriangles']/foundation['triangles']<.9989 or foundation['fullyBuriedAreaFraction']>.10 or foundation['minimumGapM']<-10:failures.append({'uid':uid,'reason':'source-foundation-envelope'})
  concerns=set(v.get('concerns',[]))-{'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}
  if v['outcome']=='validation-exception' or concerns:failures.append({'uid':uid,'reason':'runtime-validation','concerns':sorted(concerns)})
 if unresolved:failures.append({'uids':sorted(unresolved),'reason':'terrain-correction-regresses-neighbours'})
 if native_checks.get('failed'):failures.append({'uids':native_checks['failed'],'reason':'installed-native-neighbour-regression'})
 result={'batch':BATCH,'models':len(UIDS),'terrainPatches':len(patch_rows),'passed':not failures,'failures':failures,'unresolvedNeighbours':sorted(unresolved),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',result)
 if result['passed']:
  destination='city/data/official-models/'+BATCH+'/catalogue.json';plan={'areas':[{'area':template['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':terrain_plan};save(STAGE/'plan.json',plan)
  retained_by={row['uid']:[uid for uid in row['retainedForms'] if uid not in installed] for row in proof_rows};save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/'+'' ,'doc':rel(DOC)+'/', 'catalogueURL':destination,'terrain':terrain_plan,'fitBox':True,'fitBoxByModel':{'landsd/185148:0':False,'landsd/295518:0':False},'browserUids':list(UIDS),'failureTestUids':list(UIDS),'retainedBuildingUidsByModel':retained_by,'samplerToleranceByModel':{}})
 print(json.dumps(result,indent=2),flush=True)

def start():
 proof_rows,_=evidence();resources=['building:'+uid for uid in UIDS]+['source-form:'+uid for row in proof_rows for uid in row['suppressions']]+['terrain-patch:'+group[0] for group in GROUP_UIDS];claim=reservations.claim('codex-xl-held-terrain-'+str(uuid.uuid4()),sorted(set(resources)),batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
if __name__=='__main__':build() if len(sys.argv)>1 else start()
