"""Diagnose original scene ownership for the 196 frozen full-projection holds."""
import importlib.util
import json
import subprocess
import sys
import uuid
from collections import Counter
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,dict_row,Jsonb
from original_source_ownership import evidence

BATCH='government-xl-source-ownership-196-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH

def original_inputs():
    spec=importlib.util.spec_from_file_location('frozen_section_sources',HERE/'xl-source-section-diagnostic-20261006.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module,module.inputs()

def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    original,(checkpoint,held,sources,contexts,refs)=original_inputs()
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    refs += [manifest,Path(__file__),HERE/'original_source_ownership.py',HERE/'test_original_source_ownership.py']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');original.verify_native(con,sources)
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(checkpoint['jobId'],)).fetchone()==('complete',checkpoint)
    pinned=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in refs]
    rows=[]
    for uid,row in sources.items():
        assert reservations.owns(lease)
        raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
        assert row['native']['model']['asset']['bytes']==len(raw)
        assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
        for tile,sha in contexts[uid]['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
        result=evidence(raw,row,contexts[uid])
        result.update(nativeCacheKey=row['native']['cacheKey'],nativeResultSHA256=row['native']['resultSha'],
            previousFullProjectionHoldReasons=held[uid]['reasons'],modelGeometryChanges=0,scriptExternalAICalls=0,
            fullProjectionGateChanged=False,requiresAI=False,requiresHumanDecision=False)
        rows.append(result);path=DOC/(uid.split('/')[1].replace(':','-')+'.json.gz');save(path,result)
        pinned.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())})
    payload={'evidenceRefs':pinned,'sourceCheckpoint':checkpoint['jobId'],'runnerSHA256':digest(Path(__file__).read_bytes())}
    stage='original-government-source-scene-ownership-diagnostic-v1';jobid=jobs.enqueue(BATCH,stage,payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**payload,'jobId':jobid,'batch':BATCH,'rows':rows,'sourcesChecked':196,
        'sourceGraphsVerified':sum(r['sourceGraphVerified'] for r in rows),
        'provenanceAndSpatialDiagnosticsPassed':sum(r['provenanceAndSpatialDiagnosticPassed'] for r in rows),
        'reasonCounts':dict(Counter(x for r in rows for x in r['reasons'])),
        'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'fullProjectionGateChanged':False,'qualification':'Independent full original graph ownership evidence. This phase grants no identity, architecture or installation approval; existing full-source and all downstream gates are unchanged. The 100-new-XL target remains active.'}
    for ref in pinned:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    with connect() as con:
        con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));original.verify_native(con,sources)
        con.row_factory=dict_row;assert reservations._current(con,lease)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({k:result[k] for k in ['jobId','sourcesChecked','sourceGraphsVerified','provenanceAndSpatialDiagnosticsPassed','reasonCounts','newlyInstalled']}),flush=True)

def start():
    assert not DOC.exists(),'Fresh immutable stage only'
    _,(_,held,_,_,_)=original_inputs()
    claim=reservations.claim('codex-xl-source-ownership-'+str(uuid.uuid4()),['building:'+uid for uid in held],batch=BATCH);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)

if __name__=='__main__':owned() if sys.argv[1:]==['owned'] else start()
