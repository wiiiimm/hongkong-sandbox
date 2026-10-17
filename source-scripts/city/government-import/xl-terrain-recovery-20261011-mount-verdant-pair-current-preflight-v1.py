"""Fresh ordinary identities of both complete Mount originals, no support or acceptance."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from terrain_source_preflight import preflight,SourceSheetIndex
SOURCES={'landsd/261717:0':'c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1','landsd/75782:0':'4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781'}
BATCH='xl-terrain-recovery-20261011-mount-verdant-pair-current-inputs-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-mount-verdant-two-original-current-probe-v2-20261011/selection.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261011-mount-verdant-pair-preflight-v1-lease.json'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    assert not DOC.exists();lease=read(LEASE);prior=read(INPUT.parent/'result.json')
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    assert {'path':str(INPUT.relative_to(ROOT)),'sha256':digest(INPUT.read_bytes())}in prior['evidenceRefs'];assert reservations.heartbeat(lease)['ok']
    final=module('rooftop_current_forms','xl-final-script-pass.py');decoder=module('rooftop_current_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
    manifest=ROOT/'3d-viewer/city/data/manifest.json';index=ROOT/'source-scripts/city/landmark-acquisition/index.json'
    current_sha=digest(manifest.read_bytes());assert current_sha=='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e';catalogue_refs=[{'path':str((ROOT/'3d-viewer'/u).relative_to(ROOT)),'sha256':digest((ROOT/'3d-viewer'/u).read_bytes())}for u in read(manifest)['officialModelCatalogues']]
    installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    rows=[];contexts=[];results=[];refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [Path(__file__),INPUT,INPUT.parent/'result.json',manifest,index,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'government_georef_cell_identity.py',HERE/'routed_original_cell_identity.py',HERE/'component_type_resolution.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',HERE/'terrain_source_preflight.py']]
    for original in read(INPUT)['rows']:
        assert original['uid'] in SOURCES
        row=dict(original);assert row['sourceSHA256']==row['native']['model']['asset']['sha256']==SOURCES[row['uid']];row['modelId']=row['native']['model']['modelId'];row['triangles']=row['native']['model']['triangles'];row.setdefault('currentReview',None);row.setdefault('historicallyPublished',False);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==row['candidate']['entry']['sha256']
        destination=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
        tri=decoder.glb_triangles(row);low=tri.min(axis=(0,1));high=tri.max(axis=(0,1));forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2]);form,_,tile=next(f for f in forms if f[0]['uid']==row['uid']);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']
        row.update(source={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},candidate={**row['candidate'],'path':str(destination.relative_to(ROOT))})
        context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}}
        refs.extend({'path':str((ROOT/'3d-viewer'/t).relative_to(ROOT)),'sha256':sha}for t,sha in context['neighbourTileHashes'].items());refs.append({'path':str(destination.relative_to(ROOT)),'sha256':digest(destination.read_bytes())});assert reservations.heartbeat(lease)['ok']
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');actual=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone();assert actual and actual[0]==row['native']['resultSha']
        assert row['uid'] not in installed
        identity=verify_files(row,context,LOCAL/('identity-'+row['uid'].split('/')[1].replace(':','-')))
        routing=preflight(row,context,SourceSheetIndex(read(index)));routing.update(legacyProjectionIdentity=routing['identity'],identity=identity,canStartTerrainWork=identity['passed'] and routing['primarySheetIntersects'],uid=row['uid'],currentForms=len(forms))
        assert identity['passed'] and identity['proof']['identityAccepted'] and identity['proof']['uniqueViewerMatch']
        assert not row['candidate']['entry'].get('footprintScope') and not row['candidate']['entry'].get('suppressesBuildingUids'),'Ordinary source-only candidate required'
        rows.append(row);contexts.append(context);results.append(routing);refs.append({'path':str(asset.relative_to(ROOT)),'sha256':digest(raw)})
        print(json.dumps({'uid':row['uid'],'identityPassed':identity['passed'],'identityReasons':identity['reasons'],'currentForms':len(forms),'canStartTerrainWork':routing['canStartTerrainWork']}),flush=True)
    assert [r['uid']for r in rows]==list(SOURCES) and all(digest((ROOT/r['path']).read_bytes())==r['sha256']for r in refs)
    assert digest(manifest.read_bytes())==current_sha and reservations.owns(lease);assert all(digest((ROOT/r['path']).read_bytes())==r['sha256']for r in catalogue_refs);refs.extend(catalogue_refs)
    DOC.mkdir(parents=True,exist_ok=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append({'path':str((DOC/'historical-current-manifest.json').relative_to(ROOT)),'sha256':digest(manifest.read_bytes())})
    save(DOC/'check-selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':current_sha});save(DOC/'context.json.gz',{'rows':contexts});save(DOC/'indexed-preflight.json',{'rows':results,'manifestSHA256':current_sha,'evidenceRefs':refs,'installationApproved':False,'publication':False,'sourceGeometryChanges':0})
    frozen=module('mount_ordinary_preflight_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');frozen.freeze(BATCH,'mount-pair-fresh-two-ordinary-identities-indexed-terrain-preflight-v1',[ROOT/r['path']for r in refs]+list(DOC.glob('*.json*')),dict(uids=[r['uid']for r in rows],allOrdinaryIdentitiesPassed=all(r['identity']['passed']for r in results),bothOriginalsCandidatesNoUnqualifiedSupportCredit=True,currentManifestSHA256=current_sha,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':
    import uuid
    claim=reservations.claim('codex-mount-verdant-pair-preflight-'+str(uuid.uuid4()),['building:'+uid for uid in SOURCES],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    try:main()
    finally:assert reservations.release(read(LEASE))['ok']
