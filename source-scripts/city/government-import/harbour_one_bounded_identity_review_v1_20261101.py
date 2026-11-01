"""Exact Harbour One component identity; retain all raw spatial negatives.

A named evidence interpretation, not a generic threshold or collision exception.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbour-one-exact-component-identity-review-v1-20261101'
CAPTURE='government-xl-harbour-one-after-hkdi-a-current-v1-20261101-runtime';IDENTITY='government-xl-harbour-one-after-hkdi-a-current-v1-20261101-identity'
EXACT={'landsd/319571:0':('c6a1be96a01cddb4b4b14bff7f9acf6730b67c2964e9d8964562fb4f5df97113','3174916474T20120301','B317491647401063C0',['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']),
       'landsd/269828:0':('287dbcbf5237d514865f4f99d50dfd13cc98028942f00c8cd086a5e528952e91','3174716475P20120301','B317471647502063C0',['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'])}
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json'
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('harbour-one-component-identity-'+str(uuid.uuid4()),['building:'+u for u in EXACT],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        f=BASE/batch/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selection=take(CAPTURE,'selection.json.gz');sources={r['uid']:r for r in selection['rows']};assert set(sources)==set(EXACT)
    observation=BASE/'government-xl-harbour-one-actual-source-observations-v1-20261101.json';seen=read(observation);assert seen['reviewer']=='Codex ROOT';seen_images={q['path']:q['sha256']for q in seen['identityDiagramsActuallyViewed']};refs.append(observation)
    boundary=take('government-xl-harbour-one269828-foreign-boundary-context-v1-20261101','summary.json');assert not boundary['collisionApproved']and boundary['rawExactContactsPreserved']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());assert start==selection['manifestSHA256']==boundary['currentManifestSHA256'];refs.append(manifest);rows=[]
    for uid,(sha,csuid,mid,reasons)in EXACT.items():
        raw=take(IDENTITY,uid.split('/')[1]+'/identity.json');ctx=take(IDENTITY,uid.split('/')[1]+'/context.json')['identity'];source=sources[uid]
        assert raw['uid']==uid and raw['sourceSHA256']==source['sourceSHA256']==sha and raw['reasons']==reasons and not raw['passed']
        assert raw['exactRouteManifestSHA256']==start and raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==mid==source['modelId']
        assert source['source']['building']['parent']=='way/320984100'and source['source']['building']['buildingCSUID']==csuid
        route=raw['exactCurrentComponentRoute'];assert route['qualified']and route['official']['objectId']==int(uid.split('/')[1].split(':')[0])and route['official']['buildingCSUID']==csuid
        assert raw['exactWholeCellCoverage']['covered']and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==source['triangles']and raw['geographicCell']['targetCoversWholeCell']
        assert ctx['exactObjectAndCSUID']and ctx['targetCoveredBySourceProjection']>.99
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==sha;refs.append(asset)
        for tile,expected in raw['exactRouteTileHashes'].items():f=ROOT/'3d-viewer'/tile;assert digest(f.read_bytes())==expected;refs.append(f)
        plot=take('government-xl-harbour-one'+uid.split('/')[1].split(':')[0]+'-identity-views-v1-20261101','summary.json');image=plot['image'];assert image['sha256']==seen_images[image['path']]==digest((ROOT/image['path']).read_bytes());refs.append(ROOT/image['path'])
        assert plot['sourceSHA256']==sha and plot['originalWorldSHA256']==raw['worldTrianglesSHA256']and plot['completeSourceFaces']==source['triangles']
        if uid=='landsd/319571:0':assert ctx['unrelatedIntersectingForms']==0 and ctx['sourceExcessMaximumDistanceFromTargetM']==10.223424323787395
        else:assert {r['uid']for r in ctx['intersectingForms']if not r['sameParent']}=={'landsd/232185:0','landsd/254814:0'}and ctx['sourceExcessCoveredByUnrelatedFormsM2']==1.17054904392152
        proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
        review=dict(uid=uid,sourceSHA256=sha,sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],identityAccepted=True,identityProof=proof,rawProof=raw,rawReasonsPreserved=reasons,componentIdentityOnly=True,sourceGeometryChanges=0,sourcePoseChanges=0,genericThresholdChanges=0,collisionApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,imagesActuallyViewed=[image],basis=[
            'Accept only the exact source identity from the unique current official OBJECTID/CSUID/component route, intact original root and whole geographic cell. Original source bytes and fixed1x/HKPD pose are unchanged.',
            'Both complete-source projection/3D diagrams were inspected. The tower includes projecting facade/roof detail outside its smaller mapped tower outline and aligned to the named common podium; its maximum extent proxy remains failed. The podium follows its curved mapped frontage, with a narrow overlap at the adjacent Industrial Building boundary. This is source identity context, not a collision waiver.',
            'Keep all exact current footprint coverage, extent, unrelated projected areas and failed raw proof booleans verbatim. The double-precision boundary context and complete rational finite contacts remain independently bound and unapproved for physical purposes. No footprint threshold is widened; no other source may consume this named review.',
            'No whole-building completeness, neighbour geometry, support, terrain, runtime, visual, installation or publication approval is granted by identity alone.'])
        save(out/(uid.split('/')[1]+'-identity-review.json'),review);rows.append(dict(uid=uid,sourceSHA256=sha,identityAccepted=True,identityProof=proof,rawReasonsPreserved=reasons))
    assert reservations.owns(lease)and digest(manifest.read_bytes())==start
    result=dict(uids=list(EXACT),rows=rows,identityAccepted=True,currentManifestSHA256=start,sourceSHA256ByUid={u:v[0]for u,v in EXACT.items()},physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False)
    save(out/'summary.json',result)
    module('harbour_one_exact_component_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'named-exact-harbour-one-component-identity-review-raw-spatial-warnings-preserved',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
