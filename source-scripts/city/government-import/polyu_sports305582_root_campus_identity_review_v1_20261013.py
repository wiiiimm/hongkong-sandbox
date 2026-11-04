"""Freeze a bounded ROOT source-identity interpretation; grant no physical credit."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / 'source-scripts/city/government-import'
BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-polyu-sports305582-root-campus-identity-review-v1-20261013'
DOC = BASE / BATCH
GEO = BASE / 'government-xl-polyu-sports305582-geographic-campus-label-context-v1-20261013'
PRIMARY = BASE / 'government-xl-polyu-sports305582-root-primary-interface-lookup-v1-20261013'
VIEWS = BASE / 'government-xl-polyu-sports305582-saved-contact-facet-subset-views-v1-20261012'
CAPTURE = BASE / 'government-xl-polyu-sports305582-current-surviving-neighbour-geometry-context-v1-20261012'
sys.path.insert(0, str(HERE))
from run import read, connect


def ref(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    pins = {
        GEO / 'context.json': '4388a944adc56dee64bac687a1140fd8d868efe0c8915ea1d334b95d3bf9165c',
        HERE / 'polyu_source_campus_geographic_label_binding_v1_20261013.mjs': '8f76783c157b3e7f85bb2c15ca94295f8b7f4ac8bc21f5fc953825483d614955',
        BASE / 'government-xl-polyu-sports305582-source-specific-disposition-proposal-v1-20261012/proposal-v2-name-erratum-and-bounded-primary-lookup.json': '36ea5f15464f49771111d7fab06a92654623993181cbff0f57e9ea1cbb7b1d81',
        CAPTURE / 'actual-surviving-neighbour-attributes.json.gz': '9a68a4719cd2b8d3c5ed04d6afbe31fbf27014187256731d1b788ac645f99210',
        CAPTURE / 'current-neighbour-input.json.gz': '76f65343d0f22f06f1fb707da2412243232c4da8248b70c2a52ea35c7ab96fbd',
        VIEWS / 'view-context.json': '16162a3f0992306e5aa41c47dc31ba4d4e0ebbb8c9bc14f70d998acea5866c89',
        VIEWS / '305793-0-complete-contact-facet-subset-1800x1500.png': 'fd1869afa7aaa7201ecfc249793d626e0e4940fa236cc20a205a22cdf067c03f',
        VIEWS / '72322-0-complete-contact-facet-subset-1800x1500.png': '16ea8b14fd2fcfd2ba2584e17250f3aec8d1a41222df28d1cf89d72f49c99f65',
        VIEWS / '258852-0-complete-contact-facet-subset-1800x1500.png': '70e09b3f304e64f62d50b04af9f97ce53c8755a380fd25ba63965ef69ac43169',
        BASE / 'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012/context.json': 'ee6d84e93a1b5f18ccb25117631b81c24f82443a10c256144f2eec9933bffd18',
        BASE / 'government-xl-polyu-sports305582-original-component-overlap-context-v1-20261012/complete-original-and-saved-regions-1800x1500.png': '0dee0c3840234222db1738604351ba9fba225a50631148c58d21c11c6ac62456',
        HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py': 'b1f5dce8c740e955ee4da35ebfd3438724e02f0db6f0f7d369decb47e4298fb0',
    }
    geo = read(GEO / 'context.json')
    for item in geo['inputRefs']:
        path = ROOT / item['path']
        assert path not in pins or pins[path] == item['sha256']
        pins[path] = item['sha256']
    attrs = read(CAPTURE / 'actual-surviving-neighbour-attributes.json.gz')
    captured = read(CAPTURE / 'current-neighbour-input.json.gz')
    native, = attrs['nativeContextRows']
    old_native, = captured['rows']
    assert native['uid'] == old_native['uid'] == 'landsd/305793:0'
    assert native['rawInstalledEntry'] == old_native['entry']
    assert native['loadedGroupScale'] == [1, 1, 1]
    asset = ROOT / old_native['path']
    catalogue = asset.parent.parent / 'catalogue.json'
    source_asset = HERE / 'local/government-xl-four-pending-original-inputs-20261007/assets/ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15.glb.gz'
    pins[asset] = native['sourceSHA256']
    pins[source_asset] = 'ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'

    def matching_entries(value):
        if isinstance(value, dict):
            if value.get('uid') == native['uid'] and 'asset' in value:
                yield value
            else:
                for child in value.values():
                    yield from matching_entries(child)
        elif isinstance(value, list):
            for child in value:
                yield from matching_entries(child)

    current_native, = matching_entries(read(catalogue))
    assert current_native == native['rawInstalledEntry']
    assert current_native['publicationApproved'] is False  # independent existing hold retained
    refs = [ref(path) for path in sorted(pins)] + [ref(catalogue), ref(Path(__file__))]

    def fence():
        for path, sha in pins.items():
            assert ref(path)['sha256'] == sha, str(path)
        for item in refs:
            assert ref(ROOT / item['path']) == item

    fence()
    rows = {row['uid']: row for row in geo['rows']}
    podium = rows['landsd/305793:0']
    sports = rows['landsd/305582:0']
    assert podium['sourceStructureType'] == 'Podium'
    assert podium['sourceBuildingCSUID'] == current_native['buildingCSUID']
    assert podium['footprintRingVertexCounts'] == [905, 48, 14, 8, 5, 8]
    inside = lambda p: p['markerInsideApproximateGeographicFootprint'] or p['mapMarkerInsideApproximateGeographicFootprint']
    campus_labels = [p for p in podium['primaryLabels'] if p['category'] == 'Building' and inside(p)]
    assert len(campus_labels) == 40
    block_x, = [p for p in sports['primaryLabels'] if p['category'] == 'Building' and inside(p)]
    assert block_x['name'] == 'Block X' and block_x['markerInsideApproximateGeographicFootprint']
    assert not block_x['mapMarkerInsideApproximateGeographicFootprint']
    sports_label, = [p for p in sports['primaryLabels'] if p['category'] == 'CoreLocation' and p['loc'] == 'Block X (G/F)']
    assert inside(sports_label)
    assert 14 < block_x['approximateMarkerDistanceFromSourceCentreM'] < 16
    innovation, = [p for p in rows['landsd/72322:0']['primaryLabels'] if p['category'] == 'Building' and inside(p)]
    communal, = [p for p in rows['landsd/258852:0']['primaryLabels'] if p['category'] == 'Building' and inside(p)]
    assert innovation['name'] == 'Block V (Jockey Club Innovation Tower)'
    assert communal['name'] == 'Core S (Communal Building)'
    prior_jobs = []
    for batch in ['government-xl-polyu-sports305582-current-surviving-neighbour-finite-region-context-v2-20261012', 'government-xl-polyu-sports305582-saved-contact-locus-context-v1-20261012', 'government-xl-polyu-sports305582-root-primary-interface-lookup-v1-20261013']:
        path = BASE / batch / 'result.json'
        result = read(path)
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
        refs.append(ref(path))
        prior_jobs.append({'jobId': result['jobId'], 'result': ref(path), 'readBackExact': True})
    fence()
    review = {
        'executor': 'Codex ROOT', 'sourceOnly': True, 'uids': ['landsd/305582:0'],
        'sourceSHA256': pins[source_asset], 'sourceModelId': 'B365931850802063C0',
        'sourceBuildingCSUID': sports['sourceBuildingCSUID'],
        'identityAccepted': True,
        'identityAcceptanceScope': 'Bounded original Sports305582 identity and adjoining campus-podium/perimeter representation interpretation requested by the source-specific proposal v2. This is not acquisition, placement or publication approval.',
        'sourceIdentityReviewUsedAI': True, 'aiGeometryModelling': False,
        'sourceGeometryChanges': 0, 'terrainGeometryChanges': 0,
        'physicalAccepted': False, 'supportAccepted': False, 'installationApproved': False,
        'scriptFullAcceptancePassed': False, 'newlyInstalled': 0,
        'currentNativeCatalogueExactMatch': ref(catalogue),
        'nativePublicationHoldRetained': True,
        'currentSourceLocationFacts': {
            'native305793SourceType': 'Podium', 'native305793BuildingCSUID': podium['sourceBuildingCSUID'],
            'native305793WorldOuterBoundsXZ': podium['exactSourceWorldBoundsXZ'][0],
            'campusBuildingLabelsWithinApproximateFootprint': [p['name'] for p in campus_labels],
            'sportsBlockXBuildingLabel': block_x, 'sportsBlockXCoreLocationLabel': sports_label,
            'innovationBlockVLabel': innovation, 'communalCoreSLabel': communal,
        },
        'boundedRootSourceInterpretation': [
            'The retained original305793 is the government campus-scale podium, not an exclusively separate library tower. Its provider attributes, approximately400m footprint and40 official building location labels independently corroborate the campus-platform interpretation.',
            'Original Sports305582 matches its stable provider object/model/CSUID, its complete footprint passes the unchanged95%/10m identity limits, and its source footprint locates the independently named official BlockX Sports Centre. KwongOnJubilee in the Communal Building is distinct.',
            'ROOT inspected the complete-original plan and all three saved-contact whole-facet views. The original305793 contact subset shows stepped campus-platform facets beside Sports upright perimeter surfaces. In source context these are the adjoining campus podium and Sports perimeter representations, not evidence of a wrongly named separate library tower.',
            'Innovation and Communal are independently located adjacent campus buildings. Their viewed actors are approximate BASIC walls, not original native meshes. Their surface crossings remain physical questions; no solid-penetration or intentional-joint interpretation is approved.',
        ],
        'existingRawIdentityReasonsRetained': ['fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2', 'full-source-unrelated-overlap'],
        'savedContactDiagnosticsRetained': {'native305793ProperSegments': 239, 'native305793PartialCoplanarPatches': 13, 'native305793WholeTriangleDuplicates': 0, 'innovationBASICProperSegments': 296, 'communalBASICProperSegments': 91},
        'noPhysicalExceptions': ['No engineering, ownership, intentional joint, solid penetration, ground root or support claim.', 'No facet omissions, foreign collision exemptions, terminal-role wholesale exemptions or source-placement changes.', 'Historical6649-native/old-manifest contact arrays remain historical; they are not relabelled current6650-native placement evidence.', 'The neighbour305793 publicationApproved:false remains unchanged; this review does not approve it.'],
        'allOriginalObligationsRetained': {'faces': 10536, 'bodies': 21, 'zeroFaces': 4, 'worldRepresentations': ['original', 'literal', 'explicitLeftFloat32', 'explicitBalancedFloat32']},
        'priorCompleteNeonResults': prior_jobs, 'inputRefs': refs,
        'currentHeldReason': 'complete-current-four-world-ground-support-native-BASIC-physical-runtime-checks-required',
        'nextStep': 'Use this exact source-only interpretation in a narrow identity binder while retaining raw ordinary identity results. Reuse unchanged original/native attributes only after exact current bindings; complete current ground and native/BASIC foreign physical, component support, runtime and browser checks before installation.',
        'permanentRejection': False,
    }
    DOC.mkdir(exist_ok=True)
    path = DOC / 'root-campus-source-identity-review.json'
    assert not path.exists()
    path.write_text(json.dumps(review, sort_keys=True, indent=2) + '\n')
    fence()
    spec = importlib.util.spec_from_file_location('polyu_identity_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.freeze(BATCH, 'bounded-root-campus-podium-and-sports-source-identity-only', [ROOT / item['path'] for item in refs] + [path, GEO / 'context.json'], {
        'uids': review['uids'], 'sourceOnly': True, 'rootReview': ref(path),
        'identityAccepted': True, 'sourceIdentityReviewUsedAI': True,
        'physicalAccepted': False, 'supportAccepted': False, 'scriptFullAcceptancePassed': False,
        'currentHeldReason': review['currentHeldReason'], 'nextStep': review['nextStep'],
        'xlIdentityCasesAdvanced': 1,
    })
    fence()
    print(json.dumps({'jobId': result['jobId'], 'refs': len(result['evidenceRefs']), 'rootReview': ref(path), 'identityOnly': True, 'newlyInstalled': 0}))


if __name__ == '__main__':
    main()
