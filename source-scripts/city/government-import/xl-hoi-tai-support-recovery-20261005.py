"""Recover the exact original upper Hoi Tai House component for full source interface checks."""
import json
from pathlib import Path
import subprocess
import sys
import uuid
import zipfile
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import canonical_bytes,entry,scan,acquire,_convert_one

GROUP=sys.argv[1]
CONFIG={'hoi-tai':('landsd/229881:0','11-NW-19C',['landsd/235557:0'],'government-xl-extended-229881-20261005')}
UID,SHEET,EXPECTED,CONTACT_BATCH=CONFIG[GROUP]
BATCH='government-xl-'+GROUP+'-original-support-group-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=LOCAL/'native-input.json'
CONTACT=ROOT/'docs/astra-city/government-import'/CONTACT_BATCH


def start():
    podium=read(CONTACT/'selection.json.gz')['rows'][0];key=podium['native']['cacheKey']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        resultsha,data=con.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()
    native=[]
    for model in data['models']:
        hits=[v['uid'] for v in model.get('matching',{}).get('viewerMatches',[]) if v['uid'] in EXPECTED]
        if hits:native.append({'cacheKey':key,'resultSha':resultsha,'sheet':SHEET,'uids':hits,'model':model})
    assert {u for row in native for u in row['uids']}==set(EXPECTED)
    assert all(len(row['uids'])==1 for row in native)
    save(INPUT,{'native':native})
    save(DOC/'source-podium-selection.json.gz',{'rows':[podium]})
    uids=[u for r in native for u in r['uids']]
    assert len(set(uids))==len(EXPECTED)
    claim=reservations.claim('codex-hsbc-centre-supports-'+str(uuid.uuid4()),
        ['building:'+u for u in [UID,*uids]],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,GROUP,'owned'],cwd=ROOT,check=True)


def owned():
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    native=read(INPUT)['native'];sheet=SHEET
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        pinned=con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
    folder=LOCAL/'sheets'/sheet
    current,_=scan({'SHEETNO':sheet,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},folder/'directory')
    wanted={r['model']['modelId'] for r in native}
    current['models']=[m for m in current['models'] if m['modelId'] in wanted]
    assert {m['modelId'] for m in current['models']}==wanted
    proof=acquire(current,folder/'directory/zip-directory.bin',folder/'original')
    packed=folder/'packed';packed.mkdir(parents=True,exist_ok=True)
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');forms={}
    uids={u for r in native for u in r['uids']}
    for t in manifest['tiles']:
        path=ROOT/'3d-viewer'/t['url']
        for b in read(path)['buildings']:
            if b['uid'] in uids:forms[b['uid']]={'building':b,'tile':t['url'],'tileSHA256':digest(path.read_bytes())}
    assert set(forms)==uids
    rows=[]
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as archive:
        for outcome in native:
            m=outcome['model'];uid=outcome['uids'][0]
            converted=_convert_one(archive,archive.getinfo(m['sourceEntry']),folder/'decoded',packed,{}, {'modelId':m['modelId']})
            raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),m['asset']['sha256'])
            assert len(raw)==m['asset']['bytes']
            dest=LOCAL/'assets'/(m['asset']['sha256']+'.glb.gz');dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw)
            candidate=entry(outcome,forms[uid]['building'])
            rows.append({'uid':uid,'modelId':m['modelId'],'native':outcome,'sourceSHA256':m['asset']['sha256'],
                'triangles':m['triangles'],'source':forms[uid],
                'candidate':{'entry':candidate,'path':str(dest.relative_to(ROOT))}})
            assert reservations.owns(receipt)
            print(json.dumps({'recovered':uid,'originalSHA256':m['asset']['sha256']}),flush=True)
    save(DOC/'selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),
        'sourceDirectorySHA256':current['directorySHA256'],'sourceArchiveSHA256':proof['sha256'],
        'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False})
    template=read(HERE/'accepted/government-xxl-20260911/catalogue.json')
    template.update(area=BATCH,models=[r['candidate']['entry'] for r in rows],counts={'packedModels':len(rows)})
    save(LOCAL/'catalogue.json',template);save(LOCAL/'catalogue-index.json',{'models':len(rows),'catalogues':['catalogue.json']})
    save(LOCAL/'source-forms.json',{r['uid']:r['source'] for r in rows})
    save(DOC/'recovery.json',{'recovered':uids and sorted(uids),'sourcePreserved':True,
        'sourceBytes':sum(r['native']['model']['asset']['bytes'] for r in rows),
        'receivedBytes':proof['newThisInvocationBytes'],'sourceDirectoryChanged':current['directorySHA256']!=pinned['directorySHA256'],
        'qualification':'Every converted payload has the exact original native-stage SHA and byte count; changed directory offsets never substitute changed model bytes.',
        'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False})



def sync():
    selection=read(DOC/'selection.json.gz');interfaces=read(DOC/'interfaces.json.gz')
    for path,pinned in interfaces['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pinned
    scope=[UID,*[r['uid'] for r in selection['rows']]]
    claim=reservations.claim('codex-coronation-result-'+str(uuid.uuid4()),['building:'+u for u in scope],batch=BATCH)
    assert claim['ok'],claim
    receipt=claim['reservation']
    try:
        refs=[{'path':str((DOC/name).relative_to(ROOT)),'sha256':digest((DOC/name).read_bytes())} for name in ('selection.json.gz','recovery.json','interfaces.json.gz')]
        refs.extend({'path':str((CONTACT/name).relative_to(ROOT)),'sha256':digest((CONTACT/name).read_bytes())} for name in ('selection.json.gz','metrics.json','foundation.json','neighbour-checks.json','native-neighbour-checks.json','terrain-candidates.json'))
        payload={'evidenceRefs':refs,'pipelineSHA256':digest(Path(__file__).read_bytes())}
        stage='exact-original-source-support-group-v1'
        jobid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,receipt['owner'],[stage],lease_seconds=1800)
        assert job and job['id']==jobid
        by_uid={r['uid']:r for r in interfaces['rows']};rows=[]
        for row in selection['rows']:
            proof=by_uid[row['uid']]['interface']
            rows.append({'uid':row['uid'],'modelId':row['modelId'],'sourceSHA256':row['sourceSHA256'],
                'nativeCacheKey':row['native']['cacheKey'],'nativeResultSHA256':row['native']['resultSha'],
                'humanStatus':'held-unknown','installed':False,'requiresAI':False,'requiresHumanDecision':False,
                'interfacePassed':proof['passed'],'samples':proof['samples'],'strictContacts':proof['strictContacts'],
                'wallIntersections':proof['wallIntersections'],'unresolved':len(proof['unresolved']),
                'minimumGapM':proof['strictLowRim']['minGap'],'maximumGapM':proof['strictLowRim']['maxGap'],
                'nextStep':'Retain exact original components. Complete identity, support closure, runtime and publication gates; unresolved interfaces grant no installation credit.'})
        result={**payload,'batch':BATCH,'jobId':jobid,'rows':rows,'sourcePodiumUid':UID,
            'newlyInstalled':0,'recoveredOriginalMeshes':len(EXPECTED),'interfacesPassed':sum(r['interfacePassed'] for r in rows),
            'activeWorkers':0,'queuedFollowups':0,'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False,
            'widerXLCheckpoint':{'models':352,'installed':44,'held':308},
            'qualification':'Original source terrain and complete foundation pass, but overlapping basic forms regress. Exact original support sources are recovered and tested in full; no acceptance or architectural judgement is inferred.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,receipt)
            for source in selection['rows']:
                native=source['native']
                actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,native['cacheKey'])).fetchone()
                assert actual and actual['result_sha']==native['resultSha']
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
        print(json.dumps({'jobId':jobid,'neonVerified':True,'recovered':len(EXPECTED),'interfacesPassed':result['interfacesPassed'],'installed':0}),flush=True)
    finally:reservations.release(receipt)

if __name__=='__main__':
    if 'sync' in sys.argv:sync()
    else:owned() if 'owned' in sys.argv else start()
