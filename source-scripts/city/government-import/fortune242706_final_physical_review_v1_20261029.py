"""Review an unchanged standalone original using ordinary passing physical gates."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

UID='landsd/242706:0';SOURCE='c48db570a1012723e1f8610f3660619aa62e32c48e4a9e46bf5ccfa033c30166'
BATCH='government-xl-fortune242706-final-physical-review-v1-20261029'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime='government-xl-fortune242706-final-runtime-v1-20261029';rows=take(runtime,base/runtime/'selection.json.gz');assert len(rows['rows'])==1;row=rows['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset);original=decode_original_world_triangles(asset.read_bytes());assert len(original)==row['triangles']==14439
    identity=take('government-xl-six-current-clearance-v1-20261029-identity',base/'government-xl-six-current-clearance-v1-20261029-identity/242706:0/identity.json');assert identity['passed']and not identity['reasons']and identity['sourceSHA256']==SOURCE
    assert all(identity['proof'][k]for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    attrs=take('government-xl-fortune242706-final-attributes-v1-20261029',base/'government-xl-fortune242706-final-attributes-v1-20261029/attributes.json.gz')['rows'][0]
    before=take('government-xl-two-complete-tin-recovery-v1-20261029-242706-0-attributes',base/'government-xl-two-complete-tin-recovery-v1-20261029-242706-0-attributes/attributes.json.gz')['rows'][0]
    assert attrs['sourceSHA256']==before['sourceSHA256']==SOURCE and attrs['completeOriginalIndex']==before['completeOriginalIndex']
    preserved=[]
    for field in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
        old=np.asarray(before[field],dtype='<f8');new=np.asarray(attrs[field],dtype='<f8');assert old.tobytes()==new.tobytes();preserved.append(dict(field=field,worldArraySHA256=digest(new.tobytes())))
    foundation=take('government-xl-fortune242706-final-foundations-v1-20261029',base/'government-xl-fortune242706-final-foundations-v1-20261029/summary.json');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    assert all(r['triangles']==r['completeTerrainTriangles']==14439 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    rims=take('government-xl-fortune242706-final-raw-rims-v1-20261029',base/'government-xl-fortune242706-final-raw-rims-v1-20261029/summary.json');assert len(rims['rows'])==4 and all(r['groundContactResolved']and r['minimumRimGapM']>=-.5 and r['maximumRimGapM']<=1 and r['minimumRimGapM']<=.1 for r in rims['rows'])
    neighbours=take('government-xl-fortune242706-final-neighbours-v1-20261029',base/'government-xl-fortune242706-final-neighbours-v1-20261029/summary.json');assert neighbours['forms']==28 and not neighbours['basicFlags']and not neighbours['requiredNativeUids']and not neighbours['nativeRows']
    scopebatch='government-xl-fortune242706-final-terrain-scope-v1-20261029';scope=take(scopebatch,base/scopebatch/'scope.json');forms=take(scopebatch,base/scopebatch/'form-obligations.json.gz');assert len(forms)==28 and not scope['terrainContacts']and not scope['touchingNativeUids']and scope['currentNativeActors']==7015
    modelbatch='government-xl-fortune242706-corrected-model-scope-v1-20261029';modelscope=take(modelbatch,base/modelbatch/'summary.json');assert len(modelscope['rows'])==1 and not modelscope['rows'][0]['nearbyNativeActors']and modelscope['rows'][0]['currentNativeActorsChecked']==7015
    foreign=take('government-xl-fortune242706-corrected-foreign-contacts-v1-20261029',base/'government-xl-fortune242706-corrected-foreign-contacts-v1-20261029/summary.json');assert len(foreign['rows'])==12 and all(r['uid']==UID and all(m['positiveContactPairs']==0 for m in r['modes'])for r in foreign['rows'])
    patchbatch='government-xl-fortune242706-rendered-floor-return-v2-20261029';patch=take(patchbatch,base/patchbatch/'summary.json');assert patch['status']=='private-terrain-validator-passed'and patch['sourceSHA256ByUid']=={UID:SOURCE};candidate=ROOT/patch['candidate']['path'];take(patchbatch,candidate)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==rows['manifestSHA256']==pins[scopebatch][str(manifest.relative_to(ROOT))]==modelscope['currentManifestSHA256'];refs.append(manifest)
    resources=sorted({'building:'+f['uid']for f in forms}|{'terrain:city/data/terrain.json'})
    result=dict(uids=[UID],reviewer='Codex ROOT',sourceSHA256ByUid={UID:SOURCE},requiredOriginalAssembly={UID:SOURCE},supportByUid={},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,identityAccepted=True,identityProof=identity['proof'],completeFourWorldFoundations=True,completeCurrentNeighbourChecks=28,leaseResources=resources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceWorldArraysPreserved=preserved,completeOriginalFaces=14439,positiveForeignContactPairs=0,currentNativeActors=7015,terrainCandidate=patch['candidate'],ordinaryRimRows=rims['rows'],ordinaryFoundationRows=foundation['rows'],noClearanceExceptionUsed=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,visualAcceptance=False,installationApproved=False,publication=False,basis='Exact current typed source identity passes unchanged. Complete four-world foundations and ordinary low-rim contact policy pass without exceptions; every scoped neighbour is retained and has no regression. All twelve immediate foreign actors have zero positive source contacts in each measured representation; original model arrays are bit-identical before/after the private terrain correction. The complete government source remains at native pose/1x scale. Four indexed original terrain sheets plus the existing bounded source-floor return provide terrain, with the production Float32 representation independently verified. Final exact-output visual/browser and guarded publication remain separate.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'summary.json',result)
    module('fortune_final_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'ordinary-gates-exact-fortune-original-current-physical-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
