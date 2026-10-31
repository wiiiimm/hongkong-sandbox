"""Evaluate existing limits for exact exposed lower walls/downward stair skins.

Conditional role accounting only. No architectural or publication approval.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_reviewed_lower_facet_rim_accounting_v1_20261029 import verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-oceanwalk81743-conditional-lower-rims-v1-20261029'
CURRENT='government-xl-oceanwalk-depot-current-v1-20261029'
UID='landsd/81743:0';SHA='52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        p=BASE/batch/name
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    source=next(r for r in take(CURRENT+'-runtime','selection.json.gz')['rows']if r['uid']==UID)
    attr=next(r for r in take(CURRENT+'-attributes','attributes.json.gz')['rows']if r['uid']==UID)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==attr['sourceSHA256']==source['sourceSHA256']==SHA;refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);original=literal.copy();original[ix.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    out.mkdir();rows=[]
    for mode,positions in worlds.items():
        cm={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)
        cap=take('government-xl-clearance-81743-cap-paths-v1-20261029',cm+'.json.gz')
        low=take('government-xl-clearance-81743-low-faces-v1-20261029',cm+'.json.gz')
        rim=take('government-xl-oceanwalk81743-current-rims-v1-20261029',mode+'.json.gz')
        worldsha=digest(positions[ix].astype('<f8').tobytes());assert worldsha==cap['sourceWorldSHA256']==low['sourceWorldSHA256']==rim['sourceWorldSHA256']
        assert cap['completeDrawnGroundSHA256']==low['groundSHA256']==rim['groundSHA256']
        partition=cap['completeGroundClearancePartition'];assert partition['negativeNonWallFaces']==[6034,6035]and len(partition['paths'])==97
        byface={r['sourceFace']:r for r in low['rows']};roles={p['sourceFace']:'wall'for p in partition['paths']}
        unresolved=[]
        for path in partition['paths']:
            witness=byface[path['sourceFace']]
            assert witness['highestVertexAboveEveryOverlappingGroundFace']and witness['absoluteNormalYRatio']<.25
            if not path['hasExactSharedEdgeClearCapPath']:
                assert witness['absoluteNormalYRatio']==0
                unresolved.append(path['sourceFace'])
        for face in [6034,6035]:
            assert byface[face]['highestVertexAboveEveryOverlappingGroundFace']
            roles[face]='downward-skin'
        metric=dict(checks=rim['samples'],lowRimChecks=rim['lowRimSamples'],minSurfaceGap=rim['minimumSampleGapM'],minLowGap=rim['minimumRimGapM'],maxLowGap=rim['maximumRimGapM'])
        account=verify(positions,ix,float(positions[:,1].min()),rim['completeOriginalSamples'],approved_roles=roles,source_role_review_approved=True,expected_metric=metric)
        account['conditionalOnFutureBoundedRoleReview']=True;save(out/(mode+'-account.json'),account)
        rows.append(dict(mode=mode,sourceWorldSHA256=worldsha,drawnGroundSHA256=rim['groundSHA256'],conditionalLimitsPassed=account['verified'],strictOrdinaryAnchorSamples=account['strictOrdinaryAnchorSamples'],ordinaryRimSamples=account['ordinaryRimSamples'],rawReviewedClearanceFailuresRetained=account['rawReviewedClearanceFailuresRetained'],unresolvedSharedEdgePathsRetained=unresolved,noContactPathInvented=True))
    result=dict(uids=[UID],sourceSHA256=SHA,rows=rows,allFourConditionalLimitsPassed=all(r['conditionalLimitsPassed']for r in rows),sourceRoleReviewApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Exact four-world ordinary rim limits retained.97negative wall faces have independently exposed upper vertices. Unresolved shared-edge paths are pure vertical faces and remain explicitly unresolved. Two negative non-wall facets are downward-facing inclined skins with exposed upper vertices, not upward walkable faces. Bounded architectural role review is still required; no contact/support path is invented.')
    save(out/'summary.json',result);refs.extend([HERE/'original_reviewed_lower_facet_rim_accounting_v1_20261029.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('oceanwalk_conditional_lower_account_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'conditional-exact-exposed-wall-and-downward-inclined-skin-rim-account',refs,result)


if __name__=='__main__':main()
