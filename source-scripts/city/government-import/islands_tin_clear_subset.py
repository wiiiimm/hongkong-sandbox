"""Freeze only entire clear original-terrain groups for guarded browser admission."""
import argparse
import copy
from pathlib import Path
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from run import connect


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-batch',required=True);parser.add_argument('--batch',required=True);parser.add_argument('--identity',type=Path,required=True)
    args=parser.parse_args()
    assert all(v.startswith('government-islands-') and '/' not in v for v in (args.source_batch,args.batch))
    base=ROOT/'docs/astra-city/government-import'/args.source_batch
    runtime=base/'runtime-current';result=read(runtime/'results.json.gz')
    assert read(runtime/'neon-sync.json')['exactResultMatch'] and 0<result['models']<=50
    receipt=read(runtime/'neon-sync.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        status, stored=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (receipt['jobId'],)).fetchone()
    assert status=='complete' and stored['evidence']=={'path':rel(runtime/'results.json.gz'),'sha256':sha(runtime/'results.json.gz')}
    assert {k:v for k,v in stored.items() if k not in ('jobId','evidence')}==result
    clear={r['uid']for r in result['rows']if not r['reasons']};assert clear
    batch=args.batch
    doc=ROOT/'docs/astra-city/government-import'/batch;stage=HERE/'accepted'/batch
    assert not doc.exists()and not stage.exists()
    source_stage=HERE/'accepted'/args.source_batch
    pins={}
    for report_name in('metrics.json','native-neighbour-checks.json'):
        for p,h in read(runtime/report_name)['inputHashes'].items():assert sha(ROOT/p)==h,p;pins[p]=h
    terrain_receipt=base/'terrain-stage.json'
    if not terrain_receipt.exists():
        # A byte-identical private proposal can have fresh current-context
        # checks after a verified additive catalogue change. Its rebind receipt
        # replaces construction metadata only, never the runtime checks above.
        terrain_receipt=base/'rebind.json'
        rebound=read(terrain_receipt)
        assert rebound['sourceGeometryChanges']==rebound['terrainGeometryChanges']==0
        assert rebound['publication'] is False
        assert rebound['currentManifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    for p in [runtime/'results.json.gz',runtime/'neon-sync.json',runtime/'neighbour-checks.final.json',terrain_receipt,Path(__file__)]:pins[rel(p)]=sha(p)
    fullplan=read(source_stage/'plan.json');neighbours=read(runtime/'neighbour-checks.final.json')
    all_clear=set(clear)
    candidates=[(i,p) for i,p in enumerate(neighbours['patches']) if set(p['uids'])&clear]
    assert set().union(*(set(p['uids'])for _,p in candidates))==clear and not any(p['blockedBy']for _,p in candidates)
    scope=read(runtime/'neighbour-inputs.json.gz')
    # Admit only complete terrain groups. The existing single browser lease is
    # capped at 1000 keys; reserve every affecting actor plus server/terrain.
    patches=[];lease_uids=set();deferred=[]
    for i,patch in candidates:
        affected={r['building']['uid'] for r in scope['rows'] if i in r['patchIndexes']}|set(patch['uids'])
        if len(lease_uids|affected)>950:
            deferred.extend(patch['uids']);continue
        patches.append(patch);lease_uids.update(affected)
    assert patches,'A whole terrain group exceeds this browser lease slice; retain it for a separately scoped follow-up'
    clear=set().union(*(set(p['uids'])for p in patches));assert clear<=all_clear
    wanted={p['path']for p in patches};top=[p for p in fullplan['topLevelTerrainPatches']if p['source']in wanted]
    assert len(top)==len(patches)==len(clear)
    catalogue=read(source_stage/'catalogue.json');catalogue['models']=[m for m in catalogue['models']if m['uid']in clear]
    catalogue['area']='Island original government models with verified source terrain';catalogue['counts']={'packedModels':len(clear)}
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
    identity_path=args.identity.resolve();assert identity_path.is_relative_to(ROOT);pins[rel(identity_path)]=sha(identity_path)
    for p,h in pins.items():assert sha(ROOT/p)==h,p
    save(doc/'stage.json',{'batch':batch,'uids':sorted(clear),'sources':len(clear),'inputHashes':pins,'identityEvidencePath':rel(identity_path),
        'additionalLeaseResources':['building:'+u for u in sorted(lease_uids)]+['terrain:city/data/terrain.json'],
        'terrainCandidates':rel(doc/'terrain-candidates.json'),'catalogueSHA256':sha(stage/'catalogue.json'),'planSHA256':sha(stage/'plan.json'),
        'completeClearTerrainGroups':len(patches),'scriptClearSourcesBeforeLeaseSlicing':len(all_clear),'scriptClearSourcesQueuedForAnotherSlice':deferred,'rejectedNeighbourGroupsRetained':len(neighbours['patches'])-len(patches),'sourceGeometryChanges':0,'publication':False})
    print({'batch':batch,'clearSources':len(clear),'wholeTerrainGroups':len(patches),'publication':False},flush=True)


if __name__=='__main__':main()
