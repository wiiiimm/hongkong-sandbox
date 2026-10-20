"""Full current-parent neighbour regression for the private terrain proposal."""
from pathlib import Path
import json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-neighbours-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CONTRACT=BASE/'government-xl-plaza-ascot-terrain-validation-v2-20261020';SCOPE=BASE/'government-xl-plaza-ascot-current-scope-v1-20261020';CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020'
def owned():
    assert reservations.owns(read(LOCAL/'reservation.json')) and not DOC.exists();pins={};refs=[Path(__file__)]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (CONTRACT,SCOPE,CAP):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    patches=take(CONTRACT,CONTRACT/'terrain-candidates.json');scope=take(SCOPE,SCOPE/'scope.json');required=scope['touchingBaseDomainNativeUids'];candidateids=take(CAP,CAP/'summary.json')['uids'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);hashes={str(manifestpath.relative_to(ROOT)):digest(manifestpath.read_bytes())};native=set()
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());native.update(e['uid'] for e in read(p)['models'])
    final=module('mount_sterling_neighbour_forms',HERE/'xl-final-script-pass.py');forms={b['uid']:(b,tile) for b,_,tile in final.load_forms(scope['baseReplacementExtent'])}
    missing=set(required)-set(forms)
    for tile in manifest['tiles']:
        if not missing:break
        for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
            if b['uid'] in missing:forms[b['uid']]=(b,tile['url']);missing.remove(b['uid'])
    assert not missing
    rows=[]
    for uid,(b,tile) in forms.items():
        p=ROOT/'3d-viewer'/tile;hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());rows.append(dict(building=b,patchIndexes=[0],existingNative=uid in native))
    for patch in patches:
        assert digest((ROOT/patch['path']).read_bytes())==patch['sha256'];hashes[patch['path']]=patch['sha256']
    save(DOC/'neighbour-inputs.json.gz',dict(rows=rows,candidateIds=candidateids,requiredNativeUids=required,patches=patches,inputHashes=hashes))
    folder=str(DOC.relative_to(ROOT))+'/'
    for name in ['check-neighbours-multi-retained.mjs','check-native-neighbours-multi-retained-scoped-v4.mjs']:
        subprocess.run(['node',str(HERE/name),folder],cwd=ROOT,check=True);refs.append(HERE/name)
    reports=[]
    for name in ['neighbour-checks.json','native-neighbour-checks.json']:
        report=read(DOC/name);reports.append(report)
        for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    summary=dict(uids=candidateids,ordinaryForms=len(rows),requiredNativeUids=required,ordinaryFlagged=[r['uid'] for r in reports[0]['rows'] if r['reasons']],installationApproved=False)
    save(DOC/'summary.json',summary);module('mount_sterling_neighbour_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-parent-current-neighbour-regression',list(dict.fromkeys(refs)),summary)
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
