"""Check retained-source fidelity, section coverage and every island arrival."""
import collections
import hashlib
import json
import math
from shapely.geometry import Point, Polygon
from build import HERE, DOCS, OUT, ROOT, ArrivalAudit, load_sources, source_shape, classify, polys


def main():
    path = OUT / 'regional/islands.json'
    raw = path.read_bytes()
    package = json.loads(raw)
    provenance = json.loads((DOCS / 'provenance.json').read_text())
    config = json.loads((HERE / 'config.json').read_text())
    manifest, records, detail_records, sources = load_sources()
    expected = {f'10.{i}' for i in range(1, 17)} | {'11.6', '11.7', '14.8'}
    assert package['schemaVersion'] == 1 and package['regionGroup'] == 'islands'
    assert len(package['sections']) == 19 and {s['id'] for s in package['sections']} == expected
    assert {p['sectionId'] for p in package['places']} == expected
    assert {s['sectionId'] for s in package['surfaces']} == expected
    assert len({p['id'] for p in package['places']}) == len(package['places'])
    assert len({s['id'] for s in package['surfaces']}) == len(package['surfaces'])
    legacy = json.loads((ROOT / 'source-scripts/city/destinations.json').read_text())['places']
    assert not set(legacy).intersection(p['id'] for p in package['places']), 'Existing URL must not be replaced'
    assert not package['buildingOverrides'], 'This package does not invent height measurements'
    assert hashlib.sha256(raw).hexdigest() == provenance['outputSha256']
    assert len(raw) == provenance['outputBytes']
    assert sources == provenance['sources'], 'Source provenance or chronology changed'
    for source in sources:
        if source['role'] == 'island-detail':
            snapshot = ROOT / source['file']
            assert snapshot.with_suffix('.query.txt').is_file(), 'Missing reproducible query'
    maximum_displacement, max_area_delta, total_area = 0, 0, 0
    holes = 0
    shapes = {}
    for surface in package['surfaces']:
        assert surface['sectionId'] in expected
        assert all(len(ring) >= 4 and ring[0] == ring[-1] for ring in surface['rings'])
        assert all(math.isfinite(v) for ring in surface['rings'] for point in ring for v in point)
        polygon = Polygon(surface['rings'][0], surface['rings'][1:])
        assert polygon.is_valid and polygon.area > .1
        oid = surface['source'].removeprefix('https://www.openstreetmap.org/')
        assert oid in detail_records and classify(detail_records[oid].get('tags', {})) == surface['kind']
        if oid not in shapes:
            shapes[oid] = source_shape(detail_records[oid])
        original = polys(shapes[oid])[int(surface['id'].rsplit(':', 1)[1])]
        displacement = original.hausdorff_distance(polygon)
        assert displacement <= .58, (surface['id'], displacement)
        assert len(original.interiors) == len(polygon.interiors), 'Source hole removed'
        assert abs(surface['area'] - polygon.area) <= .011
        maximum_displacement = max(maximum_displacement, displacement)
        max_area_delta = max(max_area_delta, abs(original.area-polygon.area))
        total_area += polygon.area
        holes += len(polygon.interiors)
    audit = ArrivalAudit(manifest, records)
    paths_by_id = dict(zip(audit.path_ids, audit.paths))
    arrivals = []
    for place in package['places']:
        oid = place['source'].removeprefix('https://www.openstreetmap.org/')
        assert oid in records
        assert len(place['target']) == 3 and all(math.isfinite(v) for v in place['target'])
        if place.get('aerialOnly'):
            assert place['id'] in ('heilingchauaerial', 'sokoislandsaerial')
            assert not place.get('arrivalVerified'), 'Aerial visit cannot assert a walking arrival'
            continue
        assert place.get('arrivalVerified') and place.get('arrivalSource')
        point = Point(place['spawn'])
        assert audit.valid(point), 'Unsafe rounded spawn: '+place['id']
        arrival_id = place['arrivalSource'].removeprefix('https://www.openstreetmap.org/')
        assert arrival_id in paths_by_id, 'Arrival source is not a retained public path'
        assert paths_by_id[arrival_id].distance(point) <= .071, 'Rounded spawn leaves source path'
        source_distance = source_shape(records[oid]).centroid.distance(point)
        assert source_distance <= 1000
        assert abs(place['terrainY']-audit.ground(point.x, point.y, True)[0]) <= .001
        arrivals.append({'id': place['id'], 'sourceDistanceMetres': round(source_distance, 2), 'result': 'passed'})
    report = {'result': 'passed', 'sections': len(expected), 'places': len(package['places']), 'checkedArrivals': len(arrivals), 'intentionalAerialOnly': 2, 'surfacePolygons': len(package['surfaces']), 'surfaceAreaSquareMetres': round(total_area, 2), 'preservedSourceHoles': holes, 'maximumSourceBoundaryDisplacementMetres': round(maximum_displacement, 4), 'maximumSurfaceAreaChangeSquareMetres': round(max_area_delta, 2), 'outputSha256': hashlib.sha256(raw).hexdigest(), 'terrainSha256': hashlib.sha256((OUT / 'terrain.json').read_bytes()).hexdigest(), 'manifestSha256': hashlib.sha256((OUT / 'manifest.json').read_bytes()).hexdigest(), 'checks': ['all 19 assigned sections have new visit points and mapped surfaces', 'no legacy destination IDs replaced', 'all retained source hashes and chronology match provenance', 'closed valid source polygon rings and preserved holes', 'every output boundary within 0.58 m of its source before simplification and rounding', 'every walking spawn remains within 0.071 m of its mapped public path', 'exact rounded arrivals pass fully dry triangle, slope and 1.2 m building clearance checks', 'aerial-only destinations do not claim walking support', 'no invented building-height overrides'], 'limitations': ['Local data checks do not establish complete walkable routes or detailed architectural accuracy.', 'Rendered surface heights inherit existing terrain; no surveyed pier elevations or shoreline corrections are supplied.'], 'arrivals': arrivals}
    (DOCS / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'arrivals'}, indent=2))


if __name__ == '__main__':
    main()
