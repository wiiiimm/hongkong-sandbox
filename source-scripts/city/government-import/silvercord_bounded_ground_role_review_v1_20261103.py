"""Bind Silvercord's exact buried-wall context to its reviewed original skins.

This source-specific ground-role disposition preserves the ordinary failed
foundation/rim reports. It cannot approve the whole assembly or publication.
"""
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-bounded-ground-role-review-v1-20261103'
LOCAL = HERE / 'local' / BATCH
UID = 'landsd/233997:0'
SHA = '11b03482304ea9f139e6863d259891f06aecc5def1df2e18abd921e0a0aebc5d'
WALLS = 'government-xl-silvercord-buried-wall-grade-context-v1-20261103'
SKINS = 'government-xl-silvercord-lippo-lower-skin-role-review-v1-20261103'
BELOW = 'government-xl-silvercord-lippo-complete-floor-roles-v1-20261103-below-233997-0'
RIMS = 'government-xl-silvercord-existing-grade-endpoint-retry-grouped-v1-20261103'


def validate_partition(wall, below, rim):
    assert wall['sourceWorldSHA256'] == below['sourceWorldSHA256'] == rim['sourceWorldSHA256']
    assert wall['completeGroundSHA256'] == below['completeGroundSHA256'] == rim['completeGroundSHA256']
    assert len(below['completeNegativeFaces']) == 416 and len(below['negativeWallFaces']) == 410
    assert below['negativeNonWallFaces'] == [1347,1348,1349,6240,6241,6242]
    assert not below['wallsWithoutSharedEdgeClearCapPath']
    assert len(below['allWallCapPaths']) == 410
    assert all(p['hasExactSharedEdgeClearCapPath'] for p in below['allWallCapPaths'])
    assert len(wall['originalBuriedWallFaceIds']) == len(set(wall['originalBuriedWallFaceIds'])) == 23
    assert set(wall['originalBuriedWallFaceIds']) <= set(below['negativeWallFaces'])
    assert wall['originalBuriedDownwardFaceIds'] == below['negativeNonWallFaces']
    assert set(wall['allOriginalBuriedFaceIds']) == set(wall['originalBuriedWallFaceIds'] + wall['originalBuriedDownwardFaceIds'])
    assert len(wall['allOriginalBuriedFaceIds']) == 29
    foundation = wall['rawFoundation']
    assert foundation['fullyBuriedTriangles'] == 29 and foundation['fullyBuriedUpwardTriangles'] == 0
    assert foundation['fullyBuriedAreaFraction'] > .001
    context = wall['originalWallGradeContext']
    assert not context['unresolvedWallFaces'] and len(context['actualGradeWallFaces']) == 394
    assert {p['sourceFace'] for p in context['paths']} == set(wall['originalBuriedWallFaceIds'])
    assert all(p['reachesActualGradeWall'] and p['actualGradeWallFace'] in context['actualGradeWallFaces']
               and len(p['sharedNonzeroOriginalEdges']) == len(p['originalWallFacePath'])-1
               for p in context['paths'])
    assert len(rim['rows']) == len(rim['rawCanonicalWarningIndices']) == 505
    # The saved disconnected rows intentionally have no path/endpoint field.
    # Require their explicit failed-attachment marker rather than inventing one.
    unresolved = [p for p in rim['rows'] if p.get('passesExistingEndpointHeight') is not True]
    assert len(unresolved) == 18
    assert all(p['hasUnrestrictedFiniteAttachment'] is False and p['incidentFaces']
               and set(p['incidentFaces']) <= {1347,1348,1349} for p in unresolved)
    return dict(sourceWorldSHA256=wall['sourceWorldSHA256'], completeGroundSHA256=wall['completeGroundSHA256'],
        completeNegativeFaces=416, lowerWallsWithClearOriginalCaps=410, sampledBuriedWallsWithActualGradeWallPaths=23,
        preservedLowerSkinFaceIds=below['negativeNonWallFaces'], rawFoundation=foundation,
        finiteOriginalRimPaths=487, preservedTinySkinRimWarnings=18,
        ordinaryFoundationPolicyPassed=False, sourceGroundRoleAccepted=True)


def owned():
    lease = read(LOCAL/'reservation.json')
    assert reservations.owns(lease) and not (BASE/BATCH).exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, filename):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = BASE/batch/filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    summary = take(WALLS,'summary.json')
    assert summary['sourceSHA256'] == SHA and summary['allBuriedWallFacetsReachActualGradeViaOriginalWalls']
    skin = take(SKINS,'ROOT-LOWER-SOURCE-REVIEW.json')
    assert skin['sourceSHA256ByUid'][UID] == SHA and skin['sourceRoleAccepted']
    assert not skin['groundRootCredit'] and not skin['interComponentBridgeCredit']
    rows = []
    for mode in ['original','literal','leftF32','balancedF32']:
        wall, below, rim = (take(name,mode+'.json.gz') for name in [WALLS,BELOW,RIMS])
        rows.append(dict(mode=mode, **validate_partition(wall,below,rim)))
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == '1c482bc3265f90bab44d62f5b2216d16adaf2688c9e2cfe00fbd9f0e0821fd63'
    refs.append(manifest)
    review = dict(uids=[UID], sourceSHA256ByUid={UID:SHA}, reviewer='Codex ROOT', rows=rows,
        sourceSpecificBuriedSurfaceInterpretationAccepted=True, sourceGroundRoleAccepted=True,
        rawOrdinaryFoundationPolicyPassed=False, rawCanonicalFailuresPreserved=True,
        sourceSpecificPhysicalInterpretationAccepted=False, physicalAcceptance=False,
        installationApproved=False, publication=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        modelAndEffort='Not verified from available runtime metadata',
        basis=[
            'The exact29sampled buried facets are exhaustively identified in each world:23wall facets and6previously reviewed downward lower skins. All23buried walls have paths consisting only of exact nonzero shared original wall edges to walls with independently computed positive actual-terrain contacts. All410continuous negative wall faces retain clear original-cap paths. This is positive source-surface/grade context; no roof, walking surface or upward-buried facet is excused.',
            'The6downward facets retain the bounded exact-source lower-skin disposition, slopes and every source contact. The18remaining rim warnings belong only to the isolated0.05764m2 three-face skin1347/1348/1349. That skin receives no support root, fabricated attachment, structural, floor or route credit. Its source-preserved presence does not create a new per-component engineering gate.',
            'All505raw rim warnings remain;487have existing exact original paths within unchanged endpoint/incidence limits. The raw ordinary burial fraction0.00351564926 still exceeds0.001. This named exact-source ground-role interpretation does not rewrite that failure or alter any numerical threshold. It accepts the represented lower source surfaces rather than asserting an as-built basement purpose.',
            'Whole-source identity, full assembly/native/foreign collisions, retained terrain, mobile budgets, original-podium and retained-owner dependency qualification, actual browser exports, failure/retry, fenced publication and independent readback remain mandatory. This record alone cannot approve or install any model.'
        ])
    save(BASE/BATCH/'ROOT-GROUND-ROLE-REVIEW.json',review)
    assert reservations.owns(lease)
    module('silvercord_bounded_ground_role',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'bounded-exact-original-buried-wall-and-lower-skin-ground-role-review',list(dict.fromkeys(refs)),review)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE/BATCH).exists()
        claim = reservations.claim('silvercord-bounded-ground-role-'+str(uuid.uuid4()),
            ['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
