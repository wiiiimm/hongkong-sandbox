"""Reuse bounded grade witnesses only for exactly identical source and ground."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-unnamed265269-'
BATCH=P+'exact-current-grade-rebind-v1-20261029'
OLD=P+'current-evidence-v1-20261029'
NEW=P+'after-academy-current-v1-20261029'
UID='landsd/265269:0'
SHA='0adf753f5832d3598fd1d99c3700b704e33de74aa97c4d4f868ba68c6cb445da'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def doc(batch,name):return take(batch,BASE/batch/name)
    attrs=[];grounds=[];selections=[]
    for prefix in [OLD,NEW]:
        runtime=prefix+'-runtime';attribute=prefix+'-attributes'
        selections.append(next(r for r in doc(runtime,'selection.json.gz')['rows']if r['uid']==UID))
        attrs.append(next(r for r in doc(attribute,'attributes.json.gz')['rows']if r['uid']==UID))
        grounds.append(next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']==UID)['drawnGroundGeometry'])
    for s in selections:assert s['sourceSHA256']==SHA
    assert selections[0]['source']==selections[1]['source']
    for key in ['sourceSHA256','completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
        assert attrs[0][key]==attrs[1][key],key
    oldground,newground=[np.asarray(g,dtype='<f8')for g in grounds]
    assert oldground.shape==newground.shape and np.array_equal(oldground,newground)
    groundsha=digest(newground.tobytes())
    rolebatch=P+'lower-role-rim-account-v3-20261029';roles=doc(rolebatch,'ROOT-LOWER-ROLE-REVIEW.json');account=doc(rolebatch,'summary.json')
    assert roles['boundedLowerRolesAccepted']and roles['sourceSHA256']==SHA and account['allFourRimAccountsVerified']
    attr=attrs[1];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)
    asset=ROOT/selections[1]['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    original=literal.copy();original[ix.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    proofs=[]
    for mode,positions in worlds.items():
        rim=doc(P+'complete-canonical-rims-v1-20261029',mode+'.json.gz')
        cap=doc(P+'current-cap-paths-v1-20261029',{'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)+'.json.gz')
        worldsha=digest(positions[ix].astype('<f8').tobytes())
        assert worldsha==rim['sourceWorldSHA256']==cap['sourceWorldSHA256']
        assert groundsha==rim['groundSHA256']==cap['completeDrawnGroundSHA256']
        prior=next(r for r in account['rows']if r['mode']==mode)
        assert prior['verified']and prior['sourceWorldSHA256']==worldsha
        proofs.append(dict(mode=mode,sourceWorldSHA256=worldsha,drawnGroundSHA256=groundsha,priorRoleRimAccountStillApplicable=True,
                           ordinaryRimSamples=prior['ordinaryRimSamples'],strictOrdinaryAnchorSamples=prior['strictOrdinaryAnchorSamples'],
                           rawReviewedClearanceFailuresRetained=prior['rawReviewedClearanceFailuresRetained']))
    selection=doc(NEW+'-runtime','selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    foundation=doc(NEW+'-foundation-265269-0','summary.json');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    assert all(r['fullyBuriedTriangles']==2 and r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    scope=doc(NEW+'-model-scope','summary.json');assert scope['currentManifestSHA256']==selection['manifestSHA256']
    assert scope['rows'][0]['currentNativeActorsChecked']==7017 and scope['rows'][0]['currentFormsWithinTwoMetreRegion']==6
    result=dict(uids=[UID],sourceSHA256=SHA,currentManifestSHA256=selection['manifestSHA256'],sourceWorldArraysExactlyUnchanged=True,
                completeDrawnGroundArraysExactlyUnchanged=True,rows=proofs,priorBoundedLowerRoleReviewApplicable=True,
                allFourCurrentFoundationsPassed=True,rawWarningsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,
                identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='All indexed source arrays, actual complete drawn terrain arrays and source form metadata are identical. Every reused raw rim/cap witness is checked against the exact current source-world and ground hashes. Bounded prior lower-wall/two-downward-closure role interpretation remains applicable; eight literal exact shared-edge warnings remain unresolved and retained. Whole identity/canopy/foreign/visual/publication review remains separate.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('unnamed_exact_grade_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-source-complete-ground-equality-and-grade-witness-rebind',refs,result)


if __name__=='__main__':main()
