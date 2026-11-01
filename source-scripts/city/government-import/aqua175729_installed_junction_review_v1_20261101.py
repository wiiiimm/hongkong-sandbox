"""Bounded review of the exact original Aqua Block5/podium authoring junction.

Preserves all raw support/roof-envelope negatives and every original facet.
No global policy, geometry, pose, terrain or installed-parent metadata changes.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
UID='landsd/175729:0';PARENT='landsd/193086:0'
SHA='9e92d0a14f9d9c230745c49d84ed33cfda40c41d826a067e2c0ff72f0dbd1044'
PSHA='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91'
P='government-xl-cohort19-';BASE=ROOT/'docs/astra-city/government-import'
RUNTIME=P+'current-original-checks-v1-20261101-runtime'
AFFECTED=[1815,1816,1817,1818,2482,2483,4757,4758,4759,4760,4761,5620,6579,6580,6581,6582,9508,10886]
MODES=['original','literal','leftF32','balancedF32']

def main():
    batch=P+'aqua-physical-review-v1-20261101';out=BASE/batch;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,file='summary.json',local=False):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        p=(HERE/'local'/n if local else BASE/n)/file
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(RUNTIME,'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==UID)
    assert source['sourceSHA256']==SHA and source['triangles']==11052
    attrs=take(P+'original-attributes-v1-20261101','attributes.json.gz');assert attrs['startEndAllInputsVerified']
    attr=next(r for r in attrs['rows']if r['uid']==UID);assert attr['sourceSHA256']==SHA
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    worlds={'original':decode_original_world_triangles(asset.read_bytes())}
    for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[key],dtype='<f8').reshape(-1,3)[index]
    geom=next(r for r in take(RUNTIME,'runtime-geometry.json.gz',True)['rows']if r['uid']==UID)
    assert np.array_equal(worlds['literal'],np.asarray(geom['position']).reshape(-1,3)[np.asarray(geom['index']).reshape(-1,3)])
    ground=np.asarray(geom['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert len(ground)>0
    margin=min(float(t[:,:,1].min()-ground[:,:,1].max())for t in worlds.values());assert margin>14 and all(len(t)==11052 for t in worlds.values())
    metric=next(r for r in take(RUNTIME,'metrics.json')['rows']if r['uid']==UID)
    assert metric['sourcePreserved']and metric['sourceSHA256']==SHA and metric['missingTerrain']==metric['missingDrawnTerrain']['count']==metric['samplerDisagreement']['count']==0
    assert metric['budget']['triangles']==11052 and metric['budget']['geometryBytes']<50331648 and metric['budget']['residentBytes']<134217728
    identity=next(r for r in take(P+'current-original-checks-v1-20261101-identity')['rows']if r['uid']==UID)
    assert identity['passed']and identity['reasons']==[]and identity['sourceSHA256']==SHA
    scope=take(P+'complete-source-scope-v1-20261101');row=next(r for r in scope['rows']if r['uid']==UID)
    assert row['currentNativeActorsChecked']==7067 and [r['uid']for r in row['nearbyNativeActors']]==[PARENT]
    forms=take(P+'complete-source-scope-v1-20261101','175729:0-forms.json.gz');assert len(forms)==4
    own={r['building']['uid']:r['building']for r in forms};assert own[UID]['parent']==own[PARENT]['parent']=='way/232252505'
    foreign=take(P+'aqua-twin-current-foreign-v1-20261101');foreign_rows=[r for r in foreign['rows']if r['uid']==UID]
    assert {r['foreignUid']for r in foreign_rows}==set(own)-{UID,PARENT} and all(m['allFiniteContactPairs']==0 for r in foreign_rows for m in r['modes'])
    native_batch=P+'installed-native-contacts-v1-20261101';contacts=take(native_batch)
    pair=next(r for r in contacts['rows']if r['uid']==UID and r['nativeUid']==PARENT);parent=pair['rawCurrentNativeEntry']
    assert pair['sourceSHA256']==SHA and pair['nativeSHA256']==parent['sha256']==PSHA
    assert parent['publicationApproved']and parent['sourceIdentityReviewed']and parent['placementReviewed']and parent['identityReviewApproved']
    assert parent['rootTranslation']==[-834500,0,816500]and parent.get('verticalPlacementOffsetHKPD',0)==0
    strict=take(P+'aqua175729-installed-support-v1-20261101');assert strict['installedNativeEntry']==parent
    anchors_batch=P+'aqua-canonical-anchor-paths-v1-20261101';anchors=take(anchors_batch)
    assert anchors['sourceSHA256ByUid']=={UID:SHA,PARENT:PSHA}
    compound_batch=P+'aqua-complete-compound-context-v1-20261101';compound=take(compound_batch)
    buried=take(P+'aqua-buried-face-context-v1-20261101')
    role_batch=P+'native-contact-roles-v1-20261101';roles=take(role_batch);original_roles=take(role_batch,'175729:0--193086:0--original.json.gz')
    original_pairs={(r['sourceFaceA'],r['sourceFaceB'])for r in original_roles};facts={}
    for mode in MODES:
        t=worlds[mode];world_sha=digest(t.astype('<f8').tobytes());raw=take(P+'aqua175729-installed-support-v1-20261101','175729:0-'+mode+'.json.gz')
        assert raw['sourceWorldSHA256']==world_sha and raw['sourceSHA256']==SHA and raw['supportSHA256']==PSHA
        assert raw['strictSupport']['strictContacts']==335 and raw['strictSupport']['samples']==343 and len(raw['strictSupport']['unresolved'])==8 and not raw['strictSupport']['passed']
        paths=take(anchors_batch,mode+'.json.gz');assert paths['sourceWorldSHA256']==world_sha and paths['canonicalStrictAnchorCount']==335 and paths['noIntercomponentJoins']
        assert len(paths['rows'])==8 and all(r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 and r['terminal']['kind']=='canonical-strict-vertical-support-anchor'for r in paths['rows'])
        label={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);cap=take(compound_batch,label+'-cap-paths.json.gz');summary=next(r for r in compound['rows']if r['mode']==label)
        assert cap['sourceWorldSHA256']==world_sha and cap['supportWorldSHA256']==raw['supportWorldSHA256'] and cap['proof']['allAffectedHavePaths']
        assert summary['exactAffectedFaces']==AFFECTED and summary['compoundCapPathsPassed']and summary['allAffectedWallLike']and summary['negativeNonWallFaces']==[]
        faces=next(r for r in buried['rows']if r['mode']==mode)['buriedFaces'];assert [r['faceIndex']for r in faces]==[6580]
        assert abs(faces[0]['normal'][1])<.25*np.linalg.norm(faces[0]['normal']) and faces[0]['areaM2']==0.05968874063355749
        classified=take(role_batch,'175729:0--193086:0--'+mode+'.json.gz');cross=[r for r in classified if r['contactRole']=='transverse-surface-crossing']
        assert len(cross)==(201 if mode in ['original','literal']else 78) and all((r['sourceFaceA'],r['sourceFaceB'])in original_pairs for r in cross)
        role=next(r for r in roles['rows']if r['uid']==UID and r['nativeUid']==PARENT and r['mode']==mode);assert role['sourceWorldSHA256']==world_sha and role['contactBounds'][1][1]<27
        facts[mode]=dict(sourceWorldSHA256=world_sha,canonicalAnchors=335,unresolvedRawWarnings=raw['strictSupport']['unresolved'],allEightHaveCanonicalPaths=True,exactNegativeWallFaces=AFFECTED,compoundCapPathsPassed=True,buriedFaces=[6580],rawTransverseCrossings=len(cross),allCrossingsHaveOriginalFacetPairContact=True,rawStrictSupportPassed=False)
    browser=P+'aqua-installed-supported-preview-v1-20261101';images=[];retained=[];reports=[]
    inspected=take(P+'recovery-progress-v2-20261101');opened={r['path']:r for r in inspected['imagesActuallyOpenedByRoot']};assert len(opened)==8
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        reports.append(dict(path=str((BASE/browser/str(width)/'staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/browser/str(width)/'staged-browser.json').read_bytes())))
        for kind,views,target in [('source',report['views'],images),('retained',report['retainedNativeOwnViews'],retained)]:
            views=[r for r in views if r.get('file')];assert len(views)==2
            for view in views:
                p=BASE/browser/str(width)/view['file'];item=dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),uid=view['uid'],width=width,time=view['time']);assert opened[item['path']]==item and item['sha256']==pins[browser][item['path']];refs.append(p)
                assert view['active']and view['visible']and view['fullyFramed']and not view['fallbackFaces']and view['sourceSHA256']==(SHA if kind=='source'else PSHA)
                if kind=='source':assert view['solidAppearance']and view['pick']==view['collision']==UID
                target.append(item)
    take(P+'aqua-face6580-local-views-v1-20261101');take(P+'aqua-source-interface-context-v1-20261101')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={UID:PARENT},nativeSupportByUid={UID:PARENT},retainedNativeEntries={PARENT:parent},retainedNativeUids=[PARENT],reviewer='ROOT',identityAccepted=True,identityProof=identity,rawIdentityReasonsRetained=[],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=4,leaseResources=sorted('building:'+r['building']['uid']for r in forms),retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=msha),currentManifestSHA256=msha,terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawCanonicalFailuresPreserved=True,unresolvedExternalBasicContacts=[],acceptedInstalledSupportContacts=[dict(uid=UID,nativeUid=PARENT,physicalInterpretationAccepted=True,rawContactSummary=pair)],junctionFacts=facts,rawSupportAndCompoundVerdicts=strict,rawCompoundClearance=compound,actualEarthGlobalClearanceLowerBoundM=margin,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,browserReports=reports,visualAcceptance=False,installationApproved=False,publication=False,interpretation=[
        'Accept only these exact unchanged Block5/podium sources and fixed1x/HKPD placement. Every original source vertex is more than14m above the maximum actual drawn-earth vertex. Both foreign BASIC neighbours have zero finite contacts; the sole native is the exact installed Aqua podium, with unchanged metadata and source bytes.',
        'Retain strict335of343 and all eight support-above-rim warnings. Each has an original shared-edge path to a reproduced canonical accepted support anchor in all four worlds, with zero rise beyond the existing endpoint-height gate. This is bounded interpretation of the authored lower building/podium joint, not a new support tolerance or structural certification.',
        'All18 exact compound-negative facets are wall-like and have exact original clear-cap paths; there are no negative nonwalls. The sole wholly roof-envelope-buried sampled facet6580 is a0.0596887406m2 near-vertical source junction strip. ROOT inspected the exact local red-face/teal-podium diagram and the complete original source. It is part of this lower facade/podium seam; podium upper surfaces are not earth. No source floor is granted a burial exception.',
        'All201 original/literal transverse segments and78Float32 segments remain explicit, confined below27mHKPD in the lower authoring junction. Every represented crossing has an already-contacting original facet pair. This named same-source joint interpretation changes no collision policy, unrelated source, ground, procedural skin or geometry.',
        'ROOT opened all eight source/retained desktop1280/mobile390 day/night exports. Complete roof/body/base are visible; original plain grey and unlit night surfaces are retained with procedural windows disabled. Picking, collision, failure/retry and retained own views passed. Guarded stage, live verification, unchanged-old-asset and full521ledger readback remain mandatory.'])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'junction-facts.json',facts)
    refs.append(HERE/'original_installed_support_model_only_contract_v1_20261027.py')
    module('aqua_original_junction_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-original-aqua-block5-installed-podium-junction-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
