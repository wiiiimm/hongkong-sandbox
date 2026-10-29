"""Account for exact original wall grades and two downward lower closure facets."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_reviewed_lower_facet_rim_accounting_v1_20261029 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed265269-lower-role-rim-account-v3-20261029';P='government-xl-unnamed265269-';UID='landsd/265269:0';SHA='0adf753f5832d3598fd1d99c3700b704e33de74aa97c4d4f868ba68c6cb445da'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    runtime=P+'current-evidence-v1-20261029-runtime';attrs=P+'current-evidence-v1-20261029-attributes';caps=P+'current-cap-paths-v1-20261029';rims=P+'complete-canonical-rims-v1-20261029';components=P+'two-low-caps-v1-20261029'
    source=take(runtime,BASE/runtime/'selection.json.gz')['rows'][0];attr=take(attrs,BASE/attrs/'attributes.json.gz')['rows'][0];assert source['uid']==UID and source['sourceSHA256']==attr['sourceSHA256']==SHA
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3);original=literal.copy();original[ix.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=dict(original=original,literal=literal,leftF32=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balancedF32=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    foundation=take(P+'current-evidence-v1-20261029-foundation-265269-0',BASE/(P+'current-evidence-v1-20261029-foundation-265269-0')/'summary.json');assert foundation['establishedFoundationPolicyPassed']and all(r['fullyBuriedTriangles']==2 and r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    component=take(components,BASE/components/'summary.json');assert component['sourceSHA256']==SHA;authored_caps={f['sourceFace']:f for f in next(r for r in component['rows']if r['mode']=='original')['faces']};assert all(f['downward']and f['exactlyHorizontal']for f in authored_caps.values());out.mkdir();rows=[];roles_review=[]
    for mode,positions in worlds.items():
        cm={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);cap=take(caps,BASE/caps/(cm+'.json.gz'));rim=take(rims,BASE/rims/(mode+'.json.gz'));tri=positions[ix];worldsha=digest(tri.astype('<f8').tobytes());assert worldsha==cap['sourceWorldSHA256']==rim['sourceWorldSHA256']
        partition=cap['completeGroundClearancePartition'];assert partition['negativeNonWallFaces']==[11454,11455]
        unresolved=sorted(r['sourceFace']for r in partition['paths']if not r['hasExactSharedEdgeClearCapPath'])
        correspondence=[]
        if mode=='literal':
            assert unresolved==list(range(11527,11535))
            original_cap=take(caps,BASE/caps/'original.json.gz')['completeGroundClearancePartition']
            original_paths={r['sourceFace']:r for r in original_cap['paths']}
            lowbatch=P+'current-low-faces-v1-20261029';low=take(lowbatch,BASE/lowbatch/'literal.json.gz');assert low['sourceWorldSHA256']==worldsha;byface={r['sourceFace']:r for r in low['rows']}
            for face in unresolved:
                witness=byface[face];assert witness['absoluteNormalYRatio']==0 and witness['highestVertexAboveEveryOverlappingGroundFace']is True
                assert original_paths[face]['hasExactSharedEdgeClearCapPath']and len(original_paths[face]['originalPath'])>1
                correspondence.append(dict(sourceFace=face,exactOriginalSourcePath=original_paths[face]['originalPath'],literalPureVertical=True,literalHighestVertexExposed=True,literalSharedEdgePathUnresolved=True,sourceRoleOnly=True,noContactOrSupportPathInvented=True))
        else:assert not unresolved
        roles={r['sourceFace']:'wall'for r in partition['paths']};assert not set(roles)&{11454,11455}
        context=next(r for r in component['rows']if r['mode']==cm);assert context['sourceWorldSHA256']==worldsha
        for f in context['faces']:
            assert f['sourceFace']in [11454,11455]and f['downward']and 2.45<f['areaM2']<2.47
            if mode!='literal':assert f['exactlyHorizontal']
            authored=authored_caps[f['sourceFace']]
            assert any(max(p[1]for p in r['vertices'])==11 for r in authored['adjacentFaces'])
            assert any(max(p[1]for p in r['vertices'])>10 for r in f['adjacentFaces'])
            roles[f['sourceFace']]='downward-skin'
        metric=dict(checks=rim['samples'],lowRimChecks=rim['lowRimSamples'],minSurfaceGap=rim['minimumSampleGapM'],minLowGap=rim['minimumRimGapM'],maxLowGap=rim['maximumRimGapM'])
        result=verify(positions,ix,float(positions[:,1].min()),rim['completeOriginalSamples'],approved_roles=roles,source_role_review_approved=True,expected_metric=metric)
        name=mode+'-account.json';save(out/name,result);rows.append(dict(mode=mode,sourceWorldSHA256=worldsha,verified=result['verified'],ordinaryRimSamples=result['ordinaryRimSamples'],strictOrdinaryAnchorSamples=result['strictOrdinaryAnchorSamples'],rawReviewedClearanceFailuresRetained=result['rawReviewedClearanceFailuresRetained'],proof=name));roles_review.append(dict(mode=mode,literalRoleCorrespondence=correspondence,sourceWallFaces=sorted(f for f,r in roles.items()if r=='wall'),downwardClosureFaces=[11454,11455]))
    images=[BASE/(P+'low-cap-views-v1-20261029')/'named-faces-current-ground.png']+[BASE/(P+'canopy-private-preview-v1-20261029')/str(w)/f'staged-landsd-265269-0-{w}-{t}-canvas.png'for w in [390,1280]for t in [1500,2200]]
    for image in images:
        batch=image.parent.name if image.parent.name not in ['390','1280']else image.parent.parent.name
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(image.read_bytes())==pins[batch][str(image.relative_to(ROOT))];refs.append(image)
    role=dict(reviewer='ROOT',sourceSHA256=SHA,rows=roles_review,imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],boundedLowerRolesAccepted=True,sourceGeometryChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,basis='Original and both Float32 negative wall sets retain exact exposed clear-cap paths. Eight literal pure-vertical facets lose exact represented shared-edge paths; their exact original face correspondences retain those paths and every represented upper vertex is independently exposed. Their bounded wall role is recognised from the immutable source plus direct represented geometry; unresolved literal join flags remain and no finite contact/support path is invented. The only two negative non-wall facets are the adjacent downward horizontal lower closure of an above-grade source wall/box, directly joined to original walls rising to11HKPD. They are preserved beneath current terrain, rather than raised or removed. Their raw burial remains and the unmodified ordinary four-world foundation policy passes with zero upward burial. ROOT inspected the local lower-closure diagram and all four actual whole-source exports. This is an opaque lower-surface role account, not a surveyed foundation/support or source-identity claim.')
    save(out/'ROOT-LOWER-ROLE-REVIEW.json',role);result=dict(uids=[UID],sourceSHA256=SHA,rows=rows,allFourRimAccountsVerified=all(r['verified']for r in rows),ordinaryClearanceMinimumLimitM=-.5,rimMaximumLimitM=1,strictOrdinaryAnchorBandM=[-.1,.1],rawCanonicalFlagsPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,groundRootCredit=False,physicalAcceptance=False,installationApproved=False,publication=False)
    save(out/'summary.json',result);refs.extend([HERE/'original_reviewed_lower_facet_rim_accounting_v1_20261029.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('unnamed_lower_role_account_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-two-downward-closure-and-wall-complete-rim-accounting',refs,result)
if __name__=='__main__':main()
