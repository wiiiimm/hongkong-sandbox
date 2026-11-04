"""Complete changed-domain BASIC and installed-source terrain regression checks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-eight-neighbours-v4-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019'
SCOPE=BASE/'government-xl-lai-chi-kok-expanded-terrain-scope-v1-20261019'

def main():
    assert not DOC.exists();pins={};refs=[Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,SCOPE,BASE/'government-xl-lai-chi-kok-eight-runtime-v4-20261019',BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019',BASE/'government-xl-lai-chi-kok-component-support-review-v1-20261019']:
            r=read(folder/'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
            refs.append(folder/'result.json')
            for e in r['evidenceRefs']:
                assert e['path'] not in pins or pins[e['path']]==e['sha256']
                pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    scope=read(SCOPE/'summary.json');wanted=set(scope['touchingNativeUids']);assert len(wanted)==3
    attr=BASE/'government-xl-lai-chi-kok-eight-render-attributes-v1-20261019';assembly=read(attr/'selection.json.gz')['rows'];candidate_ids=[r['uid']for r in assembly];assert len(set(candidate_ids))==8
    extent=scope['expandedExtent']
    for row in read(attr/'attributes.json.gz')['rows']:
        for key in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']:
            lo,hi=row[key];assert extent[0]<=lo[0]<=hi[0]<=extent[2]and extent[1]<=lo[2]<=hi[2]<=extent[3],(row['uid'],key)
    final=module('star_complete_forms',HERE/'xl-final-script-pass.py')
    forms=final.load_forms(scope['expandedExtent']);inputs={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in forms}
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
    assert set(candidate_ids)<=set(buildings)
    for row in assembly:assert buildings[row['uid']]==row['source']['building']
    patches=read(CAP/'terrain-candidates.json')
    assert set(patches[0]['replaces']['retainedUids'])<=wanted
    save(DOC/'neighbour-inputs.json.gz',dict(requiredNativeUids=sorted(wanted),candidateIds=candidate_ids,patches=patches,rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid'] in live) for b in buildings.values()],inputHashes=inputs))
    for name in ['check-neighbours.mjs','check-native-neighbours-multi-retained-scoped-v4.mjs']:
        with (DOC/(name+'.log')).open('w') as log:
            subprocess.run(['node',str(HERE/name),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        refs.append(HERE/name)
    basic=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json')
    summary=dict(uids=candidate_ids,requiredNativeUids=sorted(wanted),forms=len(buildings),basicReasons=[dict(uid=r['uid'],reasons=r['reasons']) for r in basic['rows'] if r['reasons']],unresolvedNatives=sorted(set(native['blocked'])-set(native['resolved'])),installationApproved=False)
    save(DOC/'summary.json',summary)
    for report in [basic,native]:
        for p,h in {**report.get('inputHashes',{}),**report.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    for p,h in {**pins,**inputs}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    refs.extend([manifestpath,CAP/'terrain-candidates.json',HERE/'xl-final-script-pass.py'])
    module('star_complete_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-complete-changed-domain-neighbours',list(dict.fromkeys(refs)),summary)
    print(summary,flush=True)

if __name__=='__main__':main()
