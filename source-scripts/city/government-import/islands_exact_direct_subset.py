"""Nominate exact-cell originals that already fit the current unchanged terrain.

Historical metrics nominate only; fresh renderer/contact and full identity replay
are mandatory in the guarded worker. No terrain edits or approval here.
"""
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,policy
from run import connect


def main():
    identity_path=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-identity-20261106-v1/identities.json.gz'
    identities={r['uid']:r for r in read(identity_path)['rows']};pins={rel(identity_path):sha(identity_path)};chosen=[]
    for name in ('government-islands-peng-chau-0000-1000-20261106','government-islands-peng-chau-1000-425-20261106'):
        base=ROOT/'docs/astra-city/government-import'/name
        selected={r['uid']:r for r in read(base/'check-selection.json.gz')['rows']}
        report=read(base/'results.json.gz');profile=read(base/'metrics.json')['profiles']['mobile']
        for p in (base/'check-selection.json.gz',base/'results.json.gz',base/'metrics.json'):pins[rel(p)]=sha(p)
        for row in report['rows']:
            identity=identities.get(row['uid'])
            if not identity or not identity['passed']:continue
            reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':identity['proof']},row['metrics'],profile)
            if reasons or row['validation']['concerns']:continue
            source={**selected[row['uid']],'identityProof':identity['proof']};chosen.append(source)
    assert {r['uid']for r in chosen}=={'landsd/163726:0','landsd/163727:0','landsd/163736:0','landsd/278444:0','landsd/305187:0','landsd/6090:0','landsd/81726:0','landsd/81780:0'}
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);pins[rel(manifest_path)]=sha(manifest_path)
    installed={m['uid']for url in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not installed&{r['uid']for r in chosen}
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');native=dict(db.execute('SELECT cache_key,result_sha FROM astra_modelling.native_stage_results WHERE cache_key=ANY(%s)',([r['native']['cacheKey']for r in chosen],)))
    for row in chosen:
        assert native[row['native']['cacheKey']]==row['native']['resultSha']
        p=ROOT/row['candidate']['path'];assert sha(p)==row['candidate']['entry']['sha256'];pins[rel(p)]=sha(p)
        p=ROOT/'3d-viewer'/row['source']['tile'];assert sha(p)==row['source']['tileSHA256'];pins[rel(p)]=sha(p)
    batch='government-islands-peng-chau-exact-direct-eight-20261106-v1';doc=ROOT/'docs/astra-city/government-import'/batch;stage=HERE/'accepted'/batch
    assert not doc.exists()and not stage.exists()
    catalogue={k:v for k,v in read(HERE.parent/'kai-tak-port/staged/catalogue.json').items()if k not in ('area','models','counts')}
    models=[]
    for row in chosen:
        e=dict(row['candidate']['entry']);e.update(priority='detail',proceduralWindows=False,placementReviewed=False,sourceIdentityReviewed=False,identityReviewApproved=False,publicationApproved=False)
        p=stage/e['asset'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/row['candidate']['path']).read_bytes());models.append(e)
    catalogue.update(area='Peng Chau eight exact original ports on existing terrain',models=models,counts={'packedModels':len(models)})
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']})
    save(stage/'source-forms.json',[{**r['source']['building'],'tile':Path(r['source']['tile']).stem}for r in chosen])
    save(doc/'selection.json.gz',{'rows':chosen,'batch':batch,'manifestSHA256':sha(manifest_path),'nominationOnly':True})
    destination=f'city/data/official-models/{batch}/catalogue.json'
    save(stage/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(stage/'catalogue.json'),'destination':destination,'terrain':[]}],'topLevelTerrainPatches':[]})
    save(stage/'browser-config.json',{'stage':rel(stage)+'/','doc':rel(doc)+'/','catalogueURL':destination,'terrain':[],
         'fitBox':True,'browserUids':[r['uid']for r in chosen],'failureTestUids':[r['uid']for r in chosen],'visibilitySupplementUids':[]})
    pins[rel(Path(__file__))]=sha(Path(__file__))
    save(doc/'stage.json',{'batch':batch,'uids':[r['uid']for r in chosen],'sources':len(chosen),'inputHashes':pins,
        'identityEvidencePath':rel(identity_path),'catalogueSHA256':sha(stage/'catalogue.json'),'planSHA256':sha(stage/'plan.json'),
        'historicalMetricsAreNominationsOnly':True,'sourceGeometryChanges':0,'terrainChanges':0,'publication':False})
    print({'batch':batch,'sources':len(chosen),'publication':False},flush=True)


if __name__=='__main__':main()
