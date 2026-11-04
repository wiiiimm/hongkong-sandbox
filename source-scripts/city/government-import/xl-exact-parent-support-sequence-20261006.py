"""Recover and test the fourteen explicit unprocessed original support pairs."""
import json, subprocess, sys
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
BATCH='government-xl-exact-parent-support-sequence-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
AUDIT=ROOT/'docs/astra-city/government-import/government-xl-exact-parent-support-audit-20261006'
def main():
    assert not (DOC/'commands.json').exists(), 'Do not repeat a completed explicit sequence'
    route=read(AUDIT/'routing.json');assert route['auditSHA256']==digest((AUDIT/'audit.json').read_bytes())
    rows=route['rows'];assert len(rows)==14 and len({(r['uid'],r['supportUid']) for r in rows})==14
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [AUDIT/'routing.json', AUDIT/'audit.json', Path(__file__),HERE/'xl-exact-support-closure.py',HERE/'original-support-closure-interfaces.mjs']]
    LOCAL.mkdir(parents=True,exist_ok=True);outcomes=[]
    for i,row in enumerate(rows,1):
        for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
        previous=read(ROOT/'docs/astra-city/government-import'/row['sourceBatch']/'result.json')
        assert previous['jobId']==row['jobId'] and previous['sourceSHA256']==row['sourceSHA256']
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(row['jobId'],)).fetchone()==('complete',previous)
        token=row['uid'].split('/')[1].replace(':','-');batch=BATCH+'-'+token
        command=[sys.executable,str(HERE/'xl-exact-support-closure.py'),'--base',row['base'],'--batch',batch,'--pair',row['uid']+'='+row['supportUid']]
        save(DOC/'working-commands.json',{'finished':outcomes,'running':row,'queued':len(rows)-i,'publication':False,'scriptExternalAICalls':0})
        print(json.dumps({'starting':row['uid'],'support':row['supportUid'],'position':i,'total':len(rows)}),flush=True)
        log=LOCAL/(token+'.log')
        with log.open('w') as output:status=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT).returncode
        resultpath=ROOT/'docs/astra-city/government-import'/batch/'result.json'
        result=read(resultpath) if resultpath.exists() else None
        outcomes.append({'uid':row['uid'],'supportUid':row['supportUid'],'batch':batch,'command':command,'returncode':status,'log':str(log.relative_to(ROOT)),'result':result})
        save(DOC/'working-commands.json',{'finished':outcomes,'running':None,'queued':len(rows)-i,'publication':False,'scriptExternalAICalls':0})
        print(json.dumps({'finished':row['uid'],'interfacesPassed':result.get('interfacesPassed') if result else None,'returncode':status}),flush=True)
    save(DOC/'commands.json',{'batch':BATCH,'rows':outcomes,'evidenceRefs':refs,'activeWorkers':0,'queuedFollowups':0,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Original support diagnostics only. Exact identity, terrain, foundation, current neighbours/runtime/browser/installation remain required. Command failures remain explicit logs for further fenced recovery.'})
if __name__=='__main__':main()
