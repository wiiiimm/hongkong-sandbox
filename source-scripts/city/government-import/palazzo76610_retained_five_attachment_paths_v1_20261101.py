"""Run unchanged finite source attachment mathematics for five recovered originals."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'retained-five-attachment-sequence-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json'
    keys=['68540','88780','252555','252556','252558'];uids=['landsd/76610:0',*['landsd/'+k+':0'for k in keys]]
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-finite-attachments-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out=BASE/BATCH;assert not out.exists();out.mkdir();tool=HERE/'original_pair_rim_attachment_v3_20261101.py';sha=digest(tool.read_bytes());refs=[Path(__file__),tool];jobs=[]
    for key in keys:
        batch=P+key+'-finite-original-attachments-v1-20261101';cmd=[sys.executable,str(tool),'--batch',batch,'--runtime',P+'twenty-authentic-tin-runtime-v1-20261101','--attributes',P+'twenty-original-attributes-v1-20261101','--contacts',P+'twenty-all-pairs-reused-v1-20261101','--strict-support',P+key+'-original-owner-support-v1-20261101','--uid','landsd/'+key+':0']
        assert reservations.owns(lease)
        with(out/(key+'.log')).open('w')as f:subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        r,_=authenticate(BASE/batch);jobs.append(dict(batch=batch,jobId=r['jobId']));refs.append(BASE/batch/'result.json');assert digest(tool.read_bytes())==sha
    assert reservations.owns(lease)
    module('palazzo_five_attachment_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-finite-source-attachment-sequence',refs,dict(uids=uids,completedJobs=jobs,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':main()
