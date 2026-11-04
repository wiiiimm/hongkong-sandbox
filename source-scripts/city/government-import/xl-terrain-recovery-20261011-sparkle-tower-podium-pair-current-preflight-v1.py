"""Fresh ordinary identities of both complete Sparkle originals, no support or acceptance."""
import importlib.util,json,subprocess,sys
from pathlib import Path
from shapely.geometry import box
from shapely import union_all
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files
from terrain_source_preflight import preflight,SourceSheetIndex
SOURCES={'landsd/242198:0':'5dcc709e25d0801ae3e2cef4a59c214babfa2adc4de42ce5fd956e649315c3f3','landsd/228000:0':'7429ad91552966b7e5ab6717626cb8e84d195da698140bcaf0b57ce890b89800'}
BATCH='xl-terrain-recovery-20261011-sparkle-tower-podium-pair-current-inputs-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
AUTHENTIC_SHEETS={'11-NW-13A','11-NW-13B'}
INPUT=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-sparkle-tower-podium-current-probe-v1-20261011/selection.json.gz'
LEASE='/tmp/xl-terrain-recovery-20261011-sparkle-tower-podium-pair-preflight-v1-lease.json'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def owned():
    assert not DOC.exists();lease=read(LEASE);prior=read(INPUT.parent/'result.json')
    with connect()as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    assert {'path':str(INPUT.relative_to(ROOT)),'sha256':digest(INPUT.read_bytes())}in prior['evidenceRefs'];assert reservations.heartbeat(lease)['ok']
    for pin in prior['evidenceRefs']:
        path=ROOT/pin['path'];assert path.is_file() and digest(path.read_bytes())==pin['sha256']
    final=module('rooftop_current_forms','xl-final-script-pass.py');decoder=module('rooftop_current_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
    manifest=ROOT/'3d-viewer/city/data/manifest.json';index=ROOT/'source-scripts/city/landmark-acquisition/index.json'
    current_sha=digest(manifest.read_bytes());assert current_sha=='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6';catalogue_refs=[{'path':str((ROOT/'3d-viewer'/u).relative_to(ROOT)),'sha256':digest((ROOT/'3d-viewer'/u).read_bytes())}for u in read(manifest)['officialModelCatalogues']]
    installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    rows=[];contexts=[];results=[];refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [Path(__file__),INPUT,INPUT.parent/'result.json',manifest,index,HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'government_georef_cell_identity.py',HERE/'routed_original_cell_identity.py',HERE/'component_type_resolution.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',HERE/'terrain_source_preflight.py']]
    refs.extend(prior['evidenceRefs'])
    sheet_index=SourceSheetIndex(read(index))
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
        routing=preflight(row,context,sheet_index);routing.update(legacyProjectionIdentity=routing['identity'],identity=identity,canStartTerrainWork=identity['passed'] and routing['primarySheetIntersects'],uid=row['uid'],currentForms=len(forms))
        assert identity['passed'] and identity['proof']['identityAccepted'] and identity['proof']['uniqueViewerMatch']
        assert routing['canStartTerrainWork'] and routing['primarySheetIntersects']
        required={s['sheet'] for s in routing['indexedSheets']}
        assert required and required <= AUTHENTIC_SHEETS and routing['primarySheet'] in required
        whole_bounds=row['completeOriginalPOSITIONProof']['originalWholeSourceBounds']
        assert whole_bounds==row['native']['model']['worldBounds']
        lo,hi=whole_bounds;original_xz=box(834500+lo[0],816500-hi[2],834500+hi[0],816500-lo[2])
        sheets=union_all([p for f,p in zip(sheet_index.features,sheet_index.polygons) if f['attributes']['SHEETNO'] in required])
        assert sheets.covers(original_xz),'Declared original sheets do not cover complete source POSITION bounds'
        routing.update(completeOriginalPOSITIONBounds=whole_bounds,requiredOriginalSheets=sorted(required),
            indexedSheetsCoverCompleteOriginalXZBounds=True,actualTINFiniteFacetCoverageStillRequired=True)

        assert not row['candidate']['entry'].get('footprintScope') and not row['candidate']['entry'].get('suppressesBuildingUids'),'Ordinary source-only candidate required'
        rows.append(row);contexts.append(context);results.append(routing);refs.append({'path':str(asset.relative_to(ROOT)),'sha256':digest(raw)})
        print(json.dumps({'uid':row['uid'],'identityPassed':identity['passed'],'identityReasons':identity['reasons'],'currentForms':len(forms),'canStartTerrainWork':routing['canStartTerrainWork']}),flush=True)
    assert [r['uid']for r in rows]==list(SOURCES) and all(digest((ROOT/r['path']).read_bytes())==r['sha256']for r in refs)
    assert digest(manifest.read_bytes())==current_sha and reservations.owns(lease);assert all(digest((ROOT/r['path']).read_bytes())==r['sha256']for r in catalogue_refs);refs.extend(catalogue_refs)
    DOC.mkdir(parents=True,exist_ok=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append({'path':str((DOC/'historical-current-manifest.json').relative_to(ROOT)),'sha256':digest(manifest.read_bytes())})
    save(DOC/'check-selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':current_sha});save(DOC/'context.json.gz',{'rows':contexts});save(DOC/'indexed-preflight.json',{'rows':results,'manifestSHA256':current_sha,'evidenceRefs':refs,'installationApproved':False,'publication':False,'sourceGeometryChanges':0})
    frozen=module('sparkle_ordinary_preflight_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');frozen.freeze(BATCH,'sparkle-pair-fresh-two-ordinary-identities-indexed-terrain-preflight-v1',[ROOT/r['path']for r in refs]+list(DOC.glob('*.json*')),dict(uids=[r['uid']for r in rows],allOrdinaryIdentitiesPassed=all(r['identity']['passed']for r in results),bothOriginalsCandidatesNoUnqualifiedSupportCredit=True,currentManifestSHA256=current_sha,currentAcceptance=False,newlyInstalled=0))
def main():
    if '--owned' in sys.argv:return owned()
    import uuid
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim('codex-sparkle-pair-preflight-'+str(uuid.uuid4()),['building:'+uid for uid in SOURCES],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',LEASE,'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
