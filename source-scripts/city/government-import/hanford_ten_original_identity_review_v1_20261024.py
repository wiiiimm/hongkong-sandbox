"""Bounded exact Hanford identity review, retaining individual coverage failures."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
from hanford_ten_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,FLAGGED
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-hanford-ten-original-'
BATCH=P+'bounded-identity-review-v1-20261024'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'hanford_ten_original_catalogue_scope_v1_20261024.py'];pins={}
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    def take(batch,file):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/file;assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);return read(path)
    runtime=P+'current-runtime-v1-20261024';selection=take(runtime,'selection.json.gz')
    assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    context_name=P+'assembly-identity-context-v1-20261024';context=take(context_name,'summary.json')
    assert context['requiredOriginalAssembly']==SOURCES and context['completeOriginalFaces']==28973
    assert set(context['uids'])==FLAGGED
    support_name=P+'support-followthrough-v1-20261024';support=take(support_name,'summary.json')
    assert support['nominatedPairs']==8 and all(r['allUnresolvedHaveFinitePaths']for r in support['rows'])
    for uid,parent in SUPPORTS.items():assert any(r['uid']==uid and r['supportUid']==parent and r['allUnresolvedHaveFinitePaths']for r in support['rows'])
    pairs=take(P+'all-pair-context-v1-20261024','summary.json');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==45 and len(pairs['rows'])==180
    yawname='government-xl-next-repairs-hanford-194725-original-yaw-context-v1-20261024';yaw=take(yawname,'proof.json')
    assert yaw['sourceSHA256']==SOURCES['landsd/194725:0']and yaw['sourceBoundRootFramePassed']and yaw['completeNativeBoundsErrorM']==0
    records=[]
    for row in selection['rows']:
        uid=row['uid'];name=P+'current-identity-v1-20261024'
        raw=take(name,uid.split('/')[1]+'/identity.json');spatial=take(name,uid.split('/')[1]+'/context.json')['identity']
        assert raw['sourceSHA256']==SOURCES[uid]and raw['exactCurrentComponentRoute']['qualified']and raw['originalOwnership']['originalRootName']==row['modelId']
        assert spatial['exactObjectAndCSUID']and spatial['sourceExcessCoveredByUnrelatedFormsM2']<=1
        if uid=='landsd/194725:0':assert set(raw['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage','original-unit-hkpd-root-pose'}
        else:assert raw['originalOwnership']['sourceGraphVerified']
        if uid not in FLAGGED:assert raw['passed']and not raw['reasons']and raw['exactWholeCellCoverage']['covered']
        else:
            expected={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
            if uid=='landsd/194214:0':expected.add('original-source-does-not-cover-whole-georef-cell')
            if uid=='landsd/194725:0':expected.add('original-unit-hkpd-root-pose')
            assert set(raw['reasons'])==expected
            c=next(r for r in context['rows']if r['uid']==uid)
            assert c['completeAssemblyWholeCellCovered']and c['completeAssemblyTargetCoverage']>=.9999
            asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==SOURCES[uid];refs.append(asset)
            tri=decode_original_world_triangles(asset.read_bytes());projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
            target=shapely.Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:])
            envelope=target.convex_hull.intersection(projection.convex_hull).area/target.convex_hull.area
            centroid=projection.centroid.distance(target.centroid)
            assert envelope>=.99 and centroid<1 and spatial['sourceExcessMaximumDistanceFromTargetM']<1
            assert .93<=c['ownTargetCoverage']<.95
        records.append(dict(uid=uid,sourceSHA256=SOURCES[uid],rawPassed=raw['passed'],rawReasonsRetained=raw['reasons'],rawOwnTargetCoverage=spatial['targetCoveredBySourceProjection'],exactCurrentComponentRoute=raw['exactCurrentComponentRoute'],sourceRootName=row['modelId'],boundedIdentityAccepted=True))
    figures=[]
    for batch,file in [(context_name,'source-record-context.png'),(P+'source-views-v1-20261024','complete-original-assembly.png')]:
        if batch not in pins:take(batch,'summary.json')
        path=BASE/batch/file;assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);figures.append(ref(path))
    observations=[
        'ROOT inspected the four source/record projection panels and complete unchanged ten-source3Dassembly. The original towers contain repeating open recesses/returns that the filled GIS outlines simplify. This is retained original negative space, not absent GLB buffers or discarded model components. Raw individual93.91-94.64percent coverage remains below the unchanged generic95percent proxy and is NOT reported as passed.',
        'All ten exact government files have unique current ObjectID/CSUID/GeoRef and tower/podium-type routing, source-owned complete root graphs, or the separately proven original unit yaw for Block4. No name replacement, source move, scale edit or unrelated footprint is used. The four flagged towers retain greater99percent outer-envelope coverage, less1m centroid/exterior alignment differences, and no meaningful unrelated overlap. These measurements corroborate the authoritative exact component routes; they do not by themselves create a generic envelope-only identity rule.',
        'The verified authored compound originals cover each flagged record to greater99.99percent and every complete1mGeoRefcell exactly, including the0.0691168m2corner omitted by Block6alone. That cell is covered by the required compound, not falsely asserted to be covered by the individual tower. All45pair contexts and eight finite support alternatives bind actual original construction relationships; all ten exact hashes must be co-imported together for this qualification.',
        'Accept identity for these exact ten current components based on complete provider ownership/routing plus the inspected source-authored recesses and bounded compound context. Preserve every original raw coverage/cell/root-pattern failure. Generic identity thresholds/policies are unchanged. Actual-ground, source-role, current neighbour, stage/live browser, support metadata, publication and installed-ledger gates still remain.'
    ]
    result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,currentManifest=ref(manifest),rows=records,identityAccepted=True,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},reviewer='ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,figuresActuallyViewed=figures,observations=observations,rawIndividualCoverageFlagsRetained=True,genericIdentityPolicyChanges=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False)
    save(out/'ROOT-IDENTITY-REVIEW.json',result)
    module('hanford_exact_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-ten-original-hanford-provider-identity-and-inspected-recess-review',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
