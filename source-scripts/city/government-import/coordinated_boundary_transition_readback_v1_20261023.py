"""Preserve prior installation evidence across an opt-in validator code change."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/'government-xl-coordinated-boundary-contract-v1-20261023'
    assert not(out/'result.json').exists()
    context=read(out/'code-transition-context.json');aliases={};refs=[Path(__file__),out/'code-transition-context.json']
    for row in context['historicalMutableByteSnapshots']:
        historical=ROOT/row['savedHistoricalBytes']['path'];assert digest(historical.read_bytes())==row['originalSHA256']==row['savedHistoricalBytes']['sha256']
        assert digest((ROOT/row['originalPath']).read_bytes())==row['currentSHA256']
        aliases[row['originalPath'],row['originalSHA256']]=historical;refs.extend([historical,ROOT/row['originalPath']])
    prior=base/'government-xl-fu-tor-loy-installed-root-check-v1-20261023/verification.json';proof=read(prior);refs.append(prior);checked=[]
    for ref in proof['verifiedReferences']:
        path=aliases.get((ref['path'],ref['sha256']),ROOT/ref['resolvedBytes'])
        assert digest(path.read_bytes())==ref['sha256'],ref['path']
        refs.append(path);checked.append(dict(path=ref['path'],sha256=ref['sha256'],resolvedBytes=str(path.relative_to(ROOT))))
    assert len(checked)==860
    installed=base/'government-xl-fu-tor-loy-five-source-retained-original-installed-v9-20261023'
    final=read(installed/'result.json');counts=read(installed/'full-xl-current-count.json');pointerpath=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json';pointer=read(pointerpath);refs.extend([installed/'result.json',installed/'full-xl-current-count.json',pointerpath])
    assert pointer['snapshotId']==counts['snapshotId']==final['snapshotId']=='2311b29ba8906f61'
    manifestpath=ROOT/final['manifest']['path'];assert digest(manifestpath.read_bytes())==final['manifest']['sha256']==counts['manifestSHA256'];refs.append(manifestpath)
    models={}
    for url in read(manifestpath)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path)
        for model in read(path)['models']:
            assert model['uid']not in models;models[model['uid']]=model
    assert len(models)==6856 and len(counts['rows'])==len({r['sourceKey']for r in counts['rows']})==521
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(final['jobId'],)).fetchone()==('complete',final)
        reviews=dict(db.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE snapshot_id=%s',(counts['snapshotId'],)).fetchall())
        for row in counts['rows']:
            assert (reviews.get(row['uid'])=='installed-verified')==row['installedVerified']
            if row['installedVerified']:assert models[row['uid']]['sha256']==row['runtimeSourceSHA256']
    assert sum(r['installedVerified']for r in counts['rows'])==335
    result=dict(uids=['landsd/20270:0','landsd/159422:0','landsd/269430:0'],historicalReferences=checked,counts=dict(total=521,installedVerified=335,remaining=186),catalogueActors=6856,unresolvedSourceUIDs=sum(r['uid']is None for r in counts['rows']),snapshotId=counts['snapshotId'],currentManifest=final['manifest'],sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,qualification='All 860 prior ROOT references rehashed; historical publisher bytes resolve only to their immutable archive. Full 521 ledger review states read back under a read-only transaction and installed runtime catalogue SHA tuples unchanged. New opt-in validator contract is separate and does not transfer model acceptance.')
    save(out/'transition-readback.json',result)
    for batch in ['government-xl-island-industrial-paired-surface-binding-v3-20261023','government-xl-island-industrial-paired-current-runtime-v1-20261023','government-xl-island-industrial-contact-connectivity-v1-20261023','government-xl-island-industrial-component-interfaces-archive-v1-20261023']:refs.append(base/batch/'result.json')
    refs.extend(HERE/p for p in ['coordinated_native_boundary_v1_20261023.py','finite_native_boundary_strip_v1_20261023.py','test_coordinated_native_boundary_v1_20261023.py','test_coordinated_native_boundary_binding_v1_20261023.py','test_finite_native_boundary_strip_v1_20261023.py'])
    refs.append(HERE.parent/'island-detail-integration/coordinated_native_boundary.py')
    module('transition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'opt-in-finite-native-boundary-code-transition-readback',list(dict.fromkeys(refs)),result)
    print(dict(references=len(checked),installed=335,remaining=186,newInstallationCredit=0),flush=True)

if __name__=='__main__':main()
