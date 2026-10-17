"""Stage unchanged Horizon Cove podium/tower with bounded source terrain; never AI."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;DOC=s.DOC/'fourth-pass/horizon-cove';LOCAL=s.LOCAL/'fourth-pass-horizon-cove';STAGE=HERE/'accepted/government-xxl-horizon-cove-20260913';UID='landsd/283473:0';TOWER='landsd/282761:0';BATCH='government-xxl-horizon-cove-20260913';read,save,h,rel=s.read,s.save,s.h,s.rel

def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT);assert result.returncode in allowed,(args,result.returncode)

def primary_row():
 original=next(r for r in read(s.BASE/'selection.json.gz')['rows'] if r['modelId']=='B353741083402063C0');second=next(r for r in read(s.DOC/'selection.json.gz')['rows'] if r['modelId']==original['modelId']);match=next(c for c in second['diagnosticSourceCandidates'] if c['building']['uid']==UID);form=match['building'];native=original['native'];model=native['model'];official=model['matching']['officialCandidates'][0]
 entry={**model['asset'],'uid':UID,'modelId':original['modelId'],'objectId':form['objectId'],'buildingCSUID':form['buildingCSUID'],'label':'Horizon Cove Podium','recordedBaseHeight':form['base'],'recordedTopHeight':form['base']+form['height'],'worldBounds':model['worldBounds'],'triangles':original['triangles'],'footprintCentroidDistanceMetres':official['footprintCentroidDistanceMetres'],'overlapOfSmallerFootprint':official['overlapOfSmallerFootprint'],'placementReviewed':False,'priority':'unreviewed','publicationApproved':False,'rootTranslation':[-834500,0,816500],'sourceTile':native['sheet']}
 return {'uid':UID,'source':{'building':form,'tile':match['tile'],'tileSHA256':match['tileSHA256']},'candidate':{'path':str(s.LOCAL/'assets'/(entry['sha256']+'.glb.gz')),'entry':entry},'native':native}

def start():
 rows=[primary_row(),read(LOCAL/'tower-runtime.json')];assert [r['uid'] for r in rows]==[UID,TOWER]
 neighbours=read(DOC/'neighbour-inputs.json.gz')['rows'];resources={('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:')+n['building']['uid'] for n in neighbours}|{'building:'+UID,'building:'+TOWER}
 claim=s.reservations.claim('codex-horizon-cove-'+str(uuid.uuid4()),sorted(resources),batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));save(DOC/'selection.json.gz',{**read(s.DOC/'runtime-selection.json.gz'),'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'rows':rows});save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows});call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
 assert s.reservations.owns(read(LOCAL/'reservation.json'));selection=read(DOC/'selection.json.gz');assert h(ROOT/'3d-viewer/city/data/manifest.json')==selection['manifestSHA256'];rows=selection['rows'];assert all(h(ROOT/'3d-viewer'/r['source']['tile'])==r['source']['tileSHA256'] for r in rows)
 proof=next(r for r in read(s.DOC/'final-script-pass/results.json.gz')['rows'] if r['uid']==UID);identity,foundation=proof['identity'],proof['foundation'];assert proof['scriptedWorkComplete'] and identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.98 and identity['sourceExcessFraction']<.006 and identity['sourceExcessMaximumDistanceFromTargetM']<4.4 and identity['sourceExcessCoveredByUnrelatedFormsM2']==0 and identity['unrelatedIntersectingForms']==0 and identity['sameParentIntersectingForms']==1
 components=foundation['components'];outside_area=sum(c['areaM2'] for c in components if not c['centroidsInsideTarget']);inside_centroids=sum(c['centroidsInsideTarget'] for c in components);assert foundation['completeTerrainTriangles']==foundation['triangles'] and foundation['fullyBuriedAreaFraction']<.0012 and foundation['fullyBuriedAreaM2']<115 and foundation['fullyBuriedUpwardAreaM2']<16 and inside_centroids>=265 and outside_area<.001
 terrain_result=read(DOC/'terrain-result.json');assert terrain_result['blockedBy']==[] and terrain_result['patch']['uids']==[UID,TOWER];patch_source=ROOT/terrain_result['patch']['path'];assert h(patch_source)==terrain_result['patch']['sha256'];patch=read(patch_source)
 entries=[];forms=[]
 for row in rows:
  entry=dict(row['candidate']['entry']);entry.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact unchanged Horizon Cove government assembly with a deterministic five-metre grid sampled from the original government TIN. Scripted identity, terrain, neighbour and runtime checks; no AI or model geometry edits.')
  if row['uid']==TOWER:entry['supportDependencies']=[{'uid':UID,'state':'candidate'}]
  entries.append(entry);asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert h(asset)==entry['sha256'];form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;forms.append(form)
 cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat.update(area='Horizon Cove original government podium and tower',counts={'packedModels':2},models=entries);save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms)
 staged_patch=STAGE/patch_source.name;shutil.copyfile(patch_source,staged_patch);terrain={'source':rel(staged_patch),'sha256':h(staged_patch),'destination':'city/data/'+staged_patch.name,'resolution':patch['cell'],'area':'Horizon Cove original government terrain'};patch_entry={**terrain_result['patch'],'path':rel(staged_patch),'sha256':h(staged_patch)};save(DOC/'terrain-candidates.json',[patch_entry])
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1))
 metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');reasons=[]
 for metric in metrics['rows']:
  if metric.get('error') or not metric.get('sourcePreserved') or metric.get('missingTerrain') or metric.get('maxSamplerDelta',0)>.004:reasons.append('source-integrity-or-terrain')
  if any(metric['budget'][k]>metrics['profiles']['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):reasons.append('mobile-runtime-budget')
 for result in validation['results']:
  if result['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
  allowed={'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'} if result['uid']==TOWER else {'sampled-terrain-above-model-bottom'}
  reasons.extend(c for c in result.get('concerns',[]) if c not in allowed)
 decision={'uids':[UID,TOWER],'policy':'original-government-horizon-cove-assembly-v1','passed':not reasons,'reasons':sorted(set(reasons)),'terrain':patch_entry,'neighbourChecksSHA256':h(DOC/'neighbour-checks.json'),'supportRecoverySHA256':h(DOC/'support-source-recovery.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',decision)
 if decision['passed']:
  destination='city/data/official-models/government-xxl-horizon-cove-20260913/catalogue.json';save(STAGE/'plan.json',{'areas':[{'area':cat['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}],'topLevelTerrainPatches':[terrain]});save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[terrain],'fitBox':True,'browserUids':[UID,TOWER],'failureTestUids':[UID]})
 print(json.dumps(decision))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
