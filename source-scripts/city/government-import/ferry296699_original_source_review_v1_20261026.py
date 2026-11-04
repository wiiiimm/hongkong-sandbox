"""Bind the exact original ferry terminal's inspected source/interface evidence."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

P='government-xl-after-marco-next-five-'
UID='landsd/296699:0'
SHA='2b8df5f8d1d6b2e5a00b52fc0a46cdae910e0d460d09c7543e5cd1f334702dc4'
SOURCES={UID:SHA}


def main():
    base=ROOT/'docs/astra-city/government-import';batch=P+'ferry-source-review-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(suffix,file='summary.json'):
        name=P+suffix+'-20261026'
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take('ferry-group-runtime-v2','selection.json.gz');assert len(selected['rows'])==1
    source=selected['rows'][0];assert source['uid']==UID and source['sourceSHA256']==SHA and source['triangles']==10683
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes())
    identity=take('identity-v1','296699:0/identity.json')
    assert identity['sourceSHA256']==SHA and identity['worldTrianglesSHA256']==digest(tri.astype('<f8').tobytes())
    assert identity['originalOwnership']['sourceGraphVerified'] and identity['originalOwnership']['originalRootName']=='B336951676801063C0'
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['freshCurrentIdentity']['exactObjectAndCSUID'] and identity['exactWholeCellCoverage']['covered']
    assert identity['freshCurrentIdentity']['targetCoveredBySourceProjection']>.998
    expected_reasons={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
    assert not identity['passed'] and set(identity['reasons'])==expected_reasons
    form=source['source']['building'];assert form['objectId']==296699 and form['buildingCSUID']=='3369516768T20050430'
    tile=ROOT/'3d-viewer'/source['source']['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==UID)==form;refs.append(tile)
    metrics=take('ferry-group-runtime-v2','metrics.json');assert len(metrics['rows'])==1
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    policy=module('ferry_source_acceptance_policy',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py')
    assert policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=proof),metrics['rows'][0],metrics['profiles']['mobile'])==[]
    foundation=take('ferry-group-foundation-v1');assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows'])==4
    assert all(r['triangles']==r['completeTerrainTriangles']==10683 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    clearance=take('ferry-group-clearance-v1');assert len(clearance['rows'])==4
    assert all(r['completeSourceFaces']==10683 and r['noAffectedFaces'] and r['exactAffectedFaces']==[] and r['negativeNonWallFaces']==[] for r in clearance['rows'])
    scope=take('ferry-source-scope-v1');assert scope['uids']==[UID] and len(scope['rows'])==1
    assert scope['rows'][0]['currentNativeActorsChecked']==6966 and scope['rows'][0]['nearbyNativeActors']==[]
    forms=take('ferry-source-scope-v1','296699:0-forms.json.gz');assert {f['building']['uid'] for f in forms}=={UID,'landsd/97556:0'}
    foreign=take('foreign-v1');pairs=[r for r in foreign['rows'] if r['uid']==UID]
    assert len(pairs)==1 and pairs[0]['foreignUid']=='landsd/97556:0'
    assert all(r['allFiniteContactPairs']==r['positiveContactPairs']==(0 if r['mode']=='before-basic' else 10) for r in pairs[0]['modes'])
    for mode in ['original','literal','leftF32','balancedF32']:
        contact=take('foreign-v1','296699:0--97556:0--'+mode+'.json.gz')
        assert len(contact['contacts'])==10 and all(c['dimension']==1 and c['sourceFaceA'] in [10470,10473] for c in contact['contacts'])
    context=take('ferry-basic97556-views-v1');assert len(context['contactContext'])==10
    assert all(r['absoluteNormalY'][0]>.99999 and r['absoluteNormalY'][1]==0 and r['dimension']==1 for r in context['contactContext'])
    affected=take('ferry-changed-actor-scope-v1');assert affected['completeInstalledActorsAccounted']==6966 and affected['allRegisteredBasicSupportsAccounted']==10
    assert affected['allCurrentInstalledAssetBytesVerified'] and affected['allExistingNativeWholeSourceTerrainUnaffectedProved'] and affected['affectedNativeUids']==affected['affectedRegisteredBasicSupportUids']==[]
    formchecks=take('ferry-group-form-checks-v1');assert formchecks['forms']==5402 and formchecks['flagged']==[] and formchecks['ordinaryFlagged']==0
    patch=take('ferry-retained-group-v2');assert patch['status']=='private-terrain-validator-passed' and patch['hierarchicalRetention']['retainedChildren']==14 and patch['hierarchicalRetention']['exactOldGridNodes']==375789
    browser=take('ferry-private-preview-v1');assert browser['allBrowserDiagnosticsPassed'] and browser['canonicalPublisherDryRunPassed'] and browser['retainedSourcesReapproved'] is False
    images=[]
    for width in [1280,390]:
        report=take('ferry-private-preview-v1',str(width)+'/staged-browser.json');assert report['passed'] and report['errors']==[]
        views=[v for v in report['views'] if 'time' in v];assert len(views)==2
        for v in views:
            assert v['uid']==UID and v['sourceSHA256']==SHA and v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['pick']==v['collision']==UID
            path=base/(P+'ferry-private-preview-v1-20261026')/str(width)/v['file'];assert digest(path.read_bytes())==pins[P+'ferry-private-preview-v1-20261026'][str(path.relative_to(ROOT))];refs.append(path)
            images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=UID,width=width,time=v['time'],actuallyOpenedByROOT=True))
        if width==390:assert any(v.get('phase')=='failed-download' and v['uid']==UID and v['fallbackRetained'] for v in report['views'])
    for filename in ['whole-source-plan.png','whole-source-perspectives.png']:
        path=base/(P+'296699-identity-plots-v1-20261026')/filename
        take('296699-identity-plots-v1',filename) if False else None
        _,bound=authenticate(path.parent);assert digest(path.read_bytes())==bound[str(path.relative_to(ROOT))];refs.extend([path,path.parent/'result.json'])
    diagram=base/(P+'ferry-basic97556-views-v1-20261026')/'before-after-contact-context.png';assert digest(diagram.read_bytes())==pins[P+'ferry-basic97556-views-v1-20261026'][str(diagram.relative_to(ROOT))];refs.append(diagram)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==browser['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256ByUid=SOURCES,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,identityProofByUid={UID:proof},supportByUid={},retainedNativeEntries={},retainedSourcesReapproved=False,rawIdentityReasons=identity['reasons'],imagesActuallyViewed=images,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,review=dict(identity='Exact original root B336951676801063C0, official ObjectID/CSUID route and full geographic-cell coverage bind the source. Inspected complete-source plans/perspectives show the long terminal and its surrounding platform; the 21.053m extent warning describes this platform beyond the narrower recorded building footprint. All original faces retained; no ownership credit assigned to neighbouring97556.',interface='All10 exact crossings remain: source horizontal platform faces10470/10473 meet retained BASIC97556 vertical walls aroundHKPD4.05m, slightly above its recorded3.9m base. The inspected diagram shows the small BASIC structure standing through the deck boundary, not a roof replacement or suppression. Preserve it unchanged. This is bounded source/interface interpretation, not an invented support dependency.',ground='Exact original source stays1x/nativeHKPD. Four-world fullground clearance has no affected faces and no wholly buried source faces. Existing mobile acceptance policy yields no reasons after bounded identity review. Existing terrain group children/grid are preserved exactly; all6966oldassets,10BASICsupports and5402forms pass non-effect/regression.',visual='All4individual desktop/mobile day/night exports actually opened. Longroof/controltower/platform are readable. Foregroundtower partly conceals lowerfacade onmobile; no fine facade visibility is claimed. Source remainsgrey/day,dark/night with no proceduralwindows.',limits='Source review only. Qualification, guarded publication, fresh live verification and independent installed readback still required. Raw source extent/unrelated-overlap failures preserved; prior terrain revisions/held models receive no transferred approval.'))
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('ferry_original_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-ferry-source-and-platform-interface-review',refs,result)


if __name__=='__main__':main()
