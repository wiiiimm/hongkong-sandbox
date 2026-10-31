"""Review only exact original pier extents; retain every placement/duplicate gate."""
from pathlib import Path
import json
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-disneyland-piers-extent-identity-review-v1-20261029'
SELECT='government-xl-disneyland-piers-current-selection-v1-20261029'
IDENTITY='government-xl-disneyland-piers-current-identities-v1-20261029'
CONTEXT='government-xl-after-sha-tin-four-source-fit-context-v1-20261029'
PRIMARY='government-xl-disneyland-piers-primary-context-v2-20261029'
ALLOWED=['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(SELECT,BASE/SELECT/'selection.json.gz');primary=take(PRIMARY,BASE/PRIMARY/'summary.json');context=take(CONTEXT,BASE/CONTEXT/'summary.json');decisions=[]
    pimage=ROOT/primary['mapImage']['path'];assert digest(pimage.read_bytes())==primary['mapImage']['sha256'];refs.append(pimage)
    for source in selection['rows']:
        uid=source['uid'];part=uid.split('/')[1];raw=take(IDENTITY,BASE/IDENTITY/part/'identity.json');ctx=take(IDENTITY,BASE/IDENTITY/part/'context.json')['identity']
        assert raw['uid']==uid and raw['sourceSHA256']==source['sourceSHA256']and raw['reasons']==ALLOWED and not raw['passed']
        assert raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==source['modelId']
        assert raw['exactCurrentComponentRoute']['qualified']and raw['exactCurrentComponentRoute']['uid']==uid
        assert raw['exactWholeCellCoverage']['covered']and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==source['triangles']
        assert ctx['unrelatedIntersectingForms']==1 and 0<=ctx['sourceExcessCoveredByUnrelatedFormsM2']<=1
        # Keep the ordinary <=1m2 identity overlap limit. This is association
        # evidence only; the retained foreign form still needs complete contacts.
        form=source['source']['building'];tile=ROOT/'3d-viewer'/source['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==form;refs.append(tile)
        assert digest(json.dumps(form,sort_keys=True,separators=(',',':')).encode())==raw['sourceFormSHA256']
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==raw['sourceSHA256'];refs.append(asset)
        tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==source['triangles']and digest(tri.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
        view=next(r for r in context['rows']if r['uid']==uid);assert view['sourceSHA256']==source['sourceSHA256']and view['currentForm']==form
        image=BASE/CONTEXT/(part.replace(':','-')+'.png');assert digest(image.read_bytes())==pins[CONTEXT][str(image.relative_to(ROOT))];refs.append(image)
        decision=dict(uid=uid,sourceSHA256=raw['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],modelId=source['modelId'],completeOriginalFaces=len(tri),reviewer='ROOT',sourceIdentityInterpretationApproved=True,identityOnlyApproved=True,interpretedRawReasons=ALLOWED,rawUnrelatedIntersectingForms=ctx['unrelatedIntersectingForms'],rawUnrelatedExcessAreaM2=ctx['sourceExcessCoveredByUnrelatedFormsM2'],unrelatedFormPhysicalReviewApproved=False,rawIdentityEvidence=dict(path=str((BASE/IDENTITY/part/'identity.json').relative_to(ROOT)),sha256=digest((BASE/IDENTITY/part/'identity.json').read_bytes())),imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),primary['mapImage']],interpretation='The exact uniquely routed government original is a complete pier/platform feature, including its source-authored deck, lower piers, roof or lamps. The small BASIC footprint represents a roof structure at one end, not the complete authored feature. ROOT inspected full-source plan/oblique exports. The LandsD Sunny Bay/Disney map supports general Disneyland Resort Pier site/name context only; it does not measure the full model or approve individual component labels. Accept only this exact source extent/association. Preserve every raw extent reason; no source move, GIS footprint edit, source geometry edit, duplicate suppression, support/height/terrain or publication approval.',placementApproved=False,installationApproved=False,publication=False,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
        folder=out/part;save(folder/'ROOT-SOURCE-IDENTITY-DECISION.json',decision)
        boundary=shapely.MultiPoint(tri[:,:,[0,2]].reshape(-1,2)).convex_hull;assert boundary.geom_type=='Polygon'
        scope=dict(policy='reviewed-original-feature-v1',identityReviewed=True,uid=uid,modelId=source['modelId'],sha256=source['sourceSHA256'],worldBounds=source['candidate']['entry']['worldBounds'],boundary=list(map(list,boundary.exterior.coords)),form=dict(uid=form['uid'],objectId=form['objectId'],buildingCSUID=form['buildingCSUID'],parent=form.get('parent'),osmRefs=form.get('osmRefs'),rings=form['rings'],baseHeightHKPD=form.get('baseHeightHKPD'),topHeightHKPD=form.get('topHeightHKPD')),sourceReview=dict(path=str((folder/'ROOT-SOURCE-IDENTITY-DECISION.json').relative_to(ROOT)),sha256=digest((folder/'ROOT-SOURCE-IDENTITY-DECISION.json').read_bytes())))
        save(folder/'prepared-scope.json',scope);decisions.append(decision)
    result=dict(uids=[r['uid']for r in decisions],rows=decisions,sourceIdentityInterpretationApproved=True,identityOnlyApproved=True,sourceGeometryChanges=0,sourcePoseChanges=0,productionIntegrated=False,placementApproved=False,installationApproved=False,publication=False,qualification='Two explicit original extent decisions and prepared inactive loader scopes. All other source-fit, physical, duplicate, neighbour, runtime and browser gates remain mandatory. Source graphics and official map actually inspected; no new source asset tier or optimisation.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('disneyland_two_extent_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-exact-original-pier-extent-identity-interpretations-only',list(dict.fromkeys(refs)),result)
    print(dict(batch=BATCH,identityOnlyReviews=len(decisions),installationApproved=False),flush=True)

if __name__=='__main__':main()
