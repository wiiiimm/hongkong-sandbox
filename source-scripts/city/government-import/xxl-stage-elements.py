"""Prepare current guarded import of the exact previously approved Elements package."""
import importlib.util,json,sys,uuid,subprocess,shutil
from pathlib import Path
from shapely.geometry import Polygon,box
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
ROOT,HERE,DOC,LOCAL=s.ROOT,s.HERE,s.DOC/'elements',s.LOCAL/'elements'
STAGE=HERE/'accepted/government-xxl-elements-20260911';read,save,h,rel=s.read,s.save,s.h,s.rel
UID='landsd/273061:0'

def start():
    restored=read(DOC/'restoration.json');assert restored['exactApprovedTerrainMatch'] and h(ROOT/restored['path'])==restored['approvedSHA256'];patch=read(ROOT/restored['path']);g=patch['meta']['georef'];bb=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(patch['w']-1),816500-g['bN']+(patch['h']-1)];region=box(*bb)
    mf=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in mf['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
    for t in mf['tiles']:
        p=ROOT/'3d-viewer'/t['url'];raw=p.read_bytes();touched=False
        for b in json.loads(raw)['buildings']:
            if Polygon(b['rings'][0],b['rings'][1:]).intersects(region):neighbours.append({'building':b,'patchIndexes':[0],'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))});touched=True
        if touched:hashes[rel(p)]=s.digest(raw)
    save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':[UID],'patches':[{'path':restored['path'],'sha256':restored['sha256'],'uids':[UID],'bounds':bb}]})
    resources=set(read(s.LOCAL/'reservation.json')['resources'])|{('building:' if n['building']['uid'].startswith('landsd/') else 'source-form:')+n['building']['uid'] for n in neighbours}|{'building:landsd/204153:0'}
    claim=s.reservations.claim('codex-xxl-elements-stage-'+str(uuid.uuid4()),sorted(resources),batch=s.BATCH+'-elements-stage');assert claim['ok'];save(LOCAL/'stage-reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    s.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'stage-reservation.json'),'--',sys.executable,__file__,'owned'])

def owned():
    assert s.reservations.owns(read(LOCAL/'stage-reservation.json'));origin=ROOT/'source-scripts/city/identity-four-native';guard=read(ROOT/'docs/astra-city/identity-four-native/guard.json')
    for p,sha in guard['inputHashes'].items():assert h(ROOT/p)==sha
    assert h(origin/'approved/catalogue.json')==guard['catalogueSHA256']
    cat=read(origin/'approved/catalogue.json');e=next(e for e in cat['models'] if e['uid']==UID);cat['models']=[e];cat['counts']['packedModels']=1;cat['area']='Elements original source and approved native terrain';src=s.LOCAL/'assets'/(e['sha256']+'.glb.gz');assert h(src)==e['sha256'];dst=STAGE/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    frozen=read(s.DOC/'runtime-selection.json.gz');r=next(r for r in frozen['rows'] if r['uid']==UID);r['candidate']={'path':str(dst),'entry':{**e,'rootTranslation':cat['rootTranslation']}};save(DOC/'selection.json.gz',{**frozen,'rows':[r]});save(LOCAL/'source-forms.json',{UID:r['source']});b=dict(r['source']['building']);b['tile']=Path(r['source']['tile']).stem;save(STAGE/'source-forms.json',[b])
    with s.connect() as c:
        c.execute('SET TRANSACTION READ ONLY');review=c.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'],UID)).fetchone()
    assert review[0]=='approved-for-integration' and review[1]==e['sha256'] and h(ROOT/review[2]['evidence'])==review[2]['sha256'];save(DOC/'existing-approval.json',{'state':review[0],'sourceSHA256':review[1],'result':review[2],'reusedWithoutNewAI':True})
    old=read(origin/'publication-plan.json');t=old['topLevelTerrainPatches'][0];patch=read(DOC/'restoration.json');dst=STAGE/'terrain-elements-native.json';shutil.copyfile(ROOT/patch['path'],dst);t={**t,'source':rel(dst)};assert h(dst)==t['sha256'];dep=read(origin/'dependency-replacements.json')
    for c in dep['catalogues']:assert h(ROOT/c['source'])==c['oldSHA256']
    plan={**old,'areas':[{'area':cat['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':'city/data/official-models/government-xxl-elements-20260911/catalogue.json'}],'topLevelTerrainPatches':[t]};save(STAGE/'plan.json',plan);save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':plan['areas'][0]['destination'],'terrain':[t],'fitBox':True,'catalogueReplacements':[{'url':dep['catalogues'][0]['url'],'source':rel(origin/'harbourside-migrated-catalogue.json')}]})
    save(DOC/'terrain-candidates.json',[{'path':rel(dst),'sha256':h(dst)}]);s.call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
    v=subprocess.run(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],cwd=ROOT);assert v.returncode in (0,1)
    s.call([sys.executable,str(HERE.parent/'model-integration-20260909/publish.py'),rel(STAGE/'plan.json'),'--receipt',str(LOCAL/'stage-reservation.json'),'--phase','government-xxl-elements-20260911'])
    n=read(DOC/'neighbour-checks.json');print(json.dumps({'preparedModels':1,'neighbours':len(n['rows']),'flagged':[{'uid':r['uid'],'reasons':r['reasons']} for r in n['rows'] if r['reasons']],'publication':False}),flush=True)

if __name__=='__main__':owned() if len(sys.argv)>1 else start()
