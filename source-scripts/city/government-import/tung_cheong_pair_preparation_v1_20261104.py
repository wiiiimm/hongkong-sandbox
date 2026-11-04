"""Run existing paired-original diagnostics under the complete current retained lease."""
import sys,uuid,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tung-cheong-pair-preparation-v1-20261104'
SELECTION='government-xl-tung-cheong-paired-diagnostic-selection-v1-20261104'
OLD_PATCH='government-xl-tung-cheong53799-retained-inset-v1-20261103'
OLD_RUNTIME='government-xl-tung-cheong53799-after-silvercord-v1-20261103-runtime'
INVENTORY='government-xl-after-silvercord-current-native-bounds-v2-20261103'

def main():
    out=BASE/BATCH;local=HERE/'local'/(BATCH+'-control');lp=local/'reservation.json';assert not out.exists()
    selection,pins=authenticate(BASE/SELECTION);resources=selection['leaseResources'];uids=selection['uids'];assert set(uids)=={'landsd/53799:0','landsd/223636:0'}and selection['identityAccepted']is False
    if '--owned'not in sys.argv:
        assert not local.exists();c=reservations.claim('tung-cheong-pair-preparation-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['currentManifestSHA256'];refs=[Path(__file__),BASE/SELECTION/'result.json',manifest]
    terrain=BATCH+'-terrain';runtime=BATCH+'-runtime';attributes=BATCH+'-attributes'
    steps=[(terrain,'rebind_private_original_terrain_v3_20261102.py',['--previous',OLD_PATCH,'--capture',SELECTION,'--previous-capture',OLD_RUNTIME]),(runtime,'selected_original_patch_runtime_v8_20261101.py',['--patch',terrain,'--capture',SELECTION,*[v for u in uids for v in ['--uid',u]]]),(BATCH+'-identity','selected_original_identity_v3.py',['--capture',runtime]),(attributes,'selected_original_render_attributes_v1.py',['--capture',runtime]),(BATCH+'-source-scope','selected_original_model_only_scope_v1_20261023.py',['--runtime',runtime,'--attributes',attributes,'--inventory',INVENTORY]),(BATCH+'-terrain-scope','selected_original_retained_patch_scope_v3_20261026.py',['--inventory',INVENTORY,'--patch',terrain])]
    out.mkdir();save(out/'commands.json',dict(steps=steps,resources=resources,installationApproved=False));completed=[]
    for batch,tool,args in steps:
        assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and not(BASE/batch).exists()
        producer=HERE/tool;before=digest(producer.read_bytes());save(out/'state.json',dict(running=True,phase=batch,completed=completed));print('starting '+batch,flush=True)
        with(out/(batch+'.log')).open('w')as log:subprocess.run([sys.executable,str(producer),'--batch',batch,*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        assert digest(producer.read_bytes())==before and reservations.owns(lease);r,_=authenticate(BASE/batch);refs.extend([producer,BASE/batch/'result.json']);completed.append(dict(batch=batch,jobId=r['jobId']));print(completed[-1],flush=True)
        if batch==terrain:assert r['status']=='private-terrain-validator-passed'and r['candidateBytesUnchanged']and r['additionalExplicitCompanionUids']==['landsd/223636:0']
        if batch==attributes:
            fresh={r['uid']:r for r in read(BASE/attributes/'attributes.json.gz')['rows']}
            previous=[('landsd/53799:0','government-xl-tung-cheong53799-post-inset-v1-20261103-attributes','attributes.json.gz'),('landsd/223636:0','government-xl-tung-cheong-unmatched-four-world-context-v2-20261103','raw-renderer-attributes.json.gz')]
            comparisons=[]
            for uid,old,name in previous:
                _,bound=authenticate(BASE/old);p=BASE/old/name;assert digest(p.read_bytes())==bound[str(p.relative_to(ROOT))];refs.extend([BASE/old/'result.json',p]);prior=next(r for r in read(p)['rows']if r['uid']==uid)
                assert prior['sourceSHA256']==fresh[uid]['sourceSHA256']
                for field in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert prior[field]==fresh[uid][field],(uid,field)
                comparisons.append(dict(uid=uid,sourceSHA256=fresh[uid]['sourceSHA256'],completeSourceArraysExactlyEqual=True))
            save(out/'unchanged-complete-four-world-source-arrays.json',comparisons)
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    save(out/'state.json',dict(running=False,completed=completed))
    result=dict(uids=uids,completed=completed,currentManifestSHA256=mh,sourceGeometryChanges=0,sourcePoseChanges=0,terrainBytesChanged=0,nativeLowViewerUid=None,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,diagnosticOnly=True,qualification='Existing current private terrain/runtime/identity/full-attribute and full source/terrain scope producers. Raw identity failures and native unmatched status are preserved. All original coordinate/index arrays match their prior authenticated complete four-world captures exactly. New paired scene/publication checks remain outstanding; no installation or terrain-ownership expansion.')
    save(out/'summary.json',result);module('tung_cheong_pair_preparation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-private-paired-original-preparation-preserving-unmatched-source',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
