"""Measure twelve viable original dependants against the unchanged original podium.

Four local compute processes share the complete original-group lease. Each
existing support/foundation producer writes its own immutable diagnostic batch.
No source-role, identity, physical or publication approval is granted.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
import sys
import uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-viable-original-support-sequence-v1-20261104'
OUT = BASE/BATCH
LEASE = HERE/'local'/BATCH/'reservation.json'
REBOUND = 'government-xl-southside-viable-originals-current-rebind-v2-20261104'
RUNTIME, ATTRIBUTES = REBOUND+'-runtime', REBOUND+'-attributes'
UID = 'landsd/315025:0'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned',action='store_true')
    a=p.parse_args()
    receipt,_=authenticate(BASE/REBOUND)
    uids=receipt['uids']
    assert len(uids)==13 and UID in uids and not OUT.exists()
    resources={'building:'+u for u in uids}|{'terrain:city/data/terrain.json'}
    if not a.owned:
        assert not LEASE.parent.exists()
        claim=reservations.claim('southside-viable-original-support-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'],LEASE,[sys.executable,__file__,'--owned'])
    lease=read(LEASE)
    assert reservations.owns(lease) and resources<=set(lease['resources'])
    refs=[Path(__file__),BASE/REBOUND/'result.json']
    for name,filename in [(RUNTIME,'selection.json.gz'),(ATTRIBUTES,'attributes.json.gz')]:
        _,pins=authenticate(BASE/name)
        path=BASE/name/filename
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs += [BASE/name/'result.json',path]
    selection=read(BASE/RUNTIME/'selection.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256']
    refs.append(manifest)
    tool=HERE/'original_multiple_four_world_support_v1_20261023.py'
    producer_sha=digest(tool.read_bytes())
    refs.append(tool)
    OUT.mkdir()
    state=dict(running=True,completed=[],sourceUids=uids,localComputeProcesses=4,installationApproved=False)
    save(OUT/'state.json',state)

    def run(uid):
        assert reservations.owns(lease) and digest(tool.read_bytes())==producer_sha
        batch='government-xl-southside-'+uid.split('/')[1].replace(':','-')+'-current-original-support-v1-20261104'
        assert not (BASE/batch).exists()
        command=[sys.executable,str(tool),'--batch',batch,'--runtime',RUNTIME,'--attributes',ATTRIBUTES,'--supported',uid,'--support',UID]
        save(OUT/(uid.split('/')[1]+'-command.json'),dict(command=command,producerSHA256=producer_sha))
        logpath=OUT/(uid.split('/')[1]+'.log')
        with logpath.open('w')as log:
            proc=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        assert proc.returncode==0,uid+' support diagnostic failed; preserve '+str(logpath.relative_to(ROOT))
        child,_=authenticate(BASE/batch)
        assert reservations.owns(lease) and digest(tool.read_bytes())==producer_sha
        return dict(uid=uid,batch=batch,jobId=child['jobId'],allFourModesPassed=child['allFourModesPassed'],modes=[dict(mode=r['mode'],strictContacts=r['support']['strictContacts'],samples=r['support']['samples'],unresolved=len(r['support']['unresolved']),compoundBuried=r['compoundFoundation']['fullyBuriedTriangles'],compoundUpwardBuried=r['compoundFoundation']['fullyBuriedUpwardTriangles'],passed=r['passed'])for r in child['rows']])

    try:
        with ThreadPoolExecutor(max_workers=4)as pool:
            futures=[pool.submit(run,u)for u in uids if u!=UID]
            for future in as_completed(futures):
                result=future.result()
                state['completed'].append(result)
                save(OUT/'state.json',state)
                print(result,flush=True)
        assert len(state['completed'])==12 and reservations.owns(lease)
        assert digest(manifest.read_bytes())==selection['manifestSHA256']
        for row in state['completed']:
            refs.append(BASE/row['batch']/'result.json')
        state['running']=False
        save(OUT/'state.json',state)
        result=dict(uids=uids,dependants=12,rows=sorted(state['completed'],key=lambda r:r['uid']),allFourModePasses=sum(r['allFourModesPassed']for r in state['completed']),originalsUnchanged=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification=__doc__+' The four excluded Southland originals receive no approval or installation credit. Every direct-support/compound-foundation negative remains available for exact shared-edge/whole-source follow-through.')
        save(OUT/'summary.json',result)
        module('southside_viable_original_support_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-viable-original-group-four-world-support-foundation-diagnostics',list(dict.fromkeys(refs)),result)
    except BaseException as error:
        state.update(running=False,error=repr(error))
        save(OUT/'state.json',state)
        raise


if __name__=='__main__':
    main()
