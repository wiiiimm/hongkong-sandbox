"""Reuse exact original bytes for a leased current selection and runtime capture.

No old terrain/source/physical approvals transfer and no public files change.
"""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,reservations
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.capture])
    assert 0<len(a.uid)==len(set(a.uid))<=40 and all(u.startswith('landsd/')and ':'in u for u in a.uid)
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/(a.batch+'-lease');assert not out.exists()
    resources=sorted(['building:'+u for u in a.uid]+['terrain:city/data/terrain.json'])
    if not a.owned:
        assert not local.exists();claim=reservations.claim('current-original-preparation-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],local/'reservation.json',[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(local/'reservation.json');assert reservations.owns(lease)and lease['resources']==resources
    selection=a.batch+'-selection';runtime=a.batch+'-runtime';commands=[]
    for label,tool,batch,capture in [('selection','selected_original_refresh_selection_v1.py',selection,a.capture),('runtime','selected_original_current_capture_v3.py',runtime,selection)]:
        command=[sys.executable,str(HERE/tool),'--batch',batch,'--capture',capture]
        for uid in a.uid:command+=['--uid',uid]
        out.mkdir(exist_ok=True)
        with(out/(label+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert reservations.owns(lease);commands.append(dict(step=label,command=command,exitCode=0))
    result=dict(uids=a.uid,selection=selection,runtime=runtime,commands=commands,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,qualification='Exact original selection and actual unchanged-current-ground runtime capture under existing complete source leases. Reuses source bytes only; no prior approval or source placement changes.')
    save(out/'summary.json',result)
    refs=[Path(__file__),HERE/'selected_original_refresh_selection_v1.py',HERE/'selected_original_current_capture_v3.py',base/selection/'result.json',base/runtime/'result.json']
    module('owned_current_preparation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'leased-exact-current-original-selection-and-runtime-preparation',refs,result)
if __name__=='__main__':main()
