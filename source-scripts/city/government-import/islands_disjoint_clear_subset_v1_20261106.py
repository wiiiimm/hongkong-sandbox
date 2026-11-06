"""Freeze only entire clear original-terrain groups for guarded browser admission."""
import copy
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from run import connect


def main():
    base=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-disjoint-terrain-20261106-v1'
    runtime=base/'runtime-current';result=read(runtime/'results.json.gz')
    assert read(runtime/'neon-sync.json')['exactResultMatch'] and 0<result['models']<=31
    receipt=read(runtime/'neon-sync.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        status, stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone()
    assert status=='complete' and stored['evidence']=={'path':rel(runtime/'results.json.gz'),'sha256':sha(runtime/'results.json.gz')}
    assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==result
    clear={r['uid']for r in result['rows']if not r['reasons']};assert clear
    batch='government-islands-peng-chau-disjoint-clear-20261106-v1'
    doc=ROOT/'docs/astra-city/government-import'/batch;stage=HERE/'accepted'/batch
    assert not doc.exists()and not stage.exists()
    source_stage=HERE/'accepted/government-islands-peng-chau-disjoint-terrain-20261106-v1'
    pins={}
    for report_name in('metrics.json','native-neighbour-checks.json'):
        for p,h in read(runtime/report_name)['inputHashes'].items():assert sha(ROOT/p)==h,p;pins[p]=h
    for p in [runtime/'results.json.gz',runtime/'neon-sync.json',runtime/'neighbour-checks.final.json',base/'terrain-stage.json',Path(__file__)]:pins[rel(p)]=sha(p)
    fullplan=read(source_stage/'plan.json');neighbours=read(runtime/'neighbour-checks.final.json')
    patches=[p for p in neighbours['patches']if set(p['uids'])&clear]
    assert set().union(*(set(p['uids'])for p in patches))==clear and not any(p['blockedBy']for p in patches)
    wanted={p['path']for p in patches};top=[p for p in fullplan['topLevelTerrainPatches']if p['source']in wanted]
    assert len(top)==len(patches)==len(clear)
    catalogue=read(source_stage/'catalogue.json');catalogue['models']=[m for m in catalogue['models']if m['uid']in clear]
    catalogue['area']='Peng Chau disjoint clear original source/terrain ports';catalogue['counts']={'packedModels':len(clear)}
    for m in catalogue['models']:
        m['priority']='detail';target=stage/m['asset'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((source_stage/m['asset']).read_bytes());assert sha(target)==m['sha256']
    save(stage/'catalogue.json',catalogue);save(stage/'catalogue-index.json',{'models':len(clear),'catalogues':['catalogue.json']})
    selected=read(runtime/'selection.json.gz');selected['rows']=[r for r in selected['rows']if r['uid']in clear]
    assert selected['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    save(doc/'selection.json.gz',selected)
    save(stage/'source-forms.json',[{**r['source']['building'],'tile':Path(r['source']['tile']).stem}for r in selected['rows']])
    destination=f'city/data/official-models/{batch}/catalogue.json'
    save(stage/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(stage/'catalogue.json'),'destination':destination,'terrain':[]}],'topLevelTerrainPatches':top})
    save(doc/'terrain-candidates.json',[{'path':p['source'],'sha256':p['sha256']}for p in top])
    save(stage/'browser-config.json',{'stage':rel(stage)+'/','doc':rel(doc)+'/','catalogueURL':destination,'terrain':[{'source':p['source'],'destination':p['destination'],'resolution':p['resolution'],'area':p['area']}for p in top],
        'fitBox':True,'browserUids':sorted(clear),'failureTestUids':sorted(clear),'visibilitySupplementUids':[], 'captureDirectionByModel':{u:[.2,4,.2] for u in clear},'viewQualification':'High oblique original views with retained neighbours; no every-facade/as-built claim.'})
    identity_path=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-identity-20261106-v1/identities.json.gz';pins[rel(identity_path)]=sha(identity_path)
    for p,h in pins.items():assert sha(ROOT/p)==h,p
    save(doc/'stage.json',{'batch':batch,'uids':sorted(clear),'sources':len(clear),'inputHashes':pins,'identityEvidencePath':rel(identity_path),
        'additionalLeaseResources':['building:'+r['building']['uid']for r in read(runtime/'neighbour-inputs.json.gz')['rows']]+['terrain:city/data/terrain.json'],
        'terrainCandidates':rel(doc/'terrain-candidates.json'),'catalogueSHA256':sha(stage/'catalogue.json'),'planSHA256':sha(stage/'plan.json'),
        'completeClearTerrainGroups':len(patches),'rejectedNeighbourGroupsRetained':len(neighbours['patches'])-len(patches),'sourceGeometryChanges':0,'publication':False})
    print({'batch':batch,'clearSources':len(clear),'wholeTerrainGroups':len(patches),'publication':False},flush=True)


if __name__=='__main__':main()
