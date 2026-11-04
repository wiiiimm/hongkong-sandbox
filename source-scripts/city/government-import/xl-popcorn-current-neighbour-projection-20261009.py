"""Classify current neighbours against every unchanged original PopCorn face.

Diagnostic only: a disjoint basic footprint can be considered for exact parent
retention; installed native actors still require their whole original geometry.
"""
import importlib.util
import numpy as np
import shapely
from shapely.geometry import Polygon, LineString, Point
from run import ROOT, HERE, read, save, digest

BATCH = 'government-xl-popcorn-current-neighbour-projection-20261009'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
PHYSICAL = ROOT / 'docs/astra-city/government-import/government-xl-popcorn-current-complete-original-physical-v2-20261009'
FACE_INPUT = ROOT / 'docs/astra-city/government-import/government-xl-popcorn-current-complete-face-ground-20261009/exact-current-renderer-face-inputs.json.gz'

def main():
    assert not (DOC / 'result.json').exists(), 'Use a distinct immutable diagnosis'
    sources = read(FACE_INPUT)['rows']
    facets = []
    source_bindings = []
    for source in sources:
        triangles = np.asarray(source['position'], dtype='<f8').reshape(-1, 3, 3)
        assert len(triangles) == source['triangles']
        assert digest(triangles.tobytes()) == source['worldTriangleSHA256']
        source_bindings.append({k: source[k] for k in ['uid', 'sourceSHA256', 'triangles', 'worldTriangleSHA256']})
        for triangle in triangles[:, :, [0, 2]]:
            polygon = Polygon(triangle)
            if polygon.area > 0:
                assert polygon.is_valid
                facets.append(polygon)
            elif np.any(triangle != triangle[0]):
                facets.append(LineString(triangle))
            else:
                facets.append(Point(triangle[0]))
    projection = shapely.union_all(facets)
    assert projection.is_valid and not projection.is_empty
    inputs = read(PHYSICAL / 'neighbour-inputs.json.gz')
    rows = []
    for row in inputs['rows']:
        building = row['building']
        rings = building['rings']
        footprint = Polygon(rings[0], rings[1:])
        assert footprint.is_valid and not footprint.is_empty, building['uid']
        distance = float(projection.distance(footprint))
        disjoint = bool(projection.disjoint(footprint))
        rows.append({'uid': building['uid'], 'name': building.get('name'),
                     'existingNative': row['existingNative'],
                     'strictlyDisjoint': disjoint, 'distanceM': distance,
                     'intersectionAreaM2': float(projection.intersection(footprint).area),
                     'basicParentRetentionCandidate': disjoint and distance > 0 and not row['existingNative'],
                     'requiresWholeNativeProjection': bool(row['existingNative']),
                     'installationApproved': False})
    save(DOC / 'neighbour-projection.json', {'wholeOriginalFacesAccounted': len(facets),
         'sourceBindings': source_bindings, 'originalProjectionWKB_SHA256': digest(projection.wkb),
         'rows': rows, 'diagnosticOnly': True, 'installationApproved': False})
    spec = importlib.util.spec_from_file_location('popcorn_projection_checkpoint', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
    checkpoint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checkpoint)
    checkpoint.freeze(BATCH, 'whole-original-current-neighbour-projection-v1',
        [__import__('pathlib').Path(__file__), FACE_INPUT, PHYSICAL / 'neighbour-inputs.json.gz', PHYSICAL / 'result.json'],
        {'uids': sorted(source['uid'] for source in sources), 'rows': rows,
         'wholeOriginalFacesAccounted': len(facets), 'currentFormsAccounted': len(rows),
         'humanStatus': 'held-unknown', 'requiresHumanDecision': False,
         'requiresMoreComputeOrSourceEvidence': True, 'requiresAIModelGeometry': False,
         'remainingReason': 'strict-disjoint-basic-parent-retention-and-whole-native-projection-replay-pending',
         'nextStep': 'Preserve exact parent ground only after complete region coverage proof; resolve genuinely intersecting actors independently. Full current source roles, foundation, runtime, neighbours and staged/live browser checks remain mandatory.'})
    print({'forms': len(rows), 'basicRetentionCandidates': sum(r['basicParentRetentionCandidate'] for r in rows),
           'nativeWholeProjectionRequired': sum(r['requiresWholeNativeProjection'] for r in rows)}, flush=True)

if __name__ == '__main__':
    main()
