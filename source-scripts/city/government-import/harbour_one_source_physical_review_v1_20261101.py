"""Bounded original Harbour One assembly review with raw failures preserved.

No thresholds, geometry, source pose, foreign BASIC actors or public data change.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_supported_model_only_contract_v1_20261025 import verify_metadata
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbour-one-source-physical-review-v1-20261101'
P='government-xl-harbour-one-after-hkdi-a-';PRIVATE=P+'private-ground-v1-20261101';J=P+'junction-v1-20261101';PREVIEW=P+'unapproved-preview-v1-20261101'
TOWER,PODIUM='landsd/319571:0','landsd/269828:0';SUPPORTS={TOWER:PODIUM}
SOURCES={TOWER:'c6a1be96a01cddb4b4b14bff7f9acf6730b67c2964e9d8964562fb4f5df97113',PODIUM:'287dbcbf5237d514865f4f99d50dfd13cc98028942f00c8cd086a5e528952e91'}
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';scopepath=BASE/(PRIVATE+'-scope')/'form-obligations.json.gz'
    authenticate(scopepath.parent);forms=read(scopepath);resources=[('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain:city/data/terrain.json']
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('harbour-one-original-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),HERE/'original_supported_model_only_contract_v1_20261025.py'];pins={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        f=(HERE/'local'/batch if local else BASE/batch)/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selection=take(PRIVATE+'-runtime','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    original={r['uid']:r['candidate']['entry']for r in selection['rows']};cat=take(PREVIEW,'catalogue.json',True);assert verify_metadata(cat['models'],SOURCES,SUPPORTS,original)
    for r in selection['rows']:
        f=ROOT/r['candidate']['path'];assert digest(f.read_bytes())==SOURCES[r['uid']];refs.append(f)
    identity=take('government-xl-harbour-one-exact-component-identity-review-v1-20261101');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES
    proofs={r['uid']:r['identityProof']for r in identity['rows']};assert set(proofs)==set(SOURCES)and all(all(v.values())for v in proofs.values())
    for uid in SOURCES:
        take('government-xl-harbour-one-exact-component-identity-review-v1-20261101',uid.split('/')[1]+'-identity-review.json')
        earth=take(PRIVATE+'-'+uid.split('/')[1].replace(':','-')+'-foundations');assert earth['establishedFoundationPolicyPassed']and len(earth['rows'])==4
        assert all(r['triangles']==r['completeTerrainTriangles']and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedTriangles']==0 for r in earth['rows'])
    patch=P+'terrain-trial-v1-20261101-inset';terrain=take(patch);assert terrain['status']=='private-terrain-validator-passed'and set(terrain['uids'])==set(SOURCES)
    candidate=ROOT/terrain['candidate']['path'];assert digest(candidate.read_bytes())==terrain['candidate']['sha256'];refs.append(candidate)
    scope=take(J+'-scope');assert scope['uids']==selection['uids']if 'uids'in selection else set(scope['uids'])==set(SOURCES)
    assert all(r['currentNativeActorsChecked']==7072 and not r['nearbyNativeActors']for r in scope['rows'])
    full=take(PRIVATE+'-scope','scope.json');fullforms=take(PRIVATE+'-scope','form-obligations.json.gz');assert len(fullforms)==len(forms)==29 and fullforms==forms and not full['terrainContacts']and not full['touchingNativeUids']
    neighbour=take(P+'whole-region-neighbours-v1-20261101');assert neighbour['forms']==29 and neighbour['requiredNativeUids']==[]
    retained=take(P+'unchanged-neighbour-support-v1-20261101');assert retained['allBasicFlagsResolved']and retained['remainingBasicFlags']==[]and retained['allRetainedNativeChecksPassed']
    assert len(retained['proofs'])==1 and retained['proofs'][0]['uid']=='landsd/254814:0'and retained['proofs'][0]['supportUid']=='landsd/232185:0'and retained['proofs'][0]['unchangedVerticalGap']==0
    support=take(J+'-support');assert support['supportedUid']==TOWER and support['supportUid']==PODIUM and support['sourceSHA256ByUid']==SOURCES and len(support['rows'])==4
    roots=take(P+'strict-paths-v1-20261101');assert roots['sourceSHA256ByUid']==SOURCES and len(roots['rows'])==4
    assert all(r['targets']==r['finiteAttachmentPaths']==5 and r['disconnected']==r['aboveExistingEndpointCeiling']==0 and r['riseAboveEndpointRangeM']==[0,0]for r in roots['rows'])
    for mode in ['original','literal','leftF32','balancedF32']:
        r=next(r for r in support['rows']if r['mode']==mode);assert not r['passed']and r['support']['strictContacts']==197 and len(r['support']['unresolved'])==5
        assert r['compoundFoundation']['completeTerrainTriangles']==11708 and r['compoundFoundation']['fullyBuriedTriangles']==r['compoundFoundation']['fullyBuriedUpwardTriangles']==0
        path=take(P+'strict-paths-v1-20261101',mode+'.json.gz');assert path['canonicalStrictAnchorCount']==197 and path['sourceWorldSHA256']==r['sourceWorldSHA256ByUid'][TOWER]and path['supportWorldSHA256']==r['sourceWorldSHA256ByUid'][PODIUM]
    contacts=P+'original-pair-contacts-v1-20261101';pair=take(contacts);roles=take(contacts+'-roles');assert pair['sourceSHA256ByUid']==SOURCES and len(pair['rows'])==len(roles['rows'])==4
    assert all(r['allPairsExamined']and r['sourceFacesOmitted']==0 and r['areaContactPairs']==0 for r in pair['rows'])
    foreign=take(J+'-foreign');assert foreign['foreignPairs']==16 and not foreign['independentlyMeasuredOverlappingNativePairs']and not foreign['nativeCompleteFourWorldSeparation']
    external=[]
    for r in foreign['rows']:
        if r['foreignUid']in SOURCES:continue
        if any(m['allFiniteContactPairs']for m in r['modes']):external.append((r['uid'],r['foreignUid']))
    assert set(external)=={(PODIUM,'landsd/232185:0'),(PODIUM,'landsd/254814:0')}
    boundary=take('government-xl-harbour-one269828-foreign-boundary-context-v1-20261101');assert boundary['sourceSHA256']==SOURCES[PODIUM]and len(boundary['rows'])==10 and not boundary['collisionApproved']
    for r in boundary['rows']:
        if r['mode']=='before-basic':continue
        assert r['completeSourceFaces']==700 and r['areaContactPairs']==0
        expected=.04954651979380504 if r['foreignUid']=='landsd/232185:0'else .07231881466856935
        assert r['boundaryStrip']['maximumAbsoluteDistanceFromSupportingLineM']<=expected
        assert r['finiteContactPairs']==(31 if r['foreignUid']=='landsd/232185:0'else 22)
    boundary_seen=BASE/'government-xl-harbour-one-boundary-observations-v1-20261101.json';seen_boundary=read(boundary_seen);refs.append(boundary_seen);assert seen_boundary['imagesActuallyViewed']==boundary['images']
    for image in boundary['images']:f=ROOT/image['path'];assert digest(f.read_bytes())==image['sha256'];refs.append(f)
    metrics=take(PRIVATE+'-runtime','metrics.json');policy=module('harbour_original_policy',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py');raw_policy={}
    for m in metrics['rows']:
        raw_policy[m['uid']]=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[m['uid']],identityProof=proofs[m['uid']]),m,metrics['profiles']['mobile'])
    assert raw_policy=={TOWER:['ground-contact-unresolved'],PODIUM:[]}
    seenpath=BASE/'government-xl-harbour-one-actual-source-observations-v1-20261101.json';seen=read(seenpath);refs.append(seenpath);seen_images={q['path']:q for q in seen['imagesActuallyViewed']};assert len(seen_images)==8
    images=[];reports=[]
    for width in [1280,390]:
        f=BASE/PREVIEW/str(width)/'staged-browser.json';r=take(PREVIEW,str(width)+'/staged-browser.json');assert r['passed']and not r['errors'];reports.append(dict(path=str(f.relative_to(ROOT)),sha256=digest(f.read_bytes())))
        views=[v for v in r['views']if 'time'in v];assert len(views)==4
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
            f=BASE/PREVIEW/str(width)/v['file'];item=dict(path=str(f.relative_to(ROOT)),sha256=digest(f.read_bytes()),uid=v['uid'],width=width,time=v['time']);assert seen_images[item['path']]==item;images.append(item);refs.append(f)
        assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());assert start==selection['manifestSHA256']==scope['currentManifestSHA256']==identity['currentManifestSHA256']==retained['currentManifestSHA256'];refs.append(manifest)
    assert reservations.owns(lease)
    result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORTS,identityAccepted=True,identityProof=proofs[TOWER],identityProofByUid=proofs,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=29,leaseResources=resources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=start),currentManifestSHA256=start,rawCanonicalFailuresPreserved=True,rawDirectPolicyReasons=raw_policy,ordinaryPairSupportPredicateRemainsFalse=True,rawCompoundFoundationRows=support['rows'],strictRootPaths=roots['rows'],rawForeignContacts=foreign['rows'],acceptedForeignBoundaryPairs=[dict(uid=u,foreignUid=v)for u,v in external],unchangedBasicSupportProofs=retained['proofs'],unresolvedExternalBasicContacts=[],sourceGeometryChanges=0,sourcePoseChanges=0,proposedTerrainChange=True,publicTerrainWritesPerformed=False,terrainEdits=True,imagesActuallyViewed=images,browserReports=reports,visualAcceptance=True,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation=[
        'Accept this exact immutable government tower/podium assembly at fixed1x/HKPD placement. Both complete source meshes clear actual terrain in all four worlds. Original TIN and its bounded return passed the unchanged terrain validator; every29affected current form is retained.',
        'The existing strict interface has197accepted anchors per world. All5remaining raw tower rim warnings have zero-rise shared-original-edge paths to independently reproduced canonical anchors. Preserve the ordinary false pair verdict and minimum partial embedding: no full source facet is buried by the compound envelope. The exact439/446finite pair contacts have no area-contact pairs and describe the authored facade/upper-podium join; no engineering/watertightness or generic embedding exception is introduced.',
        'Both complete source diagrams, both boundary plots and eight private source exports were inspected. The only external intersections lie along the immediately adjacent unchanged Industrial Building boundary. The full projected slivers lie in4.955cm/7.232cm strips about actual BASIC boundary segments; the exact31/22surface intersections have no area contacts. Accept this exact source-to-proxy wall-boundary interface, preserving every raw contact/area and the double-precision diagnostic limitation. No unrelated actor is hidden, replaced, shifted or remodelled; this is not a generic horizontal threshold.',
        'The sole terrain-only neighbour-gap warning resolves with the pre-existing unchanged_supports rule: Industrial tower254814 remains on its unchanged unique podium232185 with zero roof/base gap and99.9998676percent footprint coverage. Raw increased-gap warning remains; no terrain or neighbour threshold changes.',
        'Actual desktop/mobile source picking/collision, source integrity, mobile budgets, failure/retry and joint original-state reports passed. Night views are dark, neighbouring procedural skin/aliasing remains, and mobile podium own-view initially showed its peer as BASIC; later joint reports verify both originals. Live installation tests and independent whole521/oldassets/terrain readback remain mandatory. No measured mobile FPS, every-facade or whole-region completeness claim.'])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('harbour_one_source_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-harbour-one-assembly-and-exact-adjacent-boundary-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
