"""Replay the existing exact Yoho8/podium identity policy on fresh scene bindings.

Original provider/source facts are historical immutable evidence. Current forms,
manifest, source bytes and native-source versions are verified independently.
No terrain, physical, installation or component-function approval is inferred.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from yoho_eight_current_bound_identity_20261009 import DOC,QUERIES,checked_provider,stream_pin,native_rows
from yoho_eight_related_original_podium_identity_20261009 import UID,RELATED,SOURCE_SHA,PODIUM_SHA,named_proof
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','identity','scope']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)];bound={}
    for name in [a.runtime,a.identity,a.scope]:
        _,bound[name]=authenticate(base/name);refs.append(base/name/'result.json')
    historical,hp=authenticate(DOC);refs.append(DOC/'result.json')
    def take(path,pins):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selected=take(base/a.runtime/'selection.json.gz',bound[a.runtime])
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selected['manifestSHA256']==bound[a.scope][str(manifest.relative_to(ROOT))]
    refs.append(manifest)
    row=next(r for r in selected['rows']if r['uid']==UID)
    raw=take(base/a.identity/(UID.split('/')[1]+'/identity.json'),bound[a.identity])
    assert raw['sourceSHA256']==row['sourceSHA256']==SOURCE_SHA
    forms=take(base/a.scope/'form-obligations.json.gz',bound[a.scope])
    scope=take(base/a.scope/'scope.json',bound[a.scope]);assert scope['uids']==[UID]and len(forms)==scope['intersectingForms']
    source=take(DOC/'original-source-lookup.json.gz',hp)
    historical_inputs=take(DOC/'current-inputs.json.gz',hp)
    pins=take(DOC/'complete-original-stream-pins.json.gz',hp)
    for name in QUERIES:
        for suffix in ['.json','.request.json','.provider-original.gz']:
            path=DOC/(name+suffix)
            if path.exists():take(path,hp) if suffix!='.provider-original.gz'else refs.append(path)
            if path.exists():assert digest(path.read_bytes())==hp[str(path.relative_to(ROOT))]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert native_rows(db)==source['rows'],'Current original source versions changed'
    assert row['native']['model']==source['rows'][0]['model'] and row['native']['resultSha']==source['rows'][0]['resultSHA256']
    tower=ROOT/row['candidate']['path'];podium=ROOT/historical_inputs['podiumOriginalPath']
    assert digest(tower.read_bytes())==SOURCE_SHA and digest(podium.read_bytes())==PODIUM_SHA
    refs.extend([tower,podium])
    assert pins=={'tower':stream_pin(tower.read_bytes(),row['modelId'],14792),'podium':stream_pin(podium.read_bytes(),'B218783363602062G0',7731)}
    evidence=dict(rows=source['rows'],primaryRecords=checked_provider('exact-current-primary'),exactRelations=checked_provider('exact-current-structure-relations'),exactStructures=checked_provider('exact-current-structure-details'))
    assert evidence==source
    proof=named_proof(raw,row,decode_original_world_triangles(tower.read_bytes()),decode_original_world_triangles(podium.read_bytes()),forms,evidence)
    proof.update(currentManifestSHA256=selected['manifestSHA256'],historicalProviderEvidenceJobId=historical['jobId'],historicalManifestApprovalTransferred=False,currentNativeSourceVersionsReadBack=True,sourceSpecificIdentityRecomputed=True)
    save(out/'identity.json',proof)
    result=dict(uids=[UID],identityAccepted=proof['passed'],sourceSHA256=SOURCE_SHA,relatedOriginalSourceSHA256=PODIUM_SHA,currentManifestSHA256=selected['manifestSHA256'],rawReasonsRetained=raw['reasons'],remainingReasons=proof['reasons'],fullCurrentScopeForms=len(forms),exactOriginalInterfaces=len([r for r in proof['exactOriginalMainBodyToWholePodiumContacts']['contacts']if r['dimension']>0]),sourceGeometryChanges=0,installationApproved=False,physicalAccepted=False,qualification='Recompute the already source-specific named policy against complete fresh source/form bindings. Historical provider/source facts transfer only after exact byte/native-version/stream checks. Full physical, current collision, terrain, browser and publication checks remain separate.')
    save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['yoho_eight_current_bound_identity_20261009.py','yoho_eight_related_original_podium_identity_20261009.py','exact_original_component_contacts_20261009.py','exact_packed_world_geometry_20261009.py','source_closed_components.py'])
    module('yoho_rebound_identity_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-rebound-exact-original-yoho-eight-podium-identity',refs,result)
    print(result,flush=True)

if __name__=='__main__':main()
