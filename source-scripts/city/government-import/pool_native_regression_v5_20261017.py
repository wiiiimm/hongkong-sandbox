"""Check the whole-source native neighbour of the private museum terrain."""
from pathlib import Path
import subprocess, uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-sham-shui-po-pool-native-regression-v5-20261017'
DOC=BASE/BATCH
NAMES=['government-xl-sham-shui-po-pool-native-scope-v1-20261016','government-xl-sham-shui-po-pool-preserved-neighbours-v6-20261017']
def main():
    assert not DOC.exists()
    refs=[Path(__file__)];pins={}
    for name in NAMES:
        folder=BASE/name;r=read(folder/'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        for ref in r['evidenceRefs']:
            p,h=ref['path'],ref['sha256'];assert p not in pins or pins[p]==h;pins[p]=h
        refs.append(folder/'result.json')
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    refs += [ROOT/p for p in pins]
    prior=BASE/NAMES[-1];inputs=read(prior/'neighbour-inputs.json.gz');standard=read(prior/'neighbour-checks.json');scope=read(BASE/NAMES[0]/'scope.json')
    nominated=set(scope['touchingNativeUids']);assert nominated=={'landsd/113733:0','landsd/138091:0','landsd/99395:0'}
    for uid in nominated:
        row=next((r for r in standard['rows']if r['uid']==uid),None)
        if row is None:standard['rows'].append(dict(uid=uid,existingNative=True,reasons=['whole-source-parent-domain-requires-native-check']))
        elif not row['reasons']:row['reasons']=['whole-source-parent-domain-requires-native-check']
    assert nominated=={r['uid']for r in standard['rows']if r['existingNative']and r['reasons']}
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);models={}
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;refs.append(p)
        for entry in read(p)['models']:models[entry['uid']]=entry
    forms={};tile_pins={}
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];data=read(p)
        matched=[b for b in data['buildings'] if b['uid'] in models]
        if matched:
            tile_pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());forms.update({b['uid']:b for b in matched})
    assert set(models)<=set(forms)
    existing={r['building']['uid'] for r in inputs['rows']}
    inputs['rows'] += [dict(building=forms[u],patchIndexes=[],existingNative=True) for u in sorted(set(models)-existing)]
    inputs['inputHashes'].update(tile_pins);refs += [manifest_path]+[ROOT/p for p in tile_pins]
    claim=reservations.claim('museum-native-check-'+str(uuid.uuid4()),['private-museum-preserved-ground']+sorted(nominated),batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
    try:
        DOC.mkdir();save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'neighbour-checks.json',standard)
        tool=HERE/'check-native-neighbours-complete-footprints-v1-20261016.mjs'
        with (DOC/'worker.log').open('w') as log:
            subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
        checked=read(DOC/'native-neighbour-checks.json');assert set(checked['blocked'])==nominated
        for p,h in checked['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        summary=dict(rows=checked['rows'],resolved=checked['resolved'],fullAcceptance=False,newlyInstalled=0,ordinaryRegressions=[r for r in read(prior/'summary.json')['ordinaryRegressions'] if not r['existingNative']])
        save(DOC/'summary.json',summary);refs += [tool,HERE/'native-neighbour-policy.mjs']
        result=module('hotel_native_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'museum-whole-source-native-regression-v1',list(dict.fromkeys(refs)),dict(uids=sorted(nominated),summary=summary,fullAcceptance=False,newlyInstalled=0))
        print(dict(jobId=result['jobId'],resolved=checked['resolved']),flush=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
