"""Fresh private context for one unchanged Peng original after Cheung additions.

Only an independently verified additive catalogue change is admitted. No old
physical/identity approval transfers: fresh scope/runtime/browser follow next.
"""
import copy
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel

BATCH='government-islands-peng-chau-rebound-terrain-20261106-v1'


def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;stage=HERE/'accepted'/BATCH
    assert not out.exists() and not stage.exists()
    old_doc=base/'government-islands-peng-chau-disjoint-clear-20261106-v1'
    old_stage=HERE/'accepted/government-islands-peng-chau-disjoint-clear-20261106-v1'
    prior=read(old_doc/'stage.json');selection=read(old_doc/'selection.json.gz');assert prior['uids']==['landsd/80912:0']
    integration_doc=base/'government-islands-cheung-chau-direct-003-20261106-v2'
    integration=read(integration_doc/'integration.json');checked=read(integration_doc/'independent-installed-readback.json')
    assert integration['neonVerified'] and checked['passed'] and integration['snapshotId']==checked['snapshotId']
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert integration['manifestSHA256']==sha(manifest_path)
    before=read(HERE/'local/government-islands-cheung-chau-direct-003-20261106-v2/manifest-before.json')
    assert selection['manifestSHA256']==integration['oldManifestSHA256']
    current=read(manifest_path);new_url='city/data/official-models/government-islands-cheung-chau-direct-003-20261106-v2/catalogue.json'
    assert current=={**before,'officialModelCatalogues':before['officialModelCatalogues']+[new_url]}
    for p,h in prior['inputHashes'].items():
        if p!='3d-viewer/city/data/manifest.json':assert sha(ROOT/p)==h,p
    for p,h in read(integration_doc/'retained-inputs.json').items():assert sha(ROOT/p)==h,p
    catalogue=read(old_stage/'catalogue.json');assert len(catalogue['models'])==1
    for entry in catalogue['models']:
        target=stage/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((old_stage/entry['asset']).read_bytes());assert sha(target)==entry['sha256']
        assert entry['publicationApproved'] is False and entry['placementReviewed'] is False
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
    plan=read(old_stage/'plan.json');plan['areas'][0]['catalogue']=rel(stage/'catalogue.json');plan['areas'][0]['destination']=f'city/data/official-models/{BATCH}/catalogue.json'
    assert len(plan['topLevelTerrainPatches'])==1
    save(stage/'plan.json',plan);save(stage/'source-forms.json',read(old_stage/'source-forms.json'))
    selection.update(batch=BATCH,manifestSHA256=sha(manifest_path));save(out/'selection.json.gz',selection)
    patches=[]
    for p in plan['topLevelTerrainPatches']:
        terrain=read(ROOT/p['source']);assert sha(ROOT/p['source'])==p['sha256'];g=terrain['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];hi_x=x+(terrain['w']-1)*g['aE'];hi_z=z-(terrain['h']-1)*g['aN']
        patches.append({'path':p['source'],'sha256':p['sha256'],'uids':prior['uids'],'bounds':[min(x,hi_x),min(z,hi_z),max(x,hi_x),max(z,hi_z)]})
    save(out/'terrain-candidates.json',[{'path':p['path'],'sha256':p['sha256']} for p in patches])
    rows=[]
    installed={m['uid'] for u in current['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']}
    from shapely.geometry import Polygon,box
    domain=box(*patches[0]['bounds']);pins={rel(manifest_path):sha(manifest_path),rel(Path(__file__)):sha(Path(__file__))}
    for tile in current['tiles']:
        path=ROOT/'3d-viewer'/tile['url']
        for form in read(path)['buildings']:
            if form.get('rings') and Polygon(form['rings'][0],form['rings'][1:]).intersects(domain):rows.append({'building':form,'patchIndexes':[0],'existingNative':form['uid']in installed});pins[rel(path)]=sha(path)
    for path in (old_doc/'stage.json',integration_doc/'integration.json',integration_doc/'independent-installed-readback.json'):pins[rel(path)]=sha(path)
    save(out/'neighbour-inputs.json.gz',{'rows':rows,'candidateIds':prior['uids'],'patches':patches,'inputHashes':pins})
    save(out/'rebind.json',{'oldManifestSHA256':integration['oldManifestSHA256'],'currentManifestSHA256':sha(manifest_path),'sourceGeometryChanges':0,'terrainGeometryChanges':0,'contextChange':'25 independently verified additive Cheung catalogue entries; all retained inputs exact','publication':False})
    print({'privateSources':1,'affectedFootprints':len(rows),'freshRuntimeStillRequired':True},flush=True)


if __name__=='__main__':main()
