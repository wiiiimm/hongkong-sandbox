"""Capture twenty immutable originals on the unchanged authenticated terrain."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'twenty-runtime-sequence-v1-20261101';CAP=P+'twenty-original-selection-v1-20261101';RUNTIME=P+'twenty-authentic-tin-runtime-v1-20261101';ATTR=P+'twenty-original-attributes-v1-20261101';SCOPE=P+'fourteen-authentic-tin-scope-v1-20261101';PATCH=P+'fourteen-authentic-tin-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH
    uids=sorted(r['uid']for r in read(BASE/CAP/'selection.json.gz')['rows']);assert len(uids)==20
    forms=read(BASE/SCOPE/'form-obligations.json.gz');resources={('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms}|{'building:'+u for u in uids}|{'terrain:city/data/terrain.json'}
    new_scope=P+'retained-five-original-model-only-scope-v1-20261101'
    for uid in ['landsd/'+k+':0'for k in ['68540','88780','252555','252556','252558']]:
        for f in read(BASE/new_scope/(uid.split('/')[1]+'-forms.json.gz')):
            k=f['building']['uid'];resources.add(('building:'if k.startswith('landsd/')else'source-form:')+k)
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-twenty-runtime-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources and not out.exists();out.mkdir();refs=[Path(__file__)]
    for b in [CAP,SCOPE,PATCH,new_scope]:authenticate(BASE/b);refs.append(BASE/b/'result.json')
    def run(script,args,log):
        t=HERE/script;sha=digest(t.read_bytes());refs.append(t)
        with(out/log).open('w')as f:subprocess.run([sys.executable,str(t),*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        assert digest(t.read_bytes())==sha and reservations.owns(lease)
    run('selected_original_patch_runtime_v8_20261101.py',['--batch',RUNTIME,'--patch',PATCH,'--capture',CAP,'--scope',SCOPE,*sum([['--uid',u]for u in uids],[])],'runtime.log')
    authenticate(BASE/RUNTIME);refs.append(BASE/RUNTIME/'result.json')
    run('merge_exact_render_attributes_v1_20261028.py',['--batch',ATTR,'--runtime',RUNTIME,'--attributes',P+'fifteen-original-attributes-v1-20261101','--attributes',P+'retained-five-original-attributes-v1-20261101'],'attributes.log')
    authenticate(BASE/ATTR);refs.append(BASE/ATTR/'result.json')
    module('palazzo_twenty_runtime_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-original-current-terrain-renderer-capture',refs,dict(uids=uids,runtimeBatch=RUNTIME,attributesBatch=ATTR,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,physicalAcceptance=False,publication=False,qualification=__doc__+' Existing per-source runtime budgets and all terrain/source scope checks retained. V8 extends diagnostic capacity16→24 only; no geometric tolerance, runtime budget, source/ground surface or publication guard change.'))
if __name__=='__main__':main()
