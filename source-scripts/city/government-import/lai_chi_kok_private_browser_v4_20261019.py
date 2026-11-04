"""Private desktop/mobile eight-source acceptance; no live publication."""
from pathlib import Path
import argparse,os,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main(width,phase):
    batch=f'government-xl-lai-chi-kok-browser-{width}-{phase}-v4-20261019';doc=BASE/batch;local=HERE/'local'/batch
    assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
    names=['platform-grade-review-v1','v5-identity-support-review','eight-runtime-v2','eight-neighbours-v2','eight-foundations-v2','ordinary-validation-v1','functional-applicability-v1']
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY')
        for name in names:
            d=BASE/('government-xl-lai-chi-kok-'+name+'-20261019');r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
            for e in r['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    cap=BASE/'government-xl-lai-chi-kok-eight-runtime-v2-20261019';rows=read(cap/'selection.json.gz')['rows'];assert len(rows)==8
    prototype=HERE/'accepted/government-xxl-20260911/catalogue.json';cat=read(prototype);refs.append(prototype);entries=[]
    validated={e['uid']:e for e in read(HERE/'local/government-xl-lai-chi-kok-ordinary-validation-v1-20261019/catalogue.json')['models']}
    assert set(validated)=={r['uid']for r in rows}
    for r in rows:
        e={**validated[r['uid']],'priority':'landmark','proceduralWindows':False,'publicationApproved':False,'placementReviewed':False};raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==e['sha256'];dest=local/e['asset'];assert dest.resolve().is_relative_to(local.resolve());dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);entries.append(e)
    platform=next(e for e in entries if e['uid']=='landsd/281463:0');platform_form=next(r['source']['building']for r in rows if r['uid']==platform['uid']);assert platform_form['buildingCSUID']=='3215622119P20070611'
    for e in entries:
        if e['uid']!=platform['uid']:e['supportDependencies']=[dict(uid=platform['uid'],state='candidate',csuid=platform_form['buildingCSUID'])]
    cat.update(area=batch,models=entries,counts=dict(packedModels=8));save(local/'catalogue.json',cat);save(local/'source-forms.json',[r['source']['building']for r in rows]);uids=[r['uid']for r in rows]
    neighbours=read(BASE/'government-xl-lai-chi-kok-eight-neighbours-v2-20261019/summary.json');native=neighbours['requiredNativeUids'];assert len(native)==3
    patch=read(cap/'terrain-candidates.json')[0];assert digest((ROOT/patch['path']).read_bytes())==patch['sha256'];terrain=dict(source=patch['path'],destination='city/data/'+batch+'-terrain.json',sha256=patch['sha256'],resolution=read(ROOT/patch['path'])['cell'],area='Private Lai Chi Kok original government assembly',replaces=patch['replaces'])
    bounds={}
    for e in entries:
        lo,hi=e['worldBounds'];centre=[(a+b)/2 for a,b in zip(lo,hi)];bounds[e['uid']]=[[centre[i]+(v[i]-centre[i])*1.15 for i in range(3)]for v in [lo,hi]]
    rel=lambda p:str(p.relative_to(ROOT))
    cfg=dict(stage=rel(local)+'/',doc=rel(doc)+'/',catalogueURL='city/data/official-models/'+batch+'/catalogue.json',terrain=[terrain],viewportWidths=[width],browserUids=uids,failureTestUids=[]if phase=='joint'else uids,jointUids=uids if phase=='joint'else [],fitBox=True,captureBoundsByModel=bounds,nativeSupportUidsByModel={u:native for u in uids}if phase=='joint'else {},skipRetainedVisits=phase!='joint',fallbackOnly=phase=='fallback')
    preflight="import fs from 'node:fs';import {prepareModelCatalogue} from './3d-viewer/city/official-model-assets.js';const rows=prepareModelCatalogue(JSON.parse(fs.readFileSync(process.argv[1],'utf8')),'https://validation.invalid/catalogue.json');if(rows.length!==8)throw new Error('Expected8models');"
    subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node','--input-type=module','-e',preflight,str(local/'catalogue.json')],cwd=ROOT,check=True)
    if phase=='diagnostic':cfg.update(browserUids=['landsd/192968:0'],failureTestUids=[],jointUids=[],nativeSupportUidsByModel={},terrainVisibilityDiagnostic=True)
    save(local/'browser-config.json',cfg);doc.mkdir();tool=HERE/('lai_chi_kok_ray_diagnostic_v2_20261019.mjs'if phase=='diagnostic'else'olympian_thirteen_assembly_browser_v7_20261018.mjs');cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'staged',rel(local/'browser-config.json')]
    with(doc/'browser.log').open('w')as log:
        result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
    save(doc/'command.json',dict(command=cmd,exitCode=result.returncode,publication=False))
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    refs.extend([tool,*[p for p in local.rglob('*')if p.is_file()]])
    module('lai_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'private-original-assembly-browser',list(dict.fromkeys(refs)),dict(uids=uids,width=width,phase=phase,browserExitCode=result.returncode,installationApproved=False,visualAcceptance=False))
    assert result.returncode==0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--width',type=int,choices=[390,1280],required=True);p.add_argument('--phase',choices=['joint','fallback','retry','diagnostic'],default='joint');a=p.parse_args();assert a.phase!='fallback'or a.width==390;main(a.width,a.phase)
