"""Stage Tian Tan Buddha against the already installed official Ngong Ping 5 m terrain; never AI."""
import importlib.util,json,shutil,subprocess,sys,uuid
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'))
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE=s.ROOT,s.HERE
DOC=s.DOC/'third-pass/tian-tan'
LOCAL=s.LOCAL/'third-pass-tian-tan'
STAGE=HERE/'accepted/government-xxl-tian-tan-20260912'
UID='landsd/241332:0'
read,save,h,rel=s.read,s.save,s.h,s.rel


def start():
    row=next(r for r in read(s.DOC/'runtime-selection.json.gz')['rows'] if r['uid']==UID)
    source=next(r for r in read(s.DOC/'selection.json.gz')['rows'] if r['uid']==UID)
    resources=['building:'+UID]
    claim=s.reservations.claim('codex-xxl-tian-tan-'+str(uuid.uuid4()),resources,batch='government-xxl-tian-tan-20260912')
    assert claim['ok']
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(DOC/'selection.json.gz',{**read(s.DOC/'runtime-selection.json.gz'),'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'rows':[row]})
    save(LOCAL/'source-forms.json',{UID:source['source']})
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'])


def owned():
    assert s.reservations.owns(read(LOCAL/'reservation.json'))
    row=read(DOC/'selection.json.gz')['rows'][0]
    source=next(r for r in read(s.DOC/'selection.json.gz')['rows'] if r['uid']==UID)
    entry=dict(row['candidate']['entry'])
    proof=next(r for r in read(s.DOC/'third-pass/source-surface-context.json')['rows'] if r['uid']==UID)
    faces=read(s.DOC/'third-pass/tian-tan-buried-faces.json')
    upward=[f for f in faces['fullyBuried'] if f['upward']]
    assert entry['objectId']==source['source']['building']['objectId']==241332
    assert entry['buildingCSUID']==source['source']['building']['buildingCSUID']=='0824512822T20100514'
    assert entry['label']==source['source']['building']['name']=='Tian Tan Buddha Statue'
    assert entry['overlapOfSmallerFootprint']>=.999 and entry['footprintCentroidDistanceMetres']<2
    context=proof['surfaceContext']
    assert context['completeTerrainTriangles']==context['triangles']==253036
    assert context['fullyBuriedAreaRatio']<.001 and context['fullyBuriedUpwardTriangles']==1
    assert len(upward)==1 and upward[0]['area']<6 and min(upward[0]['gaps'])>-1.5
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json')
    installed=[]
    lo,hi=entry['worldBounds']
    for item in manifest['terrainPatches']:
        patch=read(ROOT/'3d-viewer'/item['url']);g=patch['meta']['georef']
        bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1)*g['aE'],816500-g['bN']-(patch['h']-1)*g['aN']]
        if bounds[0]<=lo[0] and bounds[1]<=lo[2] and bounds[2]>=hi[0] and bounds[3]>=hi[2]:
            installed.append({'url':item['url'],'sha256':item['sha256'],'resolution':item['resolution'],'area':item['area'],'bounds':bounds})
    assert len(installed)==1 and installed[0]['resolution']==5 and installed[0]['area']=='Ngong Ping landmarks'
    cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json')
    entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,placementReview='Exact unchanged government source matched by object ID, Building CSUID and Tian Tan Buddha label with full recorded-footprint coverage. Five of 253,036 faces are embedded at the hillside edge; four are foundation walls and one 5.82 m2 sloped face is 0.61-1.10 m below government terrain. Scripted only; no AI architectural review or geometry edits.')
    cat.update(area='Tian Tan Buddha original government source',counts={'packedModels':1},models=[entry])
    save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert h(asset)==entry['sha256']
    form=dict(source['source']['building']);form['tile']=Path(source['source']['tile']).stem;save(STAGE/'source-forms.json',[form])
    save(DOC/'terrain-candidates.json',[])
    s.call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')])
    result=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT)
    assert result.returncode in (0,1)
    metric=read(DOC/'metrics.json')['rows'][0];validation=read(DOC/'validation.json')['results'][0];reasons=[]
    if metric.get('error') or not metric['sourcePreserved'] or metric['sourceSHA256']!=entry['sha256']:reasons.append('source-integrity-or-runtime-check')
    if metric['missingTerrain'] or metric['maxSamplerDelta']>.004:reasons.append('terrain-coverage-or-rendered-disagreement')
    if any(metric['budget'][key]>read(DOC/'metrics.json')['profiles']['mobile'][key] for key in ('triangles','geometryBytes','residentBytes')):reasons.append('mobile-runtime-budget')
    if validation['outcome']=='validation-exception':reasons.append('runtime-validation-exception')
    allowed={'sampled-ground-gap-below-model-bottom','sampled-terrain-above-model-bottom'}
    reasons += [reason for reason in validation.get('concerns',[]) if reason not in allowed]
    decision={'uid':UID,'policy':'original-government-bounded-hillside-foundation-v1','passed':not reasons,'reasons':sorted(set(reasons)),'surfaceProof':proof,'buriedFaceProof':faces,'installedTerrain':installed[0],'aiCalls':0,'modelGeometryChanges':0,'publication':False}
    save(DOC/'result.json',decision)
    if not reasons:
        destination='city/data/official-models/government-xxl-tian-tan-20260912/catalogue.json'
        save(STAGE/'plan.json',{'areas':[{'area':cat['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination}]})
        save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[],'fitBox':True})
    print(json.dumps(decision),flush=True)


if __name__=='__main__':owned() if len(sys.argv)>1 else start()
