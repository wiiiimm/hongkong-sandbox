"""Classify the held Ngong Ping source using exact mesh components, without editing geometry."""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOC = ROOT / 'docs/astra-city/government-import/government-lantau-ngong-final-20260921'
BATCH = 'government-ngong-ping-peaks-473-20260918'
UID = 'landsd/168823:0'

spec = importlib.util.spec_from_file_location('held_review', HERE / 'lantau-final-held-review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def main():
    row = review.source_row(BATCH, UID)
    entry = row['candidate']['entry']
    _, vertices, indices = review.source_mesh(row, BATCH)
    target = Polygon(row['source']['building']['rings'][0])
    installed = Polygon(review.source_row(BATCH, 'landsd/181268:0')['source']['building']['rings'][0])
    keys = [tuple(round(value, 3) for value in point) for point in vertices]
    distinct = {key: position for position, key in enumerate(dict.fromkeys(keys))}
    mapped = [distinct[key] for key in keys]
    parent = list(range(len(distinct)))

    def find(value):
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    for offset in range(0, len(indices), 3):
        a, b, c = (mapped[indices[offset + j]] for j in range(3))
        parent[find(b)] = find(a)
        parent[find(c)] = find(a)
    components = collections.defaultdict(list)
    for offset in range(0, len(indices), 3):
        components[find(mapped[indices[offset]])].append(offset)

    target_components = []
    for offsets in components.values():
        triangles = [[vertices[indices[offset + j]] for j in range(3)] for offset in offsets]
        projection = unary_union([Polygon([(x, z) for x, _, z in triangle]) for triangle in triangles])
        if projection.intersection(target).area <= 0.01:
            continue
        target_components.append((triangles, projection))
    assert len(target_components) == 1 and len(components) == 73
    triangles, projection = target_components[0]
    roof = [triangle for triangle in triangles
            if max(point[1] for point in triangle) - min(point[1] for point in triangle) < 0.002
            and Polygon([(x, z) for x, _, z in triangle]).area > 0.001]
    roof_polygon = unary_union([Polygon([(x, z) for x, _, z in triangle]) for triangle in roof])
    assert len(triangles) == 16 and len(roof) == 4
    assert len(roof_polygon.exterior.coords) - 1 == 6
    assert len(target.exterior.coords) - 1 == 19
    assert len({round(triangle[0][1], 3) for triangle in roof}) == 1
    coverage = projection.intersection(target).area / target.area
    assert coverage > 0.997 and projection.intersection(installed).area == 0
    prior = review.read(ROOT / 'docs/astra-city/government-import/government-lantau-final-held-review-20260921/decision.json')
    previous = next(item for item in prior['rows'] if item['uid'] == UID)
    assert previous['surfaceCrossingPairsWithInstalledUid181268'] == 20
    report = {
        'uid': UID, 'state': 'good-to-go',
        'policy': 'source-component-shape-comparison-v1',
        'sourceSHA256': entry['sha256'], 'sourceTriangles': len(indices) // 3,
        'sourceComponents': len(components), 'targetComponentTriangles': len(triangles),
        'targetCoverage': coverage, 'targetComponentInstalledStationOverlapM2': 0,
        'sourceRoofTriangles': len(roof), 'sourceRoofLevelsHKPD': sorted({round(triangle[0][1], 3) for triangle in roof}),
        'sourceRoofCorners': len(roof_polygon.exterior.coords) - 1,
        'currentFootprintCorners': len(target.exterior.coords) - 1,
        'wholeSourceCrossingsWithInstalledStation': previous['surfaceCrossingPairsWithInstalledUid181268'],
        'observation': 'The exact source file bundles 73 disconnected components across several mapped forms. The one component for this form is a 16-triangle flat-roof shell with six roof-outline corners; the current 19-corner mapped form retains more footprint detail. The other government components overlap an installed station. Keep the current form; no source import or geometry edit adds useful visible detail.',
        'aiModellingCalls': 0, 'modelGeometryChanges': 0,
        'sourceReviewSHA256': hashlib.sha256((ROOT / 'docs/astra-city/government-import/government-lantau-final-held-review-20260921/decision.json').read_bytes()).hexdigest(),
    }
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / 'decision.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: report[key] for key in ('uid', 'state', 'sourceComponents', 'targetComponentTriangles', 'sourceRoofCorners', 'currentFootprintCorners', 'targetCoverage')}))


if __name__ == '__main__':
    main()
