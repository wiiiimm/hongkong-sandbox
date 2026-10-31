"""Run independent immutable captured-ground diagnostics under one full lease.

Only the two existing read-only foundation/finite-clearance producers are allowed.
No capture mutation, acquisition, acceptance, publication or optimisation work.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
ALLOWED={'original_four_world_foundation_context_v1_20261025.py','selected_original_four_world_low_face_context_v3_20261031.py'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args();path=(ROOT/a.plan).resolve();assert path.is_relative_to(ROOT/'docs/astra-city/government-import');plan=read(path);batch=plan['batch'];base=ROOT/'docs/astra-city/government-import';out=base/batch;lp=HERE/'local'/batch/'reservation.json'
    assert batch.startswith('government-xl-') and '/'not in batch and 1<=plan['workers']<=4
    phases=plan['phases'];assert phases and len({p['batch']for p in phases})==len(phases) and len(set(plan['uids']))==len(plan['uids'])
    for p in phases:
        assert p['script']in ALLOWED and p['batch'].startswith('government-xl-') and '/'not in p['batch']
        args=p['args'];assert not set(args)&{'--apply','--install','--batch','--owned'}
        assert args[args.index('--uid')+1]in plan['uids'] and args[args.index('--runtime')+1]==plan['runtime'] and args[args.index('--attributes')+1]==plan['attributes']
    required={'building:'+u for u in plan['uids']}|{'terrain:city/data/terrain.json'};assert required<=set(plan['resources'])
    if not a.owned:
        assert not out.exists() and not lp.parent.exists();claim=reservations.claim('captured-ground-parallel-'+str(uuid.uuid4()),sorted(set(plan['resources'])),batch=batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--plan',a.plan,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(plan['resources']) and not out.exists()
    runtime,rpins=authenticate(base/plan['runtime']);_,apins=authenticate(base/plan['attributes']);selection=base/plan['runtime']/'selection.json.gz';ground=HERE/'local'/plan['runtime']/'runtime-geometry.json.gz';attributes=base/plan['attributes']/'attributes.json.gz'
    for p,pins in [(selection,rpins),(ground,rpins),(attributes,apins)]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes());selected=read(selection);assert manifest_sha==selected['manifestSHA256'];assert set(plan['uids'])==set(runtime['uids'])
    refs=[Path(__file__),path,base/plan['runtime']/'result.json',base/plan['attributes']/'result.json',selection,ground,attributes,manifest];out.mkdir();pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};state=dict(running=True,completed=[],uids=plan['uids'],publication=False,installationApproved=False);save(out/'state.json',state)
    def run(index,phase):
        assert reservations.owns(lease);tool=HERE/phase['script'];sha=digest(tool.read_bytes());assert not(base/phase['batch']).exists();log=out/('phase-'+str(index)+'.log');command=[sys.executable,str(tool),'--batch',phase['batch'],*phase['args']];save(out/('command-'+str(index)+'.json'),dict(command=command,producerSHA256=sha))
        with log.open('w')as f:cp=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        assert cp.returncode==0,phase['batch']+' failed; see '+str(log.relative_to(ROOT))
        assert reservations.owns(lease) and digest(tool.read_bytes())==sha;receipt,_=authenticate(base/phase['batch']);return dict(batch=phase['batch'],jobId=receipt['jobId'],script=phase['script'],log=log)
    try:
        with ThreadPoolExecutor(max_workers=plan['workers'])as pool:
            futures=[pool.submit(run,i,p)for i,p in enumerate(phases)]
            for future in as_completed(futures):
                result=future.result();state['completed'].append({k:v for k,v in result.items()if k!='log'});save(out/'state.json',state);print('Completed immutable diagnostic '+result['batch'],flush=True)
        assert len(state['completed'])==len(phases) and reservations.owns(lease)
        for name,h in pins.items():assert digest((ROOT/name).read_bytes())==h,name
        for p in phases:refs.extend([HERE/p['script'],base/p['batch']/'result.json'])
        state['running']=False;save(out/'state.json',state);refs.extend(p for p in out.rglob('*')if p.is_file())
        module('captured_ground_parallel_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-parallel-immutable-source-ground-diagnostics',list(dict.fromkeys(refs)),dict(uids=plan['uids'],completedJobs=state['completed'],workers=plan['workers'],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,physicalAcceptance=False,newlyInstalled=0,qualification=__doc__+' Complete shared affected-scope lease renews under the existing supervisor. Each process writes a distinct batch; inputs and producer hashes are verified unchanged. No per-model AI or acceptance decisions.'))
    except BaseException as error:
        state.update(running=False,error=repr(error));save(out/'state.json',state);raise

if __name__=='__main__':main()
