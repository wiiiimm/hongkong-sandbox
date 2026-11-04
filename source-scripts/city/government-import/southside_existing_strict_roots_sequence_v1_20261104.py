"""Resolve remaining original warnings against already measured strict anchors."""
import argparse
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-southside-existing-strict-roots-sequence-v1-20261104'
OUT=BASE/BATCH
LEASE=HERE/'local'/BATCH/'reservation.json'
RUNTIME='government-xl-southside-viable-originals-runtime-complete-bindings-v3-20261104'
ATTRS='government-xl-southside-viable-originals-current-rebind-v2-20261104-attributes'
SUPPORT='landsd/315025:0'
TARGETS=['landsd/315027:0','landsd/328308:0','landsd/328310:0']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned',action='store_true')
    a=p.parse_args()
    assert not OUT.exists()
    if not a.owned:
        assert not LEASE.parent.exists()
        claim=reservations.claim('southside-existing-strict-root-followthrough-'+str(uuid.uuid4()),['building:'+u for u in TARGETS+[SUPPORT]],batch=BATCH,ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'],LEASE,[sys.executable,__file__,'--owned'])
    lease=read(LEASE)
    assert reservations.owns(lease)
    refs=[Path(__file__)]
    for n in [RUNTIME,ATTRS]:
        authenticate(BASE/n)
        refs.append(BASE/n/'result.json')
    OUT.mkdir()
    tool=HERE/'original_four_world_strict_root_paths_v2_20261104.py'
    producer=digest(tool.read_bytes())
    rows=[]
    for uid in TARGETS:
        source='government-xl-southside-'+uid.split('/')[1].replace(':','-')+'-current-original-support-v2-20261104'
        receipt,_=authenticate(BASE/source)
        assert receipt['supportUids']==[SUPPORT] and receipt['supportedUid']==uid
        assert all(r['support']['strictContacts']>0 and r['support']['unresolved'] for r in receipt['rows'])
        batch='government-xl-southside-'+uid.split('/')[1].replace(':','-')+'-existing-strict-root-paths-v1-20261104'
        assert not (BASE/batch).exists()
        command=[sys.executable,str(tool),'--batch',batch,'--runtime',RUNTIME,'--attributes',ATTRS,'--strict-support',source,'--uid',uid,'--support',SUPPORT]
        save(OUT/(uid.split('/')[1]+'-command.json'),dict(command=command,producerSHA256=producer))
        assert reservations.owns(lease) and digest(tool.read_bytes())==producer
        with (OUT/(uid.split('/')[1]+'.log')).open('w')as log:
            subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        result,_=authenticate(BASE/batch)
        item=dict(uid=uid,batch=batch,jobId=result['jobId'],rows=result['rows'])
        rows.append(item)
        refs += [BASE/source/'result.json',BASE/batch/'result.json']
        print(item,flush=True)
    refs.append(tool)
    assert reservations.owns(lease)
    result=dict(uids=TARGETS+[SUPPORT],rows=rows,installationApproved=False,supportApproved=False,physicalAccepted=False,qualification='Same complete original meshes and independently replayed canonical strict support anchors. Only the explicit supportUid versus one-element supportUids schema is normalized. Existing endpoint/incidence/shared-edge limits and every direct support/compound negative remain. This is attachment evidence, not whole-source acceptance.')
    save(OUT/'summary.json',result)
    module('southside_existing_strict_roots_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-original-strict-anchor-three-source-followthrough',refs,result)


if __name__=='__main__':
    main()
