"""Qualify exactly twenty immutable originals for guarded live verification."""
import argparse,sys,uuid
from itertools import combinations
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'twenty-original-qualification-v1-20261101';OWNER='landsd/76610:0';NATIVE='landsd/304700:0'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json';out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json',external=None):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=external if external is not None else BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    scope=P+'fourteen-authentic-tin-scope-v1-20261101';forms=take(scope,'form-obligations.json.gz');domain=take(scope,'scope.json');assert len(forms)==103 and domain['touchingNativeUids']==[NATIVE]and domain['positiveAreaTerrainOverlaps']==0
    resources=sorted({('building:'if r['uid'].startswith('landsd/')else'source-form:')+r['uid']for r in forms}|{'terrain:city/data/terrain.json'})
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-twenty-qualified-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    rt=P+'twenty-authentic-tin-runtime-v1-20261101';selection=take(rt,'selection.json.gz');selected={r['uid']:r for r in selection['rows']};sources={u:r['sourceSHA256']for u,r in selected.items()};assert len(sources)==20 and set(sources)<={f['uid']for f in forms}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    for uid,row in selected.items():
        asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==sources[uid];refs.append(asset);tile=ROOT/'3d-viewer'/row['source']['tile'];assert ref(tile)['sha256']==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
    identities={};old_identity=take(P+'fourteen-identity-review-v1-20261101');assert old_identity['identityOnlyApproved']and old_identity['identityAccepted']
    for r in old_identity['rows']:
        assert r['sourceSHA256']==sources[r['uid']]and r['identityOnlyApproved'];identities[r['uid']]=r
    for uid in ['landsd/10198:0',*['landsd/'+k+':0'for k in ['68540','252555','252556','252558']]]:
        batch=P+('jubilee10198-identity-v1-20261101'if uid=='landsd/10198:0'else'retained-five-original-identity-v1-20261101');d=take(batch,uid.split('/')[1]+'/identity.json');assert d['passed']and not d['reasons']and d['sourceSHA256']==sources[uid];identities[uid]=d
    d=take(P+'88780-original-identity-review-v1-20261101');assert d['identityOnlyApproved']and d['identityAccepted']and d['sourceSHA256ByUid']=={'landsd/88780:0':sources['landsd/88780:0']};identities['landsd/88780:0']=d['rows'][0];assert set(identities)==set(sources)
    context=take(P+'current-twenty-assembly-context-v1-20261101');assert context['sourceSHA256ByUid']==sources and context['allFifteenOriginalPeerSupportRoutesBound']and context['allTwentyCurrentTerrainContextsAccounted']and len(context['sourceAttachments'])==15 and len(context['actualGroundAttachments'])==2
    by_world={r['uid']:r['sourceWorldSHA256ByMode']for r in context['currentGroundContexts']};assert set(by_world)==set(sources)
    pairs=take(P+'twenty-all-pairs-reused-v1-20261101');assert pairs['sourceSHA256ByUid']==sources and pairs['completeUnorderedPairs']==190 and pairs['coordinateModes']==4 and len(pairs['rows'])==760
    assert {(frozenset([r['uid'],r['peerUid']]),r['mode'])for r in pairs['rows']}=={(frozenset(c),m)for c in combinations(sources,2)for m in ['original','literal','leftF32','balancedF32']}
    for r in pairs['rows']:assert r['sourceWorldSHA256ByUid']=={u:by_world[u][r['mode']]for u in [r['uid'],r['peerUid']]}
    for name in ['two-lower-source-role-review-v1-20261101','two-new-lower-role-review-v1-20261101','88780-lower-wall-role-review-v1-20261101']:
        d=take(P+name);assert d['sourceRoleAccepted']and d['lowerSourceRoleOnly']
    metrics=take(rt,'metrics.json');root=next(r for r in metrics['rows']if r['uid']=='landsd/304541:0');assert root['sourcePreserved']and root['missingTerrain']==0 and root['minSurfaceGap']>=-.5 and root['minLowGap']<=.1 and root['maxLowGap']<=1 and root['maxSamplerDelta']<=.004 and root['lowRimChecks']>0
    assert {r['uid']for r in metrics['rows']}==set(sources)and all(r['sourcePreserved']and r['missingTerrain']==0 and r['maxSamplerDelta']<=.004 for r in metrics['rows'])
    # All five formerly retained problem forms and10198 now use their own originals.
    before=take(P+'owner64-foreign-current-rebind-v1-20261101');assert before['sourceSHA256']==sources[OWNER]and before['newFinitePairComputations']==0
    assert all(r['foreignUid']in sources for r in before['retainedPositiveOriginalPairs'])
    foreign=take(P+'retained-five-model-only-foreign-contacts-v1-20261101')
    assert all(not m['positiveContactPairs']for r in foreign['rows']if r['foreignUid']not in sources for m in r['modes']if m['mode']!='before-basic')
    # Native body, its dependencies and its prior flags remain exactly unchanged.
    current=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']];assert len(current)==7041 and not set(sources)&{m['uid']for m in current};native=next(m for m in current if m['uid']==NATIVE);assert native['sha256']=='156978e13029589e7b09cb184991c2a6094840bc41d0da3fffbe34e29342432b'
    native_checks=[]
    for batch,field in [('government-xl-after-villa-premiere-76610-foreign-contacts-v1-20261031','independentlyMeasuredOverlappingNativePairs'),(P+'304541-current-native-contacts-v1-20261101','rows'),(P+'jubilee10198-native-contacts-v1-20261101','rows'),(P+'retained-five-overlapping-native-contacts-v1-20261101','rows')]:
        data=take(batch)
        for r in data[field]:
            assert r['sourceSHA256']==sources[r['uid']]and r['nativeUid']==NATIVE and r['nativeSHA256']==native['sha256']and r['rawCurrentNativeEntry']==native and {m['mode']for m in r['modes']}=={'original','literal','leftF32','balancedF32'};native_checks.append(r)
        for name,sha in pins[batch].items():
            if name.endswith(('.py','.mjs','.js')):assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    assert {r['uid']for r in native_checks}=={OWNER,'landsd/304541:0','landsd/10198:0',*['landsd/'+k+':0'for k in ['68540','88780','252555','252558']]}
    assert all(m['finiteContactPairs']==0 for r in native_checks if r['uid']not in {'landsd/304541:0','landsd/10198:0'}for m in r['modes'])
    regression=take(P+'fourteen-authentic-tin-native-regressions-v1-20261101');assert regression['nativeResolved']==[NATIVE]and len(regression['nativeRows'])==1 and regression['nativeRows'][0]['passed']and regression['nativeRows'][0]['terrain']['newlyWhollyBuried']==regression['nativeRows'][0]['terrain']['newlyUpwardWhollyBuried']==0 and all(r['uid']in sources for r in regression['basicFlags'])
    patch=take(P+'fourteen-authentic-tin-v1-20261101');asset=ROOT/patch['candidate']['path'];assert ref(asset)==patch['candidate'];refs.append(asset);assert pins[P+'fourteen-authentic-tin-native-regressions-v1-20261101'][str(asset.relative_to(ROOT))]==patch['candidate']['sha256']
    proposal=take(P+'twenty-dependency-preflight-v1-20261101');assert proposal['candidateCount']==20 and proposal['requiresAssemblyInvestigation']==0 and proposal['sourceSHA256ByUid']==sources;support=proposal['proposedSupportByUid'];assert len(support)==17
    browser=P+'twenty-private-preview-v1-20261101';br=take(browser);assert br['desktopMobileBrowserPassed']and br['atomicCases']==21 and br['sourceSHA256ByUid']==sources;atomic=take(browser,'atomic-browser/report.json');assert atomic['passed']and len(atomic['cases'])==21 and not atomic['pageErrors'];images=[]
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        for uid in sources|{NATIVE:None}:
            for hour in ['1500','2200']:
                stem=uid.replace('/','-').replace(':','-');name=f'staged-retained-own-{stem}-{width}-{hour}.png'if uid==NATIVE else f'staged-{stem}-{width}-{hour}-canvas.png';path=BASE/browser/str(width)/name;assert ref(path)['sha256']==pins[browser][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(**ref(path),uid=uid,width=width,hour=hour))
    follow=P+'10198-desktop-opposite-view-v2-20261101';assert take(follow)['desktopFollowupPassed']
    for hour in ['1500','2200']:
        path=BASE/follow/'1280'/f'staged-landsd-10198-0-1280-{hour}-canvas.png';assert ref(path)['sha256']==pins[follow][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(**ref(path),uid='landsd/10198:0',width=1280,hour=hour,supplementaryOppositeCamera=True))
    assert len(images)==86
    junction_images=[]
    for name in ['304541-native-junction-views-v1-20261101','jubilee10198-native-junction-views-v1-20261101','retained-five-original-junction-views-v1-20261101']:
        batch=P+name;take(batch)
        for path in sorted((BASE/batch).glob('*.png')):assert ref(path)['sha256']==pins[batch][str(path.relative_to(ROOT))];refs.append(path);junction_images.append(ref(path))
    assert len(junction_images)==7
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,supportByUid=support,identityAccepted=True,identityProofByUid=identities,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,qualifiedForLiveVerification=True,completeFourWorldFoundations=True,currentManifest=ref(manifest),leaseResources=resources,retainedNativeUids=[NATIVE],unchangedRetainedNativeEntry=native,imagesActuallyViewed=images,sourceJunctionImagesActuallyViewed=junction_images,rawCanonicalFailuresPreserved=True,strictDiagnosticFlagsRewritten=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',modelAndEffort='Unknown from tool-visible metadata; not inferred',installationApproved=False,publication=False,inspectionMethod='80current candidate exports inspected in4contact sheets;4native own-view exports individually;2opposite10198desktop exports individually. Five new source/source junction exports and two prior source/native junction exports inspected. Prior exact identity/lower-source views retain their bounded records. No per-building AI architecture generation.',interpretation=[
        'Exactly twenty complete government originals at fixed1x/HKPD pose, source bytes/graphs unchanged. Identity exceptions identify the supplied units and preserve all raw projection warnings; no whole landmark or complete architecture claim.',
        'Current assembly context independently binds all20ground contexts,15peer attachment routes and2actual ground routes. Four legacy/new lower-role records plus the single88780wall account for every negative current-ground face. No original diagnostic flag, root, endpoint bound or1mm incidence criterion is rewritten.',
        '252556/252558 owner-only literal routes retain failures, but all40/24raw witnesses reach actual saved drawn-ground intersections through original source incidence within existing endpoint limits. This resolves placement for source lower bodies via real terrain, without fabricating links to the podium. Their below-grade walls/downward closure records remain exact and source-specific.',
        'All190sourcepairs across4worlds and full current scopes are accounted. New5parts contact only the source podium; authored original floor/wall/roof junctions, including coplanar lower interfaces, retain all raw contacts. Same source dataset/actual pose and source-role evidence identify these component interfaces; no legal-ownership or structural-engineering inference is needed.',
        'The five coarse counterparts with positive owner contacts now each use their own exact original UID. Along with10198, this replaces every previously flagged BASIC form through normal ownUID activation, with no extra suppression or changed BASIC source fields. All remaining foreignBASIC contacts are zero; all20activate or restore together as proven by all21atomic cases.',
        'Installed304700keeps its exact33943face asset, original entry/dependencies/flags, and prior source terrain semantics. Unchanged terrain has no newly wholly/upward-wholly buried native facets. Source304541/10198 retain236/10finite native junction contacts in all4worlds at the inspected authored wall/roof interfaces; other nominated source/native pairs are zero. Functional collision/picking and retained own views pass; no geometry adjustment or native support removal.',
        'All86day/night/own/followup exports and current desktop/mobile functional checks show the original sources with current surrounding actors. Tight original10198desktop crop is supplemented by an opposite source/parent view. This qualifies a faithful source port, not physical-phone FPS, engineering, interior routes or future optimisation. Full canonical publisher dryrun, qualified-stage/live checks, unique snapshot and fenced publication/readback remain required.'
    ])
    assert reservations.owns(lease)and ref(manifest)['sha256']==selection['manifestSHA256'];save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);module('palazzo_twenty_original_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-twenty-original-source-placement-neighbour-and-runtime-qualification',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
