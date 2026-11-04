"""Bounded first pass of all XXL sources. Original meshes only; no AI or exception remodelling."""
import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN,jobs,reservations,dict_row,Jsonb
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
spec=importlib.util.spec_from_file_location('acceptance_policy',HERE/'acceptance-policy.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
BATCH='government-xxl-20260911'
LOCAL=HERE/'local'/BATCH
DOC=ROOT/'docs/astra-city/government-import'/BATCH


def command(args): return subprocess.run(args,cwd=ROOT,check=True)
def h(path): return digest(Path(path).read_bytes())
def rel(path): return str(Path(path).relative_to(ROOT))


def initial_reason(native, source, review, installed):
    m=native['model'];e=m.get('candidate');reasons=[]
    if not e or not source:return 'held-unknown',['no-unique-current-viewer-match']
    b=source['building'];same_identity=(e['uid']==b['uid'] and e['buildingCSUID']==b.get('buildingCSUID') and e['objectId']==b.get('objectId'))
    if not same_identity: reasons.append('current-source-identity-changed')
    if e['recordedBaseHeight']!=b.get('baseHeightHKPD') or e['recordedTopHeight']!=b.get('topHeightHKPD'):reasons.append('current-source-heights-changed')
    if installed:
        if not reasons and installed['sha256']==e['sha256'] and review and review['state']=='installed-verified' and review['sha']==e['sha256']:
            return 'installed',[]
        return 'held-unknown',reasons+['existing-installed-model-needs-explicit-resolution']
    if m['state']!='packed-needs-placement-review':reasons.append('native-preparation-held')
    if e['overlapOfSmallerFootprint']<.98 or e['footprintCentroidDistanceMetres']>1:reasons.append('strict-identity-fit')
    if review and review['state'] in ('held','source-unavailable','identity-unresolved','installed-verified'):reasons.append('existing-review-requires-resolution')
    if b.get('modelGeometry'):reasons.append('existing-embedded-model')
    return ('held-unknown' if reasons else 'in-process'),reasons


def prepare():
    if LOCAL.exists():raise ValueError('Frozen batch exists; inspect it and resume explicitly')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        entries=c.execute("SELECT cache_key,model_id,viewer_uid FROM astra_modelling.native_model_sizes WHERE run_id=%s AND size_group='xxl' ORDER BY triangles DESC,cache_key,model_id",(NATIVE_RUN,)).fetchall()
        keys=[r[0] for r in entries];model_ids=[r[1] for r in entries];uids=[r[2] for r in entries if r[2]]
        source_rows=c.execute("SELECT r.cache_key,r.result_sha,i.sheet,x FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE r.cache_key=ANY(%s) AND x->>'modelId'=ANY(%s)",(keys,model_ids)).fetchall()
        reviews=dict(c.execute("SELECT DISTINCT ON(uid) uid,jsonb_build_object('state',review_state,'sha',source_sha256) FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC",(uids,)))
    native={(k,m['modelId']):{'cacheKey':k,'resultSha':sha,'sheet':sheet,'model':m} for k,sha,sheet,m in source_rows}
    assert len(entries)==22 and set(native)=={(k,m) for k,m,u in entries}
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={};sources={}
    for url in manifest.get('officialModelCatalogues',[]):
        for e in read(ROOT/'3d-viewer'/url)['models']:
            if e['uid'] in uids:
                path=(ROOT/'3d-viewer'/url).parent/e['asset'];assert h(path)==e['sha256']
                installed[e['uid']]={**e,'catalogue':url,'catalogueSHA256':h(ROOT/'3d-viewer'/url),'path':rel(path)}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes()
        for b in json.loads(raw)['buildings']:
            if b['uid'] in uids:sources[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(raw)}
    rows=[]
    for k,m,uid in entries:
        o=native[k,m];status,reasons=initial_reason(o,sources.get(uid),reviews.get(uid),installed.get(uid))
        rows.append({'modelId':m,'uid':uid,'native':o,'source':sources.get(uid),'previousReview':reviews.get(uid),'installedProof':installed.get(uid),'humanStatus':status,'reasons':reasons,'name':sources.get(uid,{}).get('building',{}).get('name'),'sourceSHA256':o['model']['asset']['sha256'],'triangles':o['model']['triangles']})
    frozen={'batch':BATCH,'nativeRun':NATIVE_RUN,'rows':rows,'manifestSHA256':h(ROOT/'3d-viewer/city/data/manifest.json'),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'aiCalls':0}
    save(LOCAL/'selection.json.gz',frozen);save(DOC/'selection.json.gz',frozen)
    check=[r for r in rows if r['humanStatus']=='in-process']
    evidence={'nativeRun':NATIVE_RUN,'rows':[r['uid'] for r in check],'sources':{r['uid']:r['source'] for r in check},'native':[r['native'] for r in check]}
    save(LOCAL/'recovery-inputs.json.gz',evidence)
    # Reuse exact pilot caches when present. Never read screening scores or rerun screening.
    cache=LOCAL/'recovered/assets';cache.mkdir(parents=True,exist_ok=True)
    for r in check:
        name=r['sourceSHA256']+'.glb.gz'
        for folder in ['local/shapes/assets','local/shape-5000/assets']:
            src=HERE.parent/'enhancement-screening'/folder/name
            if src.exists() and h(src)==r['sourceSHA256']:shutil.copyfile(src,cache/name);break
    print(json.dumps({'scope':len(rows),'counts':dict(Counter(r['humanStatus'] for r in rows)),'detailedCheckModels':len(check)}),flush=True)
    return frozen


def recover():
    frozen=read(LOCAL/'selection.json.gz')
    assert h(ROOT/'3d-viewer/city/data/manifest.json')==frozen['manifestSHA256']
    return shape_prepare.prepare(LOCAL/'recovery-inputs.json.gz',LOCAL/'recovered',allow_source=True,workers=4,env_file=ROOT/'.env.modelling')


def start_checks():
    frozen=read(LOCAL/'selection.json.gz')
    receipt=reservations.claim('codex-xxl-'+str(uuid.uuid4()),['building:'+r['uid'] for r in frozen['rows'] if r['uid']],batch=BATCH)
    assert receipt['ok'],'Existing source owner; no takeover'
    save(LOCAL/'reservation.json',json.loads(json.dumps(receipt['reservation'],default=str)))
    command([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'check-owned'])


def check_owned():
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    frozen=read(LOCAL/'selection.json.gz');assert h(ROOT/'3d-viewer/city/data/manifest.json')==frozen['manifestSHA256']
    recovered=read(LOCAL/'recovered/geometry-inputs.json');by_uid={r['uid']:r for r in recovered['rows']}
    chosen=[]
    for r in frozen['rows']:
        if r['source']:assert h(ROOT/'3d-viewer'/r['source']['tile'])==r['source']['tileSHA256']
        if r['installedProof']:assert h(ROOT/r['installedProof']['path'])==r['sourceSHA256']
        if r['humanStatus']=='in-process' and r['uid'] in by_uid:
            x=by_uid[r['uid']];chosen.append({'uid':r['uid'],'source':r['source'],'candidate':x['candidate'],'native':r['native']})
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        actual=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN,[r['native']['cacheKey'] for r in frozen['rows']])))
    assert all(actual.get(r['native']['cacheKey'])==r['native']['resultSha'] for r in frozen['rows'])
    selection={**frozen,'rows':chosen};save(DOC/'check-selection.json.gz',selection)
    catalogue={k:v for k,v in read(HERE.parent/'kai-tak-port/staged/catalogue.json').items() if k not in ('models','counts','area')}
    catalogue.update(area=BATCH,models=[r['candidate']['entry'] for r in chosen],counts={'packedModels':len(chosen)})
    save(LOCAL/'recovered/catalogue.json',catalogue);save(LOCAL/'recovered/catalogue-index.json',{'models':len(chosen),'catalogues':['catalogue.json']})
    save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in chosen})
    payload={'selectionSHA256':h(DOC/'selection.json.gz'),'checkSelectionSHA256':h(DOC/'check-selection.json.gz'),'pipelineSHA256':digest(b''.join(p.read_bytes() for p in [Path(__file__),HERE/'acceptance-metrics.mjs',HERE/'acceptance-policy.py',HERE.parent/'building-batch/validate_candidates.mjs']))}
    job_id=jobs.enqueue(BATCH,'government-xxl-checks-v1',payload);job=jobs.claim(BATCH,receipt['owner'],['government-xxl-checks-v1'],lease_seconds=1800);assert job and job['id']==job_id
    if chosen:
        cmd=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL/'recovered'),'--source-forms',rel(LOCAL/'source-forms.json'),'--out',rel(DOC/'validation.json')]
        v=subprocess.run(cmd,cwd=ROOT);assert v.returncode in (0,1) and (DOC/'validation.json').exists()
        command(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'check-selection.json.gz'),'--candidates',rel(LOCAL/'recovered'),'--out',rel(DOC/'metrics.json')])
        metrics=read(DOC/'metrics.json');validation=read(DOC/'validation.json');by_metric={r['uid']:r for r in metrics['rows']};by_validation={r['uid']:r for r in validation['results']}
        assert set(by_metric)==set(by_validation)=={r['uid'] for r in chosen}
    else:metrics={'inputHashes':{}};by_metric={};by_validation={}
    outcomes=[]
    for r in frozen['rows']:
        row={k:v for k,v in r.items() if k not in ('native','source','installedProof')}
        row.update(nativeCacheKey=r['native']['cacheKey'],nativeResultSHA256=r['native']['resultSha'],sourceSheet=r['native']['sheet'],aiCalls=0,sourceEvidence=rel(DOC/'selection.json.gz'))
        if r['humanStatus']=='in-process':
            uid=r['uid']
            if uid not in by_metric:row['reasons']=['source-recovery-failed'];row['recoveryError']=recovered['errors'].get(uid,'No exact asset recovered')
            else:
                v=by_validation[uid];m=by_metric[uid];row['validation']=v;row['metrics']=m
                row['reasons']=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':r['sourceSHA256']},m,metrics['profiles']['mobile'])
                if v['outcome']=='validation-exception':row['reasons'].append('runtime-validation-exception')
                row['reasons']=sorted(set(row['reasons']+v.get('concerns',[])))
            row['humanStatus']='held-unknown' if row['reasons'] else 'in-process'
        row['state']='installed-verified' if row['humanStatus']=='installed' else 'script-validated-awaiting-browser-publication' if row['humanStatus']=='in-process' else 'held-for-second-pass'
        row['nextStep']=None if row['humanStatus']=='installed' else 'Complete staged/installed browser checks and guarded publication' if row['humanStatus']=='in-process' else 'Resolve recorded source/terrain/support evidence in the grouped second pass; no AI or human decision dependency established'
        outcomes.append(row)
    counts={key:sum(r['humanStatus']==key for r in outcomes) for key in ['installed','to-do','held-human','held-ai','held-unknown','in-process']}
    report={'batch':BATCH,'stage':'government-xxl-checks-v1','jobId':job_id,'nativeRun':NATIVE_RUN,'models':len(outcomes),'humanCounts':counts,'newlyInstalled':0,'rows':outcomes,'inputHashes':metrics['inputHashes'],'acquisition':{k:v for k,v in recovered.items() if k not in ('rows','errors')},'sourceHashesVerified':True,'aiCalls':0,'geometryChanges':0,'qualification':'Broad first pass; exact installed sources reused and exceptions retained for second pass. No AI modelling or acceptance from triangle counts.'}
    save(DOC/'results.json.gz',report);evidence={'path':rel(DOC/'results.json.gz'),'sha256':h(DOC/'results.json.gz')};result={**report,'evidence':evidence}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(c,receipt)
        assert group and {'building:'+r['uid'] for r in frozen['rows'] if r['uid']}<=set(group['resources'])
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),job_id,job['owner'],job['token'])).rowcount==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(job_id,)).fetchone()[0]==result
    save(DOC/'summary.json',{k:v for k,v in report.items() if k not in ('rows','inputHashes')})
    save(DOC/'neon-sync.json',{'jobId':job_id,'verifiedRows':len(outcomes),'exactResultMatch':True,'sourceAndJobFenced':True,'reviewWrites':0})
    print(json.dumps({'humanCounts':counts,'readyForPublication':[r['uid'] for r in outcomes if r['humanStatus']=='in-process'],'jobId':job_id}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['prepare','recover','check','check-owned']);a=p.parse_args()
    {'prepare':prepare,'recover':recover,'check':start_checks,'check-owned':check_owned}[a.phase]()
