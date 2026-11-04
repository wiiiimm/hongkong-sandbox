"""Account for exact Lookout post walls and its provider-authored bottom cap.

A source-specific evidence interpretation, never a generic acceptance-policy
change, installation approval, mesh edit or terrain publisher.
"""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_wall_rim_accounting_20261009 import original_samples
from exact_original_triangle_pair_column_gap_20261010 import verify as exact_gap

P='government-xl-lookout99482-after-sha-tin-'
BATCH=P+'landing-source-role-account-v1-20261029'
UID='landsd/99482:0'
SOURCE='1ec68112caa3e93f200c6a07851e7e9d85f4fa8a25e9b9271877e7098e99e030'
TERRAIN='d60e8d9a53ffd9df03955f7c2ddd6ce3e6458885b4d15a19c94f66e2c6ee3df5'
BOTTOM=24653


def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    def doc(suffix,name='summary.json'):
        batch=P+suffix+'-v1-20261029';return take(batch,base/batch/name)
    runtime=P+'landing-runtime-v1-20261029'
    selection=take(runtime,base/runtime/'selection.json.gz')
    source=next(r for r in selection['rows']if r['uid']==UID)
    g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']==UID)
    attrs=doc('targeted-attributes','attributes.json.gz')['rows'];attr=next(r for r in attrs if r['uid']==UID)
    assert source['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']==SOURCE
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    literal=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)
    assert len(set(index.ravel()))==len(literal)
    original=literal.copy();original[index.ravel()]=decode_original_world_triangles(asset.read_bytes()).reshape(-1,3)
    worlds=dict(original=original,literal=literal,left=np.asarray(attr['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3),balanced=np.asarray(attr['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3))
    assert np.array_equal(literal[index],np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);ground_sha=digest(ground.tobytes())
    patch=doc('landing-inset');assert patch['status']=='private-terrain-validator-passed' and patch['candidate']['sha256']==TERRAIN
    candidate=ROOT/patch['candidate']['path'];assert digest(candidate.read_bytes())==TERRAIN;refs.append(candidate)
    foundation=doc('landing-foundations');assert foundation['establishedFoundationPolicyPassed']
    provider=doc('provider-floor-context');assert provider['sourceSHA256']==SOURCE
    bottom=next(r for r in provider['rows']if r['sourceFace']==BOTTOM)
    assert bottom['providerAndCurrent']['provider']['coverage']['exactProjectionCovered']
    assert Fraction(bottom['providerAndCurrent']['provider']['exactMinimumFiniteColumnGapM'])<Fraction(-1,2)
    views=doc('landing-low-role-views');assert views['completeAffectedFaces'] and len(views['exports'])==3
    images=[]
    for image in views['exports']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256'];refs.append(path);images.append(image)
    rows=[]
    for mode,position in worlds.items():
        tri=position[index];assert len(tri)==source['triangles']==25564
        sha=digest(tri.astype('<f8').tobytes())
        cap=doc('landing-cap-paths',mode+'.json.gz');partition=cap['completeGroundClearancePartition']
        low=doc('landing-low-faces',mode+'.json.gz')
        grade=doc('landing-wall-grade',mode+'.json.gz')
        rim_mode={'left':'leftF32','balanced':'balancedF32'}.get(mode,mode)
        rim=doc('landing-rim-diagnostic',rim_mode+'.json.gz')
        assert cap['sourceWorldSHA256']==low['sourceWorldSHA256']==grade['sourceWorldSHA256']==rim['sourceWorldSHA256']==sha
        assert cap['completeDrawnGroundSHA256']==low['groundSHA256']==grade['groundSHA256']==rim['completeDrawnGroundSHA256']==ground_sha
        assert partition['negativeNonWallFaces']==[BOTTOM]
        walls={r['sourceFace']for r in partition['paths']}
        assert len(walls)==28 and all(r['hasExactSharedEdgeClearCapPath']for r in partition['paths'])
        assert {r['sourceFace']for r in grade['sourceFaces']}==walls
        assert {r['sourceFace']for r in grade['exactFiniteUpperGradeInterfaces']}==walls
        assert all(r['highestVertexAboveEveryOverlappingGroundFace']and r['absoluteNormalYRatio']<.25 for r in grade['sourceFaces'])
        bottom_face=tri[BOTTOM];normal=np.cross(bottom_face[1]-bottom_face[0],bottom_face[2]-bottom_face[0])
        area=float(np.linalg.norm(normal)/2)
        assert normal[0]==normal[2]==0 and normal[1]<0 and area==.0010223388671875
        vertices=set(map(tuple,bottom_face));adjacent=sorted(i for i in walls if len(vertices&set(map(tuple,tri[i])))>=2)
        assert adjacent==[24654,24660,24662]
        for f in foundation['rows']:
            assert f['uid']==UID and f['triangles']==f['completeTerrainTriangles']==25564
            assert f['fullyBuriedTriangles']==1 and f['fullyBuriedUpwardTriangles']==0 and f['fullyBuriedAreaM2']==area
        pairs=[]
        xz=ground[:,:,[0,2]];lo,hi=bottom_face[:,[0,2]].min(0),bottom_face[:,[0,2]].max(0)
        for j in np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)):
            proof=exact_gap(bottom_face,ground[j])
            if proof['exactClosedHorizontalProjectionsMeet']:pairs.append(dict(groundFace=int(j),proof=proof))
        assert pairs and min(Fraction(r['proof']['exactMinimumFiniteColumnGapM'])for r in pairs)<Fraction(-1,2)
        samples=original_samples(position,index,float(position[:,1].min()))
        assert len(samples)==rim['samples']==len(rim['completeOriginalSamples'])
        retained=[];low_samples=[]
        for expected,actual in zip(samples,rim['completeOriginalSamples']):
            assert all(actual[k]==v for k,v in expected.items())
            assert np.isfinite([actual['ground'],actual['gap']]).all() and actual['gap']==actual['point'][1]-actual['ground']
            if actual['gap']<-.5:
                assert set(actual['originalIncidentFaces'])<=walls|{BOTTOM};retained.append(actual)
            if actual['low']:
                assert actual['gap']<=1;low_samples.append(actual)
        assert retained==rim['failedSamplesVerbatim'] and len(retained)==43
        assert len(low_samples)==rim['lowSamples'] and min(r['gap']for r in low_samples)<=.1
        rows.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=ground_sha,wallFaces=sorted(walls),bottomFace=BOTTOM,bottomAreaM2=area,bottomExactWallEdgeNeighbours=adjacent,bottomGroundPairs=pairs,wholeCanonicalSamples=len(samples),rawClearanceWarningsRetained=len(retained),originalLowSamples=len(low_samples),maximumLowGapM=max(r['gap']for r in low_samples),sourceSpecificContactRoleAccounted=True))
    result=dict(uids=[UID],sourceSHA256=SOURCE,terrainCandidateSHA256=TERRAIN,rows=rows,reviewer='Codex ROOT',imagesActuallyViewed=images,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,rawCanonicalFailuresPreserved=True,sourceSpecificContactRoleAccounted=True,physicalAcceptance=False,installationApproved=False,publication=False,basis=[
        'ROOT inspected all three two-angle source-region exports. The flagged geometry is the lower shaft of one slender post and two larger posts, with unchanged exposed upper structures; all28 wall facets finitely cross actual ground and retain original clear-cap paths.',
        'Exact face24653 is the small downward horizontal bottom cap of the slender post, sharing full original edges with three reviewed walls. Its0.0010223388671875m2 area is already within the unchanged four-world foundation policy. The original provider TIN also buries this same face. This interpretation preserves it as a source-authored post underside rather than cutting the model or lowering terrain to expose the bottom cap.',
        'All43 raw negative canonical samples remain archived in each of four streams and belong exclusively to these exact29 reviewed lower post facets. Every other sample retains the ordinary clearance bound; all low samples retain the1m maximum and canonical minimum contact <=0.1m. No generic source, normal, area or clearance exemption is introduced.'
    ],remaining=['Complete current identity/physical composition and runtime budget review','Private desktop/mobile full-scene visual, collision/picking and failure/retry checks','Guarded publication, live verification, exact inventory/Neon readback and commit/push'])
    save(out/'ROOT-SOURCE-CONTACT-ROLE-ACCOUNT.json',result);save(out/'summary.json',result)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','original_wall_rim_accounting_20261009.py','exact_original_triangle_pair_column_gap_20261010.py'])
    module('lookout_landing_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-lookout-original-post-wall-and-provider-bottom-contact-role-account',list(dict.fromkeys(refs)),result)
    print(dict(batch=BATCH,worlds=len(rows),warningsPerWorld=43,installationApproved=False),flush=True)

if __name__=='__main__':main()
