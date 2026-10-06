"""Run fresh full physical checks for the seven qualified provisional XL holds.

Every original prior hold stays intact. This explicit diagnostic sequence never
publishes, changes geometry, waives a numeric gate, or calls architectural AI.
"""
import importlib.util,json,subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from provisional_original_review import verify,SCOPED_UIDS
BATCH='government-xl-provisional-physical-sequence-20261007'
BASE=ROOT/'docs/astra-city/government-import/government-xl-twelve-provisional-original-inputs-20261007'
IDENTITY=ROOT/'docs/astra-city/government-import/government-xl-twelve-provisional-cell-identity-20261007'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH

def main():
    assert not DOC.exists(),'Fresh immutable sequence only'
    identity=read(IDENTITY/'result.json');assert identity['sourcesChecked']==12
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(identity['jobId'],)).fetchone()==('complete',identity)
    for ref in identity['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    qualified={r['uid'] for r in identity['rows'] if r['passed']};assert len(qualified)==7 and qualified<=SCOPED_UIDS
    rows=[r for r in read(BASE/'check-selection.json.gz')['rows'] if r['uid'] in qualified]
    spec=importlib.util.spec_from_file_location('provisional_routing',HERE/'xl-cell-source-sequence.py')
    routing=importlib.util.module_from_spec(spec);spec.loader.exec_module(routing)
    scripts=['xl-provisional-cell-terrain-continuation.py','xl-provisional-cell-contact-resolution.py',
        'xl-provisional-retained-terrain-followthrough.py','xl-provisional-retained-overlap-followthrough.py',
        'xl-provisional-retained-overlap-contact.py','provisional_original_review.py','test_provisional_original_review.py']
    refs=[{'path':str((HERE/n).relative_to(ROOT)),'sha256':digest((HERE/n).read_bytes())} for n in scripts]
    save(DOC/'routing.json',{'uids':sorted(qualified),'identityJobId':identity['jobId'],'evidenceRefs':refs,
        'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
    LOCAL.mkdir(parents=True,exist_ok=True);outcomes=[]
    for i,row in enumerate(rows,1):
        for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');verify(c,row['uid'],row['sourceSHA256'],row['currentReview'])
        token=row['uid'].split('/')[1].replace(':','-');retained=routing.retained_route(row)
        script='xl-provisional-retained-overlap-followthrough.py' if retained else 'xl-provisional-cell-terrain-continuation.py'
        batch=BATCH+'-'+token
        command=[sys.executable,str(HERE/script),'--uid',row['uid'],'--batch',batch,'--base',str(BASE.relative_to(ROOT))]
        if retained:command+=['--retained',retained,'--allow-basic-targets']
        save(DOC/'working-commands.json',{'finished':outcomes,'running':row['uid'],'queued':len(rows)-i})
        print(json.dumps({'starting':row['uid'],'position':i,'total':len(rows),'retained':retained}),flush=True)
        log=LOCAL/(token+'.log')
        with log.open('w') as out:status=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT).returncode
        p=ROOT/'docs/astra-city/government-import'/batch/'result.json';result=read(p) if p.exists() else None
        outcomes.append({'uid':row['uid'],'name':row['name'],'sourceSHA256':row['sourceSHA256'],
            'command':command,'returncode':status,'result':result,'log':str(log.relative_to(ROOT))})
        print(json.dumps({'finished':row['uid'],'scriptChecksPassed':bool(result and result['scriptChecksPassed']),
            'reasons':result['reasons'] if result else ['command-failure-see-log']}),flush=True)
    save(DOC/'commands.json',{'rows':outcomes,'scriptChecksPassed':sum(bool(r['result'] and r['result']['scriptChecksPassed']) for r in outcomes),
        'activeWorkers':0,'queuedFollowups':0,'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0})
    save(DOC/'working-commands.json',{'finished':outcomes,'running':None,'queued':0})
if __name__=='__main__':main()
