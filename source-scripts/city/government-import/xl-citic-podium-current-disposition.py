"""Fresh original identity and physical checks for the historical CITIC podium dependency.

Retains deployed models and original bytes. Never waives current limits or
retroactively grants installed verification from a historical browser image.
"""
import importlib.util
import subprocess
import uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row,NATIVE_RUN
from government_georef_cell_identity import verify_files,POLICY

BATCH='government-xl-citic-podium-current-disposition-20261008'
UIDS=['landsd/232579:0']
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert not DOC.exists()
    claim=reservations.claim('codex-xl-legacy-current-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH)
    assert claim['ok'],claim
    lease=claim['reservation']
    from publication_lock import locked_publication
    guard=locked_publication(ROOT);guard.__enter__()
    try:
        manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
        models={m['uid']:(m,ROOT/'3d-viewer'/url) for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models'] if m['uid'] in UIDS}
        sources={}
        for tile in manifest['tiles']:
            p=ROOT/'3d-viewer'/tile['url']
            for b in read(p)['buildings']:
                if b['uid'] in UIDS:sources[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(p.read_bytes())}
        assert set(sources)==set(models)==set(UIDS)
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            native=con.execute("SELECT p.viewer_uid,p.cache_key,p.source_result_sha,p.sheet,x FROM astra_modelling.native_model_sizes p JOIN astra_modelling.native_stage_results r USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE p.run_id=%s AND p.viewer_uid=ANY(%s) AND x->>'modelId'=p.model_id",(NATIVE_RUN,UIDS)).fetchall()
        rows=[]
        for uid,key,sha,sheet,n in native:
            deployed,cat=models[uid];entry={**deployed,'rootTranslation':read(cat)['rootTranslation'],'overlapOfSmallerFootprint':n['candidate']['overlapOfSmallerFootprint'],'footprintCentroidDistanceMetres':n['candidate']['footprintCentroidDistanceMetres']};asset=cat.parent/entry['asset']
            assert digest(asset.read_bytes())==entry['sha256']==n['asset']['sha256']
            rows.append({'uid':uid,'sourceSHA256':entry['sha256'],'source':sources[uid],
                         'native':{'cacheKey':key,'resultSha':sha,'sheet':sheet,'model':n},
                         'candidate':{'entry':entry,'path':str(asset.relative_to(ROOT))}})
        assert len(rows)==1
        closure=ROOT/'docs/astra-city/government-import/government-xl-four-towers-original-supports-20261006'
        complete=next(r for r in read(closure/'support-inputs.json')['sources'] if r['uid']==UIDS[0])
        context=next(r for r in read(closure/'context.json.gz')['rows'] if r['uid']==UIDS[0])
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(UIDS[0],)).fetchone() is None
        assert rows[0]['sourceSHA256']==complete['sourceSHA256']
        positive=verify_files(complete,context,LOCAL/'identity-current')
        save(DOC/'owned-source-identity.json',positive)
        save(DOC/'identity-context.json',context)
        save(DOC/'selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':digest(manifest_path.read_bytes())})
        catalogue=read(models[UIDS[0]][1]);catalogue.update(area=BATCH,models=[r['candidate']['entry'] for r in rows])
        # Local catalogue resolves its original assets through unchanged copied bytes.
        for row in rows:
            entry=row['candidate']['entry'];dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/row['candidate']['path']).read_bytes())
        save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',{'models':len(rows),'catalogues':['catalogue.json']})
        save(LOCAL/'source-forms.json',sources);save(DOC/'terrain-candidates.json',[])
        rel=lambda p:str(p.relative_to(ROOT))
        cmd=['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')]
        subprocess.run(cmd,cwd=ROOT,check=True)
        metrics=read(DOC/'metrics.json');geometry=read(LOCAL/'runtime-geometry.json.gz')
        for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
        assert digest(manifest_path.read_bytes())==read(DOC/'selection.json.gz')['manifestSHA256']
        final=module('legacy_foundation','xl-final-script-pass.py');policy=module('legacy_policy','acceptance-policy.py')
        outcomes=[]
        for row in rows:
            uid=row['uid'];g=next(r for r in geometry['rows'] if r['uid']==uid);m=next(r for r in metrics['rows'] if r['uid']==uid)
            triangles=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
            ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
            f=final.foundation_context(triangles,ground,Polygon(b['rings'][0],b['rings'][1:]))
            accepted=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0
            reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},m,metrics['profiles']['mobile'])
            if not positive['passed']:reasons.extend(positive['reasons'])
            if not accepted:reasons.append('whole-source-foundation')
            outcomes.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'reasons':sorted(set(reasons)),
                             'scriptChecksPassed':not reasons,'foundation':f,'strictFoundationAccepted':accepted,
                             'metrics':m,'identity':positive,'historicallyPublished':True,'retainCurrentModel':True,
                             'qualification':'Fresh current-rendered-terrain physical checks. Existing publication retained; no source identity exception inferred from old acceptance. Failures prevent new installed verification; a passing result would still require the missing identity/browser evidence.'})
        save(DOC/'physical-results.json',{'rows':outcomes})
        refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [*DOC.iterdir(),__import__('pathlib').Path(__file__).resolve()]]
        payload={'uids':UIDS,'evidenceRefs':refs};stage='citic-original-podium-current-physical-disposition-v1'
        jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'batch':BATCH,'stage':stage,'jobId':jid,'rows':outcomes,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print({'jobId':jid,'rows':[{'uid':r['uid'],'reasons':r['reasons']} for r in outcomes]})
    finally:
        guard.__exit__(None,None,None)
        assert reservations.release(lease)

if __name__=='__main__':main()
