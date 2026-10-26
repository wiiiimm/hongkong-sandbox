"""Review the exact QE311317 authored envelope; no physical or publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
UID='landsd/311317:0'
SHA='6feeea5687b060e9b39d17be3d6336c0668e92c23a15955602ec7256be4268a1'
PREFIX='government-xl-after-tung-on-qe311317-'


def main():
    base=ROOT/'docs/astra-city/government-import';batch=PREFIX+'source-identity-review-v1-20261026';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    raw=take(PREFIX+'identity-v1-20261026','311317:0/identity.json');context=take(PREFIX+'identity-v1-20261026','311317:0/context.json')['identity']
    selected=take(PREFIX+'selection-v1-20261026','selection.json.gz');row,=selected['rows'];assert row['uid']==raw['uid']==UID and row['sourceSHA256']==raw['sourceSHA256']==SHA
    assert row['modelId']=='B361581883001063C0' and row['source']['building']['buildingCSUID']=='3615818830T20161031'
    assert raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==row['modelId']
    route=raw['exactCurrentComponentRoute'];assert route['qualified']and not route['reasons']and route['uid']==UID
    assert route['official']['objectId']==311317 and route['official']['buildingCSUID']=='3615818830T20161031'
    assert raw['exactWholeCellCoverage']['covered']and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==11584
    assert raw['geographicCell']['targetCoversWholeCell']and raw['geographicCell']['originalProjectionCoversWholeCell']
    assert raw['passed']is False and set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
    assert context['exactObjectAndCSUID']and context['sourceExcessMaximumDistanceFromTargetM']==16.992119189944756
    assert context['sourceExcessCoveredByUnrelatedFormsM2']==0.279130813841137 and context['unrelatedIntersectingForms']==1
    assert {r['uid']for r in context['intersectingForms']}=={UID,'landsd/161194:0'}
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==11584 and digest(tri.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
    pair=take(PREFIX+'pair161194-contacts-v1-20261026','summary.json');assert pair['uids']==[UID,'landsd/161194:0']and pair['rows'][0]['sourceSHA256']==SHA
    assert pair['contactRoles']['shared-plane-area-contact']==5 and pair['contactRoles']['transverse-surface-crossing']==1
    images=[]
    for name,file in [('government-xl-qe311317-original-shape-context-v1-20261026','whole-source-plan.png'),('government-xl-qe311317-original-shape-context-v1-20261026','whole-source-perspectives.png')]:
        take(name,'summary.json');path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    primary=HERE/'local'/(PREFIX+'primary-project-sources-v1-20261026');downloads=read(primary/'downloads.json');photos=read(primary/'photos.json');refs.extend([primary/'downloads.json',primary/'photos.json']);sources=[]
    for r in downloads+photos:
        if 'error'in r:continue
        path=primary/r['name'];assert digest(path.read_bytes())==r['sha256'];refs.append(path);sources.append(r)
        if r['name'].startswith('architect-photo-'):images.append(dict(path=str(path.relative_to(ROOT)),sha256=r['sha256']))
    assert len(sources)==7 and len(images)==6
    mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==selected['manifestSHA256']==raw['exactRouteManifestSHA256'];refs.append(mp)
    for url,sha in raw['exactRouteTileHashes'].items():
        path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==sha;refs.append(path)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True,sourceSpecificOriginalEnvelopeReview=True,reviewedUid=UID,reviewedSourceSHA256=SHA)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},sourceSpecificIdentityReviewAccepted=True,identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},reviewer='ROOT',rawIdentityPassed=False,rawReasons=raw['reasons'],rawIdentityProof=raw['proof'],rawCanonicalFailuresPreserved=True,currentManifestSHA256=digest(mp.read_bytes()),primarySources=sources,imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis=[
      'Exact current ObjectID/CSUID, publisher root B361581883001063C0 and native geographic cell all identify this source. The full 11584-face geometry remains byte-identical, with all original record projection and exact cell coverage retained.',
      'ROOT opened the complete source plan/perspectives and all four downloaded architect project photographs. Exterior photographs 1,3,4 show the stepped glazed block, tall side cores, projecting horizontal facade bands and rooftop framing seen in the unchanged source. Photograph2 is interior context only and supplies no envelope/terrain precision.',
      'The architect identifies this as the completed 2016 eleven-storey ACC extension. The Hospital Authority opening release identifies Block T and its two connecting footbridges. These support the identity and connected design; they are not dimensional surveys or approval of each low appendage.',
      'The raw 16.992119189944756m maximum source extension remains recorded. The full model includes facade/roof projections and low adjoining detail beyond the simplified current footprint. It covers 99.99982016566905 percent of that footprint, while its sole other footprint overlap is the recorded 0.279130813841137m2 junction with161194. Exact peer originals share five coplanar facet areas; this is source identity context, not acceptance of the crossing, neighbour identity, support, physical or collision relationship.',
      'This source-specific identity decision resolves the two exact envelope warnings only. It grants no physical, terrain, shared-face, partial-burial, BASIC-contact, mobile, browser, collision or publication approval, and suppresses no other building. All those checks remain mandatory for this source and pinned scene. No source mesh edits or new generic threshold.' ])
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('qe_original_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-qe311317-original-envelope-identity-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
