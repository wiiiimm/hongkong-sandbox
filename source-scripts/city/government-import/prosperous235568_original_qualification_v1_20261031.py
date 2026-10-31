"""Bounded six-original assembly review; retains every raw strict failure."""
import argparse,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-';BATCH=P+'original-qualification-v1-20261031';OWNER='landsd/235568:0'
SCOPE='government-xl-after-villa-premiere-235568-floor-return-scope-v1-20261031'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json',external=None):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=external if external is not None else BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    forms=take(SCOPE,'form-obligations.json.gz');assert len(forms)==58
    resources=sorted({('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms}|{'terrain:city/data/terrain.json'})
    if not a.owned:
        assert not lp.parent.exists();claim=reservations.claim('prosperous-qualified-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(resources)==set(lease['resources'])
    runtime=P+'six-original-patch-runtime-v1-20261031';selection=take(runtime,'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==6
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    for row in selection['rows']:
        p=ROOT/row['candidate']['path'];assert ref(p)['sha256']==sources[row['uid']];refs.append(p);p=ROOT/'3d-viewer'/row['source']['tile'];assert ref(p)['sha256']==row['source']['tileSHA256']and next(b for b in read(p)['buildings']if b['uid']==row['uid'])==row['source']['building'];refs.append(p)
    identity=take(P+'podium-identity-review-v1-20261031','235568:0-review.json');assert identity['identityOnlyApproved']and identity['sourceSHA256']==sources[OWNER]
    identities={OWNER:identity['identityProof']}
    for uid in sources.keys()-{OWNER}:
        d=take(P+'six-original-identity-v1-20261031',uid.split('/')[1]+'/identity.json');assert d['passed']and not d['reasons']and d['sourceSHA256']==sources[uid];identities[uid]=d['proof']
    lower=take(P+'lower-source-role-review-v1-20261031','ROOT-LOWER-SOURCE-REVIEW.json');assert lower['sourceRoleAccepted']and lower['sourceSHA256']==sources[OWNER]and not lower['groundRootCredit']and not lower['interComponentBridgeCredit']
    ground=take(P+'podium-complete-ground-v1-20261031');assert len(ground['rows'])==4
    attrs=take(P+'six-original-attributes-v1-20261031','attributes.json.gz');assert attrs['startEndAllInputsVerified']
    # Every tower's complete compound clearance includes every terrain face.
    geometry=take(runtime,external=HERE/'local'/runtime/'runtime-geometry.json.gz');counts={r['uid']:len(np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3))for r in geometry['rows']}
    expected={'234691':(43,0,0,45),'235119':(1,1,0,23),'235888':(18,0,0,2),'236076':(139,43,4,199),'237129':(75,0,0,78)};raw=[]
    for key,(warning_count,buried,up,negative)in expected.items():
        uid='landsd/'+key+':0';strict_batch=P+key+'-0-four-world-support-v1-20261031';strict=take(strict_batch);paths_batch=P+key+'-0-finite-self-attachments-v1-20261031';paths=take(paths_batch);assert strict['sourceSHA256ByUid']==paths['sourceSHA256ByUid']=={u:sources[u]for u in [uid,OWNER]}
        low_batch=P+('block5-compound-lower-context-v1-20261031'if key=='235119'else key+'-compound-lower-context-v1-20261031');low=take(low_batch);assert low['sourceSHA256']==sources[uid]
        for row in strict['rows']:
            mode=row['mode'];name={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode);f=row['compoundFoundation'];assert f['completeTerrainTriangles']==f['triangles']and f['fullyBuriedTriangles']==buried and f['fullyBuriedUpwardTriangles']==up
            s=row['support'];assert s['strictContacts']>0 and len(s['unresolved'])==warning_count
            proof=take(paths_batch,mode+'.json.gz');assert [r['witness']for r in proof['rows']]==s['unresolved']
            assert all(r['hasUnrestrictedFiniteAttachment']and r['passesExistingEndpointHeight']and r['riseAboveEndpointsM']==0 and r['maximumResidualM']<=.001 and r['terminal']['contact']['peerUid']==OWNER and r['terminal']['contact']['dimension']>0 for r in proof['rows'])
            context=take(low_batch,name+'.json.gz');assert context['sourceWorldSHA256']==row['sourceWorldSHA256ByUid'][uid]and len(context['rows'])==negative
            assert all(p['groundFace']>=counts[uid]for r in context['rows']for p in r['negativeGroundPairProofs']),'Actual terrain burial is separate from original peer intersections'
        raw.append(dict(uid=uid,strictDiagnostic=strict,fullOriginalAttachmentDiagnostic=paths,completeCompoundLowFaceContext=ref(BASE/low_batch/'result.json')))
    wall=take(P+'block5-wall-skin-context-v1-20261031');assert wall['rawStrictCompoundFoundationStillFails']and all(r['allTargetsReachClearOriginalWalls']and r['clearOriginalWallFaces']==[1445,1446]and not r['groundRootCredit']for r in wall['rows'])
    shared=take(P+'block4-shared-lower-floor-context-v1-20261031');assert len(shared['rows'])==4 and all(r['allCompleteLowerFloorCoverage']and r['allWithinExistingStrictNativeInterfaceInterval']for r in shared['rows'])
    continuous=take(P+'six-original-continuous-v1-20261031');assert len(continuous['rows'])==6
    for r in continuous['rows']:
        assert r['sourceSHA256']==sources[r['uid']]
        if r['uid']!=OWNER:assert not r['continuousAffectedFaces']and not r['otherAffectedFaces']
    fallback=take(P+'numerical-ground-context-v1-20261031');assert fallback['sourceSHA256ByUid']==sources and fallback['allFourGridFallbackClear']
    pairs=take(P+'six-original-all-pairs-v1-20261031');assert pairs['sourceSHA256ByUid']==sources and pairs['completeUnorderedPairs']==15 and len(pairs['rows'])==60
    foreign=take(P+'six-original-foreign-contacts-v1-20261031');retained=[r for r in foreign['rows']if r['foreignUid']not in sources];assert len(retained)==7 and all(m['positiveContactPairs']==0 for r in retained for m in r['modes']if m['mode']!='before-basic')
    scope=take(SCOPE,'scope.json');assert not scope['touchingNativeUids']and scope['positiveAreaTerrainOverlaps']==0
    life=P+'six-original-atomic-retry-v2-20261031';atomic=take(life);assert atomic['desktopMobileBrowserPassed']and atomic['atomicCases']==7 and atomic['sourceSHA256ByUid']==sources
    report=take(life,'atomic-browser/report.json');assert report['passed']and not report['pageErrors']and {(r['width'],r['failedUid'])for r in report['cases']}=={(1280,None)}|{(390,u)for u in sources}
    for r in report['cases']:
        assert r['completeGroupEvicted']and r['baseOnlyRestoredCompleteGroup']and not r['audit']['violations']
        if r['failedUid']:assert r['failureKeptAllBasics']
    images=[];browser=P+'six-original-private-preview-v3-20261031'
    # These completed original-width reports/canvases are sealed by the atomic retry receipt.
    for width in [1280,390]:
        p=BASE/browser/str(width)/'staged-browser.json';r=take(life,external=p);assert r['passed']and not r['errors']
        for uid in sources:
            for hour in ['1500','2200']:
                p=BASE/browser/str(width)/('staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+hour+'-canvas.png');assert ref(p)['sha256']==pins[life][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(**ref(p),uid=uid,width=width,hour=hour))
    source_views=[]
    for name in ['block5-compound-wall-views-v1-20261031','236076-nonwall-peer-views-v1-20261031','234691-nonwall-peer-views-v1-20261031']:
        v=take(P+name)
        for image in v['exports']:
            p=ROOT/image['path'];assert ref(p)['sha256']==image['sha256'];refs.append(p);source_views.append(image)
    assert len(images)==24 and len(source_views)==11
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,supportByUid={u:OWNER for u in sources if u!=OWNER},identityAccepted=True,identityProofByUid=identities,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,qualifiedForLiveVerification=True,completeFourWorldFoundations=True,currentManifest=ref(manifest),leaseResources=resources,retainedNativeUids=[],imagesActuallyViewed=images,sourceJunctionImagesActuallyViewed=source_views,rawStrictInterfaceAndCompoundFailures=raw,rawCanonicalFailuresPreserved=True,strictDiagnosticFlagsRewritten=False,groundRootCreditFromEmbeddedSkins=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',modelAndEffort='Not available from tool-visible metadata; no inferred model/effort or token estimate',inspectionMethod='All24actual current desktop/mobile day/night exports inspected in two contact sheets; all11source/peer wall/floor exports inspected. Actual7case atomic frame/collision-map/failure/fallback evidence is independent of image review.',installationApproved=False,publication=False,interpretation=[
        'This is a bounded manual review of exactly six immutable government source parts, not a claim that strict-interface/maximum-roof diagnostics passed. Their complete raw failures and all original facets remain. No resolve_contact output or numerical threshold is changed.',
        'The podium lower walls/closures retain the independently accepted exact85facet four-world source-role review. Every tower is independently clear of every actual terrain facet in the complete compound check; all negative tower pairs belong to the original podium, not terrain.',
        'Every remaining tower rim witness has its exact saved positive finite source-to-original-podium attachment, within its original endpoint ceiling and1mm incidence bound. The podium foundation/role is independently qualified. Embedded skins provide no new ground root or intercomponent bridge.',
        'Block5s eight unresolved upward-cap queries belong to an original10facet wall-only skin. Exact shared nonzero edges reach ordinary-clear wall facets1445/1446 in all4streams. This is an original wall skin crossing the podium interface; it has no horizontal cap or floor to classify. No closed-solid/structural or decorative-component assertion is made.',
        'Block4s4fullyflagged upward facets coincide with the original lower podium floor layer in source/Float32 geometry. Exact full projected coverage and finite-column gaps independently reproduce that relationship in all4streams; the small literal offsets remain explicit and lie inside the existing strict native interval. A maximum-surface query also sees higher original surfaces and therefore cannot label these exact shared lower floors as soil burial. Original adjacent lower skins and partial source/peer floor-wall joins are retained as authored interfaces; no general covered-floor/ground exception is granted.',
        'The other partial source/peer wall-floor crossings are the exact same compound estate parts, with complete current raw pair accounts and source context. They do not introduce foreign contacts. All7retained foreign pairs have0positive source contacts; the complete58form terrain scope has no affected installed native or terrain overlap. The5old BASIC tower ground warnings remain safe only with all6originals activated or restored together, proven by all7atomic failure/Base-only/eviction cases.',
        'The24exports and actual desktop/mobile source picking/collision/draw/failure checks show the six unchanged originals together. These are software functional/source-placement checks; no physical-phone FPS, engineering foundation, interior route or performance improvement is certified. Full canonical publisher dryrun, exact qualified-stage lifecycle, fenced snapshot/publication and live readback remain required.'
    ])
    assert reservations.owns(lease)and ref(manifest)['sha256']==selection['manifestSHA256']
    for row in selection['rows']:assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
    save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result)
    module('prosperous_original_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-six-original-source-interface-neighbour-and-runtime-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
