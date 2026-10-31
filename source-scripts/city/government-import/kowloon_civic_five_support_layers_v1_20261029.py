"""Inspect existing finite support layers for two exact original pairs; no acceptance."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-kowloon-city-civic-five-after-fuying-'
BATCH=PREFIX+'support-layers-v1-20261029';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PAIRS=[('landsd/159177:0','landsd/230911:0'),('landsd/82290:0','landsd/82291:0')]
def main():
    if '--owned'not in sys.argv:
        assert not DOC.exists()and not LOCAL.exists()
        keys=sorted({'building:'+uid for pair in PAIRS for uid in pair})
        claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
        try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        finally:
            if reservations.owns(lease):assert reservations.release(lease)['ok']
        return
    lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();runtime=BASE/(PREFIX+'current-ground-v1-20261029');_,pins=authenticate(runtime);selection=runtime/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))];rows=read(selection)['rows'];wanted={uid for pair in PAIRS for uid in pair};rows=[r for r in rows if r['uid']in wanted];assert {r['uid']for r in rows}==wanted
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==read(selection)['manifestSHA256'];refs=[Path(__file__),runtime/'result.json',selection,manifest]
    for row in rows:
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    DOC.mkdir();save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid=a,supportUid=b)for a,b in PAIRS]));tool=HERE/'disney_hotel_support_layers_v1_20261016.mjs'
    with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    proof=read(DOC/'support-checks.json.gz');assert len(proof['rows'])==2;results=[]
    for path,sha in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    for row in proof['rows']:
        f=row['interface'];layers=row['layerDiagnostic']['rows'];classes={k:sum(x['classification']==k for x in layers)for k in sorted({x['classification']for x in layers})}
        results.append(dict(uid=row['uid'],supportUid=row['supportUid'],ordinaryInterfacePassed=f['passed'],samples=f['samples'],strictContacts=f['strictContacts'],unresolved=len(f['unresolved']),layerClassifications=classes))
    assert reservations.owns(lease);result=dict(uids=sorted(wanted),rows=results,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Existing production decoder/strict-interface and lower-layer inspection algorithms, exact original assets/current source bindings. Every failed strict sample and finite original source-face incidence retained. A lower-layer candidate is diagnostic only, not bearing, ownership, source-role or publication approval. No source, model, terrain or policy edits.')
    save(DOC/'summary.json',result);refs.append(tool);module('civic_five_support_layer_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-pair-support-layer-diagnostics',refs,result);print(results,flush=True)
if __name__=='__main__':main()
