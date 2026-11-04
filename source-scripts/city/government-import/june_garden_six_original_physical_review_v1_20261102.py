"""Bound exact original source roles and actual model-body neighbours; no publish.

This is a source-specific evidence interpretation. Raw scalar/interface failures
remain recorded. No strict root, gap, endpoint, incidence, source pose or geometry
limit changes. Terrain-wide retained-actor and full browser review are separate.
"""
import argparse, sys, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT/'docs/astra-city/government-import'
P = 'landsd/227380:0'; SMALL = 'landsd/264492:0'
TOWERS = ['landsd/264489:0','landsd/264491:0','landsd/264493:0','landsd/264495:0']
SIX = 'government-xl-tower3-june-garden-six-originals-current-v1-20261102'
FOUR = 'government-xl-tower3-june-garden-four-originals-current-v1-20261102'
GRADE = 'government-xl-tower3-june-garden-grade-context-v1-20261102'
SCOPE = 'government-xl-tower3-june-garden-six-originals-neighbour-context-v1-20261102-scope'
FOREIGN = 'government-xl-tower3-june-garden-six-originals-foreign-context-v2-20261102-forms'
ASSEMBLY = 'government-xl-tower3-june-garden-complete-six-original-assembly-v1-20261102'
IDENTITY = 'government-xl-tower3-june-garden-small-native-silhouette-identity-review-v1-20261102'
ROOTS = {'landsd/264489:0':'government-xl-tower3-june-garden-canonical-root-paths-v1-20261102-264489-0',
         'landsd/264493:0':'government-xl-tower3-june-garden-canonical-root-paths-v1-20261102-264493-0',
         'landsd/264491:0':'government-xl-tower3-june-garden-six-originals-remaining-roots-v1-20261102-264491-0',
         'landsd/264495:0':'government-xl-tower3-june-garden-six-originals-remaining-roots-v1-20261102-264495-0'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch',required=True); ap.add_argument('--resources-plan',required=True)
    ap.add_argument('--owned',action='store_true'); a = ap.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    out = BASE/a.batch; pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(BASE)
    resources = read(pp)['resources']; lp = HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        c = reservations.claim('june-garden-source-role-review-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__),pp], {}
    def auth(batch):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]; refs.append(BASE/batch/'result.json')
    def take(batch,name):
        auth(batch); path = BASE/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(SIX+'-runtime','selection.json.gz'); selected = {r['uid']:r for r in selection['rows']}
    ids = {P,SMALL,*TOWERS}; assert set(selected) == ids
    sources = {u:r['sourceSHA256'] for u,r in selected.items()}
    attrs = take(SIX+'-attributes','attributes.json.gz'); assert attrs['startEndAllInputsVerified']
    attrs = {r['uid']:r for r in attrs['rows']}
    auth(SIX+'-runtime'); gp = HERE/'local'/(SIX+'-runtime')/'runtime-geometry.json.gz'
    assert digest(gp.read_bytes()) == pins[SIX+'-runtime'][str(gp.relative_to(ROOT))]; refs.append(gp)
    geometry = {r['uid']:r for r in read(gp)['rows']}; worlds, grounds = {}, {}
    for uid in ids:
        asset = ROOT/selected[uid]['candidate']['path']; assert digest(asset.read_bytes()) == sources[uid] == attrs[uid]['sourceSHA256'] == geometry[uid]['sourceSHA256']; refs.append(asset)
        worlds[uid] = represented(attrs[uid],decode_original_world_triangles(asset.read_bytes()))
        grounds[uid] = np.asarray(geometry[uid]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    ordinary = take(SIX+'-identity','summary.json'); assert set(ordinary['uids']) == ids
    assert {r['uid'] for r in ordinary['rows'] if not r['passed']} == {SMALL}
    joint = take(IDENTITY,'identity-review.json')
    assert joint['identityAccepted'] and joint['requiresSameInstallationGroup']
    assert joint['sourceSHA256'] == sources[SMALL] and joint['requiredOriginalPeerBindings'] == {P:sources[P]}
    for m in joint['measures']:
        assert m['sourceWorldSHA256ByUid'] == {u:digest(worlds[u][m['mode']].astype('<f8').tobytes()) for u in [P,SMALL]}
        assert m['actualOriginalPeerOverlapM2'] <= m['ordinaryForeignLimitM2'] == 1
    # Reuse only complete foundation results with exactly identical represented
    # source arrays AND actual drawn-ground arrays. No stale approval transfers.
    foundation_rows = []
    for uid in sorted(ids):
        code = uid.split('/')[1].replace(':','-')
        batch = ('government-xl-tower3-227380-chain-current-checks-v1-20261102-foundations' if uid == P else
                 (SIX if uid in ['landsd/264491:0','landsd/264495:0'] else FOUR)+'-'+code+'-foundations')
        summary = take(batch,'summary.json'); assert summary['uids'] == [uid] and summary['establishedFoundationPolicyPassed']
        runtime_paths = [p for p in pins[batch] if p.endswith('/runtime-geometry.json.gz')]
        assert len(runtime_paths) == 1
        oldpath = ROOT/runtime_paths[0]; assert digest(oldpath.read_bytes()) == pins[batch][runtime_paths[0]]; refs.append(oldpath)
        old = next(r for r in read(oldpath)['rows'] if r['uid'] == uid)
        assert old['sourceSHA256'] == sources[uid]
        assert digest(np.asarray(old['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3).tobytes()) == digest(grounds[uid].tobytes())
        for row in summary['rows']:
            mode = {'explicitLeftF32':'leftF32','explicitBalancedF32':'balancedF32'}.get(row['mode'],row['mode'])
            raw = take(batch,row['mode']+'.json'); f = raw['foundation']
            assert raw['sourceWorldSHA256'] == digest(worlds[uid][mode].astype('<f8').tobytes())
            assert f['completeTerrainTriangles'] == f['triangles'] and f['fullyBuriedUpwardTriangles'] == 0 and f['fullyBuriedAreaFraction'] <= .001
            foundation_rows.append(dict(uid=uid,mode=mode,foundation=f))
    support_rows = []
    for uid in TOWERS:
        code = uid.split('/')[1].replace(':','-')
        support = (SIX+'-'+code+'-support' if uid in ['landsd/264491:0','landsd/264495:0'] else
                   'government-xl-tower3-june-garden-original-support-v1-20261102-'+code)
        strict = take(support,'summary.json'); root = take(ROOTS[uid],'summary.json')
        assert strict['supportedUid'] == uid and strict['supportUids'] == [P]
        assert strict['sourceSHA256ByUid'] == root['sourceSHA256ByUid'] == {uid:sources[uid],P:sources[P]}
        for mode in worlds[uid]:
            raw = next(r for r in strict['rows'] if r['mode'] == mode)
            assert raw['sourceWorldSHA256ByUid'] == {u:digest(worlds[u][mode].astype('<f8').tobytes()) for u in [uid,P]}
            f = raw['compoundFoundation']; assert f['completeTerrainTriangles'] == f['triangles'] and f['fullyBuriedTriangles'] == f['fullyBuriedUpwardTriangles'] == 0
            paths = take(ROOTS[uid],mode+'.json.gz')
            assert paths['sourceWorldSHA256'] == digest(worlds[uid][mode].astype('<f8').tobytes()) and paths['supportWorldSHA256'] == digest(worlds[P][mode].astype('<f8').tobytes())
            assert len(paths['rows']) == len(raw['support']['unresolved'])
            assert paths['canonicalStrictAnchorCount'] == raw['support']['strictContacts'] > 0
            assert all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight'] and r['riseAboveEndpointsM'] == 0 and r['maximumResidualM'] <= .001 for r in paths['rows'])
            support_rows.append(dict(uid=uid,mode=mode,rawStrictInterface=raw['support'],rawCompoundFoundation=f,originalEndpointPaths=paths['rows'],sourceRole='Original supported tower, including retained wall/overhang footings; every residual witness reaches a strict original podium anchor on unchanged source surfaces',rawStrictInterfaceReapproved=False))
    ground_rows = []
    for uid in [P,SMALL]:
        canonical = ('government-xl-tower3-june-garden-exposed-canonical-paths-v1-20261102-227380-0' if uid == P else
                     'government-xl-tower3-june-garden-small-existing-endpoint-retry-v1-20261102')
        for mode, tri in worlds[uid].items():
            row = take(canonical,mode+'.json.gz')
            assert row['sourceWorldSHA256'] == digest(tri.astype('<f8').tobytes()) and row['completeGroundSHA256'] == digest(grounds[uid].tobytes())
            assert all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight'] and r['riseAboveEndpointsM'] == 0 and r['maximumResidualM'] <= .001 for r in row['rows'])
            assert len(row['rawCanonicalWarningIndices']) == len(row['rows'])+len(row['nonrenderingOnlyWarnings'])
            normal = np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); length = np.linalg.norm(normal,axis=1)
            for witness in row['nonrenderingOnlyWarnings']:
                assert witness['originalIncidentFaces'] and all(length[i] == 0 for i in witness['originalIncidentFaces'])
            lowbatch = ('government-xl-tower3-227380-chain-current-checks-v1-20261102-low-faces' if uid == P else FOUR+'-264492-0-low-faces')
            oldmode = {'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)
            low = take(lowbatch,oldmode+'.json.gz')
            assert low['sourceWorldSHA256'] == row['sourceWorldSHA256'] and low['groundSHA256'] == row['completeGroundSHA256']
            below = take(GRADE+'-'+uid.split('/')[1].replace(':','-')+'-below-grade',mode+'.json.gz')
            bad = {r['sourceFace']:r for r in low['rows']}; assert set(below['completeNegativeFaces']) == set(bad)
            walls = set(below['negativeWallFaces']); downward = {i for i in bad if length[i] > 0 and i not in walls}
            assert all(length[i] > 0 and abs(normal[i,1]) <= .25*length[i] for i in walls)
            assert all(normal[i,1] < -.25*length[i] for i in downward)
            assert downward == ({11004,11005,11006} if uid == P else set())
            # No roof-cap/per-component engineering gate is invented for the
            # three tiny authored grade-crossing wall strips.
            for face in below['wallsWithoutSharedEdgeClearCapPath']:
                assert uid == P and face in {11099,11100,11101}
                assert bad[face]['highestVertexAboveEveryOverlappingGroundFace']
                assert any(c['sourceFaceA'] == face and c['dimension'] > 0 for c in below['completePositiveGradeContacts'])
            ground_rows.append(dict(uid=uid,mode=mode,renderingGroundPaths=len(row['rows']),nonrenderingWarningsRetainedWithoutCredit=len(row['nonrenderingOnlyWarnings']),originalNegativeWalls=sorted(walls),originalNegativeDownwardFaces=sorted(downward),sourceRole='Ground-rooted original wall bases and retained lower skins',podiumSupportCredit=False))
    assembly = take(ASSEMBLY,'summary.json')
    assert set(assembly['uids']) == ids and assembly['sourceSHA256ByUid'] == sources and assembly['completeUnorderedPairs'] == 15
    assert len(assembly['rows']) == 60
    for row in assembly['rows']:
        pair = {row['uid'],row['peerUid']}
        assert row['sourceWorldSHA256ByUid'] == {u:digest(worlds[u][row['mode']].astype('<f8').tobytes()) for u in pair}
        if P not in pair: assert row['strictBoundsSeparated'] is True
    scope = take(SCOPE,'summary.json'); foreign = take(FOREIGN,'summary.json')
    assert set(scope['uids']) == set(foreign['uids']) == ids
    assert all(r['currentNativeActorsChecked'] == 7095 and not r['nearbyNativeActors'] for r in scope['rows'])
    external = [r for r in foreign['rows'] if r['foreignUid'] not in ids]
    assert {(r['uid'],r['foreignUid']) for r in external} == {(P,'landsd/146754:0')}
    assert all(m['allFiniteContactPairs'] == 0 for r in external for m in r['modes'])
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    assert reservations.owns(lease)
    review = dict(uids=sorted(ids),sourceSHA256ByUid=sources,currentManifestSHA256=selection['manifestSHA256'],
        identityAccepted=True,requiredOriginalPeerBindings=joint['requiredOriginalPeerBindings'],activationGroup=sorted(ids),
        supportByUid=dict.fromkeys(TOWERS,P),independentGroundOwnerUids=[P,SMALL],
        sourceSpecificPhysicalInterpretationAccepted=True,completeModelBodyNeighbourInterpretationAccepted=True,
        rawPhysicalFailuresPreserved=True,foundationChecks=foundation_rows,originalSupportRoleChecks=support_rows,
        originalGroundRoleChecks=ground_rows,completeOriginalAssembly=assembly,externalBasicContacts=external,
        installedNativeBodyNominees=[],terrainWideRetainedReviewApproved=False,visualAcceptance=False,
        sourceGeometryChanges=0,sourcePoseChanges=0,installedMetadataChanges=0,
        installationApproved=False,publication=False,qualification=__doc__)
    save(out/'ROOT-PHYSICAL-REVIEW.json',review)
    refs.extend(HERE/n for n in ['original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py'])
    module('june_garden_exact_source_role_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'reviewed-six-original-source-roles-and-actual-model-body-neighbours',refs,review)


if __name__ == '__main__': main()
