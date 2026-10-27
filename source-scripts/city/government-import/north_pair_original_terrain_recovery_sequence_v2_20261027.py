"""Run the explicit North pair two-member terrain diagnostics, one lease per phase.

No installation, acceptance, optimisation, original model or source terrain edits.
"""
import json,os,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module

def main():
    base=ROOT/'docs/astra-city/government-import'
    prefix='government-xl-west-kowloon-north-pair-after-ocean-'
    batch=prefix+'two-member-recovery-sequence-v2-20261027'
    local=HERE/'local'/batch
    assert not local.exists() and not (base/batch).exists()
    uids=['landsd/182397:0','landsd/309340:0']
    phases=[
        ('original_partitioned_parent_capture_v3_20261027.py',prefix+'parent-v3-20261027',
         ['--plan',str((base/(prefix+'parent-plan-v3-20261027.json')).relative_to(ROOT))]),
        ('original_partitioned_multi_source_inset_proposal_v2_20261027.py',prefix+'partitioned-inset-v3-20261027',
         ['--batch',prefix+'partitioned-inset-v3-20261027','--parents',prefix+'parent-v3-20261027',
          '--terrain','government-xl-west-kowloon-north-pair-original-terrain-v1-20261027',
          '--runtime',prefix+'current-runtime-v1-20261027','--uid',uids[0],'--uid',uids[1]]),
        ('original_partitioned_multi_source_seam_foundation_v2_20261027.py',prefix+'partitioned-seams-v3-20261027',
         ['--batch',prefix+'partitioned-seams-v3-20261027','--candidate',prefix+'partitioned-inset-v3-20261027',
          '--runtime',prefix+'current-runtime-v1-20261027','--uid',uids[0],'--uid',uids[1]])]
    plan=base/(prefix+'context-plan-v1-20261027.json')
    resources=set(read(plan)['resources'])
    for name in ['government-native-272986-0.json','government-native-island-cheong-shing-north-v1-20261023.json']:
        resources.add('terrain:city/data/'+name)
        resources.update('building:'+u for u in read(ROOT/'3d-viewer/city/data'/name)['meta']['targetUids'])
    refs=[HERE/'north_pair_original_terrain_recovery_sequence_v2_20261027.py',plan,
          base/(prefix+'parent-plan-v3-20261027.json')]
    state=dict(uids=uids,running=True,completedJobs=[],publication=False,installationApproved=False)
    save(local/'state.json',state)
    try:
        for index,(filename,child,args) in enumerate(phases):
            assert not (base/child).exists()
            claim=reservations.claim('north-pair-two-member-'+str(uuid.uuid4()),sorted(resources|{'original-compute:'+child}),batch=batch,ttl=3600)
            assert claim.get('ok'),'Source or terrain scope currently reserved'
            lease=claim['reservation'];lp=local/('lease-'+str(index)+'.json')
            save(lp,json.loads(json.dumps(lease,default=str)))
            tool=HERE/filename;command=[sys.executable,str(tool),*args]
            command_path=local/('command-'+str(index)+'.json')
            save(command_path,dict(command=command,scriptSHA256=digest(tool.read_bytes()),resources=sorted(resources)))
            state['phase']=child;save(local/'state.json',state)
            log_path=local/('phase-'+str(index)+'.log')
            try:
                with log_path.open('w') as log:
                    subprocess.run([sys.executable,str(HERE/'bounded_reserved_runner_v2_20261022.py'),str(lp),*command],
                                   cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'},
                                   stdout=log,stderr=subprocess.STDOUT,check=True)
            finally:
                if reservations.owns(lease):assert reservations.release(lease)['ok']
            assert digest(tool.read_bytes())==read(command_path)['scriptSHA256']
            receipt=read(base/child/'result.json')
            state['completedJobs'].append(dict(batch=child,jobId=receipt['jobId']))
            save(local/'state.json',state)
            refs.extend([tool,base/child/'result.json',command_path,log_path])
            print('Completed',child,flush=True)
        state['running']=False;save(local/'state.json',state)
    except BaseException as error:
        state.update(running=False,error=repr(error));save(local/'state.json',state);raise
    refs.append(local/'state.json')
    module('north_pair_two_member_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch,'explicit-original-pair-two-member-terrain-diagnostic-sequence',refs,
        dict(uids=uids,completedJobs=state['completedJobs'],installationApproved=False,publication=False,
             sourceGeometryChanges=0,qualification='Private source-preserving terrain diagnostics only. Each phase owns a separate renewed lease. Raw diagnostic failures remain unaccepted; no installation or geometry modelling credit.'))

if __name__=='__main__':main()
