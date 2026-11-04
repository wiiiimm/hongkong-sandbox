"""Fresh physical pass for one verified retained geographic group.

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
from man_fuk_current_bound_envelope_identity_v3_20261010 import verify_files
from man_fuk_named_original_envelope_identity_v3_20261010 import POLICY
UIDS = frozenset({'landsd/266062:0'})
PARENT_URL = 'city/data/terrain.json'
RETAIN_NATIVE_URL = 'city/data/government-native-75697-0.json'
INPUT = ROOT / 'docs/astra-city/government-import/government-xl-man-fuk-current-bound-envelope-inputs-v3-20261010'

BATCH = 'government-xl-man-fuk-complete-retained-original-physical-v6-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
BASE = LOCAL / 'frozen-inputs'


def module(name, file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def frozen():
    selected=read(INPUT/'selection.json.gz'); contexts=read(INPUT/'context.json.gz')
    assert {r['uid'] for r in selected['rows']}==UIDS
    assert {r['uid'] for r in contexts['rows']}==UIDS
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selected['manifestSHA256']
    assert RETAIN_NATIVE_URL in {p['url'] for p in read(ROOT/'3d-viewer/city/data/manifest.json')['terrainPatches']}, 'Exact retained Man Oi surface must be active'
    parent=read(ROOT/'3d-viewer'/PARENT_URL)
    assert not parent.get('nativeMesh') and not parent.get('patches')
    final=module('man_fuk_full_scope','xl-final-script-pass.py')
    second=module('man_fuk_full_cells','xl-second-pass.py')
    rects=[second.resolution.rectangle_for(r['native']['model']['worldBounds'],parent) for r in selected['rows']]
    retained=read(ROOT/'3d-viewer'/RETAIN_NATIVE_URL);old=retained['coarseCells']
    cells=[min(old[0],min(r[0] for r in rects)),min(old[1],min(r[1] for r in rects)),
           max(old[2],max(r[2] for r in rects)),max(old[3],max(r[3] for r in rects))]
    bounds=second.resolution.extent(cells,parent)
    scope={b['uid'] for b,_,_ in final.load_forms(bounds)}
    scope.update(retained['meta']['targetUids'])
    for row in selected['rows']:
        assert row.get('currentReview') is None
        row.setdefault('currentReview',None)
        row['triangles']=row['native']['model']['triangles']
    return {**selected,'batch':BATCH,'nativeRun':NATIVE_RUN},contexts,scope


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    selection=read(BASE/'check-selection.json.gz');contexts=read(BASE/'context.json.gz')
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
    identities=[]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        live={m['uid'] for u in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']}
        assert not (live & UIDS), 'Candidate is already installed'
        for row in selection['rows']:
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    for row in selection['rows']:
        context=next(c for c in contexts['rows'] if c['uid']==row['uid'])
        proof=verify_files(row,context,LOCAL/'identity-precheck'/row['uid'].split('/')[1]);assert proof['passed'],proof['reasons'];identities.append(proof)
    save(DOC/'owned-source-identity.json',{'rows':identities})
    identity_paths={}
    for proof in identities:
        target=DOC/('owned-identity-'+proof['uid'].split('/')[1].replace(':','-')+'.json')
        save(target,proof);identity_paths[proof['uid']]=target
    save(DOC/'retained-parent-routing.json',{'parentURL':PARENT_URL,'parentSHA256':digest((ROOT/'3d-viewer'/PARENT_URL).read_bytes()),'retainedNativeTerrainURL':RETAIN_NATIVE_URL,'retainedNativeTerrainSHA256':digest((ROOT/'3d-viewer'/RETAIN_NATIVE_URL).read_bytes()),'candidateOnlyOverlappingProjectionRetention':True,'sourceGeometryChanges':0,'publication':False})
    terrain=module('man_fuk_indexed_terrain','xl-routed-cell-indexed-terrain-continuation.py')
    index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'))
    sheets=sorted({s['sheet'] for row in selection['rows'] for s in index.covering_sheets(row['native']['model']['worldBounds'])})
    recovered=[terrain.terrain_sheet(s,LOCAL) for s in sheets]
    save(DOC/'source-recovery.json',{'sheets':[proof for _,proof in recovered],'sourceGeometryChanges':0,'publication':False})
    resolution=module('man_fuk_complete_terrain','xl-man-fuk-original-retained-terrain-candidate-producer-v6-20261010.py')
    resolution.BATCH=BATCH;resolution.BASE=BASE;resolution.DOC=DOC;resolution.LOCAL=LOCAL;resolution.UIDS=[r['uid'] for r in selection['rows']]
    resolution.PARENT_URL=PARENT_URL;resolution.NESTED_PARENT=False;resolution.RETAIN_NATIVE_URL=RETAIN_NATIVE_URL
    resolution.OWNED_IDENTITY_PATHS=identity_paths
    resolution.SOURCE=recovered[0][0];resolution.ADJACENT_SOURCES=[f for f,_ in recovered[1:]]
    reasons=[]
    try:
        resolution.owned()
    except (AssertionError,KeyError) as error:
        save(DOC/'guard-failure.json',{'error':str(error),'traceback':traceback.format_exc(),'publication':False})
        reasons.append('full-original-source-local-physical-route-guard:'+str(error))
    if not reasons:
        metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');foundation=read(DOC/'foundation.json')
        policy=module('man_fuk_numeric_policy','acceptance-policy.py')
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
    refs += [ref(p) for p in [Path(__file__),HERE/'man_fuk_current_bound_envelope_identity_v3_20261010.py',HERE/'man_fuk_named_original_envelope_identity_v3_20261010.py',INPUT/'result.json',INPUT/'current-inputs.json.gz',INPUT.parent/'government-xl-man-fuk-current-installed-related-original-binding-v2-20261010/result.json',HERE/'xl-man-fuk-original-retained-terrain-candidate-producer-v6-20261010.py',BASE/'check-selection.json.gz',BASE/'context.json.gz',ROOT/'3d-viewer/city/official-model-footprint-scopes.js',ROOT/'3d-viewer/city/official-model-footprint-scopes-ocean-walk.js',ROOT/'3d-viewer/city/official-model-direct-osm-group-footprint.js',ROOT/'3d-viewer/city/official-model-direct-osm-group-data.js',HERE/'acceptance-metrics-direct-osm-group-parent.mjs',ROOT/'3d-viewer/city/tests/official-model-direct-osm-group-footprint.test.js',ROOT/'3d-viewer/city/official-model-assets.js',ROOT/'3d-viewer/city/official-models.js',ROOT/'3d-viewer/city/building-geometry.js']]
    for filename in ['metrics.json','validation.json','neighbour-inputs.json.gz','native-neighbour-checks.json']:
        if (DOC/filename).exists():
            report=read(DOC/filename)
            refs.extend({'path':p,'sha256':sha} for p,sha in (report.get('inputHashes') or report.get('hashes') or {}).items())
    refs += [ref(ROOT / 'docs/astra-city/government-import/government-xl-man-fuk-current-physical-cause-partition-v1-20261010/result.json')]
    refs += [ref(HERE / filename) for filename in ['man_fuk_exact_recorded_height_metadata_20261010.py', 'test_man_fuk_exact_recorded_height_metadata_20261010.py', 'retained_original_nonheight_terrain_facets_20261010.py', 'test_retained_original_nonheight_terrain_facets_20261010.py', 'man_fuk_source_ledge_terrain_ceiling_20261010.py', 'test_man_fuk_source_ledge_terrain_ceiling_20261010.py', 'man_fuk_source_wall_terrain_exposure_20261010.py', 'test_man_fuk_source_wall_terrain_exposure_20261010.py', 'man_fuk_original_post_terrain_footings_20261010.py', 'test_man_fuk_original_post_terrain_footings_20261010.py']]
    refs=list({r['path']:r for r in refs}.values());payload={'uids':sorted(UIDS),'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in selection['rows']},'evidenceRefs':refs}
    stage='man-fuk-complete-original-retained-man-oi-terrain-candidate-v6';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'jobId':jid,'batch':BATCH,'scriptChecksPassed':not reasons,'reasons':sorted(set(reasons)),'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'sourceIdentityMethod':POLICY,'sourceIdentityReviewed':True,'sourceIdentityReviewUsedAI':True,'aiGeometryModelling':False,'terrainProposalChanges':['Replace old Man Oi terrain under complete platform projection', 'Lower one repeated candidate terrain vertex using two unchanged original upward ledges', 'Solve a second repeated terrain vertex against every finite original column at three unchanged wall vertices', 'Set five near-post repeated terrain vertices to four unchanged original post bottoms; leave higher Man Oi-side vertices unchanged'], 'qualification':'Explicit terrain-only source-ledge and exact finite original-wall exposure corrections; all government building geometry unchanged. Fresh reviewed complete Man Fuk envelope identity and exact installed Man Oi source binding. Full original-source/terrain/foundation/runtime/current native and basic neighbour gates unchanged. Candidate proposes retention only of old Man Oi height-bearing terrain outside the complete Man Fuk source projection. Terrain under Man Oi may change and its entire original native actor is tested without exemption. Every original record excluded by the height sampler is preserved literally, including its genuine vertical facet. Complete surface equivalence is not yet independently accepted. Exact authoritative recorded-top metadata correction changes no source geometry or placement; no collision/support/physics exemption or publication credit.'}
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
    if '--owned' in sys.argv:return owned() # Candidate-only full manifest start/end fences; no publication flock.
    assert not DOC.exists() and not LOCAL.exists(),'Fresh named pass required'
    selected,contexts,scope=frozen()

    resources=[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope|UIDS)]+['terrain-patch:'+u for u in sorted(UIDS)]+['terrain-surface:'+RETAIN_NATIVE_URL]
    claim=reservations.claim('codex-complete-man-fuk-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(BASE/'check-selection.json.gz',selected);save(BASE/'context.json.gz',contexts)
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
