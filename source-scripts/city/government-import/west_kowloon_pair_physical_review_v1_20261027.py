"""Bounded unchanged-provider-unit physical interpretation; never install/publish."""
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from west_kowloon_pair_original_identity_review_v1_20261027 import EXPECTED

P = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = P + 'physical-source-review-v1-20261027'
SOURCES = {u: r['sha256'] for u, r in EXPECTED.items()}
NORTH, AUX, SOUTH = 'landsd/182397:0', 'landsd/309340:0', 'landsd/272986:0'
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}
MASKED = [1778,3248,3558,3559,5365,5366,5384,6355,6361,6579,6580,6582,6802,9948,9949,9950,9967,9968,9970,9971,9972,9996,9997,9998,9999,10006,10268,10269,10270,10274,10275,10276,10277,10285,10286]


def verify_current_foundation_record(record, ground_sha):
    assert record['mode'] in MODES and record['groundSHA256'] == ground_sha
    assert record['reviewedSourceFaces'] == MASKED
    assert record['allOtherSourceFaces'] == [i for i in range(10322) if i not in set(MASKED)]
    rows = record['currentMaskedFacets']
    assert [r['sourceFace'] for r in rows] == MASKED
    assert all(r['completeProjectionCovered'] and r['strictlyMasked']
               and Fraction(r['maximumAllFinitePairGapM']) < 0
               and any(g > 0 for g in r['strictCoreSeparatingAxisGapsM']) for r in rows)
    ordinary, whole = record['ordinaryFoundation'], record['wholeRawFoundation']
    assert ordinary['triangles'] == ordinary['completeTerrainTriangles'] == 10287
    assert ordinary['fullyBuriedTriangles'] == ordinary['fullyBuriedUpwardTriangles'] == 0
    assert ordinary['fullyBuriedAreaFraction'] == 0
    assert whole['triangles'] == whole['completeTerrainTriangles'] == 10322
    assert whole['fullyBuriedTriangles'] == 35 and whole['fullyBuriedUpwardTriangles'] == 24
    assert record['ordinaryFoundationPolicyPassed'] and record['allReviewedFacesStrictlyMasked']
    return True


def main():
    base, out = ROOT / 'docs/astra-city/government-import', ROOT / 'docs/astra-city/government-import' / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, filename='summary.json'):
        if batch not in pins:
            _, pins[batch] = authenticate(base / batch)
            refs.append(base / batch / 'result.json')
        path = base / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    identity = take(P + 'identity-revalidated-v1-20261027')
    assert identity['identityAccepted'] and identity['sourceSHA256ByUid'] == SOURCES
    runtime = P + 'three-member-runtime-v2-20261027'
    selected = take(runtime, 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selected['rows']} == SOURCES
    geometry_path = HERE / 'local' / runtime / 'runtime-geometry.json.gz'
    assert digest(geometry_path.read_bytes()) == pins[runtime][str(geometry_path.relative_to(ROOT))]
    refs.append(geometry_path)
    geometry = {r['uid']: r for r in read(geometry_path)['rows']}
    for r in selected['rows']:
        path = ROOT / r['candidate']['path']
        assert digest(path.read_bytes()) == SOURCES[r['uid']]
        assert not r['candidate']['entry'].get('supportDependencies')
        assert not r['candidate']['entry'].get('retainedBasicSupportDependencies')
        refs.append(path)
    ground_sha = digest(np.asarray(geometry[NORTH]['drawnGroundGeometry'], dtype='<f8').reshape(-1,3,3).tobytes())
    masked_name = P + 'current-masked-foundation-v1-20261027'
    masked = take(masked_name)
    assert masked['sourceSHA256'] == SOURCES[NORTH] and masked['groundSHA256'] == ground_sha
    assert masked['allFourCurrentMaskedRoleChecksPassed'] and masked['allOtherFacesPassEstablishedFoundationPolicy']
    assert {r['mode'] for r in masked['rows']} == MODES
    for mode in sorted(MODES):
        record = take(masked_name, mode + '.json.gz')
        assert verify_current_foundation_record(record, ground_sha)
        for row in record['currentMaskedFacets']:
            path = ROOT / row['proof']['path']
            assert digest(path.read_bytes()) == row['proof']['sha256'] == pins[masked_name][str(path.relative_to(ROOT))]
            proof = read(path)
            assert proof['completeProjectionCoverage']['completeGroundSHA256'] == ground_sha
            assert proof['completeProjectionCoverage']['exactProjectionCovered']
            assert proof['exactMaximumAllFinitePairGapM'] == row['maximumAllFinitePairGapM']
            refs.append(path)
    auxiliary = take(P + '309340-0-foundation-v1-20261027')
    assert auxiliary['establishedFoundationPolicyPassed'] and len(auxiliary['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 338
               and r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0 for r in auxiliary['rows'])
    topology = take(P + 'nonwall-exact-edge-context-v1-20261027', 'context.json.gz')
    assert topology['sourceSHA256'] == SOURCES[NORTH] and topology['groundSHA256'] == ground_sha
    assert [r['sourceFace'] for r in topology['rows']] == [5255,5284,5285,9268,9269,9270,9306,9307]
    assert [r['sourceFace'] for r in topology['rows'] if r['signedNormalY'] < -.25] == [5284,5285]
    assert [r['sourceFace'] for r in topology['rows'] if r['signedNormalY'] > .25] == [5255,9268,9269,9270,9306,9307]
    model_scope = take(P + 'model-scope-v2-20261027')
    assert {r['uid'] for r in model_scope['rows']} == set(SOURCES)
    assert all(r['currentNativeActorsChecked'] == 6989 and r['sourceModelOnly'] for r in model_scope['rows'])
    assert {r['uid'] for row in model_scope['rows'] for r in row['nearbyNativeActors']} == {SOUTH}
    foreign = take(P + 'foreign-contacts-v2-20261027')
    assert {(r['uid'], r['foreignUid']) for r in foreign['rows']} == {(NORTH, AUX), (AUX, NORTH), (NORTH, 'landsd/79799:0')}
    for row in foreign['rows']:
        if row['foreignUid'] not in SOURCES:
            assert all(m['allFiniteContactPairs'] == 0 for m in row['modes'])
    native = take(P + 'native-contact-roles-v2-20261027')
    assert len(native['rows']) == 4 and {r['mode'] for r in native['rows']} == MODES
    assert all(r['uid'] == NORTH and r['nativeUid'] == SOUTH and r['contactCount'] == 4
               and r['roles'] == {'transverse-surface-crossing': 4} for r in native['rows'])
    pair = take(P + 'original-contact-roles-v2-20261027')
    assert pair['sourceSHA256ByUid'] == SOURCES and {r['mode'] for r in pair['rows']} == MODES
    assert all(r['contactCount'] == (96 if r['mode'] == 'literal' else 102)
               and r['roles']['transverse-surface-crossing'] == 47 for r in pair['rows'])
    ground_contacts = take(P + 'original-contact-ground-v2-20261027')
    assert ground_contacts['allFourWorldTransverseSegmentsStrictlySubgrade'] is False
    viewed = []
    pair_views = take(P + 'pair-junction-views-v1-20261027')
    assert pair_views['completeOriginalContactCount'] == 102 and pair_views['sourceSHA256ByUid'] == SOURCES
    native_views = take(P + 'native-junction-views-v2-20261027')
    for image in [pair_views['image'], *[r['image'] for r in native_views['exports']]]:
        path = ROOT / image['path']
        assert digest(path.read_bytes()) == image['sha256']
        refs.append(path)
        viewed.append(image)
    neighbours = take(P + 'three-member-neighbours-v2-20261027')
    assert neighbours['forms'] == 786 and not neighbours['basicFlags']
    assert len(neighbours['nativeRows']) == len(neighbours['requiredNativeUids']) == 67
    failures = {r['uid']: r for r in neighbours['nativeRows'] if not r['passed']}
    assert set(failures) == {'landsd/20270:0', 'landsd/177605:0'} and len(neighbours['nativeResolved']) == 65
    for suffix, uid, support in [('20270-0', 'landsd/20270:0', 'landsd/159422:0'), ('177605-0', 'landsd/177605:0', 'landsd/177604:0')]:
        context = take(P + 'retained-' + suffix + '-context-v2-20261027')
        assert context['nativeUid'] == uid and context['supportUid'] == support
        assert context['proposalTerrainNonRegressionProved'] and not context['existingNativeReaccepted']
        assert context['rawNativeRegression'] == failures[uid] and context['rawSupportPolicyPassed'] is False
        assert {r['uid'] for r in context['rows']} == {uid, support}
        assert all(r['exactRenderedTerrainMultisetUnchanged'] and r['rootCoarseMaskUnchangedAcrossCompleteBounds'] for r in context['rows'])
    review = dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES,
                  sourceSpecificPhysicalInterpretationAccepted=True, physicalAcceptance=True,
                  independentlyGroundedRoots=sorted(SOURCES), requiredAvailabilityGroup=sorted([NORTH,AUX,SOUTH]),
                  rawFoundationExceptionFaces=MASKED, allOther10287FacesOrdinaryFoundationPassed=True,
                  rawPairContacts=pair['rows'], rawNativeContacts=native['rows'],
                  allCrossingsSubgrade=False, closedSolidOrVolumetricClearanceProved=False,
                  actualJunctionImagesInspected=viewed, sourceEvidenceInterpretationUsedAI=True,
                  aiGeometryModelling=False, sourceGeometryChanges=0, sourcePoseChanges=0,
                  nativeGeometryOrSupportMetadataChanges=0, visualAcceptance=False, installationApproved=False, publication=False,
                  interpretation=[
                      'The exact35 previously reviewed low landscape-base facets stay strictly masked by complete current drawn ground in all four worlds, outside the recorded tower core. No other original face is exempted: every other10287face passes the unchanged ordinary foundation policy with zero fully buried faces.',
                      'The eight remaining non-wall grade contacts are preserved original low-surface geometry. Two are downward undersides; the six upward faces belong to the low attachment/base portions shown in the original source/ground plots and exact topology context. Partial ground crossings remain recorded; no upper-floor, room, basement or closed-interior claim is made from connectivity.',
                      'The original pair junction was actually inspected in three orientations. The localized nested/abutting low provider-unit, wall and overhead-surface interfaces are retained as supplied at their exact shared survey placement. This accepts source-faithful rendering of these two exact provider units together, not a claim that their surfaces are disjoint or that47transverse contacts are subgrade. The auxiliary stays unnamed and is not asserted to be a separately surveyed complete landmark.',
                      'The four original contacts with the unchanged South Tower occur in the separately inspected low wall/forecourt junction. This source-specific original-interface interpretation does not alter the South asset, source placement, accepted supports or identity metadata. Both new units remain independent ground roots; no invented physical-support edge or cycle is introduced.',
                      'Current peer BASIC interference is not accepted as a mixed rendering state. All three originals must activate/fall back as one availability group. Unrelated BASIC79799 has zero finite contacts. All6989current natives were considered in the model-bound nomination, and the sole nearby original South interface is retained explicitly.',
                      'All786forms and67retained originals remain in the terrain-change scope.65strict passes are preserved; the two raw legacy support negatives remain false, with exact whole actor AND support terrain-multiset equality. No legacy model is reaccepted and no terrain-only decision becomes a new support approval.'
                  ], remaining=['Exact source/retained visual qualification and atomic browser receipt binding',
                                'Guarded three-member terrain and existing South availability-overlay stage',
                                'Live verification, full6989oldactor/all521XL readback, Neon installed acceptance, commit and push'])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', review)
    save(out / 'summary.json', {k:v for k,v in review.items() if k not in ['interpretation','rawPairContacts','rawNativeContacts','actualJunctionImagesInspected']})
    refs.extend([HERE / 'west_kowloon_pair_original_identity_review_v1_20261027.py', HERE / 'west_kowloon_current_masked_foundation_v1_20261027.py'])
    module('north_pair_physical_source_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'exact-two-provider-unit-bounded-physical-source-interpretation', refs,
        dict(uids=sorted(SOURCES), sourceSHA256ByUid=SOURCES, physicalAcceptance=True,
             sourceSpecificPhysicalInterpretationAccepted=True, visualAcceptance=False, installationApproved=False))


if __name__ == '__main__': main()
