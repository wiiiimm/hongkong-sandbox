"""Stage elevated XL government towers whose unchanged basic podiums support them."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,MultiPoint
sys.path.insert(0,str(Path(__file__).resolve().parent));spec=importlib.util.spec_from_file_location('second',Path(__file__).with_name('xl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
BATCH='government-xl-supported-towers-second-20260914';DOC=s.DOC/'third-pass/supported-towers-second';LOCAL=s.LOCAL/'third-pass-supported-towers-second';STAGE=HERE/'accepted'/BATCH
PAIRS={'landsd/236065:0':'landsd/242694:0','landsd/81678:0':'landsd/246824:0','landsd/81151:0':'landsd/246824:0','landsd/81008:0':'landsd/246824:0'}
def call(args,allowed=(0,)):
 result=subprocess.run(args,cwd=ROOT);assert result.returncode in allowed,(args,result.returncode)
def start():
 resources=sorted({'building:'+uid for pair in PAIRS.items() for uid in pair});claim=s.reservations.claim('codex-xl-supported-towers-second-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));runtime={r['uid']:r for r in read(s.DOC/'runtime-selection.json.gz')['rows']};save(DOC/'selection.json.gz',{'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'rows':[runtime[uid] for uid in PAIRS]});call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])
def owned():
 assert s.reservations.owns(read(LOCAL/'reservation.json'));selection=read(DOC/'selection.json.gz');assert h(ROOT/'3d-viewer/city/data/manifest.json')==selection['manifestSHA256'];runtime={r['uid']:r for r in selection['rows']};source={r['uid']:r for r in read(s.DOC/'selection.json.gz')['rows']};final={r['uid']:r for r in read(s.DOC/'final-script-pass/results.json.gz')['rows']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json');forms={b['uid']:b for tile in manifest['tiles'] for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']};proofs=[]
 for uid,support_uid in PAIRS.items():
  result=final[uid];identity,foundation,run=result['identity'],result['foundation'],result['runtime'];assert result['scriptedWorkComplete'] and result['aiCalls']==result['modelGeometryChanges']==0;assert identity['exactObjectAndCSUID'] and identity['targetCoveredBySourceProjection']>.98 and identity['sourceExcessFraction']<.18 and identity['unrelatedIntersectingForms']==0;assert foundation['fullyBuriedTriangles']==0;assert run['sourcePreserved'] and run['mobileBudgetPassed'] and not run['missingTerrain']
  triangles=s.glb_triangles(source[uid]);minimum=float(triangles[:,:,1].min());low=triangles[np.any(triangles[:,:,1]<=minimum+.35,axis=1)];hull=MultiPoint(low[:,:,[0,2]].reshape(-1,2)).convex_hull;target=Polygon(forms[uid]['rings'][0],forms[uid]['rings'][1:]);support=Polygon(forms[support_uid]['rings'][0],forms[support_uid]['rings'][1:]);top=forms[support_uid]['base']+forms[support_uid]['height'];low_coverage=support.intersection(hull).area/hull.area;target_coverage=support.intersection(target).area/target.area;margin=top-minimum;passed=low_coverage>=.97 and target_coverage>=.8 and -.1<=margin<=5
  proof={'uid':uid,'supportUid':support_uid,'sourceMinimumY':minimum,'supportTopY':top,'verticalMarginM':margin,'lowRimHullCoverage':low_coverage,'targetFootprintCoverage':target_coverage,'lowRimTriangles':len(low),'passed':bool(passed)};assert passed,proof;proofs.append(proof)
 save(DOC/'support-proof.json',{'rows':proofs,'policy':'An unchanged solid podium supports the detailed tower when it covers >=97% of the source low-rim hull and >=80% of the mapped target footprint, with source bottom no more than 5m inside and no more than 0.1m above the podium roof.','aiCalls':0,'geometryChanges':0})
 entries=[];source_forms=[]
 for uid,row in runtime.items():
  entry=dict(row['candidate']['entry']);entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview=f'Exact unchanged government tower matched by object ID and Building CSUID. Existing basic podium {PAIRS[uid]} remains visible and deterministically supports the complete source low rim. No terrain or model geometry edits; no AI modelling or review.');asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert h(asset)==entry['sha256'];entries.append(entry);form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;source_forms.append(form)
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area='Second supported elevated XL original government towers',counts={'packedModels':len(entries)},models=entries);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(entries),'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',source_forms);save(DOC/'terrain-candidates.json',[]);save(LOCAL/'source-forms.json',{uid:row['source'] for uid,row in runtime.items()})
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')]);call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')],allowed=(0,1));metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');reasons=[]
 for metric in metrics['rows']:
  if metric.get('error') or not metric.get('sourcePreserved') or metric.get('missingTerrain') or metric.get('maxSamplerDelta',0)>.004:reasons.append(metric['uid']+':source-integrity-or-terrain')
  if metric.get('budget') and any(metric['budget'][k]>metrics['profiles']['mobile'][k] for k in ('triangles','geometryBytes','residentBytes')):reasons.append(metric['uid']+':mobile-runtime-budget')
 allowed={'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}
 for result in validation['results']:
  if result['outcome']=='validation-exception':reasons.append(result['uid']+':runtime-validation-exception')
  reasons.extend(result['uid']+':'+c for c in result.get('concerns',[]) if c not in allowed)
 decision={'uids':list(PAIRS),'policy':'original-government-supported-xl-towers-v2','passed':not reasons,'reasons':sorted(set(reasons)),'supportProofSHA256':h(DOC/'support-proof.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False};save(DOC/'result.json',decision)
 if decision['passed']:
  destination='city/data/official-models/'+BATCH+'/catalogue.json';save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}]});save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[],'fitBox':True,'browserUids':list(PAIRS),'failureTestUids':list(PAIRS),'retainedBuildingUidsByModel':{uid:[support] for uid,support in PAIRS.items()}})
 print(json.dumps(decision))
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
