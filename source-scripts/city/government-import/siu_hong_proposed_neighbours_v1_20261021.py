"""Full current-parent neighbour regression for the private terrain proposal."""
from pathlib import Path
import json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-siu-hong-proposed-neighbours-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CONTRACT=BASE/'government-xl-siu-hong-private-terrain-v2-20261021';SCOPE=BASE/'government-xl-siu-hong-regional-scope-v1-20261021';CAP=BASE/'government-xl-siu-hong-private-capture-v2-20261021'
def owned():
    assert reservations.owns(read(LOCAL/'reservation.json')) and not DOC.exists();pins={};refs=[Path(__file__)]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (CONTRACT,SCOPE,CAP):
            r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    assert take(CONTRACT,CONTRACT/'summary.json')['terrainValidationPassed']
    patches=take(CONTRACT,CONTRACT/'terrain-candidates.json');scope=take(SCOPE,SCOPE/'scope.json');required=scope['touchingNativeUids'];candidateids=['landsd/233417:0','landsd/190963:0'];manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);hashes={str(manifestpath.relative_to(ROOT)):digest(manifestpath.read_bytes())};native=set()
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;hashes[str(p.relative_to(ROOT))]=digest(p.read_bytes());native.update(e['uid'] for e in read(p)['models'])
    final=module('mount_sterling_neighbour_forms',HERE/'xl-final-script-pass.py');forms={b['uid']:(b,tile) for b,_,tile in final.load_forms(scope['allRetainedPackedAffectedExtent'])}
    import numpy as np
    for patch in patches:
        points=np.asarray(read(ROOT/patch['path'])['nativeMesh']['position']).reshape(-1,3);points=np.concatenate([points,points.astype('float32').astype('float64')]);e=scope['allRetainedPackedAffectedExtent']
        assert points[:,0].min()>=e[0] and points[:,0].max()<=e[2] and points[:,2].min()>=e[1] and points[:,2].max()<=e[3], 'Actual candidate expands nominated domain'
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
    stagedFolder=CAP
    staged=take(stagedFolder,stagedFolder/'selection.json.gz')
    save(DOC/'staged-originals.json',dict(rows=staged['rows'],conditionalOnly=True))
    folder=str(DOC.relative_to(ROOT))+'/'
    for name in ['check-neighbours-multi-retained.mjs','grandiose_joint_scene_neighbours_v1_20261021.mjs']:
        subprocess.run(['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(HERE/name),folder],cwd=ROOT,check=True);refs.append(HERE/name)
    reports=[]
    for name in ['neighbour-checks.json','native-neighbour-checks.json']:
        report=read(DOC/name);reports.append(report)
        for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    for p,h in hashes.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    summary=dict(uids=candidateids,ordinaryForms=len(rows),requiredNativeUids=required,ordinaryFlagged=[r['uid'] for r in reports[0]['rows'] if r['reasons']],conditionalProposedScene=True,installationApproved=False)
    save(DOC/'summary.json',summary);module('mount_sterling_neighbour_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-parent-current-neighbour-regression',list(dict.fromkeys(refs)),summary)
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
