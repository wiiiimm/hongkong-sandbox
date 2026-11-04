"""Bounded exact-source identity review, retaining all spatial warnings.

No geometry, placement, support, collision or publication approval.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'three-original-identity-review-v1-20261101'
EXACT={275446:('3846120391P20241029','B384612039102062G1',.9812294569511628,11.349312361356587,14.06482452037884),318704:('3831520704T20241023','B383152070401063C1',.9959779559732373,25.69217277914466,442.38373300336605),318722:('3829320838T20241023','B382932083801063C1',.9979917342705705,25.357980179192175,108.36560909460437)}

def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';planpath=BASE/(P+'five-current-ground-parallel-plan-v1-20261101.json');resources=read(planpath)['resources']
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('bounded-original-identity-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)and not out.exists();refs=[Path(__file__),planpath];pins={}
    def take(batch,name):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    primary=take(P+'primary-records-v1-20261101','summary.json');assert set(EXACT)<={int(u.split('/')[1].split(':')[0])for u in read(BASE/(P+'primary-records-v1-20261101')/'result.json')['uids']}
    take(P+'primary-records-v1-20261101','footprints.json');take(P+'primary-records-v1-20261101','relations.json')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);selection=take(P+'five-original-retained-parent-runtime-v2-20261101','selection.json.gz');sources={r['uid']:r for r in selection['rows']}
    contacts=take(P+'five-current-basic-contacts-v1-20261101','summary.json');assert contacts['foreignPairs']==57
    roots=take(P+'four-current-ground-root-paths-v1-20261101','summary.json');assert all(r['finitePaths']==r['targets']and r['aboveEndpointCeiling']==0 for r in roots['rows'])
    observed=BASE/(P+'source-view-observations-v1-20261101')/'ROOT-SOURCE-VIEW-OBSERVATIONS.json';prior=read(observed);refs.append(observed);priorimages={r['path']:r['sha256']for r in prior['imagesActuallyInspected']};rows=[]
    for object_id,(csuid,root,coverage,extent,foreign_area)in EXACT.items():
        assert reservations.owns(lease);uid=f'landsd/{object_id}:0';raw=take(P+'five-original-identity-v1-20261101',f'{object_id}:0/identity.json');s=raw['freshCurrentIdentity'];route=raw['exactCurrentComponentRoute'];source=sources[uid]
        assert raw['uid']==uid and raw['sourceSHA256']==source['sourceSHA256']
        assert digest(manifest.read_bytes())==raw['exactRouteManifestSHA256']==selection['manifestSHA256']
        for tile,sha in raw['exactRouteTileHashes'].items():
            path=ROOT/'3d-viewer'/tile;assert digest(path.read_bytes())==sha;refs.append(path)
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==raw['sourceSHA256'];refs.append(asset)
        assert route['qualified']and route['official']['objectId']==object_id and route['official']['buildingCSUID']==csuid
        assert raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==root
        assert raw['exactWholeCellCoverage']['covered']and raw['geographicCell']['targetCoversWholeCell']
        assert s['exactObjectAndCSUID']and s['targetCoveredBySourceProjection']==coverage and coverage>=.98
        assert s['sourceExcessMaximumDistanceFromTargetM']==extent and s['sourceExcessCoveredByUnrelatedFormsM2']==foreign_area
        assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
        views='government-xl-after-villa-premiere-275446-coast-source-views-v2-20261031'if object_id==275446 else'government-xl-275446-arena-mall-two-source-views-v1-20261031'
        v=next(r for r in take(views,'summary.json')['rows']if r['uid']==uid);assert v['sourceSHA256']==raw['sourceSHA256']and v['completeOriginalFaces']==source['triangles']and len(v['images'])==3
        for image in v['images']:
            path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[views][image['path']];refs.append(path)
            if object_id!=275446:assert priorimages[image['path']]==image['sha256']
        basis=[
            'This review accepts only the exact original source record identity, using the unique official OBJECTID/CSUID, verified complete original root graph, whole one-metre geographic cell and current target/source footprint correspondence. All source bytes, heights and surveyed transforms remain unchanged.',
            'The full plan and both oblique source exports were inspected. The complete podium follows the recorded common low platform around the stadium and northern buildings; Arena and Mall1 retain projecting upper roof/canopy geometry beyond their smaller BASIC outlines. These observations explain why the generic footprint proxy is insufficient for these exact original records; no invented part, relocation or neighbouring-building replacement is approved.',
            'All four generic extent/unrelated-projection warnings remain in rawProof. Actual target coverage, extent and unrelated projected areas are recorded exactly. A small horizontal projection overlap is not by itself a different source identity; current finite contacts remain independently recorded and unapproved.',
            'The complete 57-pair current foreign BASIC comparison and installed-stadium contact checks remain physical/neighbour obligations. Dorsett retains line contacts with fewer area contacts than its BASIC baseline; HealthWellness line contacts also require source/retained-form review. No collision approval follows from these measurements.',
            'All four companions have complete original-edge paths to independently measured actual-ground roots in every source representation. This supports geographic source context only; no source-role, engineering, compound-foundation or support approval is transferred.',
            'No common legal ownership is inferred from OSM names or absent structure relations. Preserve every separate UID and all pending placement, lower-role, native/BASIC, runtime, browser and publication checks.'
        ]
        review=dict(uid=uid,reviewer='Codex ROOT',sourceSHA256=raw['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],identityOnlyApproved=True,sourceIdentityReviewed=True,identityReviewApproved=True,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},rawProof=raw,rawReasonsRetained=raw['reasons'],imagesActuallyInspected=v['images'],reviewBasis=basis,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,geometryMethod='scripted-original-government-port',placementReviewed=False,physicalAcceptance=False,publicationApproved=False,installationApproved=False)
        save(out/f'{object_id}:0-review.json',review);rows.append(dict(uid=uid,sourceSHA256=raw['sourceSHA256'],identityAccepted=True,rawWarningsRetained=raw['reasons']))
    for batch,ps in pins.items():
        for path in refs:
            key=str(path.relative_to(ROOT))
            if key in ps:assert digest(path.read_bytes())==ps[key]
    assert reservations.owns(lease)
    module('arena_bounded_identity_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-three-original-source-identity-review',refs,dict(uids=[r['uid']for r in rows],rows=rows,identityAccepted=True,sourceIdentityReviewUsedAI=True,physicalAcceptance=False,sourceGeometryChanges=0,installationApproved=False))

if __name__=='__main__':main()
