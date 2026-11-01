"""Bounded exact Shangri-La original tower/podium assembly review with raw failures preserved.

No thresholds, geometry, source pose, foreign BASIC actors or public data change.
"""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_supported_model_only_contract_v1_20261025 import verify_metadata
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-shangrila-source-physical-review-v2-20261102'
PRIVATE='government-xl-shangrila233824-contact-floor-return-v2-20261102'
J='government-xl-shangrila-contact-ground-mechanical-v2-20261102'
PREVIEW='government-xl-shangrila-contact-ground-unapproved-preview-v2-20261102'
IDENTITY='government-xl-shangrila-exact-component-identity-review-v1-20261101'
ENDPOINTS='government-xl-shangrila-contact-ground-mechanical-v2-20261102-endpoints'
TOWER,PODIUM='landsd/240962:0','landsd/233824:0';SUPPORTS={TOWER:PODIUM}
SOURCES={TOWER:'2b2c545fe714424d9b0af9af5acd62256f64a011a1d0c5e455ccc2e04644a6a4',PODIUM:'e7406277e84cd879c2e4ffcd9e5e19b25b52ffc740072e429ca32a0ebd79d613'}
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';scopepath=BASE/(PRIVATE+'-terrain-scope')/'form-obligations.json.gz'
    authenticate(scopepath.parent);forms=read(scopepath);resources=[('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain:city/data/terrain.json']
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('shangrila-original-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources);refs=[Path(__file__),HERE/'original_supported_model_only_contract_v1_20261025.py'];pins={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        f=(HERE/'local'/batch if local else BASE/batch)/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selection=take(PRIVATE+'-runtime','selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    original={r['uid']:r['candidate']['entry']for r in selection['rows']};cat=take(PREVIEW,'catalogue.json',True);assert verify_metadata(cat['models'],SOURCES,SUPPORTS,original)
    for r in selection['rows']:
        f=ROOT/r['candidate']['path'];assert digest(f.read_bytes())==SOURCES[r['uid']];refs.append(f)
    identity=take(IDENTITY);assert identity['identityAccepted']and {r['uid']:r['sourceSHA256']for r in identity['rows']}==SOURCES
    proofs={r['uid']:r['identityProof']for r in identity['rows']};assert set(proofs)==set(SOURCES)and all(all(v.values())for v in proofs.values())
    for uid in SOURCES:
        take(IDENTITY,uid.split('/')[1]+'-identity-review.json')
        earth=take(PRIVATE+'-'+uid.split('/')[1].replace(':','-')+'-foundations');assert earth['establishedFoundationPolicyPassed']and len(earth['rows'])==4
        assert all(r['triangles']==r['completeTerrainTriangles']and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedTriangles']==0 for r in earth['rows'])
    patch=PRIVATE+'-inset';terrain=take(patch);assert terrain['status']=='private-terrain-validator-passed'and set(terrain['uids'])==set(SOURCES)
    candidate=ROOT/terrain['candidate']['path'];assert digest(candidate.read_bytes())==terrain['candidate']['sha256'];refs.append(candidate)
    scope=take(PRIVATE+'-model-scope');assert scope['uids']==selection['uids']if 'uids'in selection else set(scope['uids'])==set(SOURCES)
    assert all(r['currentNativeActorsChecked']==7074 and not r['nearbyNativeActors']for r in scope['rows'])
    full=take(PRIVATE+'-terrain-scope','scope.json');fullforms=take(PRIVATE+'-terrain-scope','form-obligations.json.gz');assert len(fullforms)==len(forms)==12 and fullforms==forms and not full['terrainContacts']and not full['touchingNativeUids']
    neighbour=take('government-xl-shangrila-contact-ground-neighbours-v2-20261102');assert neighbour['forms']==12 and neighbour['requiredNativeUids']==[] and neighbour['basicFlags']==[] and neighbour['nativeRows']==[]
    support=take(J+'-support');assert support['supportedUid']==TOWER and support['supportUid']==PODIUM and support['sourceSHA256ByUid']==SOURCES and len(support['rows'])==4
    roots=take(ENDPOINTS);assert roots['sourceSHA256ByUid']==SOURCES and roots['targetUid']==TOWER and len(roots['rows'])==4
    assert all(r['witnesses']==r['finiteAttachmentPaths']==r['pathsWithinEndpointHeight']==351 and r['disconnected']==0 for r in roots['rows'])
    for mode in ['original','literal','leftF32','balancedF32']:
        r=next(r for r in support['rows']if r['mode']==mode);assert not r['passed']and r['support']['strictContacts']==1254 and len(r['support']['unresolved'])==351
        assert r['compoundFoundation']['completeTerrainTriangles']==11841 and r['compoundFoundation']['fullyBuriedTriangles']==r['compoundFoundation']['fullyBuriedUpwardTriangles']==0
        path=take(ENDPOINTS,mode+'.json.gz');assert [p['witness']for p in path['rows']]==r['support']['unresolved'] and all(p['hasUnrestrictedFiniteAttachment']and p['passesExistingEndpointHeight']and p['riseAboveEndpointsM']==0 and p['maximumResidualM']<=.001 for p in path['rows'])
    pair=take('government-xl-shangrila-original-pair-final-mechanical-v1-20261101-pair');roles=take(J+'-roles');assert pair['sourceSHA256ByUid']==SOURCES and roles['sourceSHA256ByUid']==SOURCES and len(pair['rows'])==len(roles['rows'])==4
    from fractions import Fraction
    joint_bounds=[]
    for r in pair['rows']:
        assert r['allPairsExamined']and r['sourceFacesOmitted']==0
        contacts=take(J+'-roles',r['mode']+'.json.gz');assert len(contacts)==r['finiteContactPairs']
        ys=[Fraction(p[1])for c in contacts for p in c['exactPoints']]
        # A named measured interface band, never a generic collision allowance.
        assert Fraction(1297,100)<=min(ys)<=max(ys)<=Fraction(1436,100)
        joint_bounds.append(dict(mode=r['mode'],exactMinimumY=str(min(ys)),exactMaximumY=str(max(ys))))
    foreign=take(J+'-foreign');assert foreign['foreignPairs']==10 and not foreign['independentlyMeasuredOverlappingNativePairs']and not foreign['nativeCompleteFourWorldSeparation']
    external=[]
    for r in foreign['rows']:
        if r['foreignUid']in SOURCES:continue
        assert all(m['allFiniteContactPairs']==0 for m in r['modes'])
    diagram='government-xl-shangrila-original-pair-coloured-context-v1-20261102';seen_pair=take(diagram);assert set(seen_pair['uids'])==set(SOURCES)and len(seen_pair['views'])==1
    for view in seen_pair['views']:
        f=ROOT/view['image']['path'];assert digest(f.read_bytes())==view['image']['sha256'];refs.append(f)
    metrics=take(PRIVATE+'-runtime','metrics.json');policy=module('shangrila_original_policy',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py');raw_policy={}
    for m in metrics['rows']:
        raw_policy[m['uid']]=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[m['uid']],identityProof=proofs[m['uid']]),m,metrics['profiles']['mobile'])
    assert raw_policy=={TOWER:['ground-contact-unresolved'],PODIUM:[]}
    seenpath=BASE/'government-xl-shangrila-actual-source-observations-v2-20261102.json';seen=read(seenpath);refs.append(seenpath);seen_images={q['path']:q for q in seen['imagesActuallyViewed']};assert len(seen_images)==8
    images=[];reports=[]
    for width in [1280,390]:
        f=BASE/PREVIEW/str(width)/'staged-browser.json';r=take(PREVIEW,str(width)+'/staged-browser.json');assert r['passed']and not r['errors'];reports.append(dict(path=str(f.relative_to(ROOT)),sha256=digest(f.read_bytes())))
        views=[v for v in r['views']if 'time'in v];assert len(views)==4
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
            f=BASE/PREVIEW/str(width)/v['file'];item=dict(path=str(f.relative_to(ROOT)),sha256=digest(f.read_bytes()),uid=v['uid'],width=width,time=v['time']);assert seen_images[item['path']]==item;images.append(item);refs.append(f)
        assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());assert start==selection['manifestSHA256']==scope['currentManifestSHA256']==identity['currentManifestSHA256'];refs.append(manifest)
    assert reservations.owns(lease)
    result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORTS,identityAccepted=True,identityProof=proofs[TOWER],identityProofByUid=proofs,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=12,leaseResources=resources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=start),currentManifestSHA256=start,rawCanonicalFailuresPreserved=True,rawDirectPolicyReasons=raw_policy,ordinaryPairSupportPredicateRemainsFalse=True,rawCompoundFoundationRows=support['rows'],strictRootPaths=roots['rows'],rawForeignContacts=foreign['rows'],acceptedForeignBoundaryPairs=[dict(uid=u,foreignUid=v)for u,v in external],unchangedBasicSupportProofs=[],unresolvedExternalBasicContacts=[],sourceGeometryChanges=0,sourcePoseChanges=0,proposedTerrainChange=True,publicTerrainWritesPerformed=False,terrainEdits=True,imagesActuallyViewed=images,browserReports=reports,visualAcceptance=True,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation=[
        'Accept only these exact immutable government tower/podium components at fixed1x/HKPD pose. Both source meshes clear actual terrain in all four worlds; the original TIN and bounded two-face5cm-clearance floor return passed existing validators, and all12affected forms remain clear.',
        'Retain the raw false strict-interface predicate,1254strictanchors,351warnings and minimum partial envelope gap. Complete compound foundations have no fully buried or upward-buried facets. Every351warning has a continuous on-source shared-edge/positive finite self-join path to an actual positive original companion contact within the unchanged endpoint-height and1mm incidence gates. This named authored tower/podium interface is accepted; no generic support-root substitution or threshold widening.',
        'Full original pair and exact four-world classifications preserve all finite surface crossings and shared-plane area contacts. Their entire measured contact band lies at12.97084–14.35320mHKPD, the low original tower/upper-podium interface shown in the complete colour diagram. These are the two unchanged component surfaces of this exact source assembly; all external non-coimport BASIC contacts are zero. No engineering/watertightness or geometry change is proposed.',
        'All eight actual private source exports and the full pair diagram were inspected. Original tower ribbing and roof detail are visible; podium is partly occluded by retained foreground BASIC actors. Mobile podium own-view initially showed peer tower BASIC; subsequent joint reports show both originals active. Night originals are dark and surrounding BASIC aliasing persists. Diagnostic diagram heading says Ocean Centre erroneously; exact UID/source bindings establish the displayed pair, not that heading.',
        'Desktop/mobile loading,picking,collision integration,failure/retry,joint-state and unchanged mobile runtime budgets pass. Live guarded installation and independent whole521/oldasset/terrain readback remain mandatory. No whole-hotel,every-facade or measuredFPS claim.'],exactOriginalJointHeightBounds=joint_bounds)
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('shangrila_source_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-original-shangrila-component-assembly-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
