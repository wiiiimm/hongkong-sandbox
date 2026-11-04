"""Export exact renderer attributes and complete current original-model scope."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','inventory']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--uid',action='append',required=True);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.runtime,a.inventory]);assert 0<len(a.uid)==len(set(a.uid))<=40
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;control=HERE/'local'/(a.batch+'-lease')/'reservation.json';assert not out.exists()
    pins=authenticate(base/a.runtime)[1];path=base/a.runtime/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];assert {r['uid']for r in read(path)['rows']}==set(a.uid)
    resources=sorted(['building:'+u for u in a.uid]+['terrain:city/data/terrain.json'])
    if not a.owned:
        assert not control.parent.exists();claim=reservations.claim('original-current-scope-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],control,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(control);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    attributes=a.batch+'-attributes';scope=a.batch+'-scope'
    commands=[('attributes',[sys.executable,str(HERE/'selected_original_render_attributes_v1.py'),'--batch',attributes,'--capture',a.runtime]),('scope',[sys.executable,str(HERE/'selected_original_model_only_scope_v1_20261023.py'),'--batch',scope,'--runtime',a.runtime,'--attributes',attributes,'--inventory',a.inventory])]
    for step,command in commands:
        out.mkdir(exist_ok=True)
        with(out/(step+'.log')).open('w')as log:subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert reservations.owns(lease)
    result=dict(uids=a.uid,runtime=a.runtime,attributes=attributes,scope=scope,currentInventory=a.inventory,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False)
    save(out/'summary.json',result);module('owned_current_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'leased-complete-current-original-attributes-and-scope',[Path(__file__),base/a.runtime/'result.json',base/a.inventory/'result.json',base/attributes/'result.json',base/scope/'result.json'],result)
if __name__=='__main__':main()
