"""Refresh Parkview16's exact original and current physical scope; no approvals."""
import subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview256319-after-tung-cheong-v1-20261104'
OLD='government-xl-cohort19-current-original-checks-v1-20261101-runtime'
INVENTORY='government-xl-after-tung-cheong-current-native-bounds-v1-20261104'
UID='landsd/256319:0'

def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json';assert not out.exists()
    resources=sorted(['building:'+u for u in [UID,'landsd/254491:0','landsd/256116:0']]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('parkview16-current-preparation-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    inventory,pins=authenticate(BASE/INVENTORY);manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==pins[str(manifest.relative_to(ROOT))]and inventory['currentNativeActors']==7108
    refs=[Path(__file__),manifest,BASE/INVENTORY/'result.json'];out.mkdir();done=[]
    selection=BATCH+'-selection';runtime=BATCH+'-runtime';attributes=BATCH+'-attributes'
    steps=[(selection,'selected_original_refresh_selection_v1.py',['--capture',OLD,'--uid',UID]),(runtime,'selected_original_current_capture_v3.py',['--capture',selection,'--uid',UID]),(BATCH+'-identity','selected_original_identity_v3.py',['--capture',runtime]),(attributes,'selected_original_render_attributes_v1.py',['--capture',runtime]),(BATCH+'-source-scope','selected_original_model_only_scope_v1_20261023.py',['--runtime',runtime,'--attributes',attributes,'--inventory',INVENTORY])]
    save(out/'commands.json',dict(steps=steps,resources=resources,publication=False))
    for batch,name,args in steps:
        assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and not(BASE/batch).exists()
        tool=HERE/name;sha=digest(tool.read_bytes());save(out/'state.json',dict(running=True,phase=batch,completed=done));print('starting '+batch,flush=True)
        with(out/(batch+'.log')).open('w')as log:subprocess.run([sys.executable,str(tool),'--batch',batch,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert digest(tool.read_bytes())==sha and reservations.owns(lease);receipt,_=authenticate(BASE/batch);done.append(dict(batch=batch,jobId=receipt['jobId']));refs.extend([tool,BASE/batch/'result.json']);print(done[-1],flush=True)
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    result=dict(uids=[UID],completed=done,currentManifestSHA256=mh,currentNativeActors=7108,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Fresh current original/identity/complete attributes and source scope only. All raw findings retained; no original terrain, contact or acceptance interpretation transferred. Next source-specific terrain/foundation and native interface work depends on these exact current results.')
    save(out/'state.json',dict(running=False,completed=done));save(out/'summary.json',result)
    module('parkview16_current_preparation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-unapproved-original-preparation-and-full-native-source-scope',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
