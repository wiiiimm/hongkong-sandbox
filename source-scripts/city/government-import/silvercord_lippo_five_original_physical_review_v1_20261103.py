"""Qualify the exact five unchanged originals and retained Lippo support interface.

Consumes completed source-bound calculations; never edits geometry, thresholds,
terrain or public metadata. Browser/source publication qualification is separate.
"""
import sys
import uuid
from itertools import combinations
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_candidate_atomic_catalogue_contract_v1_20261103 import verify as tested_metadata

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-five-original-physical-review-v1-20261103'
LOCAL = HERE/'local'/BATCH
RUNTIME = 'government-xl-silvercord-lippo-five-original-floor-runtime-v1-20261103'
ATTR = 'government-xl-silvercord-lippo-five-original-attributes-v2-20261103'
PREFIX = 'government-xl-silvercord-lippo-'
OWNER = 'landsd/239465:0'
MODES = {'original','literal','leftF32','balancedF32'}
GROUND = {'landsd/233997:0','landsd/231645:0'}


def four(rows):
    aliases = {'explicitLeftF32':'leftF32','explicitBalancedF32':'balancedF32',
               'left':'leftF32','balanced':'balancedF32'}
    result = {aliases.get(r['mode'],r['mode']):r for r in rows}
    assert len(rows) == len(result) == 4 and set(result) == MODES
    return result


class Evidence:
    def __init__(self):
        self.receipts, self.pins = {}, {}
        self.refs = [Path(__file__), HERE/'original_candidate_atomic_catalogue_contract_v1_20261103.py']
        self.hashes = {}

    def pin(self, path, sha=None):
        raw = path.read_bytes()
        actual = digest(raw)
        assert sha is None or sha == actual, 'Evidence bytes changed: '+str(path)
        assert self.hashes.setdefault(path, actual) == actual
        self.refs.append(path)
        return raw

    def file(self, path, sha=None):
        self.pin(path,sha)
        return read(path)

    def take(self, batch, filename='summary.json'):
        if batch not in self.pins:
            receipt, self.pins[batch] = authenticate(BASE/batch)
            self.receipts[batch] = receipt
            self.refs.append(BASE/batch/'result.json')
        path = BASE/batch/filename
        return self.file(path,self.pins[batch][str(path.relative_to(ROOT))])

    def finish(self):
        for path, sha in self.hashes.items():
            assert digest(path.read_bytes()) == sha, 'Input changed during review: '+str(path)


def assemble(e):
    manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
    manifest = e.file(manifest_path)
    manifest_sha = e.hashes[manifest_path]
    selection = e.take(RUNTIME,'selection.json.gz')
    assert selection['manifestSHA256'] == manifest_sha
    entries = {r['uid']:r['candidate']['entry'] for r in selection['rows']}
    source = {r['uid']:r['sourceSHA256'] for r in selection['rows']}
    assert len(source) == len(selection['rows']) == 5 and GROUND < set(source)
    triangles = {r['uid']:r['triangles'] for r in selection['rows']}
    attrs = e.take(ATTR,'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and attrs['exactCurrentRuntimeArraysVerified']
    assert {r['uid']:r['sourceSHA256'] for r in attrs['rows']} == source
    for path, sha in attrs['inputHashes'].items():
        e.pin(ROOT/path,sha)
    for row in selection['rows']:
        e.pin(ROOT/row['candidate']['path'],row['sourceSHA256'])
        tile = e.file(ROOT/'3d-viewer'/row['source']['tile'],row['source']['tileSHA256'])
        assert [b for b in tile['buildings'] if b['uid'] == row['uid']] == [row['source']['building']]
    proposal = e.take(PREFIX+'private-dependency-proposal-v1-20261103')
    supports = proposal['supportByUid']
    assert proposal['sourceSHA256ByUid'] == source and set(source)-set(supports) == GROUND
    tested = e.file(HERE/'local'/ (PREFIX+'private-six-part-browser-v4-20261103') /'catalogue.json')
    assert tested_metadata(tested['models'],source,supports,entries,GROUND)
    # The old identity is retained verbatim inside the fresh current-route binding.
    identity = {}
    for uid in source:
        batch = (PREFIX+'current-identity-binding-v1-20261103' if uid in GROUND else
                 PREFIX+'three-tower-companions-prepared-v1-20261103-identity')
        proof = e.take(batch,uid.split('/')[1]+'/identity.json')
        assert proof['sourceSHA256'] == source[uid] and proof['passed'] and not proof['reasons']
        assert proof['exactRouteManifestSHA256'] == manifest_sha
        assert all(proof['proof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
        identity[uid] = proof['proof']
    # Every source pair is either strictly separated over complete POSITION bounds,
    # or retains its exhaustive finite proof and four separately bound worlds.
    pairs = e.take(PREFIX+'five-complete-original-pairs-v1-20261103')
    assert pairs['sourceSHA256ByUid'] == source and pairs['rawContactsPreserved']
    assert {frozenset(r['uids']) for r in pairs['rows']} == {frozenset(p) for p in combinations(source,2)}
    assert len(pairs['rows']) == pairs['completeUnorderedPairs'] == 10
    world_hashes = {uid:{} for uid in source}
    for pair in pairs['rows']:
        if pair['method'] == 'strict-complete-four-world-POSITION-bounds-separation':
            assert max(pair['strictAxisGapsM']) > 0
            continue
        for mode,r in four(pair['modes']).items():
            assert set(r['sourceWorldSHA256ByUid']) == set(pair['uids'])
            for uid, sha in r['sourceWorldSHA256ByUid'].items():
                assert world_hashes[uid].setdefault(mode,sha) == sha
            ref = r['originalProof']; proof = e.file(ROOT/ref['path'],ref['sha256'])
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted'] == 0
            assert len(proof['contacts']) == r['finiteContactPairs']
    assert all(set(hashes) == MODES for hashes in world_hashes.values())
    junction = e.take(PREFIX+'original-junction-review-v1-20261103')
    assert junction['sourceSHA256ByUid'] == {u:source[u] for u in GROUND}
    assert junction['exactSourcePairJunctionInterpretationReviewed'] and junction['originalAreaContacts'] == 0
    assert junction['sourceFacesOmitted'] == junction['sourceGeometryChanges'] == junction['sourcePoseChanges'] == 0
    skins = e.take(PREFIX+'lower-skin-role-review-v1-20261103','ROOT-LOWER-SOURCE-REVIEW.json')
    assert skins['sourceRoleAccepted'] and skins['sourceSHA256ByUid'] == {u:source[u] for u in GROUND}
    assert not skins['groundRootCredit'] and not skins['interComponentBridgeCredit']
    ground_role = e.take('government-xl-silvercord-bounded-ground-role-review-v1-20261103','ROOT-GROUND-ROLE-REVIEW.json')
    assert ground_role['sourceGroundRoleAccepted'] and ground_role['rawCanonicalFailuresPreserved']
    assert ground_role['rawOrdinaryFoundationPolicyPassed'] is False
    for mode,row in four(ground_role['rows']).items():
        assert row['sourceWorldSHA256'] == world_hashes['landsd/233997:0'][mode]
        assert row['ordinaryFoundationPolicyPassed'] is False and row['sourceGroundRoleAccepted']
    lippo = e.take(PREFIX+'complete-floor-foundations-v1-20261103-231645-0')
    assert lippo['establishedFoundationPolicyPassed']
    for r in four(lippo['rows']).values():
        assert r['completeTerrainTriangles'] == r['triangles'] == triangles['landsd/231645:0']
        assert r['fullyBuriedUpwardTriangles'] == 0 and r['fullyBuriedAreaFraction'] <= .001
    for mode in MODES:
        below = e.take(PREFIX+'complete-floor-roles-v1-20261103-below-231645-0',mode+'.json.gz')
        assert below['sourceWorldSHA256'] == world_hashes['landsd/231645:0'][mode]
        assert len(below['negativeWallFaces']) == len(below['allWallCapPaths']) == 234
        assert not below['wallsWithoutSharedEdgeClearCapPath']
        assert below['negativeNonWallFaces'] == [8231,8232,8233]
    raw_support = {}
    for uid in supports:
        token = uid.split('/')[1].replace(':','-')
        soil = e.take(PREFIX+token+'-complete-private-soil-foundations-v1-20261103')
        assert soil['establishedFoundationPolicyPassed']
        for r in four(soil['rows']).values():
            assert r['triangles'] == r['completeTerrainTriangles'] == triangles[uid]
            assert r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0
        support = e.take(PREFIX+'five-original-'+token+'-support-v1-20261103')
        assert support['sourceSHA256ByUid'] == {u:source[u] for u in [uid,supports[uid]]}
        for mode,r in four(support['rows']).items():
            assert r['sourceWorldSHA256ByUid'] == {u:world_hashes[u][mode] for u in [uid,supports[uid]]}
            f = r['compoundFoundation']
            assert f['triangles'] == f['completeTerrainTriangles'] == triangles[uid]
            assert f['fullyBuriedTriangles'] == f['fullyBuriedUpwardTriangles'] == 0
            assert r['support']['strictContacts'] > 0 and r['support']['strictLowRim']['missing'] == 0
        raw_support[uid] = support
        context = ('government-xl-langham' if uid == 'landsd/237843:0' else 'government-xl-silvercord-'+token)
        context += '-complete-original-podium-lower-context-v1-20261103'
        for mode in MODES:
            filename = {'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)+'.json.gz'
            c = e.take(context,filename); caps = c['completeCompoundClearanceCapPaths']
            assert c['sourceWorldSHA256'] == world_hashes[uid][mode]
            assert c['peerWorldSHA256'] == world_hashes[supports[uid]][mode]
            assert c['completeSourceFaces'] == triangles[uid]
            assert not caps['negativeNonWallFaces']
            if caps['negativeSourceFaces']:
                assert caps['allAffectedHavePaths'] and len(caps['paths']) == len(caps['negativeSourceFaces'])
            else:
                assert not caps['paths']
    langham = e.take('government-xl-langham-original-finite-peer-attachments-v1-20261103')
    assert langham['sourceSHA256ByUid'] == {u:source[u] for u in ['landsd/237843:0','landsd/231645:0']}
    for r in four(langham['rows']).values():
        assert r['witnesses'] == r['finiteAttachmentPaths'] == r['pathsWithinEndpointHeight'] == 8 and r['disconnected'] == 0
    tower2 = e.take(PREFIX+'five-original-238659-0-strict-paths-v1-20261103')
    for r in four(tower2['rows']).values():
        assert r['targets'] == r['finiteAttachmentPaths'] == 2 and r['aboveExistingEndpointCeiling'] == r['disconnected'] == 0
    assert all(r['passed'] and not r['support']['unresolved'] for r in raw_support['landsd/239032:0']['rows'])
    owner_probe = e.take('government-xl-lippo-current-native-podium-migration-probe-v1-20261103')
    owner_paths = e.take('government-xl-lippo-native-support-strict-paths-v1-20261103')
    owner_caps = e.take('government-xl-lippo-native-compound-clearance-v1-20261103')
    assert owner_paths['allWarningsHaveExistingStrictRootPaths'] and owner_paths['newRoots'] == owner_paths['intercomponentJoins'] == 0
    for r in four(owner_probe['rows']).values():
        assert r['completeFaces'] == 3597 and r['fullyBuried'] == r['upwardBuried'] == 0 and r['strictContacts'] == 40
    for r in four(owner_paths['rows']).values():
        assert r['rawUnresolved'] == r['passingWithExistingEndpointRetry'] == 178 and r['remaining'] == 0
    for r in four(owner_caps['rows']).values():
        assert r['completeSourceFaces'] == 3597 and r['allAffectedHaveClearCapPaths']
        assert not r['negativeNonWallFaces'] and not r['unresolvedSharedEdgeWallFaces']
    # Exhaustive current source/native nominations; only the exact owner interface
    # may be accepted. Every other nominated native has zero finite contacts.
    scope = e.take(PREFIX+'five-original-collision-scope-v1-20261103')
    assert scope['currentManifestSHA256'] == manifest_sha and set(scope['uids']) == set(source)
    expected = {(r['uid'],n['uid']) for r in scope['rows'] for n in r['nearbyNativeActors']}
    assert all(r['currentNativeActorsChecked'] == 7101 for r in scope['rows'])
    native_rows = []
    for batch in [PREFIX+'current-native-contacts-v1-20261103', PREFIX+'three-companion-neighbours-v1-20261103-native']:
        native_rows.extend(e.take(batch)['rows'])
    assert len(native_rows) == len(expected) and {(r['uid'],r['nativeUid']) for r in native_rows} == expected
    accepted = []
    for r in native_rows:
        assert r['sourceSHA256'] == source[r['uid']]
        if (r['uid'],r['nativeUid']) == ('landsd/231645:0',OWNER):
            assert r['nativeSHA256'] == proposal['installedSupportUpdate']['ownerSHA256']
            accepted.append(dict(uid=r['uid'],nativeUid=OWNER,allFourWorlds=[
                dict(mode=m['mode'],sourceSHA256=r['sourceSHA256'],nativeSHA256=r['nativeSHA256'],
                     contactCount=m['finiteContactPairs']) for m in four(r['modes']).values()]))
        else:
            assert all(m['finiteContactPairs'] == m['positiveSurfaceContactPairs'] == m['areaContactPairs'] == 0 for m in four(r['modes']).values())
    assert len(accepted) == 1
    for batch in [PREFIX+'current-foreign-basic-contacts-v1-20261103', PREFIX+'three-companion-neighbours-v1-20261103-basics']:
        for r in e.take(batch)['rows']:
            assert r['uid'] in source
            if r['foreignUid'] not in source:
                assert all(m['positiveContactPairs'] == 0 and m['projectedOverlapAreaM2'] == 0
                           for m in r['modes'] if m['mode'] in MODES)
    fullscope = e.take(PREFIX+'full-current-parent-scope-v3-20261103')
    forms = e.take(PREFIX+'complete-floor-full-form-regression-v4-20261103')
    native = e.take(PREFIX+'all-native-terrain-context-v1-20261103')
    changed = e.take(PREFIX+'changed-native-check-v1-20261103')
    assert fullscope['currentManifestSHA256'] == native['currentManifestSHA256'] == manifest_sha
    assert forms['forms'] == fullscope['basicFormsInFullParentScope'] == 5408 and forms['ordinaryFlagged'] == 0
    assert forms['requiredFullNativeRegressions'] == len(fullscope['affectedNativeUids']) == len(native['allRequiredNativeUids']) == 1228
    assert set(fullscope['affectedNativeUids']) == set(native['allRequiredNativeUids'])
    assert native['exactUnchangedNativeContexts'] == 1227 and native['remainingFullMeshUids'] == [OWNER]
    assert changed['changedNativeFullMeshPassed'] and len(changed['changedNativeRows']) == 1
    row = changed['changedNativeRows'][0]
    assert row['uid'] == OWNER and row['passed'] and row['terrain']['newlyWhollyBuried'] == row['terrain']['newlyUpwardWhollyBuried'] == 0
    assert fullscope['allRegisteredNonNativeSupportsAccounted'] == 11
    # Current installed count is independently verified after June; the scope's
    # historical provisional wording is not installation credit for those actors.
    current = e.take('government-xl-after-june-current-native-bounds-reused-v1-20261103')
    assert current['currentManifestSHA256'] == manifest_sha and current['currentNativeActors'] == 7101
    pointer = e.file(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    assert pointer['snapshotId'] == current['snapshotId']
    terrain = e.take(PREFIX+'two-descriptor-terrain-dry-run-v2-20261103')
    assert terrain['canonicalTwoDescriptorTerrainStagingPassed'] and terrain['allOrdinaryTerrainGuardsPreserved']
    assert terrain['exactEffectiveMembers'] == 16 and terrain['finiteEdges'] == 22
    models = []
    for url in manifest['officialModelCatalogues']:
        models.extend(e.file(ROOT/'3d-viewer'/url)['models'])
    assert len(models) == len({m['uid'] for m in models}) == 7101 and not set(source)&{m['uid'] for m in models}
    update = proposal['installedSupportUpdate']
    assert next(m for m in models if m['uid'] == OWNER) == update['beforeEntry'] == owner_probe['installedTowerEntry']
    before = e.file(ROOT/'3d-viewer'/update['url'],update['beforeSHA256'])
    after = e.file(ROOT/update['source'],update['sha256'])
    from silvercord_lippo_private_six_part_browser_v4_20261103 import exact_owner_after
    assert exact_owner_after(before,after,update)
    retained = fullscope['affectedNativeUids']
    return dict(uids=sorted(source),reviewer='Codex ROOT',sourceSHA256ByUid=source,
        requiredOriginalAssembly=source,supportByUid=supports,groundOwnerUids=sorted(GROUND),
        identityAccepted=True,identityProofByUid=identity,sourceSpecificPhysicalInterpretationAccepted=True,
        completeNeighbourInterpretationAccepted=True,acceptedOriginalNativeInterfaces=accepted,
        unresolvedExternalBasicContacts=[],rawPhysicalFailuresPreserved=True,
        ordinarySilvercordFoundationPolicyPassed=False,sourceGroundRoleReviewJobId=e.receipts['government-xl-silvercord-bounded-ground-role-review-v1-20261103']['jobId'],
        fullTerrainForms=5408,fullTerrainNativeActors=1228,exactUnchangedNativeTerrainContexts=1227,
        retainedNativeUids=retained,registeredBasicSupportsPreserved=11,installedSupportUpdate=update,
        currentManifest=dict(path=str(manifest_path.relative_to(ROOT)),sha256=manifest_sha),
        rawSupportByUid=raw_support,sourceWorldSHA256ByUidAndMode=world_hashes,
        sourceGeometryChanges=0,sourcePoseChanges=0,installedMetadataChanges=0,
        sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,
        executorModelAndEffort='Not verified from available runtime metadata',
        visualAcceptance=False,installationApproved=False,publication=False,
        basis=[
            'Accept only these five complete immutable original sources, their exact current identities and three original native-podium dependencies. Source bytes, surveyed fixed1x placement, current complete forms and all production attribute inputs remain exact. No architectural modelling, simplification, support invention, face omission or numerical limit change.',
            'Silvercord retains its raw ordinary burial failure. The bounded source-ground review exhaustively covers its lower walls and original downward skins; all real roof/upper walking surfaces remain subject to ordinary guards. Lippo passes the ordinary foundation fraction and retains its separately reviewed lower skins. Neither review claims exact as-built basement purpose or structural engineering certification.',
            'Langham and Silvercord towers retain complete soil coverage, zero wholly/upward compound burials, authentic positive podium contacts and complete original-wall clear-cap paths. Langham eight and Tower2 two raw interface warnings have exact finite original-surface attachment paths under unchanged endpoint/incidence limits. Tower1 has no remaining direct interface warning. These are source-authored interleaved base walls beneath their own platform, not excused floating, horizontal-floor or unrelated-building intersections.',
            'The retained Lippo tower keeps every original byte and all metadata except the separately proposed supportDependencies change. Its forty strict contacts and all178 raw warning paths are independently represented in four worlds; every complete compound negative is an original wall with clear cap. No new root or component join is supplied. Native support failure must return it to BASIC as already separately tested; publication remains fenced.',
            'All ten new-source pairs, every current native nomination and foreign BASIC obligation remain accounted. The reviewed adjoining-podium junction and exact retained-owner base interface are source-specific; unrelated finite positive/area contacts are zero. No blanket collision exception is introduced.',
            'The entire terrain obligation remains5408forms/1228nativeactors:1227exact unchanged rendered face multisets plus the actual complete3597face retained-owner mesh check. All11registered BASIC support contracts stay intact. Thirty-one target entries correctly name29retained actors and the two ground-owning podiums. Three supported auxiliary towers are not terrain owners.',
            'This physical review does not publish, install or grant browser acceptance. Require separately authenticated complete desktop/mobile and per-peer atomic/owner exports, exact tested catalogue and two descriptors, guarded publisher/live verification and independent whole521readback before installed credit.'
        ])


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    evidence = Evidence()
    review = assemble(evidence)
    evidence.finish()
    assert reservations.owns(lease)
    save(BASE/BATCH/'ROOT-PHYSICAL-REVIEW.json',review)
    save(BASE/BATCH/'summary.json',dict(uids=review['uids'],sourceSHA256ByUid=review['sourceSHA256ByUid'],
         sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,
         rawPhysicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,
         installationApproved=False,publication=False))
    module('silvercord_five_original_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'bounded-complete-five-original-and-retained-owner-physical-review',list(dict.fromkeys(evidence.refs)),
        read(BASE/BATCH/'summary.json'))


if __name__ == '__main__':
    if '--preflight' in sys.argv:
        evidence = Evidence(); review = assemble(evidence); evidence.finish()
        print(dict(physicalReviewPreflightPassed=True,models=len(review['uids']),forms=5408,natives=1228,publication=False),flush=True)
    elif '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        claim = reservations.claim('silvercord-five-original-physical-review-'+str(uuid.uuid4()),
            ['building:landsd/'+u+':0' for u in ['233997','231645','237843','238659','239032','239465']]
            + ['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
