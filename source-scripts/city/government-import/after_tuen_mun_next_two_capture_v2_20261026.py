"""Continue completed ground capture under one renewed lease for remaining phases."""
import argparse,json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-after-tuen-mun-next-two-current-runner-v2-20261026'
PREFIX='government-xl-after-tuen-mun-next-two-';DATE='-20261026';UIDS=['landsd/53852:0','landsd/311317:0']
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'

def owned():
    assert reservations.owns(read(LEASE))and not DOC.exists()
    ground=PREFIX+'ground-v1'+DATE;receipt,_=authenticate(BASE/ground);assert set(receipt['uids'])==set(UIDS)
    phases=[('attributes','selected_original_render_attributes_v1.py',['--capture',ground]),('identity','selected_original_identity_v3_20261023.py',['--capture',ground]),('scope','selected_original_model_only_scope_v1_20261023.py',['--runtime',ground,'--attributes',PREFIX+'attributes-v1'+DATE,'--inventory','government-xl-after-tuen-mun-current-inventory-v1-20261026'])]
    state=dict(uids=UIDS,completedJobs=[dict(batch=ground,jobId=receipt['jobId'])],running=True,publication=False,newlyInstalled=0);save(LOCAL/'state.json',state)
    try:
        for phase,tool,args in phases:
            assert reservations.owns(read(LEASE));name=PREFIX+phase+'-v1'+DATE;state['phase']=phase;save(LOCAL/'state.json',state)
            assert not(BASE/name).exists(),'Do not restart completed or partial phase output'
            with(LOCAL/(phase+'.log')).open('w')as log:subprocess.run([sys.executable,str(HERE/tool),'--batch',name,*args],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},stdout=log,stderr=subprocess.STDOUT,check=True)
            assert reservations.owns(read(LEASE));r=read(BASE/name/'result.json');state['completedJobs'].append(dict(batch=name,jobId=r['jobId']));save(LOCAL/'state.json',state);print('Completed original phase',phase,flush=True)
        state['running']=False;save(LOCAL/'state.json',state)
    except BaseException as exc:
        state.update(running=False,error=repr(exc));save(LOCAL/'state.json',state);raise
    refs=[Path(__file__),LOCAL/'state.json',HERE/'local/government-xl-after-tuen-mun-next-two-current-runner-v1-20261026/state.json',*(LOCAL/(p[0]+'.log')for p in phases),*(BASE/r['batch']/'result.json'for r in state['completedJobs'])]
    module('next_two_reserved_continuation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'leased-next-two-current-original-compute',refs,dict(uids=UIDS,completedJobs=state['completedJobs'],installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Continue the already-completed current ground capture without repeating it. All remaining phases share one supervised renewed lease; no production queue or installation.'))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    if a.owned:return owned()
    assert not DOC.exists()and not LOCAL.exists()
    prior=read(HERE/'local/government-xl-after-tuen-mun-next-two-current-runner-v1-20261026/state.json');assert not prior['running']and len(prior['completedJobs'])==1
    claim=reservations.claim('original-next-two-continuation-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['terrain:city/data/terrain.json','original-compute:'+BATCH],batch=BATCH,ttl=3600);assert claim.get('ok'),'Original source/terrain scope currently reserved'
    lease=claim['reservation'];save(LEASE,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(LEASE),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']

if __name__=='__main__':main()
