"""Qualify five unchanged Kai Tak sources from exact completed current evidence."""
import argparse,json,sys,uuid
from itertools import combinations
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'five-original-qualification-v2-20261101'
UIDS=['landsd/275446:0','landsd/318697:0','landsd/318701:0','landsd/318704:0','landsd/318722:0'];NATIVE='landsd/318723:0'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists();refs=[Path(__file__)];pins={}
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    def take(batch,name='summary.json'):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    browser=P+'five-private-preview-v4-20261101';br=take(browser);resources=sorted(set(br['leaseResources'])-{'server:127.0.0.1:4177'});assert len(resources)==90
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('kai-tak-five-qualified-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    rt=P+'five-original-retained-parent-runtime-v2-20261101';selection=take(rt,'selection.json.gz');selected={r['uid']:r for r in selection['rows']};sources={u:r['sourceSHA256']for u,r in selected.items()};assert sorted(sources)==UIDS
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    for uid,row in selected.items():
        asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==sources[uid];refs.append(asset);tile=ROOT/'3d-viewer'/row['source']['tile'];assert ref(tile)['sha256']==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
    identity={}
    for uid in UIDS:
        if uid in ['landsd/318697:0','landsd/318701:0']:
            r=take(P+'five-original-identity-v1-20261101',uid.split('/')[1]+'/identity.json');assert r['passed']and not r['reasons']
        else:
            r=take(P+'three-original-identity-review-v2-20261101',uid.split('/')[1]+'-review.json');assert r['identityOnlyApproved']and r['identityReviewApproved']and not r['placementReviewed']
        assert r['sourceSHA256']==sources[uid];identity[uid]=r
    lower=take(P+'five-lower-source-review-v1-20261101');assert lower['sourceRoleAccepted']and lower['lowerSourceRoleOnly']and lower['sourceSHA256ByUid']==sources
    paths=take(P+'four-canonical-ground-paths-v1-20261101');assert paths['allCanonicalRenderingWarningsHavePaths']and paths['noRoundedWitnessMatching']and len(paths['rows'])==16 and all(r['pathsPassed']and r['sourceSHA256']==sources[r['uid']]for r in paths['rows'])
    for uid in UIDS:
        f=take(P+uid.split('/')[1].split(':')[0]+'-retained-parent-foundations-v1-20261101');assert f['establishedFoundationPolicyPassed']and len(f['rows'])==4 and all(r['establishedFoundationPolicyPassed']and r['fullyBuriedUpwardTriangles']==0 for r in f['rows'])
    metrics=take(rt,'metrics.json');assert {r['uid']for r in metrics['rows']}==set(UIDS)
    for r in metrics['rows']:assert r['sourcePreserved']and r['missingTerrain']==0 and r['maxSamplerDelta']<=.004 and all(r['budget'][k]<=metrics['profiles']['mobile'][k]for k in ['geometryBytes','residentBytes','triangles'])
    scope=P+'mall3-retained-parent-scope-v2-20261101';terrain_scope=take(scope,'scope.json');forms=take(scope,'form-obligations.json.gz');assert len(forms)==35 and terrain_scope['touchingNativeUids']==[]and terrain_scope['positiveAreaTerrainOverlaps']==0 and terrain_scope['currentNativeActors']==7061
    regression=take(P+'five-original-retained-parent-form-checks-v2-20261101');assert regression['forms']==35 and {r['uid']for r in regression['flagged']}=={'landsd/318697:0','landsd/318704:0','landsd/318722:0'}
    wide=take(P+'five-original-model-scope-v1-20261101');scopeuids={r['uid']for r in forms}
    for row in wide['rows']:
        scopeuids.update(r['uid']for r in row['nearbyNativeActors']);scopeuids.update(r['building']['uid']for r in take(P+'five-original-model-scope-v1-20261101',row['uid'].split('/')[1]+'-forms.json.gz'))
    expected={('building:'if u.startswith('landsd/')else'source-form:')+u for u in scopeuids}|{'terrain:city/data/terrain.json'}
    parent_plan=BASE/(P+'five-current-ground-parallel-plan-v1-20261101.json');assert ref(parent_plan)['sha256']==pins[browser][str(parent_plan.relative_to(ROOT))];refs.append(parent_plan);expected.update(read(parent_plan)['resources'])
    assert expected==set(resources)
    pairs=take(P+'five-original-all-pairs-v1-20261101');assert pairs['sourceSHA256ByUid']==sources and pairs['completeUnorderedPairs']==10 and len(pairs['rows'])==40
    assert {(frozenset([r['uid'],r['peerUid']]),r['mode'])for r in pairs['rows']}=={(frozenset(c),m)for c in combinations(UIDS,2)for m in ['original','literal','leftF32','balancedF32']}
    planes=take(P+'five-current-original-pair-planes-v3-20261101');assert planes['sourceSHA256ByUid']==sources and all(r['allContactsAccounted']for r in planes['rows'])
    foreign=take(P+'five-current-basic-contacts-v1-20261101');assert foreign['foreignPairs']==57 and len(foreign['rows'])==57
    positive=set()
    for r in foreign['rows']:
        assert {m['mode']for m in r['modes']}=={'before-basic','original','literal','leftF32','balancedF32'}
        if r['foreignUid']not in sources and any(m['positiveContactPairs']for m in r['modes']if m['mode']!='before-basic'):positive.add(r['foreignUid'])
    assert positive=={'landsd/318700:0','landsd/318724:0'}
    current=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url;refs.append(path);current.extend(read(path)['models'])
    assert len(current)==7061 and len({m['uid']for m in current})==7061 and not set(UIDS)&{m['uid']for m in current};native=next(m for m in current if m['uid']==NATIVE)
    nc=take(P+'five-current-native-contacts-v1-20261101');assert len(nc['rows'])==1;nr=nc['rows'][0];assert nr['rawCurrentNativeEntry']==native and nr['nativeSHA256']==native['sha256']and nr['sourceSHA256']==sources[nr['uid']]
    assert all(r['finiteContactPairs']==703 and r['positiveSurfaceContactPairs']==542 and r['areaContactPairs']==0 for r in nr['modes'])
    roles=take(P+'five-current-native-contact-roles-v1-20261101');assert len(roles['rows'])==4 and all(r['contactCount']==703 for r in roles['rows'])
    junction=take(P+'podium-stadium-junction-views-v1-20261101');assert junction['allNonemptyOriginalNativePairsDisplayed']and len(junction['exports'])==1
    deps=take(P+'five-early-dependencies-v1-20261101','dependencies.json');assert deps['candidateCount']==5 and deps['requiresAssemblyInvestigation']==0 and all(not r['blockers']for r in deps['rows'])
    assert br['desktopMobileBrowserPassed']and br['allBrowserDiagnosticsPassed']and br['sourceSHA256ByUid']==sources and br['atomicCases']==6
    atomic=take(browser,'atomic-browser/report.json');assert atomic['passed']and atomic['pageErrors']==[]and {(r['width'],r['failedUid'])for r in atomic['cases']}=={(1280,None)}|{(390,u)for u in UIDS}
    observation=BASE/(P+'private-browser-visual-observations-v1-20261101')/'ROOT-VISUAL-OBSERVATIONS.json';obs=read(observation);refs.append(observation);assert obs['imagesActuallyInspected']==24 and len(obs['contactSheetsActuallyInspected'])==8 and len(obs['sourceNativeJunctionImagesActuallyInspected'])==1
    for record in obs['contactSheetsActuallyInspected']+obs['sourceNativeJunctionImagesActuallyInspected']+obs['images']:
        path=ROOT/record['path'];assert ref(path)['sha256']==record['sha256'];refs.append(path)
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']and len(report['retainedNativeOwnViews'])==2
        views=[r for r in report['views']if r.get('file')];assert {(r['uid'],r['time'])for r in views}=={(u,h)for u in UIDS for h in ['15:00','22:00']}
        for r in views:assert r['sourceSHA256']==sources[r['uid']]and r['active']and r['fullyFramed']and r['pick']==r['collision']==r['uid']and r['fallbackFaces']==0
    terrain=take(P+'mall3-retained-parent-inset-v2-20261101');asset=ROOT/terrain['candidate']['path'];assert ref(asset)==terrain['candidate'];refs.append(asset)
    result=dict(uids=UIDS,sourceSHA256ByUid=sources,supportByUid={},identityAccepted=True,identityProofByUid=identity,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,qualifiedForLiveVerification=True,completeFourWorldFoundations=True,currentManifest=ref(manifest),leaseResources=resources,retainedNativeUids=[NATIVE],unchangedRetainedNativeEntry=native,terrainCandidate=terrain['candidate'],imagesActuallyViewed=obs['images'],sourceJunctionImagesActuallyViewed=obs['sourceNativeJunctionImagesActuallyInspected'],rawCanonicalFailuresPreserved=True,strictDiagnosticFlagsRewritten=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',modelAndEffort='Unknown from tool-visible metadata; not inferred',installationApproved=False,publication=False,interpretation=[
        'Five exact original government sources, fixed1x/HKPD and original graphs/bytes. Two ordinary identities and three bounded exact-source identity reviews retain all raw extent/overlap warnings; faithful component ports, not whole-landmark reconstruction.',
        'Complete four-world foundation and lower-source records account every below-grade sample and facet. Twenty-five downward source skins and three zero-area primitives are preserved. Exact actual canonical warning paths use existing endpoint/incidence bounds and real drawn-ground roots. No artificial support, geometry edit, dropped warning or raised threshold.',
        'All ten source pairs/four worlds retain complete raw finite contacts and exact represented-plane accounts. Source podium/deck and arena/mall lower surfaces meet at original interfaces; line crossings and coplanar source skins are not new standalone rejection gates. Current images show the intact original ensemble; no structural or interior-route claim.',
        'Complete57foreign BASIC before/after pairs retain their actual contacts. HealthWellness318700 projected overlap decreases870.5949to690.7735m2; Dorsett318724 has49line contacts and0area contacts versus39line/20area before, with13.0656m2projected source overhang. More triangles can increase counts; counts alone do not prove a new physical defect. Both retained coarse bodies remain visible and retain their own collision state. No extra suppression or neighbouring source-field edit.',
        'Only three selected ownUID BASIC counterparts carry terrain regression flags; atomic ownUID replacement resolves those counterparts. No installed detailed actor touches the changed terrain. Full wider90resource source/terrain scope is bound independently of the35terrain forms.',
        'Stadium318723 original5178face asset, metadata, support declarations and flags remain unchanged. All703finite source/native contacts, including516transverse crossings, remain explicit. Both opposite junction perspectives locate these at the original lower ring/deck; original source plane/role records and retained own views are consistent. No native dependency removal or arbitrary collision exemption.',
        'All24source/native exports were actually inspected in eight sheets and one complete native junction diagram inspected. Desktop/mobile loading, picking, collision, deny/retry, Base-only restoration, complete-group eviction and zero partial-group/stale-map assertions pass. No physical-phone performance claim. Full exact qualified-stage dependency/publisher and installedHTTP/readback checks remain required.'
    ])
    for batch,proofs in pins.items():
        for name,sha in proofs.items():assert digest((ROOT/name).read_bytes())==sha,name
    assert reservations.owns(lease)and ref(manifest)['sha256']==selection['manifestSHA256'];save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);module('kai_tak_five_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-five-original-source-placement-neighbour-and-runtime-qualification',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
