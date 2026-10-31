"""Render the five positive retained BASIC junctions; unchanged existing plotter."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'retained-five-views-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json'
    forms=read(BASE/(P+'fourteen-authentic-tin-scope-v1-20261101')/'form-obligations.json.gz')
    resources=sorted({('building:'if r['uid'].startswith('landsd/')else'source-form:')+r['uid']for r in forms})
    if not a.owned:
        assert not (BASE/BATCH/'result.json').exists();c=reservations.claim('palazzo-retained-views-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out=BASE/BATCH;assert not (out/'result.json').exists();out.mkdir(exist_ok=True);refs=[Path(__file__)];jobs=[]
    rebind=P+'owner64-foreign-current-rebind-v1-20261101';authenticate(BASE/rebind)
    tool=HERE/'selected_original_basic_interface_views_v1_20261029.py';toolsha=digest(tool.read_bytes())
    for key in ['68540','88780','252555','252556','252558']:
        assert reservations.owns(lease);batch=P+key+'-retained-interface-views-v1-20261101'
        cmd=[sys.executable,str(tool),'--batch',batch,'--runtime',P+'fifteen-authentic-tin-runtime-v1-20261101','--foreign','government-xl-after-villa-premiere-76610-foreign-contacts-v1-20261031','--uid','landsd/76610:0','--basic','landsd/'+key+':0']
        if not (BASE/batch/'result.json').exists():
            with(out/(key+'.log')).open('w')as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        else:
            _,pins=authenticate(BASE/batch)
            assert pins[str(tool.relative_to(ROOT))]==toolsha
            child=read(BASE/batch/'summary.json')
            assert child['basicUid']=='landsd/'+key+':0' and child['uids']==['landsd/76610:0']
        assert digest(tool.read_bytes())==toolsha
        d=authenticate(BASE/batch)[0];jobs.append(dict(batch=batch,jobId=d['jobId']));refs.append(BASE/batch/'result.json')
    assert reservations.owns(lease);refs.extend([tool,BASE/rebind/'result.json'])
    module('palazzo_retained_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-current-original-retained-basic-junction-views',refs,dict(uids=['landsd/76610:0'],completedJobs=jobs,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':main()
