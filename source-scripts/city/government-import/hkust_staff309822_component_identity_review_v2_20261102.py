"""Named exact-source identity interpretation; no physical/publication approval."""
import sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-hkust-staff309822-component-identity-review-v2-20261102'
UID='landsd/309822:0';SHA='56fe512572733202ce049360e08fe0effc15919bec6e296ac667e06f867c957f'
RUNTIME='government-xl-hkust-staff-tower-current-context-v2-20261102-runtime'
IDENTITY='government-xl-hkust-staff-three-source-contracts-v1-20261102-identity'
FOREIGN='government-xl-hkust-staff-tower-current-foreign-v1-20261102'
SCOPE='government-xl-hkust-staff-tower-current-context-v2-20261102-terrain-scope'
REASONS=['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap']

def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json'
    assert not out.exists()
    scope,scopepins=authenticate(BASE/SCOPE)
    fp=BASE/SCOPE/'form-obligations.json.gz';assert digest(fp.read_bytes())==scopepins[str(fp.relative_to(ROOT))]
    forms=read(fp);resources={'building:'+b['uid']for b in forms}|{'terrain:city/data/terrain.json'}
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('hkust-staff-identity-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
    refs=[Path(__file__),BASE/SCOPE/'result.json',fp];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(RUNTIME,'selection.json.gz');assert len(selection['rows'])==1;source=selection['rows'][0]
    raw=take(IDENTITY,'309822:0/identity.json');ctx=take(IDENTITY,'309822:0/context.json')['identity']
    assert source['uid']==raw['uid']==UID and source['sourceSHA256']==raw['sourceSHA256']==SHA
    assert raw['reasons']==REASONS and raw['passed']is False
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']==source['modelId']=='B453782220901063C0'
    route=raw['exactCurrentComponentRoute'];official=route['official'];csuid='4537822209T20050430'
    assert route['qualified'] and official['objectId']==309822 and official['buildingCSUID']==csuid==source['source']['building']['buildingCSUID']
    assert raw['exactWholeCellCoverage']['covered'] and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==12943==source['triangles']
    assert ctx['exactObjectAndCSUID'] and ctx['targetCoveredBySourceProjection']==0.9931124231271572
    assert ctx['sourceExcessMaximumDistanceFromTargetM']==1.7676158577816514
    unrelated={r['uid']:r for r in ctx['intersectingForms']if not r['sameParent']}
    assert set(unrelated)=={'landsd/29031:0','landsd/27083:0'}
    basic=take(FOREIGN,'basic.json');canopy=next(r for r in basic['rows']if r['uid']=='landsd/27083:0')
    canopy_top=float(np.asarray(canopy['position']).reshape(-1,3)[:,1].max())
    source_min=unrelated['landsd/27083:0']['sourceYRange'][0];assert source_min>canopy_top
    foreign=take(FOREIGN,'summary.json')
    canopy_contacts=next(r for r in foreign['rows']if r['foreignUid']=='landsd/27083:0')
    assert all(r['positiveContactPairs']==0 for r in canopy_contacts['modes']if r['mode']!='before-basic')
    pairs=take('government-xl-hkust-staff-tower-current-context-v2-20261102-original-pairs','summary.json')
    small=[r for r in pairs['rows']if {r['uid'],r['peerUid']}=={UID,'landsd/29031:0'}]
    assert len(small)==4 and all(r['positiveSurfaceContacts']==13 for r in small)
    fresh=take('government-xl-hkust-staff-three-source-contracts-v1-20261102-primary','footprints.json')
    current=next(f['attributes']for f in fresh['features']if f['attributes']['BuildingCSUID']==csuid)
    assert current['OBJECTID']==309966 and current['OBJECTID']!=official['objectId'] and current['Status']=='Active' and current['BuildingBlockType']=='Tower'
    assert current['BaseHeight']==59.5 and current['TopHeight']==98.2
    obs=BASE/'government-xl-hkust-staff-tower-actual-observations-v1-20261102.json';seen=read(obs);refs.append(obs);assert seen['reviewer']=='Codex ROOT'
    viewed=seen['imagesActuallyViewed']+seen['identityDiagramsActuallyViewed'];assert len(viewed)==6
    for image in viewed:
        p=ROOT/image['path'];assert digest(p.read_bytes())==image['sha256'];refs.append(p)
    plot=take('government-xl-hkust-staff-tower-identity-views-v1-20261102','summary.json');assert {k:plot['image'][k] for k in ['path','sha256']}in viewed and plot['sourceSHA256']==SHA and plot['originalWorldSHA256']==raw['worldTrianglesSHA256']
    feature=take('government-xl-hkust-staff-tower-canopy-records-v1-20261102','summary.json');assert feature['image']in viewed and feature['sourceSHA256']==SHA
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==raw['exactRouteManifestSHA256'];refs.append(manifest)
    for tile,h in raw['exactRouteTileHashes'].items():p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==h;refs.append(p)
    proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
    review=dict(uid=UID,sourceSHA256=SHA,sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],identityAccepted=True,identityProof=proof,identityProofScope='Exact frozen viewer/native epoch OBJECTID309822; current primary OBJECTID309966 separately recorded, never claimed equal.',frozenViewerObjectId=309822,currentProviderObjectId=current['OBJECTID'],buildingCSUID=csuid,rawProof=raw,rawReasonsPreserved=REASONS,componentIdentityOnly=True,canopyActualTop=canopy_top,overlappingSourceMinimumY=source_min,rawCurrentForeignContacts=foreign['rows'],rawOriginalPairContext=small,imagesActuallyViewed=viewed,sourceGeometryChanges=0,sourcePoseChanges=0,genericThresholdChanges=0,collisionApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,basis=[
        'Accept identity only for the exact original tower matched by intact provider root, unique frozen OBJECTID/CSUID route, complete geographic cell and 99.31124231271572% target-footprint coverage. Preserve current provider ID renumbering explicitly.',
        'The small projected excess occurs at the ends of this complete curved tower source, as inspected in full source diagrams and desktop/mobile exports. The canopy overlap is overhead: even the conservative original-face minimum is above actual BASIC top, and all four exact 3D contact streams are empty.',
        'The unnamed small current Tower remains BASIC and retains its independent record. Its 2.285m2 projection overlap and positive current surface contacts are not suppressed or treated as collision clearance. Thirteen exact authored contacts with its separate original in each stream provide source-interface context, not legal/common-ownership evidence or acceptance of that companion.',
        'This is a named identity interpretation of the two preserved footprint-proxy failures. It does not change thresholds, source geometry, pose, neighbours, original companion acceptance or any physical/runtime/publication gate.'])
    save(out/'309822:0-identity-review.json',review)
    result=dict(uids=[UID],rows=[dict(uid=UID,sourceSHA256=SHA,identityAccepted=True,identityProof=proof,rawReasonsPreserved=REASONS)],identityAccepted=True,currentManifestSHA256=mh,sourceSHA256ByUid={UID:SHA},physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False)
    save(out/'summary.json',result);assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    module('hkust_staff_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'named-exact-hkust-staff-component-identity-review-raw-spatial-warnings-preserved',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
