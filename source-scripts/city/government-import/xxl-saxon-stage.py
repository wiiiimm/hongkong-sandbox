"""Validate a linked original tower/podium pair with exact mechanical support proof."""
import importlib.util,json,sys,uuid,shutil,subprocess
from pathlib import Path
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'saxon',s.LOCAL/'saxon';STAGE=HERE/'accepted/government-xxl-saxon-20260911';read,save,h,rel=s.read,s.save,s.h,s.rel
TOWER='landsd/76364:0';PODIUM='landsd/232025:0'

def supported_reasons(metrics,proof):
    by={r['uid']:r for r in metrics['rows']};spec=importlib.util.spec_from_file_location('policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    p=by[PODIUM];t=by[TOWER]
    reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':proof['supportSHA256']},p,metrics['profiles']['mobile'])
    reasons+= [r for r in policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':proof['towerSHA256']},t,metrics['profiles']['mobile']) if r!='ground-contact-unresolved']
    gap=proof.get('gapRange')
    if not gap or not proof['lowRimSamples'] or proof['covered']!=proof['lowRimSamples'] or gap[0]<-.1 or gap[0]>.1 or gap[1]>1:reasons.append('incomplete-native-podium-contact')
    return sorted(set(reasons))

def start():
    owned=s.reservations.claim('codex-xxl-saxon-'+str(uuid.uuid4()),['building:'+TOWER,'building:'+PODIUM],batch=s.BATCH+'-saxon-stage');assert owned['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(owned['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'));frozen=read(s.DOC/'runtime-selection.json.gz');tower=next(r for r in frozen['rows'] if r['uid']==TOWER);recovered=read(s.LOCAL/'saxon-support/geometry-inputs.json')['rows'][0];source=read(s.LOCAL/'saxon-support/input.json.gz');podium={'uid':PODIUM,'source':source['sources'][PODIUM],'candidate':recovered['candidate'],'native':source['native'][0]};rows=[podium,tower];proof=read(s.DOC/'saxon-support-triangles.json');assert proof['uid']==TOWER and proof['supportUid']==PODIUM
    with s.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');states=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',([TOWER,PODIUM],)))
    assert not any(x in ('held','source-unavailable','identity-unresolved','installed-verified') for x in states.values())
    selection={**frozen,'rows':rows};save(DOC/'selection.json.gz',selection);cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat['models']=[];cat['area']='Original Saxon Tower and its original podium';forms=[]
    for r in rows:
        e=dict(r['candidate']['entry']);e['priority']='detail';e['rootTranslation']=[-834500,0,816500];e['sourceTile']=r['native']['sheet'];src=Path(r['candidate']['path']);assert h(src)==e['sha256'];dst=STAGE/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);cat['models'].append(e);b=dict(r['source']['building']);b['tile']=Path(r['source']['tile']).stem;forms.append(b)
    cat['counts']['packedModels']=2;save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':2,'catalogues':['catalogue.json']});save(STAGE/'source-forms.json',forms);save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
    s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--out',rel(DOC/'metrics.json')])
    v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert v.returncode in (0,1)
    metrics=read(DOC/'metrics.json');reasons=supported_reasons(metrics,proof)
    for v in read(DOC/'validation.json')['results']:
        if v['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
        reasons += [reason for reason in v.get('concerns',[]) if not (v['uid']==TOWER and reason=='sampled-ground-gap-below-model-bottom')]
    result={'policy':'original-government-supported-pair-v1','uids':[PODIUM,TOWER],'passed':not reasons,'reasons':reasons,'support':proof,'metricSHA256':h(DOC/'metrics.json'),'sourceProofSHA256':h(s.DOC/'saxon-support-triangles.json'),'aiCalls':0,'modelGeometryChanges':0};save(DOC/'decision.json',result)
    if not reasons:
        for e in cat['models']:
            e.update(placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact unchanged government source pair; native podium passes all direct-import gates and every tower lower-rim sample has actual podium surface contact within existing -0.1m/+1m allowance. No AI architectural review.')
            if e['uid']==TOWER:e['supportDependencies']=[{'uid':PODIUM,'state':'candidate'}]
        save(STAGE/'catalogue.json',cat);plan={'areas':[{'area':cat['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':'city/data/official-models/government-xxl-saxon-20260911/catalogue.json'}]};save(STAGE/'plan.json',plan);save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':plan['areas'][0]['destination'],'terrain':[],'fitBox':True})
    print(json.dumps(result),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
