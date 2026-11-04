"""Account for two new originals' lower source faces on unchanged current terrain."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'two-new-lower-context-sequence-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH
    scope=P+'fourteen-authentic-tin-scope-v1-20261101';forms=read(BASE/scope/'form-obligations.json.gz');resources=sorted({('building:'if r['uid'].startswith('landsd/')else'source-form:')+r['uid']for r in forms}|{'terrain:city/data/terrain.json'})
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-new-lower-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);assert not out.exists();out.mkdir();refs=[Path(__file__)];jobs=[]
    authenticate(BASE/scope);refs.append(BASE/scope/'result.json')
    for key in ['252556','252558']:
        grade=P+key+'-twenty-source-ground-contacts-v1-20261101';lower=P+key+'-twenty-below-grade-context-v1-20261101'
        for script,batch,extra in [('original_source_ground_contacts_v2_20261031.py',grade,[]),('original_below_grade_source_context_v2_20261101.py',lower,['--clearance',P+key+'-twenty-complete-ground-v1-20261101','--grade',grade])]:
            tool=HERE/script;sha=digest(tool.read_bytes());refs.append(tool);assert reservations.owns(lease)
            cmd=[sys.executable,str(tool),'--batch',batch,'--uid','landsd/'+key+':0','--runtime',P+'twenty-authentic-tin-runtime-v1-20261101','--attributes',P+'twenty-original-attributes-v1-20261101','--lease',str(lp),*extra]
            with(out/(key+'-'+('grade'if batch==grade else'context')+'.log')).open('w')as f:subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
            assert digest(tool.read_bytes())==sha;result,_=authenticate(BASE/batch);refs.append(BASE/batch/'result.json');jobs.append(dict(batch=batch,jobId=result['jobId']))
    assert reservations.owns(lease)
    module('palazzo_two_lower_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-new-original-complete-grade-and-lower-face-contexts',list(dict.fromkeys(refs)),dict(uids=['landsd/252556:0','landsd/252558:0'],completedJobs=jobs,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':main()
