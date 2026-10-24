"""Fenced exact topology and original support-ray diagnosis for Fung Courts. No acceptance."""
import json
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,dict_row,Jsonb,NATIVE_RUN

BATCH='government-xl-fung-support-topology-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
SCOPES=[('government-xl-three-fung-original-supports-recovered-20261006', ['landsd/79099:0','landsd/79097:0','landsd/79098:0'])]
def inputs():
    refs=[];sources={};scope=[]
    for batch,uids in SCOPES:
        previous=ROOT/'docs/astra-city/government-import'/batch
        result=read(previous/'result.json');assert read(previous/'neon-sync.json')['resultVerified']
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
        pairs=[r for r in result['rows'] if r['uid'] in uids];assert len(pairs)==len(uids)
        wanted=set(uids)|{r['supportUid'] for r in pairs}
        rows=read(previous/'support-inputs.json')['sources']
        sources.update({r['uid']:r for r in rows if r['uid'] in wanted})
        refs += [previous/n for n in ['result.json','neon-sync.json','support-inputs.json','support-checks.json.gz']]
        scope.append({'previous':str(previous.relative_to(ROOT)),'uids':uids})
    return sources,refs,scope

def verify_sources(con,sources):
    for row in sources.values():
        assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
        assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
        actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual[0]==row['native']['resultSha']

def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    sources,refs,scope=inputs()
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');verify_sources(con,sources)
    save(DOC/'inputs.json',{'scopes':scope,'sourceUids':sorted(sources)})
    subprocess.run(['node',str(HERE/'support-boundary-diagnostic.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
    diagnostic=read(DOC/'boundary-rays.json.gz')
    for path,pinned in diagnostic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pinned
    import importlib.util
    from source_closed_components import components
    spec=importlib.util.spec_from_file_location('support_topology_decoder',HERE/'xl-second-pass.py')
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
    decoder.LOCAL=LOCAL
    topology=[]
    for uid,row in sources.items():
        raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
        path=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        triangles=decoder.glb_triangles(row)
        proof=components(triangles)
        proof.update(uid=uid,sourceSHA256=row['sourceSHA256'])
        topology.append(proof)
    save(DOC/'original-edge-topology.json.gz',{'rows':topology,'publication':False,'modelGeometryChanges':0})
    refs += [Path(__file__),HERE/'support-boundary-diagnostic.mjs',DOC/'inputs.json',DOC/'boundary-rays.json.gz',
             HERE/'source_closed_components.py',HERE/'test_source_closed_components.py',HERE/'xl-second-pass.py',DOC/'original-edge-topology.json.gz']
    payload={'evidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in refs]}
    stage='exact-original-support-edge-topology-and-boundary-rays-v1';jobid=jobs.enqueue(BATCH,stage,payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**payload,'jobId':jobid,'batch':BATCH,'rows':diagnostic['rows'],'newlyInstalled':0,
        'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'topologySummaries':[{'uid':r['uid'],'triangles':r['triangles'],'components':len(r['components']),
             'closedComponents':sum(c['closedConsistentlyWound'] for c in r['components'])} for r in topology],
        'qualification':'Boundary rays explain failed contacts. No original highest-surface contact, full-source identity, terrain, foundation or runtime acceptance is changed.'}
    for ref in payload['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));verify_sources(con,sources)
        con.row_factory=dict_row;assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'jobId':jobid,'neonVerified':True,'newlyInstalled':0}),flush=True)

def start():
    assert not DOC.exists(),'Fresh immutable stage required'
    sources,_,_=inputs()
    claim=reservations.claim('codex-xl-support-rays-'+str(uuid.uuid4()),['building:'+uid for uid in sorted(sources)],batch=BATCH);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)

if __name__=='__main__':owned() if sys.argv[1:]==['owned'] else start()
