"""Replay exact current native arrays, then diagnose authentic Parkview podium support."""
import subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview256319-installed-support-sequence-v1-20261104'
CURRENT='government-xl-parkview256319-after-tung-cheong-v1-20261104'
OLDATTR='government-xl-cohort19-original-attributes-v1-20261101'
OLDCONTACT='government-xl-cohort19-installed-native-contacts-v1-20261101'
INVENTORY='government-xl-after-tung-cheong-current-native-bounds-v1-20261104'

def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json';assert not out.exists()
    resources=sorted(['building:'+u for u in ['landsd/256319:0','landsd/254491:0','landsd/256116:0']]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('parkview16-native-support-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    receipt,pins=authenticate(BASE/CURRENT);assert receipt['currentNativeActors']==7108
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==receipt['currentManifestSHA256'];out.mkdir();done=[];refs=[Path(__file__),manifest,BASE/CURRENT/'result.json']
    native=BATCH+'-native-rebind';support=BATCH+'-strict-support'
    steps=[(native,'rebind_exact_current_native_contacts_v1_20261104.py',['--scope',CURRENT+'-source-scope','--runtime',CURRENT+'-runtime','--attributes',CURRENT+'-attributes','--historical-attributes',OLDATTR,'--prior',OLDCONTACT,'--inventory',INVENTORY]),(support,'proposed_original_installed_support_diagnostic_v1_20261024.py',['--runtime',CURRENT+'-runtime','--attributes',CURRENT+'-attributes','--inventory',INVENTORY,'--native-contacts',native,'--historical-attributes',OLDATTR,'--uid','landsd/256319:0','--support','landsd/254491:0'])]
    save(out/'commands.json',dict(steps=steps,resources=resources,publication=False))
    for batch,name,args in steps:
        assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and not(BASE/batch).exists()
        tool=HERE/name;sha=digest(tool.read_bytes());save(out/'state.json',dict(running=True,phase=batch,completed=done));print('starting '+batch,flush=True)
        with(out/(batch+'.log')).open('w')as log:subprocess.run([sys.executable,str(tool),'--batch',batch,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert digest(tool.read_bytes())==sha and reservations.owns(lease);r,_=authenticate(BASE/batch);done.append(dict(batch=batch,jobId=r['jobId']));refs.extend([tool,BASE/batch/'result.json']);print(done[-1],flush=True)
    result=dict(uids=['landsd/256319:0','landsd/254491:0'],completed=done,currentManifestSHA256=mh,sourceGeometryChanges=0,nativeMetadataChanges=0,physicalSupportAccepted=False,installationApproved=False,publication=False,qualification=__doc__)
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh;save(out/'summary.json',result);save(out/'state.json',dict(running=False,completed=done))
    module('parkview16_current_support_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-installed-native-support-diagnostics-only',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
