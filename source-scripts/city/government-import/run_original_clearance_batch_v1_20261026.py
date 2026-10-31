"""Run explicit unchanged-source low-face/cap diagnostics with at most two local workers.

Immutable existing producers; no import, review, optimisation or AI calls.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json,os,subprocess,sys,threading
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True);p.add_argument('--plan',required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-')and '/'not in a.batch and not out.exists()and not local.exists()
    planpath=(ROOT/a.plan).resolve();assert planpath.is_relative_to(ROOT);plan=read(planpath);rows=plan['rows']
    assert 0<len(rows)<=40 and len({r['uid']for r in rows})==len(rows)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());refs=[Path(__file__),planpath,manifest];checked=set()
    for row in rows:
        assert set(row)=={'uid','runtime','attributes'}
        for batch in [row['runtime'],row['attributes']]:
            if batch not in checked:
                _,pins=authenticate(base/batch);assert pins[str(manifest.relative_to(ROOT))]==sha;checked.add(batch);refs.append(base/batch/'result.json')
        for phase in ['low-faces','cap-paths']:
            name=a.batch+'-'+row['uid'].split('/')[1].replace(':','-')+'-'+phase
            assert not(base/name).exists()
    local.mkdir(parents=True);out.mkdir();lock=threading.Lock();state=dict(parentPID=os.getpid(),status='running',children={},completed=[]);statepath=local/'state.json'
    save(statepath,state)
    def run(row):
        uid=row['uid'];prefix=a.batch+'-'+uid.split('/')[1].replace(':','-');done=[]
        for phase,producer in [('low-faces','selected_original_four_world_low_face_context_v1_20261024.py'),('cap-paths','selected_original_complete_ground_cap_paths_v2_20261024.py')]:
            if phase=='cap-paths':
                low=read(base/(prefix+'-low-faces')/'summary.json')
                if all(not r['exactAffectedFaces']for r in low['rows']):
                    return dict(uid=uid,status='complete-no-negative-faces',completed=done,capSkippedBecauseAllFourWorldNegativePartitionsEmpty=True)
            name=prefix+'-'+phase
            command=[sys.executable,str(HERE/producer),'--batch',name,'--runtime',row['runtime'],'--attributes',row['attributes'],'--uid',uid]
            if phase=='cap-paths':command+=['--low-faces',prefix+'-low-faces']
            logfile=local/(uid.split('/')[1].replace(':','-')+'-'+phase+'.log')
            with logfile.open('w')as log:
                process=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','OPENBLAS_NUM_THREADS':'1'})
                with lock:
                    state['children'][uid]=dict(pid=process.pid,stage=phase);save(statepath,state)
                code=process.wait()
            with lock:
                state['children'].pop(uid,None);save(statepath,state)
            if code:return dict(uid=uid,status='failed',phase=phase,exitCode=code,completed=done,log=str(logfile.relative_to(ROOT)))
            receipt,_=authenticate(base/name);done.append(dict(batch=name,jobId=receipt['jobId']))
            with lock:
                state['completed'].append(dict(uid=uid,stage=phase,batch=name,jobId=receipt['jobId']));save(statepath,state)
            print(dict(uid=uid,stage=phase,jobId=receipt['jobId']),flush=True)
        return dict(uid=uid,status='complete',completed=done)
    with ThreadPoolExecutor(max_workers=2)as executor:results=list(executor.map(run,rows))
    assert not state['children'];state['status']='complete'if all(r['status'].startswith('complete')for r in results)else'failed';save(statepath,state)
    assert digest(manifest.read_bytes())==sha
    for row in results:
        for step in row['completed']:
            receipt,pins=authenticate(base/step['batch']);assert receipt['jobId']==step['jobId']
            for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
            refs.append(base/step['batch']/'result.json')
    refs.extend([statepath,HERE/'selected_original_four_world_low_face_context_v1_20261024.py',HERE/'selected_original_complete_ground_cap_paths_v2_20261024.py'])
    result=dict(uids=[r['uid']for r in rows],status=state['status'],rows=results,workers=2,currentManifestSHA256=sha,
                sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Exact existing complete-ground and original-topology producers run once for explicit sources. Empty negative partitions skip only unnecessary cap tracing. All raw negative/nonwall/path failures retained; no role, collision, foundation, identity, browser or installed approval.')
    save(out/'summary.json',result)
    module('original_clearance_batch_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'explicit-local-original-ground-clearance-and-cap-batch',refs,result)
    print(dict(status=state['status'],sources=len(rows)),flush=True)


if __name__=='__main__':main()
