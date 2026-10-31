"""Stage Gateway Arcade and Hullett House on one exact nested Central terrain patch."""
import copy,importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,box
import native_patch_resolution as patch_resolution
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
UIDS=['landsd/73140:0'];BATCH='government-xl-hullett-central-nested-20260914';DOC=s.DOC/'third-pass/central-nested';LOCAL=s.LOCAL/'third-pass-central-nested';PARENT_URL='city/data/terrain-central.json';PARENT_PATH=ROOT/'3d-viewer'/PARENT_URL
COMPOUND_SUPPRESSIONS={'landsd/73140:0':['landsd/211916:0']}

def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT);assert result.returncode in allowed,(args,result.returncode)

def model_projection(rows):
 triangles=[]
 original={r['uid']:r for r in read(s.DOC/'selection.json.gz')['rows']}
 for row in rows:triangles.append(s.glb_triangles(original[row['uid']]))
 tri=np.concatenate(triangles);polygons=shapely.polygons(tri[:,:,[0,2]]);return shapely.union_all(polygons[shapely.area(polygons)>1e-10])

def parent_with_nested(parent,patch):
 updated=copy.deepcopy(parent);rows=[]
 for child in updated.get('patches',[]):
  approval=child.get('nativeMesh',{}).get('sourceOverlap')
  if not approval:continue
  original=ROOT/approval['evidencePath'];assert h(original)==approval['evidenceSHA256']
  inherited=DOC/('inherited-'+child['id']+'-native-overlap.json');shutil.copyfile(original,inherited);old_path=approval['evidencePath'];old_sha=approval['evidenceSHA256'];approval['evidencePath']=rel(inherited)
  binding=patch_resolution.finalize_overlap_evidence(child,inherited)
  rows.append({'patchId':child['id'],'originalEvidencePath':old_path,'originalEvidenceSHA256':old_sha,'reboundEvidencePath':rel(inherited),**binding})
 updated.setdefault('patches',[]).append(patch);save(DOC/'inherited-overlap-rebind.json',{'rows':rows,'policy':'Rebind inherited overlap audits to each unchanged final nested-child payload when publishing a new parent wrapper. Existing live evidence remains untouched; no terrain coordinates or indices change.','aiCalls':0,'modelGeometryChanges':0});return updated

def start():
 runtime={r['uid']:r for r in read(s.DOC/'runtime-selection.json.gz')['rows']};rows=[runtime[uid] for uid in UIDS];parent=read(PARENT_PATH)
 rectangles=[s.resolution.rectangle_for(row['candidate']['entry']['worldBounds'],parent) for row in rows];cells=[min(x[0] for x in rectangles),min(x[1] for x in rectangles),max(x[2] for x in rectangles),max(x[3] for x in rectangles)];assert 0<=cells[0]<cells[2]<parent['w'] and 0<=cells[1]<cells[3]<parent['h'];assert not any(s.resolution.terrain.overlap(cells,child['coarseCells']) for child in parent.get('patches',[]));bounds=s.resolution.extent(cells,parent);region=box(*bounds)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
  for building in json.loads(raw)['buildings']:
   if Polygon(building['rings'][0],building['rings'][1:]).intersects(region):neighbours.append({'building':building,'patchIndexes':[0],'existingNative':building['uid'] in live or bool(building.get('modelGeometry'))});touched=True
  if touched:hashes[rel(path)]=s.digest(raw)
 current=h(ROOT/'3d-viewer/city/data/manifest.json');save(DOC/'selection.json.gz',{'manifestSHA256':current,'rows':rows});save(DOC/'patch-plan.json',{'cells':cells,'bounds':bounds,'manifestSHA256':current,'parentURL':PARENT_URL,'parentSHA256':h(PARENT_PATH),'uids':UIDS});save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':UIDS,'patches':[]})
 resources={'building:'+uid for uid in UIDS}|{('building:' if item['building']['uid'].startswith('landsd/') else 'source-form:')+item['building']['uid'] for item in neighbours};claim=s.reservations.claim('codex-xl-central-nested-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 assert s.reservations.owns(read(LOCAL/'reservation.json'));plan=read(DOC/'patch-plan.json');assert h(ROOT/'3d-viewer/city/data/manifest.json')==plan['manifestSHA256'];assert h(PARENT_PATH)==plan['parentSHA256'];parent=read(PARENT_PATH);rows=read(DOC/'selection.json.gz')['rows'];final={r['uid']:r for r in read(s.DOC/'final-script-pass/results.json.gz')['rows']};adjacent=read(s.DOC/'adjacent-terrain-results.json');assert adjacent['complete']
 native_by_model={r['modelId']:r['native'] for r in read(s.DOC/'diagnostics.json')['rows']};native_by_model.update({r['modelId']:r['native'] for r in adjacent['rows']})
 for row in rows:
  result=final[row['uid']];foundation=result['foundation'];native=native_by_model[row['native']['model']['modelId']];assert result['publicationCandidate'] and result['scriptedWorkComplete'] and result['identityScriptAccepted'] and result['foundationScriptAccepted'] and result['aiCalls']==result['modelGeometryChanges']==0;assert foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']<=.001;assert native['covered']==native['checks']
 sources_by_sheet={source['sheet']:source for source in read(s.DOC/'recovery.json')['sheets']+adjacent['sources']};bounds=plan['bounds'];fragments=[];used=[]
 for source in sources_by_sheet.values():
  folder=s.LOCAL/'sheets'/source['sheet']/'terrain'
  for entry in source['source']['entries']:
   if entry['name'].startswith('TERRAIN') and entry['name'].endswith(('.gltf','.bin')):assert h(folder/entry['name'])==entry['sha256']
  found=[]
  for path in source['terrainPaths']:
   triangles=s.terrain_triangles(ROOT/path);near=triangles[(triangles[:,:,0].max(axis=1)>=bounds[0])&(triangles[:,:,0].min(axis=1)<=bounds[2])&(triangles[:,:,2].max(axis=1)>=bounds[1])&(triangles[:,:,2].min(axis=1)<=bounds[3])]
   if len(near):found.append(near)
  if found:
   fragments.extend(found);proof=source['source'];used.append({'sheet':source['sheet'],'revision':proof['revisionDate'],'sourceETag':proof['sourceETag'],'directorySHA256':proof['directorySHA256'],'sourceFiles':[{'path':rel(folder/e['name']),'sha256':e['sha256']} for e in proof['entries'] if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))]})
 assert fragments;native=np.concatenate(fragments);projection=model_projection(rows);low=native[:,:,1].min(axis=1)<1.2;low_projection=shapely.union_all(shapely.polygons(native[low][:,:,[0,2]])) if low.any() else shapely.GeometryCollection();low_proof={'faces':int(low.sum()),'heightRangeM':[float(native[low,:,1].min()),float(native[low,:,1].max())] if low.any() else None,'projectedAreaM2':float(low_projection.area),'modelIntersectionAreaM2':float(low_projection.intersection(projection).area),'policy':'Retain original waterfront terrain facets below the viewer water clamp in the native mesh; water renders above submerged faces and no model geometry or elevation changes.'}
 lows=[row['candidate']['entry']['worldBounds'][0] for row in rows];highs=[row['candidate']['entry']['worldBounds'][1] for row in rows];core=[min(x[0] for x in lows)-1,min(x[2] for x in lows)-1,max(x[0] for x in highs)+1,max(x[2] for x in highs)+1];group={'uids':UIDS,'cells':plan['cells']}
 patch=s.resolution.make_patch(group,parent,native,used,native_core=core,parent_url=PARENT_URL,parent_sha256=plan['parentSHA256'],allow_native_below_clamp=True);patch['id']='government-native-central-hullett-house';patch['nativeMesh']['source']['belowWaterClamp']=low_proof;patch_path=LOCAL/(patch['id']+'.json');save(patch_path,patch);patch=read(patch_path);source_files=[item for source in used for item in source['sourceFiles']];projected_excess=patch_resolution.projected_context(patch,bounds)[3]
 overlap=patch_resolution.approve_original_overlap(patch,patch_path,DOC/'native-overlap-evidence.json',source_files) if projected_excess>1e-8 else {'nativeProjectedExcessM2':projected_excess,'policy':'No overlapping source facets were present.'};sampler=s.resolution.terrain.fine.DemSampler(parent,rendered=True);fill=patch_resolution.fill_parent_only_holes(patch,parent,bounds,projection,sampler);save(patch_path,patch);patch=read(patch_path)
 if patch['nativeMesh'].get('sourceOverlap'):patch_resolution.finalize_overlap_evidence(patch,DOC/'native-overlap-evidence.json');save(patch_path,patch);patch=read(patch_path)
 s.resolution.validate_patch(patch,parent);save(DOC/'terrain-resolution.json',{'parentURL':PARENT_URL,'parentSHA256':plan['parentSHA256'],'overlapProof':overlap,'waterClamp':{**low_proof,'droppedTriangles':0,'parentHoleFill':fill},'aiCalls':0,'modelGeometryChanges':0})
 bundle={'parentTerrainURL':PARENT_URL,'parentSha256':plan['parentSHA256'],'patches':[patch]};save(LOCAL/'terrain-bundle.json',bundle);updated=parent_with_nested(parent,patch);save(LOCAL/'terrain-central-with-nested.json',updated);terrain_entry={'path':rel(LOCAL/'terrain-central-with-nested.json'),'sha256':h(LOCAL/'terrain-central-with-nested.json'),'uids':UIDS,'bounds':bounds,'triangles':len(patch['nativeMesh']['index'])//3,'replaces':{'url':PARENT_URL,'sha256':plan['parentSHA256']}};save(DOC/'terrain-candidates.json',[terrain_entry]);neighbours=read(DOC/'neighbour-inputs.json.gz');neighbours['patches']=[terrain_entry];save(DOC/'neighbour-inputs.json.gz',neighbours)
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[];source_forms=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);entry.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True)
  if COMPOUND_SUPPRESSIONS.get(row['uid']):entry['suppressesBuildingUids']=COMPOUND_SUPPRESSIONS[row['uid']]
  entries.append(entry);asset=LOCAL/'candidates'/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert h(asset)==entry['sha256'];form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;source_forms.append(form)
 catalogue.update(area='Hullett House original government model',counts={'packedModels':len(entries)},models=entries);save(LOCAL/'candidates/catalogue.json',catalogue);save(LOCAL/'candidates/catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(LOCAL/'candidates/source-forms.json',source_forms);save(LOCAL/'source-forms.json',{row['uid']:row['source'] for row in rows})
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1));call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 neighbour=read(DOC/'neighbour-checks.json');native_neighbour=read(DOC/'native-neighbour-checks.json');suppressed={uid for uids in COMPOUND_SUPPRESSIONS.values() for uid in uids};by_uid={item['building']['uid']:item['building'] for item in read(DOC/'neighbour-inputs.json.gz')['rows']}
 suppression_rows=[]
 for source_uid,uids in COMPOUND_SUPPRESSIONS.items():
  source=next(row['source']['building'] for row in rows if row['uid']==source_uid)
  for uid in uids:
   fallback=by_uid[uid];footprint=Polygon(fallback['rings'][0],fallback['rings'][1:]);intersection=footprint.intersection(projection);coverage=intersection.area/footprint.area
   parent_fields=['parent','parentId','parentUid','parentUID','parentWay','parentFeatureId'];shared=[key for key in parent_fields if source.get(key) is not None and source.get(key)==fallback.get(key)]
   names={str(source.get('name','')).upper(),str(fallback.get('name','')).upper()}
   row={'sourceUid':source_uid,'suppressedUid':uid,'sourceName':source.get('name',''),'suppressedName':fallback.get('name',''),'footprintAreaM2':footprint.area,'sourceProjectionIntersectionM2':intersection.area,'footprintCoverage':coverage,'sharedParentFields':shared,'nameContextAccepted':names=={'HULLETT HOUSE','1881 HERITAGE'}}
   assert coverage>=.999 and shared and row['nameContextAccepted'];suppression_rows.append(row)
 save(DOC/'assembly-suppression.json',{'rows':suppression_rows,'policy':'The unchanged Hullett House government source is a compound 1881 Heritage component. Suppress only a fallback form with the same source parent, accepted name context, and at least 99.9% footprint coverage by the exact source projection; restore it automatically when detail unloads.','aiCalls':0,'modelGeometryChanges':0})
 remaining=set(neighbour['patches'][0]['blockedBy'])-set(native_neighbour['resolved'])-suppressed
 if remaining:
  protected=shapely.union_all([Polygon(by_uid[uid]['rings'][0],by_uid[uid]['rings'][1:]) for uid in sorted(remaining)]);protected_with_fringe=protected.buffer(.01,join_style='mitre');assert protected_with_fringe.intersection(projection).area<1e-8,'neighbour-preservation-intersects-source-model'
  proof=patch_resolution.preserve_parent_under_projection(patch,bounds,protected_with_fringe,sampler);proof['boundaryFringeM']=.01;proof['parentHoleFill']=patch_resolution.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
  if patch['nativeMesh'].get('sourceOverlap'):patch_resolution.finalize_overlap_evidence(patch,DOC/'native-overlap-evidence.json')
  s.resolution.validate_patch(patch,parent);save(patch_path,patch);patch=read(patch_path);resolution=read(DOC/'terrain-resolution.json');resolution['protectedNeighbourTerrain']={'uids':sorted(remaining),**proof};save(DOC/'terrain-resolution.json',resolution)
  bundle={'parentTerrainURL':PARENT_URL,'parentSha256':plan['parentSHA256'],'patches':[patch]};save(LOCAL/'terrain-bundle.json',bundle);updated=parent_with_nested(parent,patch);save(LOCAL/'terrain-central-with-nested.json',updated);terrain_entry.update(path=rel(LOCAL/'terrain-central-with-nested.json'),sha256=h(LOCAL/'terrain-central-with-nested.json'),triangles=len(patch['nativeMesh']['index'])//3);save(DOC/'terrain-candidates.json',[terrain_entry]);neighbours=read(DOC/'neighbour-inputs.json.gz');neighbours['patches']=[terrain_entry];save(DOC/'neighbour-inputs.json.gz',neighbours)
  call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL/'candidates'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'candidates'),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1));call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(DOC)+'/'])
 spec=importlib.util.spec_from_file_location('policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);metrics=read(DOC/'metrics.json');validations={r['uid']:r for r in read(DOC/'validation.json')['results']};reasons=[];foundation_rows=[];identity_rows=[]
 for metric in metrics['rows']:
  uid=metric['uid'];row=next(r for r in rows if r['uid']==uid);result=final[uid];identity=result['identity'];proof={'exactObjectId':row['candidate']['entry']['objectId']==row['source']['building']['objectId'],'exactBuildingCSUID':row['candidate']['entry']['buildingCSUID']==row['source']['building']['buildingCSUID'],'uniqueViewerMatch':len(row['native']['model']['matching']['viewerMatches'])==1 and row['native']['model']['matching']['viewerMatches'][0]['uid']==uid}
  if uid=='landsd/73140:0':proof['identityAccepted']=bool(result['publicationCandidate'] and result['identityScriptAccepted'] and identity['exactObjectAndCSUID'])
  acceptance={'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['candidate']['entry']['sha256'],'identityProof':proof};item_reasons=policy.reasons(acceptance,metric,metrics['profiles']['mobile']);foundation=result['foundation'];foundation_ok=foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']<=.001 and metric['missingTerrain']==0 and metric['maxLowGap']<=1 and metric['minLowGap']<=.25 and metric['maxSamplerDelta']<=.004
  if foundation_ok:item_reasons=[reason for reason in item_reasons if reason not in ('terrain-intersects-source-over-0.5m','ground-contact-unresolved')]
  concerns=list(validations[uid].get('concerns',[]));
  if foundation_ok:concerns=[c for c in concerns if c!='sampled-terrain-above-model-bottom']
  if validations[uid]['outcome']=='validation-exception':concerns.append('runtime-validation-exception')
  item_reasons+=concerns;reasons.extend(uid+':'+reason for reason in item_reasons);foundation_rows.append({'uid':uid,'accepted':bool(foundation_ok),'completeFaceFoundation':foundation,'metricContact':{key:metric[key] for key in ('missingTerrain','minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta')}});identity_rows.append({'uid':uid,'accepted':not any(r in item_reasons for r in ('strict-identity-fit','source-integrity')),'proof':proof,'detailedProjection':identity})
 save(DOC/'foundation-resolution.json',{'rows':foundation_rows,'policy':'Complete exact government terrain coverage, no buried upward faces, at most 0.1% buried area, at most 0.25m unchanged-source low-rim gap, rendered/sampled agreement and unchanged source geometry.','aiCalls':0,'modelGeometryChanges':0});save(DOC/'identity-resolution.json',{'rows':identity_rows,'policy':'Exact object and Building CSUID; strict fit or the frozen bounded complete-face identity proof.','aiCalls':0,'modelGeometryChanges':0})
 neighbour=read(DOC/'neighbour-checks.json');native_neighbour=read(DOC/'native-neighbour-checks.json');remaining=set(neighbour['patches'][0]['blockedBy'])-set(native_neighbour['resolved'])-suppressed;reasons.extend('terrain-correction-regresses-neighbour:'+uid for uid in sorted(remaining));decision={'uids':UIDS,'policy':'original-government-xl-nested-central-terrain-v1','passed':not reasons,'reasons':sorted(set(reasons)),'patch':terrain_entry,'terrainBundle':rel(LOCAL/'terrain-bundle.json'),'assemblySuppressionSHA256':h(DOC/'assembly-suppression.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',decision);print(json.dumps(decision),flush=True)
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
