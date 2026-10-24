"""Check the new stadium original and retained opposite stand before/after private terrain."""
from pathlib import Path
import copy,json,subprocess,uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-inset-pair-runtime-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)];pins={}
    def take(batch,p):
        receipt,ps=authenticate(BASE/batch);key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[key];pins[key]=ps[key];refs.extend([BASE/batch/'result.json',p]);return read(p)
    batch='government-xl-mongkok-current-runtime-v1-20261021';selection=take(batch,BASE/batch/'selection.json.gz');rows=selection['rows'];assert len(rows)==1
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifestpath.read_bytes());assert mh==selection['manifestSHA256'];manifest=read(manifestpath);refs.append(manifestpath)
    batch='government-xl-mongkok-expanded-regional-scope-v1-20261021';scope=take(batch,BASE/batch/'scope.json');assert scope['touchingNativeUids']==['landsd/240527:0']
    obligations=take(batch,BASE/batch/'native-obligations.json.gz');retained=obligations[0];found=[]
    for url in manifest['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url
        for entry in read(path)['models']:
            if entry['uid']==retained['uid']:found.append((path,entry))
    assert len(found)==1;catalogue,entry=found[0];assert entry['sha256']==retained['sourceSHA256'];refs.append(catalogue)
    forms=[]
    for item in manifest['tiles']:
        p=ROOT/'3d-viewer'/item['url']
        for b in read(p)['buildings']:
            if b['uid']==retained['uid']:forms.append((p,b))
    assert len(forms)==1;tile,b=forms[0];refs.append(tile)
    asset=catalogue.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
    rows.append(dict(uid=entry['uid'],sourceSHA256=entry['sha256'],triangles=entry['triangles'],source=dict(tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()),building=b),candidate=dict(path=str(asset.relative_to(ROOT)),entry=entry)))
    for r in rows:
        p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
        target=LOCAL/r['candidate']['entry']['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());r['candidate']['path']=str(target.relative_to(ROOT));refs.append(target)
    batch='government-xl-mongkok-local-inset-v4-20261021';receipt,_=authenticate(BASE/batch);assert receipt['terrainValidationPassed'];candidates=take(batch,BASE/batch/'terrain-candidates.json');assert len(candidates)==1
    c=candidates[0];p=ROOT/c['path'];assert digest(p.read_bytes())==c['sha256'];refs.append(p)
    oldurl='city/data/government-native-240527-0.json';oldpath=ROOT/'3d-viewer'/oldurl;c['replaces']=dict(url=oldurl,sha256=digest(oldpath.read_bytes()),retainedUids=[retained['uid']]);refs.append(oldpath)
    save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',candidates)
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        results={};final=module('stadium_pair_foundation',HERE/'xl-final-script-pass.py');tool=HERE/'acceptance-metrics-multi-retained.mjs'
        for phase in ['before','after']:
            out=DOC/(phase+'-metrics.json');geometry=LOCAL/(phase+'-geometry.json.gz');cmd=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--out',str(out.relative_to(ROOT)),'--geometry-out',str(geometry.relative_to(ROOT))]
            if phase=='after':cmd+=['--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT))]
            with(DOC/(phase+'-worker.log')).open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            metrics=read(out);assert len(metrics['rows'])==2 and not any(r.get('error')for r in metrics['rows'])
            for name,h in metrics['inputHashes'].items():assert digest((ROOT/name).read_bytes())==h;refs.append(ROOT/name)
            refs.append(geometry);geo={r['uid']:r for r in read(geometry)['rows']};foundation=[]
            for row in rows:
                g=geo[row['uid']];assert g['sourceSHA256']==row['sourceSHA256'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building'];f=final.foundation_context(t,ground,Polygon(b['rings'][0],b['rings'][1:]));foundation.append(dict(uid=row['uid'],foundation=f))
            results[phase]=dict(metrics=metrics['rows'],foundations=foundation)
            print(phase,[(r['uid'],r['foundation']['fullyBuriedTriangles'])for r in foundation],flush=True)
        assert reservations.owns(lease) and digest(manifestpath.read_bytes())==mh
        for name,h in pins.items():assert digest((ROOT/name).read_bytes())==h
        save(DOC/'summary.json',dict(rows=results,installationApproved=False))
        refs.extend([tool,HERE/'xl-final-script-pass.py'])
        module('stadium_inset_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'new-and-retained-original-stadium-runtime',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=results,installationApproved=False))
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
