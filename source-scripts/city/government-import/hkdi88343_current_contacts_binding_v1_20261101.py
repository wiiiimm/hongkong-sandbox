"""Rebind unchanged numerical contacts to HKDI's fresh complete scene scope.

The old manifest remains historical context, not a false current hash. Existing
source-array and full-native-input equality proofs must pass; no approval added.
"""
import sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from hkdi88343_installed_parent_contract_v1_20261101 import UID, PARENT, SHA, PSHA
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-hkdi88343-current-native-contacts-v1-20261101'
OLD='government-xl-cohort19-installed-native-contacts-v1-20261101'
P='government-xl-hkdi88343-after-one-peking-'
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json'
    assert not out.exists()
    resources=['building:'+u for u in [UID,PARENT]]
    if '--owned' not in sys.argv:
        assert not lp.parent.exists()
        c=reservations.claim('hkdi-current-contacts-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert c['ok'];return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        f=BASE/batch/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))]
        refs.append(f);return read(f)
    old=take(OLD);support=take(P+'support-v1-20261101');scope=take(P+'scope-v1-20261101')
    assert support['historicalSourceArraysIdentical'] and support['allOtherHistoricalNativeInputsIdentical']
    assert scope['uids']==[UID] and len(scope['rows'])==1
    assert scope['rows'][0]['sourceSHA256']==SHA and scope['rows'][0]['currentNativeActorsChecked']==7071
    assert [r['uid']for r in scope['rows'][0]['nearbyNativeActors']]==[PARENT]
    pair=next(r for r in old['rows']if r['uid']==UID and r['nativeUid']==PARENT)
    assert pair['sourceSHA256']==SHA and pair['nativeSHA256']==PSHA
    current={m['uid']:m for u in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/u)['models']}
    assert len(current)==7071 and UID not in current and current[PARENT]==pair['rawCurrentNativeEntry']
    # All old geometry/module/form/asset inputs remain exact. Manifest has its
    # separate fresh all-actor scope, and is explicitly retained as historical.
    historical=[]
    for name,sha in pins[OLD].items():
        f=ROOT/name
        if name=='3d-viewer/city/data/manifest.json':historical.append(dict(path=name,sha256=sha));continue
        assert digest(f.read_bytes())==sha,name
        refs.append(f)
    assert len(historical)==1
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==scope['currentManifestSHA256'];refs.append(manifest)
    assert reservations.owns(lease)
    result={**old,'uids':[UID],'rows':[pair],'strictlySeparatedNativePairs':[],
        'currentManifestSHA256':digest(manifest.read_bytes()),'historicalContextOnly':historical,
        'completeFreshCurrentScope':str((BASE/(P+'scope-v1-20261101')/'result.json').relative_to(ROOT)),
        'sourceGeometryChanges':0,'numericContactRecomputation':False,'installationApproved':False,
        'qualification':'Exact old contact arrays and every nonmanifest input unchanged; complete fresh7071actor scope checks sole current parent. All raw contact outcomes retained. No acceptance or publication.'}
    save(out/'summary.json',result)
    module('hkdi_current_native_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-unchanged-hkdi-contact-numerics-current-full-scene-binding',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
