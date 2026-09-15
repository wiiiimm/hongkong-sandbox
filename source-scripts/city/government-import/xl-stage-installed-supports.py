"""Stage unchanged XL towers on exact government supports already installed in the viewer."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
from shapely.geometry import MultiPoint,Polygon
sys.path.insert(0,str(Path(__file__).resolve().parent));spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
BATCH='government-xl-installed-supports-20260914';DOC=s.DOC/'third-pass/installed-supports';LOCAL=s.LOCAL/'third-pass-installed-supports';STAGE=HERE/'accepted'/BATCH
PAIRS={'landsd/83670:0':'landsd/224399:0','landsd/256112:0':'landsd/254491:0'}
PROBE=s.DOC/'third-pass/elevated-ready/support-probe-raw.json'
def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT);assert result.returncode in allowed,(args,result.returncode)
def installed_models():
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');models={}
 for url in manifest['officialModelCatalogues']:
  catalogue=read(ROOT/'3d-viewer'/url)
  for model in catalogue['models']:models[model['uid']]={**model,'catalogue':url}
 return models
def start():
 resources=sorted({'building:'+uid for pair in PAIRS.items() for uid in pair});claim=s.reservations.claim('codex-xl-installed-supports-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));runtime={r['uid']:r for r in read(s.DOC/'runtime-selection.json.gz')['rows']};save(DOC/'selection.json.gz',{'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'rows':[runtime[uid] for uid in PAIRS]});call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 assert s.reservations.owns(read(LOCAL/'reservation.json'));selection=read(DOC/'selection.json.gz');assert h(ROOT/'3d-viewer/city/data/manifest.json')==selection['manifestSHA256'];runtime={r['uid']:r for r in selection['rows']};final={r['uid']:r for r in read(s.DOC/'final-script-pass/results.json.gz')['rows']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json');forms={b['uid']:b for tile in manifest['tiles'] for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']};installed=installed_models()
 for uid,support_uid in PAIRS.items():
  result=final[uid];identity,foundation,run=result['identity'],result['foundation'],result['runtime'];assert result['scriptedWorkComplete'] and result['aiCalls']==result['modelGeometryChanges']==0;assert identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.98 and identity['sourceExcessFraction']<.05 and identity['unrelatedIntersectingForms']==0;assert foundation['fullyBuriedTriangles']==0;assert run['sourcePreserved'] and run['mobileBudgetPassed'] and not run['missingTerrain'];assert support_uid in installed
 call(['node',str(HERE/'xl-ready-support-probe.mjs')]);probe=read(PROBE);proofs=[]
 for raw in probe['rows']:
  row=dict(raw);target=forms[row['uid']];polygon=Polygon(target['rings'][0],target['rings'][1:]);contacts=MultiPoint([(p[0],p[2]) for p in row.pop('contactPositions')]).convex_hull;coverage=contacts.intersection(polygon).area/polygon.area;support=installed[row['supportUid']];passed=row['within05']>=100 and coverage>=.8 and row['minimumDistance']<=.5 and row['sourceSHA256']==runtime[row['uid']]['candidate']['entry']['sha256'] and row['supportSHA256']==support['sha256'];proofs.append({**row,'contactProjectionAreaM2':contacts.area,'contactHullTargetCoverage':coverage,'contactHullBounds':list(contacts.bounds),'supportCatalogue':support['catalogue'],'passed':bool(passed)})
 assert {r['uid'] for r in proofs}==set(PAIRS) and all(r['passed'] for r in proofs),proofs;save(DOC/'support-proof.json',{'rows':proofs,'policy':'The exact installed government support mesh must have at least 100 interface vertices within 0.5m, and their projected convex hull must cover at least 80% of the tower target footprint. This is the established supported-tower target-coverage threshold.','probeSHA256':h(PROBE),'aiCalls':0,'geometryChanges':0})
 entries=[];source_forms=[]
 for uid,row in runtime.items():
  support_uid=PAIRS[uid];support=installed[support_uid];entry=dict(row['candidate']['entry']);entry.update(priority='landmark',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,supportDependencies=[{'uid':support_uid,'state':'installed','csuid':support['buildingCSUID'],'sha256':support['sha256']}],placementReview=f'Exact unchanged government tower matched by object ID and Building CSUID. Exact installed government support {support_uid} has a deterministic mesh-contact proof covering at least 80% of the target footprint. The runtime loads the support first and retains it with the tower. No terrain or model geometry edits; no AI modelling or review.');asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert h(asset)==entry['sha256'];entries.append(entry);form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;source_forms.append(form)
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area='XL original government towers with exact installed government supports',counts={'packedModels':len(entries)},models=entries);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',source_forms);save(DOC/'terrain-candidates.json',[]);save(LOCAL/'source-forms.json',{uid:row['source'] for uid,row in runtime.items()})
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');reasons=[]
 for metric in metrics['rows']:
  if metric.get('error') or not metric.get('sourcePreserved') or metric.get('missingTerrain') or metric.get('maxSamplerDelta',0)>.004:reasons.append(metric['uid']+':source-integrity-or-terrain')
  if metric.get('budget') and any(metric['budget'][k]>metrics['profiles']['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):reasons.append(metric['uid']+':mobile-runtime-budget')
 allowed={'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}
 for result in validation['results']:
  if result['outcome']=='validation-exception':reasons.append(result['uid']+':runtime-validation-exception')
  reasons.extend(result['uid']+':'+c for c in result.get('concerns',[]) if c not in allowed)
 decision={'uids':list(PAIRS),'policy':'original-government-tower-on-installed-government-support-v1','passed':not reasons,'reasons':sorted(set(reasons)),'supportProofSHA256':h(DOC/'support-proof.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',decision)
 if decision['passed']:
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}]});save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[],'fitBox':True,'browserUids':list(PAIRS),'failureTestUids':list(PAIRS)})
 print(json.dumps(decision))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
