"""Fresh joint full physical pass for two complete original market halls.

No model geometry changes or automatic publication. Complete geographic component scope retains all other forms.
Original source-local terrain and every physical limit are checked unchanged.
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import traceback
import uuid
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN
from terrain_source_preflight import SourceSheetIndex
from ocean_walk_complete_source_identity import verify_files, POLICY, UIDS

BATCH = 'government-xl-ocean-walk-complete-source-local-20261008'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
BASE = LOCAL / 'frozen-inputs'


def module(name, file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def frozen():
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    selected = read(ROOT / 'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz')
    rows = [{**r,'currentReview':None} for r in selected['rows'] if r['uid'] in UIDS]; assert len(rows)==1
    final=module('market_frozen_forms','xl-final-script-pass.py'); second=module('market_frozen_terrain','xl-second-pass.py')
    parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    rects=[second.resolution.rectangle_for(r['native']['model']['worldBounds'],parent) for r in rows]
    cells=[min(r[0] for r in rects),min(r[1] for r in rects),max(r[2] for r in rects),max(r[3] for r in rects)]
    bounds=second.resolution.extent(cells,parent); scope={b['uid'] for b,_,_ in final.load_forms(bounds)}
    contexts=[]
    decoder=module('market_context_decoder','xl-second-pass.py');decoder.LOCAL=HERE/'local/government-xl-22-complete-group-official-context-v2-20261008'
    for row in rows:
        lo,hi=row['native']['model']['worldBounds']; forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
        tri=decoder.glb_triangles(row)
        contexts.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),
            'neighbourTileHashes':{url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms}})
    return {'rows':rows,'batch':BATCH,'manifestSHA256':digest(manifest.read_bytes()),'nativeRun':NATIVE_RUN},{'rows':contexts},scope


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    selection=read(BASE/'check-selection.json.gz');contexts=read(BASE/'context.json.gz')
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
    identities=[]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert not con.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=ANY(%s)',(sorted(UIDS),)).fetchall()
        for row in selection['rows']:
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    for row in selection['rows']:
        context=next(c for c in contexts['rows'] if c['uid']==row['uid'])
        proof=verify_files(row,context,LOCAL/'identity-precheck'/row['uid'].split('/')[1]);assert proof['passed'],proof['reasons'];identities.append(proof)
    save(DOC/'owned-source-identity.json',{'rows':identities})
    terrain=module('market_indexed_terrain','xl-routed-cell-indexed-terrain-continuation.py')
    index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'))
    sheets=sorted({s['sheet'] for row in selection['rows'] for s in index.covering_sheets(row['native']['model']['worldBounds'])})
    recovered=[terrain.terrain_sheet(s,LOCAL) for s in sheets]
    save(DOC/'source-recovery.json',{'sheets':[proof for _,proof in recovered],'sourceGeometryChanges':0,'publication':False})
    resolution=module('market_complete_terrain','xl-ocean-walk-complete-source-local-contact-resolution.py')
    resolution.BATCH=BATCH;resolution.BASE=BASE;resolution.DOC=DOC;resolution.LOCAL=LOCAL;resolution.UIDS=[r['uid'] for r in selection['rows']]
    resolution.SOURCE=recovered[0][0];resolution.ADJACENT_SOURCES=[f for f,_ in recovered[1:]]
    reasons=[]
    try:
        resolution.owned()
    except (AssertionError,KeyError) as error:
        save(DOC/'guard-failure.json',{'error':str(error),'traceback':traceback.format_exc(),'publication':False})
        reasons.append('full-original-source-local-physical-route-guard:'+str(error))
    if not reasons:
        metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');foundation=read(DOC/'foundation.json')
        policy=module('market_numeric_policy','acceptance-policy.py')
        from terrain_diagnostic_resolution import resolve_global_bottom_warning
        decisions=[]
        for row in selection['rows']:
            uid=row['uid'];m=next(r for r in metrics['rows'] if r['uid']==uid);f=next(r for r in foundation['rows'] if r['uid']==uid)
            positive=next(p for p in identities if p['uid']==uid)
            raw=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},m,metrics['profiles']['mobile'])
            diagnostic=resolve_global_bottom_warning(next(v for v in validation['results'] if v['uid']==uid),m,f)
            reasons.extend(uid+':'+r for r in [*raw,*diagnostic['remaining']])
            if not f['strictFoundationAccepted']:reasons.append(uid+':whole-source-foundation')
            decisions.append({'uid':uid,'numericReasons':raw,'diagnosticResolution':diagnostic})
        save(DOC/'physical-decisions.json',{'rows':decisions})
        if validation['checksPassed']!=1 or validation['loaderAccepted']!=1 or validation['exceptions']:reasons.append('runtime-validation')
        native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved'])
        reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved)
        reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    refs=[ref(p) for p in sorted(DOC.iterdir()) if p.is_file() and p.name not in ['result.json','neon-sync.json']]
    refs += [ref(p) for p in [Path(__file__),HERE/'ocean_walk_complete_source_identity.py',HERE/'xl-ocean-walk-complete-source-local-contact-resolution.py',BASE/'check-selection.json.gz',BASE/'context.json.gz',ROOT/'3d-viewer/city/official-model-footprint-scopes.js',ROOT/'3d-viewer/city/official-model-footprint-scopes-ocean-walk.js',ROOT/'3d-viewer/city/official-model-assets.js',ROOT/'3d-viewer/city/official-models.js',ROOT/'3d-viewer/city/building-geometry.js']]
    for filename in ['metrics.json','validation.json','neighbour-inputs.json.gz','native-neighbour-checks.json']:
        if (DOC/filename).exists():
            report=read(DOC/filename)
            refs.extend({'path':p,'sha256':sha} for p,sha in (report.get('inputHashes') or report.get('hashes') or {}).items())
    refs=list({r['path']:r for r in refs}.values());payload={'uids':sorted(UIDS),'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in selection['rows']},'evidenceRefs':refs}
    stage='complete-market-original-terrain-full-physical-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'scriptChecksPassed':not reasons,'reasons':sorted(set(reasons)),'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceIdentityMethod':POLICY,'sourceIdentityReviewed':True,'sourceIdentityReviewUsedAI':True,'aiGeometryModelling':False,'qualification':'Fresh complete same-building official footprint scope with unchanged original source geometry. Full original terrain/source/foundation/runtime/neighbour checks; no browser or installation credit yet.'}
    try:
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'scriptChecksPassed':not reasons,'reasons':result['reasons'],'neonVerified':True}),flush=True)
    except Exception as error:
        jobs.finish(job,error=str(error));raise


def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists(),'Fresh named pass required'
    selected,contexts,scope=frozen()
    
    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope|UIDS)]+['terrain-patch:'+u for u in sorted(UIDS)]
    claim=reservations.claim('codex-complete-market-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(BASE/'check-selection.json.gz',selected);save(BASE/'context.json.gz',contexts)
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
