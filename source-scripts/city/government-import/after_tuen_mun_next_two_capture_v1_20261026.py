"""Run the next two original-source checks under existing leases; no installation."""
import json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-after-tuen-mun-next-two-current-runner-v1-20261026'
PREFIX='government-xl-after-tuen-mun-next-two-'
DATE='-20261026'
UIDS=['landsd/53852:0','landsd/311317:0']

def main():
    doc=ROOT/'docs/astra-city/government-import'/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
    selection=PREFIX+'selection-v1'+DATE;inventory='government-xl-after-tuen-mun-current-inventory-v1-20261026'
    phases=[('ground','selected_original_current_capture_v3.py',['--capture',selection,*sum((['--uid',u]for u in UIDS),[])]),('attributes','selected_original_render_attributes_v1.py',['--capture',PREFIX+'ground-v1'+DATE]),('identity','selected_original_identity_v3_20261023.py',['--capture',PREFIX+'ground-v1'+DATE]),('scope','selected_original_model_only_scope_v1_20261023.py',['--runtime',PREFIX+'ground-v1'+DATE,'--attributes',PREFIX+'attributes-v1'+DATE,'--inventory',inventory])]
    claim=reservations.claim('original-next-two-current-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json','original-compute:'+BATCH],batch=BATCH,ttl=3600);assert claim.get('ok'),'Original source/terrain scope currently reserved'
    lease=claim['reservation'];leasepath=local/'reservation.json';save(leasepath,json.loads(json.dumps(lease,default=str)));state=dict(uids=UIDS,completedJobs=[],running=True,publication=False,newlyInstalled=0);save(local/'state.json',state)
    try:
        for phase,tool,args in phases:
            name=PREFIX+phase+'-v1'+DATE;command=[sys.executable,str(HERE/tool),'--batch',name,*args];state['phase']=phase;save(local/'state.json',state)
            log=local/(phase+'.log')
            with log.open('w')as stream:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(leasepath),*command],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},stdout=stream,stderr=subprocess.STDOUT,check=True)
            receipt=read(ROOT/'docs/astra-city/government-import'/name/'result.json');state['completedJobs'].append(dict(batch=name,jobId=receipt['jobId']));save(local/'state.json',state);print('Completed original phase',phase,flush=True)
        state['running']=False;save(local/'state.json',state)
    except BaseException as exc:
        state.update(running=False,error=repr(exc));save(local/'state.json',state);raise
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
    refs=[Path(__file__),local/'state.json',*(local/(p[0]+'.log')for p in phases),*(ROOT/'docs/astra-city/government-import'/r['batch']/'result.json'for r in state['completedJobs'])]
    module('next_two_reserved_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'leased-next-two-current-original-compute',refs,dict(uids=UIDS,completedJobs=state['completedJobs'],installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Explicit immediate computation only. Every source remains uninstalled and unapproved pending current exact source/terrain/identity/physical/retained/browser work. No optimisation or queued production work.'))

if __name__=='__main__':main()
