"""Source-specific identity review; no placement or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-identity-review-v1-20261020'
DOC=BASE/BATCH
ID=BASE/'government-xl-mount-sterling-eight-identity-v1-20261020'
IMAGES=BASE/'government-xl-mount-sterling-identity-imagery-v1-20261020'
EXTENT=BASE/'government-xl-mount-sterling-extent-context-v1-20261020'

def main():
    assert not DOC.exists()
    refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [ID,IMAGES,EXTENT]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    extent=take(EXTENT,EXTENT/'summary.json')['rows']
    provenance=take(IMAGES,IMAGES/'provenance.json')
    for tile in provenance['tiles']:
        p=ROOT/tile['path'];assert digest(p.read_bytes())==tile['sha256'];refs.append(p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
    reviews=[]
    for key in ['103465:0','289787:0']:
        proof=take(ID,ID/key/'identity.json');uid=proof['uid'];route=proof['exactCurrentComponentRoute']
        assert proof['originalOwnership']['sourceGraphVerified'] and route['qualified']
        assert proof['exactWholeCellCoverage']['covered'] and proof['geographicCell']['targetCoversWholeCell']
        assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
        assert digest(manifest.read_bytes())==proof['exactRouteManifestSHA256']
        for tile,h in proof['exactRouteTileHashes'].items():
            p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==h;refs.append(p)
        tile=ROOT/'3d-viewer'/route['source']['tile']
        assert next(b for b in read(tile)['buildings'] if b['uid']==uid)==route['source']['building']
        projection=proof['freshCurrentIdentity'];assert projection['exactObjectAndCSUID']
        assert projection['targetCoveredBySourceProjection']>.987
        context=next(r for r in extent if r['uid']==uid)
        assert context['farFaceYRange'][1]<20
        unrelated=[r for r in projection['intersectingForms'] if not r['sameParent'] and r['uid']!=uid]
        if key=='103465:0':
            assert not unrelated and projection['sourceExcessCoveredByUnrelatedFormsM2']==0
            assert 12.959<projection['sourceExcessMaximumDistanceFromTargetM']<12.960
        else:
            assert len(unrelated)==1 and unrelated[0]['uid']=='landsd/111045:0'
            assert .565<unrelated[0]['intersectionAreaM2']<.566
            assert unrelated[0]['sourceYRange'][0]>unrelated[0]['top']
            assert 17.371<projection['sourceExcessMaximumDistanceFromTargetM']<17.372
        image=IMAGES/(key+'.png');assert digest(image.read_bytes())==pins[IMAGES][str(image.relative_to(ROOT))];refs.append(image)
        review=dict(uid=uid,reviewer='Codex ROOT',sourceSHA256=proof['sourceSHA256'],
                    sourceFormSHA256=proof['sourceFormSHA256'],worldTrianglesSHA256=proof['worldTrianglesSHA256'],
                    identityOnlyApproved=True,identityReviewApproved=True,
                    identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),
                    rawProof=proof,rawReasonsRetained=proof['reasons'],extentContext=context,
                    imagesActuallyInspected=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()))],
                    reviewBasis=[
                        'Exact original graph ownership, qualified GeoRef/type/ObjectID/CSUID route and complete coordinate-cell coverage bind this source to the current form. The aerial was projected directly between EPSG:2326 and EPSG:3857 without fitting or shifting.',
                        'ROOT inspected the two full-source aerial overlays. The tower cross-shaped body and the triangular mall perimeter coincide with this complex. The coarse target footprint omits low source projections; the measured far-face heights remain below20m, rather than representing a second displaced tower.',
                        'Aerial shadows and unknown capture date do not resolve every small projection. Their ownership is bound by the unchanged government source graph, not inferred from a visually plausible name or arbitrary geometry trimming.',
                        'The tower has zero unrelated-form overlap. The mall has0.565094m2 projected overlap with MeiFoo111045, in source faces above that form recorded roof. This does not imply wrong source identity; full collision and placement checks remain separate.',
                        'The two original maximum-extent failures remain recorded. This approval concerns these exact source identities only and changes no global threshold, source geometry, pose, support acceptance or publication state.'
                    ],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,
                    placementReviewed=False,publicationApproved=False,installationApproved=False)
        save(DOC/(key+'-review.json'),review);reviews.append(dict(uid=uid,identityReviewApproved=True,sourceSHA256=proof['sourceSHA256']))
    module('mount_sterling_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'two-exact-original-identity-only-reviews',list(dict.fromkeys(refs)),
        dict(uids=[r['uid'] for r in reviews],rows=reviews,identityAccepted=True,installationApproved=False))

if __name__=='__main__':main()
