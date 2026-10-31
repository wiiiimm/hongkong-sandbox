"""Bounded original lower-skin role review, independent of whole installation acceptance."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-prosperous235568'
UID='landsd/235568:0'
SHA='ef354fbb79cbbf576a0e146cf019f2a1ae73c75b031dde2ece59dcdee8f78ac2'
BATCH=P+'-lower-source-role-review-v1-20261031'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lease',required=True);a=ap.parse_args()
    lease=read(Path(a.lease));assert reservations.owns(lease) and 'building:'+UID in lease['resources']
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    identity=take(P+'-podium-identity-review-v1-20261031','235568:0-review.json')
    assert identity['uid']==UID and identity['sourceSHA256']==SHA and identity['identityOnlyApproved']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==identity['rawProof']['exactRouteManifestSHA256'];refs.append(manifest)
    context=P+'-lower-source-context-v1-20261031';summary=take(context,'summary.json');assert summary['sourceSHA256']==SHA and summary['sourceRoleProposalOnly']
    assert {r['mode']for r in summary['rows']}=={'original','literal','leftF32','balancedF32'}
    rows=[]
    for mode in ['original','literal','leftF32','balancedF32']:
        r=take(context,mode+'.json.gz');assert len(r['completeNegativeFaces'])==85 and len(r['negativeWallFaces'])==65
        assert all(p['hasExactSharedEdgeClearCapPath']for p in r['all65WallCapPaths'])
        body=r['original84FaceClosedSkin'];assert len(body['sourceFaceIds'])==84 and len(body['upwardCaps'])==20 and len(body['wallFaces'])==44
        assert body['allUpwardCapsOutsideNegativePartition'] and len(body['negativeDownwardFaceIds'])==18
        assert len(r['originalTwoUndersideFaces'])==2 and r['lowerFacesProvideNoRootOrBridge']
        rows.append(dict(mode=mode,sourceWorldSHA256=r['sourceWorldSHA256'],completeGroundSHA256=r['completeGroundSHA256'],qualifiedSourceFaceIds=r['completeNegativeFaces'],standingSourceWallFaceIds=r['negativeWallFaces'],originalLowerClosureFaceIds=sorted(body['negativeDownwardFaceIds']+[f['sourceFace']for f in r['originalTwoUndersideFaces']])))
    for image in summary['imagesActuallyInspectedByROOT']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256'];refs.append(path)
    assert len(summary['imagesActuallyInspectedByROOT'])==7
    review=dict(uids=[UID],uid=UID,reviewer='Codex ROOT',sourceSHA256=SHA,rows=rows,
        sourceRoleAccepted=True,qualifiedRole='unchanged-original-lower-wall-and-underside-skins',
        reviewBasis=[
            'ROOT inspected all seven complete low-face group exports against actual drawn terrain. The65 affected wall facets form original lower wall skins; each has an exact original path to an upper source face outside the complete negative partition.',
            'Eighteen downward negative facets belong to an independently authored84-face closed source skin. All20 upward caps remain outside the negative partition, and all44 side-wall facets have positive finite contact with actual drawn grade. These are original lower closure skins, not new supports.',
            'The remaining2 downward facets retain their original shared diagonal and four lower side interfaces within the original main podium. Each incident original wall has actual positive finite grade contact and an independent original clear-cap path. Their small represented slopes are retained; they are not labelled horizontal, removed or fitted.',
            'This accepts only the exact lower-skin role of the85 preserved source facets in the four explicitly bound coordinate streams and this exact drawn-ground hash. No negative underside supplies a root or bridge between independent parts. No structural function or engineering closed-solid claim is made for the whole podium.',
            'Exact source bytes, fixed1x pose and every raw negative proof remain. Whole-source support, neighbouring actors, authored tower intersections, current picking/collision, desktop/mobile output, failure/retry, budget and guarded publication checks remain independent and mandatory.'
        ],imagesActuallyInspected=summary['imagesActuallyInspectedByROOT'],rawContextBatch=context,
        groundRootCredit=False,interComponentBridgeCredit=False,sourceGeometryChanges=0,sourcePoseChanges=0,
        sourceRoleReviewUsedAI=True,aiGeometryModelling=False,physicalAcceptance=False,placementReviewed=False,publicationApproved=False,installationApproved=False)
    save(out/'ROOT-LOWER-SOURCE-REVIEW.json',review);assert reservations.owns(lease)
    module('prosperous_lower_role_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-original-lower-skin-role-review',list(dict.fromkeys(refs)),review)

if __name__=='__main__':main()
