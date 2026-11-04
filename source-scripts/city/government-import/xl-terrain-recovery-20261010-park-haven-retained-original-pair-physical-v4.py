"""Reusable fresh full current physical pass for one exact ordinary provider source.

No model geometry changes or automatic publication. Complete geographic component scope retains all other forms.
Original source-local terrain and every physical limit are checked unchanged.
"""
import importlib.util,argparse,re
import json
from pathlib import Path
import subprocess
import sys
import traceback
import uuid
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs, Jsonb, dict_row, NATIVE_RUN
from terrain_source_preflight import SourceSheetIndex
from exact_original_georef_cell_identity_20261009 import verify_files,POLICY
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--uid',required=True,action='append');parser.add_argument('--preflight',required=True);parser.add_argument('--batch',required=True);parser.add_argument('--retain-native',action='append',default=[]);parser.add_argument('--owned',action='store_true')
args=parser.parse_args();assert all(re.fullmatch(r'landsd/\d+:0',u) for u in args.uid) and re.fullmatch(r'[a-z0-9-]+',args.batch)
UIDS=frozenset(args.uid);assert len(UIDS)==len(args.uid);UID=sorted(UIDS)[0];RETAINED_URLS=sorted(set(args.retain_native));BATCH=args.batch;DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;BASE=LOCAL/'frozen-inputs'


def module(name, file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def frozen():
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    primary=read(ROOT/args.preflight/'check-selection.json.gz')
    assert primary['manifestSHA256']==digest(manifest.read_bytes())
    selected=primary
    rows = [r for r in selected['rows'] if r['uid'] in UIDS]; assert len(rows)==len(UIDS)
    for row in rows:
        row.setdefault('currentReview',None);row.setdefault('historicallyPublished',False)
        row['triangles']=row['native']['model']['triangles']
    assert all(r['currentReview'] is None for r in rows)
    final=module('market_frozen_forms','xl-final-script-pass.py'); second=module('market_frozen_terrain','xl-second-pass.py')
    parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    rects=[second.resolution.rectangle_for(r['native']['model']['worldBounds'],parent) for r in rows]
    cells=[min(r[0] for r in rects),min(r[1] for r in rects),max(r[2] for r in rects),max(r[3] for r in rects)]
    for url in RETAINED_URLS:
        old=read(ROOT/'3d-viewer'/url);assert old.get('nativeMesh') and not old.get('patches')
        c=old['coarseCells'];cells=[min(cells[0],c[0]),min(cells[1],c[1]),max(cells[2],c[2]),max(cells[3],c[3])]
    bounds=second.resolution.extent(cells,parent); scope={b['uid'] for b,_,_ in final.load_forms(bounds)}
    contexts=[]
    decoder=module('market_context_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
    (LOCAL/'assets').mkdir(parents=True)
    for row in rows:
        raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
        (LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw)
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
    assert sorted(UIDS)==['landsd/246467:0','landsd/320705:0'] and RETAINED_URLS==['city/data/government-native-246270-0.json']
    resolution=module('market_complete_terrain','xl-terrain-recovery-20261010-park-haven-retained-original-pair-contact-v4.py')
    resolution.BATCH=BATCH;resolution.BASE=BASE;resolution.DOC=DOC;resolution.LOCAL=LOCAL;resolution.UIDS=[r['uid'] for r in selection['rows']]
    resolution.RETAIN_NATIVE_URLS=RETAINED_URLS
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
        if validation['checksPassed']!=len(UIDS) or validation['loaderAccepted']!=len(UIDS) or validation['exceptions']:reasons.append('runtime-validation')
        native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved'])
        reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved)
        reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    refs=[ref(p) for p in sorted(DOC.iterdir()) if p.is_file() and p.name not in ['result.json','neon-sync.json']]
    refs += [ref(p) for p in [Path(__file__),HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-terrain-recovery-20261010-park-haven-retained-original-pair-contact-v4.py',BASE/'check-selection.json.gz',BASE/'context.json.gz',ROOT/'3d-viewer/city/official-model-footprint-scopes.js',ROOT/'3d-viewer/city/official-model-footprint-scopes-ocean-walk.js',ROOT/'3d-viewer/city/official-model-direct-osm-group-footprint.js',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js',HERE/'acceptance-metrics-direct-osm-group-parent.mjs',ROOT/'3d-viewer/city/tests/official-model-direct-osm-group-footprint.test.js',ROOT/'3d-viewer/city/official-model-assets.js',ROOT/'3d-viewer/city/official-models.js',ROOT/'3d-viewer/city/building-geometry.js']]
    for filename in ['metrics.json','validation.json','neighbour-inputs.json.gz','native-neighbour-checks.json']:
        if (DOC/filename).exists():
            report=read(DOC/filename)
            refs.extend({'path':p,'sha256':sha} for p,sha in (report.get('inputHashes') or report.get('hashes') or {}).items())
    refs=list({r['path']:r for r in refs}.values());payload={'uids':sorted(UIDS),'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in selection['rows']},'evidenceRefs':refs}
    stage='park-haven-two-original-retained-current-physical-v4';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'scriptChecksPassed':not reasons,'reasons':sorted(set(reasons)),'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'terrainProposalGeometryChanged':True,'disjointProjectionProtectionAccepted':False,'scriptExternalAICalls':0,'sourceIdentityMethod':POLICY,'sourceIdentityReviewed':True,'sourceIdentityReviewUsedAI':False,'aiGeometryModelling':False,'qualification':'Explicit NEW terrain-only proposal restores the current native parent under every complete original246270 face projection, including measured overlap with owned original246467. Previous disjoint protection failure stays immutable. Full current foreign/native/source/foundation/runtime gates remain unchanged and no automatic root or identity credit. Fresh complete distinct original Park Haven tower/podium pair under their individually verified exact provider identities. No source footprint exemption, common ownership claim or automatic support credit. Unchanged original source geometry. Full original terrain/source/foundation/runtime/neighbour checks; no browser or installation credit yet.'}
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
    if args.owned:return owned()
    assert not DOC.exists() and not LOCAL.exists(),'Fresh named pass required'
    selected,contexts,scope=frozen()

    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope|UIDS)]+['terrain-patch:'+u for u in sorted(UIDS)]+['terrain-surface:'+u for u in RETAINED_URLS]
    claim=reservations.claim('codex-complete-market-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(BASE/'check-selection.json.gz',selected);save(BASE/'context.json.gz',contexts)
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*[arg for u in sorted(UIDS) for arg in ['--uid',u]],'--preflight',args.preflight,'--batch',BATCH,'--owned',*[arg for url in RETAINED_URLS for arg in ['--retain-native',url]]],cwd=ROOT,check=True)


if __name__=='__main__':main()
