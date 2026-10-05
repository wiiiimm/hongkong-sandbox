"""Fresh four-form original-terrain continuation; no model edits or AI calls."""
import importlib.util
import json
import subprocess
import sys
import uuid
import zipfile
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import scan,acquire

CASES={'coronation-circle':('landsd/10664:0','11-NW-24A'),
       'stonecutters-pumping':('landsd/270142:0','11-NW-12D'),
       'royal-green-3':('landsd/11093:0','3-SW-11B'),
       'south-hillcrest':('landsd/198440:0','6-NW-21D')}
ADJACENT={}
CASE=sys.argv[1];UID,SHEET=CASES[CASE]
BATCH='government-xl-'+CASE+'-terrain-continuation-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PREVIOUS=ROOT/'docs/astra-city/government-import/government-xl-next-100-20261005'


def start():
    claim=reservations.claim('codex-xl-'+CASE+'-'+str(uuid.uuid4()),
        ['building:'+UID,'terrain-patch:'+UID],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
        '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,CASE,
        'classify' if 'reclassify' in sys.argv else 'owned'],cwd=ROOT,check=True)


def owned():
    assert reservations.owns(read(LOCAL/'reservation.json'))
    old=read(PREVIOUS/'check-selection.json.gz');row=next(r for r in old['rows'] if r['uid']==UID)
    assert row['native']['sheet']==SHEET and row['currentReview'] is None
    assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        pinned=con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(SHEET,)).fetchone()[0]
    save(LOCAL/'source-directory.json',pinned)
    source=LOCAL/'sheets'/SHEET
    directory,_=scan({'SHEETNO':SHEET,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},source/'directory')
    directory['models']=[]
    receipt=acquire(directory,source/'directory/zip-directory.bin',source/'original',include_terrain=True)
    with zipfile.ZipFile(source/'original'/f'{SHEET}.zip') as archive:
        for e in receipt['entries']:
            if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):
                target=source/'terrain'/e['name'];target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.read(e['name']));assert digest(target.read_bytes())==e['sha256']
    save(DOC/'source-recovery.json',{'uid':UID,'sheet':SHEET,'sourceSHA256':row['sourceSHA256'],
        'sourceDirectorySHA256':directory['directorySHA256'],'sourceArchiveSHA256':receipt['sha256'],
        'sourceDirectoryChanged':directory['directorySHA256']!=pinned['directorySHA256'],
        'transferredBytes':receipt['newThisInvocationBytes'],'terrainFiles':[e for e in receipt['entries'] if e['name'].startswith('TERRAIN')],
        'scriptExternalAICalls':0,'modelGeometryChanges':0,'publication':False})
    fresh=LOCAL/'frozen-inputs'
    save(fresh/'check-selection.json.gz',{**old,'rows':[row],
        'previousSelectionSHA256':digest((PREVIOUS/'check-selection.json.gz').read_bytes()),
        'previousManifestSHA256':old['manifestSHA256'],
        'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())})
    context=next(r for r in read(PREVIOUS/'context.json.gz')['rows'] if r['uid']==UID)
    save(fresh/'context.json.gz',{'rows':[context]})
    spec=importlib.util.spec_from_file_location(CASE+'_contact',HERE/'xl-contact-resolution-20261005.py')
    resolution=importlib.util.module_from_spec(spec);spec.loader.exec_module(resolution)
    resolution.BATCH=BATCH;resolution.BASE=fresh;resolution.DOC=DOC;resolution.LOCAL=LOCAL
    resolution.SOURCE=source;resolution.UIDS=[UID]
    for adjacent_sheet in ADJACENT.get(CASE,[]):
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            adjacent_pinned=con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(adjacent_sheet,)).fetchone()[0]
        adjacent=LOCAL/'sheets'/adjacent_sheet
        adjacent_directory,_=scan({'SHEETNO':adjacent_sheet,'Format_glTF':adjacent_pinned['sourceURL'],'REVISIONDATE':adjacent_pinned['revision']},adjacent/'directory')
        adjacent_directory['models']=[]
        adjacent_receipt=acquire(adjacent_directory,adjacent/'directory/zip-directory.bin',adjacent/'original',include_terrain=True)
        with zipfile.ZipFile(adjacent/'original'/f'{adjacent_sheet}.zip') as archive:
            for e in adjacent_receipt['entries']:
                if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin')):
                    target=adjacent/'terrain'/e['name'];target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(archive.read(e['name']));assert digest(target.read_bytes())==e['sha256']
        save(DOC/('adjacent-source-'+adjacent_sheet+'.json'),{'sheet':adjacent_sheet,
            'sourceDirectorySHA256':adjacent_directory['directorySHA256'],'sourceArchiveSHA256':adjacent_receipt['sha256'],
            'terrainFiles':[e for e in adjacent_receipt['entries'] if e['name'].startswith('TERRAIN')],
            'transferredBytes':adjacent_receipt['newThisInvocationBytes'],'publication':False,'modelGeometryChanges':0})
        resolution.ADJACENT_SOURCES.append(adjacent)
    try:
        resolution.owned()
    except AssertionError as error:
        save(DOC/'guard-failure.json',{'uid':UID,'error':str(error),'publication':False,'modelGeometryChanges':0})
        finish(row,['terrain-construction-guard:'+str(error)])
        return
    classify(row)


def classify(row=None):
    assert reservations.owns(read(LOCAL/'reservation.json'))
    row=row or read(DOC/'selection.json.gz')['rows'][0]
    spec=importlib.util.spec_from_file_location(CASE+'_policy',HERE/'acceptance-policy.py')
    policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    metrics=read(DOC/'metrics.json');metric=metrics['rows'][0]
    for path,pinned in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pinned
    reasons=policy.reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256']},metric,metrics['profiles']['mobile'])
    foundation=read(DOC/'foundation.json')['rows'][0]
    if not foundation['strictFoundationAccepted']:reasons.append('whole-source-foundation')
    reasons.extend(read(DOC/'validation.json')['results'][0].get('concerns',[]))
    native=read(DOC/'native-neighbour-checks.json')
    resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+uid for uid in set(native['blocked'])-resolved)
    reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(DOC/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    finish(row,reasons)


def finish(row,reasons):
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
          for p in sorted(DOC.iterdir()) if p.is_file() and p.name not in ('result.json','neon-sync.json','README.md')]
    payload={'uid':UID,'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs,
        'pipelineSHA256':digest((HERE/'xl-contact-resolution-20261005.py').read_bytes()),
        'classificationSHA256':digest((HERE/'xl-terrain-continuation-20261005.py').read_bytes())}
    stage='exact-original-terrain-continuation-v1'
    jobid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,receipt['owner'],[stage],lease_seconds=1800)
    assert job and job['id']==jobid
    result={**payload,'jobId':jobid,'batch':BATCH,'reasons':sorted(set(reasons)),
        'humanStatus':'held-unknown' if reasons else 'in-process','scriptChecksPassed':not reasons,
        'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'activeWorkers':0,'queuedFollowups':0,'requiresAI':False,'requiresHumanDecision':False,
        'nextStep':'Resolve the exact saved original terrain, foundation and neighbour blockers without source shifts or tolerance increases.' if reasons else 'Complete staged/live browser, guarded publication and installed-ledger gates; script results grant no installation credit.',
        'widerXLCheckpoint':{'models':352,'installed':42,'held':310}}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,receipt)
        actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual['result_sha']==row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'case':CASE,'checksPassed':not reasons,'reasons':result['reasons'],'jobId':jobid,'neonVerified':True}),flush=True)


if __name__=='__main__':
    if 'classify' in sys.argv:classify()
    else:owned() if 'owned' in sys.argv else start()
