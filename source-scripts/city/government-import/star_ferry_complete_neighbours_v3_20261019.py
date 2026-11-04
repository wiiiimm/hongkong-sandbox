"""Complete changed-domain BASIC and installed-source terrain regression checks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-star-ferry-complete-neighbours-v3-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-star-ferry-retained-wrapper-metrics-v3-20261019'
SCOPE=BASE/'government-xl-star-ferry-retained-projection-v1-20261019'

def main():
    assert not DOC.exists();pins={};refs=[Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,SCOPE]:
            r=read(folder/'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            refs.append(folder/'result.json')
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256']
                pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    scope=read(SCOPE/'projection-checks.json');wanted={r['uid'] for r in scope['actors']};assert len(wanted)==5
    final=module('star_complete_forms',HERE/'xl-final-script-pass.py')
    forms=final.load_forms(scope['mergedExtent']);inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in forms}
    buildings={b['uid']:b for b,_,_ in forms}
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath)
    live=set()
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;inputs[str(p.relative_to(ROOT))]=digest(p.read_bytes());live.update(m['uid'] for m in read(p)['models'])
    missing=wanted-set(buildings)
    for tile in manifest['tiles']:
        if not missing:break
        p=ROOT/'3d-viewer'/tile['url']
        for b in read(p)['buildings']:
            if b['uid'] in missing:
                buildings[b['uid']]=b;missing.remove(b['uid']);inputs[str(p.relative_to(ROOT))]=digest(p.read_bytes())
    assert not missing and wanted<=live
    patches=read(CAP/'terrain-candidates.json')
    from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
    bounds_path=BASE/'government-xl-remaining-two-current-scope-v1-20261019/complete-bounds.json.gz'
    assert digest(bounds_path.read_bytes())==pins[str(bounds_path.relative_to(ROOT))]
    bounds_by_uid={r['uid']:r['completeFourWorldBounds'] for r in read(bounds_path)['rows']}
    excluded=[]
    for patch in patches:
        retained=patch['replaces']['retainedUids']
        for uid in set(retained)-wanted:
            assert uid in bounds_by_uid and closed_disjoint(bounds_by_uid[uid],scope['mergedExtent']),uid
            excluded.append(dict(uid=uid,completeFourWorldBounds=bounds_by_uid[uid]))
        patch['replaces']['retainedUids']=sorted(set(retained)&wanted)
    proof=read(CAP/'retained-proof.json')
    assert proof['otherChildrenUnchanged']==12 and all(r['missing']==0 for r in proof['children'])
    save(DOC/'unchanged-outside-domain.json',dict(changedExtent=scope['mergedExtent'],requiredNativeUids=sorted(wanted),excludedRegionalActors=excluded,retainedProof=proof,policy='Only native checks outside the complete changed rectangle are excluded; current four-world bounds and unchanged regional grid/other-child payload are required.',installationApproved=False))
    refs.extend([bounds_path,HERE/'heritage_saved_native_bounds_binding_v1_20261014.py',CAP/'retained-proof.json'])
    save(DOC/'neighbour-inputs.json.gz',dict(requiredNativeUids=sorted(wanted),candidateIds=['landsd/210032:0'],patches=patches,rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid'] in live) for b in buildings.values()],inputHashes=inputs))
    for name in ['check-neighbours.mjs','check-native-neighbours-multi-retained-scoped-v4.mjs']:
        with (DOC/(name+'.log')).open('w') as log:
            subprocess.run(['node',str(HERE/name),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        refs.append(HERE/name)
    basic=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json')
    summary=dict(uids=['landsd/210032:0'],requiredNativeUids=sorted(wanted),forms=len(buildings),basicReasons=[dict(uid=r['uid'],reasons=r['reasons']) for r in basic['rows'] if r['reasons']],unresolvedNatives=sorted(set(native['blocked'])-set(native['resolved'])),installationApproved=False)
    save(DOC/'summary.json',summary)
    for report in [basic,native]:
        for p,h in {**report.get('inputHashes',{}),**report.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    for p,h in {**pins,**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    refs.extend([manifestpath,CAP/'terrain-candidates.json',HERE/'xl-final-script-pass.py'])
    module('star_complete_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'star-ferry-complete-changed-domain-neighbours',list(dict.fromkeys(refs)),summary)
    print(summary,flush=True)

if __name__=='__main__':main()
