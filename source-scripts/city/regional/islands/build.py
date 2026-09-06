"""Build HKS-122/123 island detail from retained OSM geometry, without requests.

Only writes the islands regional package and its adjacent evidence. Source island
polygons filter features; they do not replace the existing coastline or terrain.
"""
import collections
import gzip
import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from build_city import ROOT, OUT, ORIGIN, xy, coords, geometry, polys, packed
from pyproj import Transformer
from shapely.geometry import Point, Polygon, LineString
from shapely.strtree import STRtree

DOCS = ROOT / 'docs/astra-city/regional/islands'
INVERSE = Transformer.from_crs(2326, 4326, always_xy=True)
PUBLIC_PIER_REFERENCE = 'https://www.cedd.gov.hk/eng/about-us/organisation/ceo/pwd/port-main/public_piers/nti/index.html'
BEACH_REFERENCE = 'https://www.lcsd.gov.hk/en/beach/'


def source_id(element):
    return f'{element["type"]}/{element["id"]}'


def load_sources():
    manifest = json.loads((OUT / 'manifest.json').read_text())
    entries = []
    files = [ROOT / source['file'] for source in manifest['sources']]
    detail_files = sorted((HERE / 'snapshots').glob('*.json.gz'))
    for path in files + detail_files:
        raw = gzip.decompress(path.read_bytes())
        data = json.loads(raw)
        entries.append((data['osm3s']['timestamp_osm_base'], path, data, hashlib.sha256(raw).hexdigest()))
    records, detail_records, sources = {}, {}, []
    for stamp, path, data, sha in sorted(entries, key=lambda e: (e[0], str(e[1]))):
        sources.append({'file': str(path.relative_to(ROOT)), 'snapshot': stamp, 'sha256': sha, 'elements': len(data['elements']), 'role': 'island-detail' if path in detail_files else 'existing-city'})
        for element in data['elements']:
            records[source_id(element)] = element
            if path in detail_files:
                detail_records[source_id(element)] = element
    return manifest, records, detail_records, sources


def source_shape(element):
    polygon = geometry(element)
    if polygon is not None and not polygon.is_empty:
        return polygon
    if element.get('geometry'):
        points = coords(element['geometry'])
        return LineString(points) if len(points) > 1 else Point(points[0])
    if 'lon' in element:
        return Point(xy(element['lon'], element['lat']))
    raise ValueError('Source has no usable geometry: ' + source_id(element))


class ArrivalAudit:
    """Same terrain diagonal and clearance contract as the city navigation mesh."""
    def __init__(self, manifest, records):
        self.dem = json.loads((OUT / 'terrain.json').read_text())
        self.georef = self.dem['meta']['georef']
        self.blocks, self.heights = [], []
        for tile in manifest['tiles']:
            for building in json.loads((ROOT / '3d-viewer' / tile['url']).read_text())['buildings']:
                poly = Polygon(building['rings'][0], building['rings'][1:]).buffer(0)
                if poly.is_empty:
                    continue
                self.blocks.append(poly)
                self.heights.append((building['base'] + building['minimum'], building['base'] + building['height']))
        self.block_tree = STRtree(self.blocks)
        self.paths, self.path_ids = [], []
        for oid, element in sorted(records.items()):
            tags = element.get('tags', {})
            if tags.get('highway') not in ('footway', 'pedestrian', 'path', 'living_street'):
                continue
            if tags.get('access') in ('private', 'no') or tags.get('foot') == 'no' or tags.get('area') == 'yes':
                continue
            if tags.get('location') == 'underground' or tags.get('tunnel') in ('yes', 'building_passage') or tags.get('bridge') == 'yes' or tags.get('layer', '0') not in ('0', 0):
                continue
            if element.get('geometry') and len(element['geometry']) > 1:
                self.paths.append(LineString(coords(element['geometry'])))
                self.path_ids.append(oid)
        self.path_tree = STRtree(self.paths)

    def ground(self, x, z, rendered=False):
        g, dem = self.georef, self.dem
        c, r = (x + ORIGIN[0] - g['bE']) / g['aE'], (ORIGIN[1] - z - g['bN']) / g['aN']
        if not (0 <= c < dem['w'] - 1 and 0 <= r < dem['h'] - 1):
            return -1000, False
        i, j, w = int(c), int(r), dem['w']
        u, v = c - i, r - j
        a, b, d, e = [dem['elev'][idx] for idx in (j*w+i, j*w+i+1, (j+1)*w+i, (j+1)*w+i+1)]
        dry = all(value > 0 for value in ((a, b, d) if u+v <= 1 else (b, d, e)))
        if rendered:
            a, b, d, e = [max(1.2, value) if value > 0 else -4 for value in (a, b, d, e)]
        height = a+(b-a)*u+(d-a)*v if u+v <= 1 else e+(d-e)*(1-u)+(b-e)*(1-v)
        return max(1.2, height) if rendered else height, dry

    def valid(self, point):
        raw, dry = self.ground(point.x, point.y)
        y, _ = self.ground(point.x, point.y, rendered=True)
        if raw <= .8 or not dry:
            return False
        disc = point.buffer(1.2)
        for i in self.block_tree.query(disc):
            lo, hi = self.heights[i]
            # Check raw and rendered samples to agree with both the shared builder
            # audit and rendered character height near minimum-height land.
            if (y+1.8 > lo and y < hi or raw+1.8 > lo and raw < hi) and self.blocks[i].intersects(disc):
                return False
        for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            neighbour, dry = self.ground(point.x+dx, point.y+dz)
            rendered, _ = self.ground(point.x+dx, point.y+dz, rendered=True)
            if not dry or abs(neighbour-raw) >= 1.5 or abs(rendered-y) >= 1.5:
                return False
        return True

    def nearest(self, centre):
        candidates = []
        for i in self.path_tree.query(centre.buffer(1000)):
            path = self.paths[i]
            near = path.project(centre)
            for shift in (0, -5, 5, -15, 15, -40, 40, -90, 90, -180, 180):
                source_point = path.interpolate(max(0, min(path.length, near+shift)))
                # Audit exactly the 0.1 m coordinates the browser will consume.
                point = Point(round(source_point.x, 1), round(source_point.y, 1))
                if point.distance(centre) <= 1000 and self.valid(point):
                    candidates.append((point.distance(centre), self.path_ids[i], point, path.distance(point)))
        return min(candidates, key=lambda c: (c[0], c[1])) if candidates else None


def classify(tags):
    if tags.get('man_made') == 'pier':
        return 'pier'
    if tags.get('natural') == 'beach':
        return 'beach'
    if tags.get('highway') == 'pedestrian' and tags.get('area') == 'yes':
        return 'plaza'
    if tags.get('leisure') == 'pitch':
        return 'pitch'
    if tags.get('aeroway') == 'apron':
        return 'apron'
    return None


def main():
    config = json.loads((HERE / 'config.json').read_text())
    manifest, records, detail_records, sources = load_sources()
    source_geometries = {}
    def shape(oid):
        if oid not in source_geometries:
            if oid not in records:
                raise ValueError('Missing retained source ' + oid)
            source_geometries[oid] = source_shape(records[oid])
        return source_geometries[oid]
    centres = {entry['id']: shape(entry['source']).centroid for entry in config['places']}
    islands = [(entry, shape(entry['source']).buffer(25)) for entry in config['islands']]
    section_anchors = collections.defaultdict(list)
    for entry in config['places']:
        section_anchors[entry['sectionId']].append(centres[entry['id']])
    # Do not duplicate outer ways that are represented by a complete tagged area relation.
    relation_members = {member['ref'] for element in detail_records.values() if element['type'] == 'relation' and classify(element.get('tags', {})) for member in element.get('members', []) if member.get('role') == 'outer'}
    surfaces, omissions = [], collections.Counter()
    retained_tags = ('man_made', 'natural', 'highway', 'area', 'leisure', 'aeroway', 'sport', 'surface', 'access', 'foot', 'floating', 'layer', 'name:zh', 'name:zh-Hant', 'name:en', 'ref', 'source', 'note', 'construction:man_made', 'building', 'building:levels')
    for oid, element in sorted(detail_records.items()):
        tags = element.get('tags', {})
        kind = classify(tags)
        if not kind:
            continue
        if element['type'] == 'way' and element['id'] in relation_members:
            omissions['duplicate-multipolygon-member'] += 1
            continue
        geo = geometry(element)
        if geo is None or geo.is_empty:
            omissions['open-or-empty-source-area'] += 1
            continue
        owners = [(entry, mask) for entry, mask in islands if mask.intersects(geo)]
        if not owners:
            omissions['outside-assigned-islands'] += 1
            continue
        if tags.get('construction:man_made') == 'pier' or tags.get('construction') or tags.get('abandoned') == 'yes' or tags.get('disused') == 'yes':
            omissions['construction-or-inactive'] += 1
            continue
        if tags.get('location') in ('roof', 'rooftop', 'underground') or tags.get('indoor') == 'yes':
            omissions['indoor-or-non-ground-surface'] += 1
            continue
        island, _ = max(owners, key=lambda pair: geo.intersection(pair[1]).area)
        centre = geo.centroid
        section = min(island['sections'], key=lambda sid: (min(centre.distance(anchor) for anchor in section_anchors[sid]), sid))
        # Round and validate complete source polygons. Never buffer an open pier
        # to invent its width, and never clip a complete feature at a section edge.
        for part_index, original in enumerate(polys(geo)):
            simplified = original.simplify(.5, preserve_topology=True)
            rings = packed(simplified)
            result = Polygon(rings[0], rings[1:])
            if not result.is_valid or result.area <= .1:
                rings = packed(original)
                result = Polygon(rings[0], rings[1:])
            if not result.is_valid or result.area <= .1:
                omissions['invalid-at-decimetre-precision'] += 1
                continue
            surfaces.append({'id': f'islands:{oid}:{part_index}', 'kind': kind, 'sectionId': section, 'rings': rings, 'source': 'https://www.openstreetmap.org/'+oid, 'name': tags.get('name:en', tags.get('name', '')), 'tags': {key: tags[key] for key in retained_tags if key in tags}, 'area': round(result.area, 2)})
    print('Built', len(surfaces), 'mapped surface polygons', flush=True)
    audit = ArrivalAudit(manifest, records)
    places, arrivals = [], []
    for entry in config['places']:
        centre = centres[entry['id']]
        if entry.get('aerialOnly') and not shape(entry['source']).covers(centre):
            centre = shape(entry['source']).representative_point()
        x, z = round(centre.x, 1), round(centre.y, 1)
        lon, lat = INVERSE.transform(x + ORIGIN[0], ORIGIN[1] - z)
        p = {key: value for key, value in entry.items() if key != 'source'}
        p.update(lat=round(lat, 6), lon=round(lon, 6), source='https://www.openstreetmap.org/'+entry['source'], target=[x, round(max(35, audit.ground(x, z, True)[0]+30), 1), z])
        result = None if entry.get('aerialOnly') else audit.nearest(centre)
        if result:
            distance, path, point, off_path = result
            p.update(spawn=[point.x, point.y], terrainY=round(audit.ground(point.x, point.y, True)[0], 3), arrivalSource='https://www.openstreetmap.org/'+path, arrivalVerified=True)
            arrivals.append({'id': p['id'], 'sectionId': p['sectionId'], 'result': 'dry-public-path-building-clear', 'source': p['source'], 'arrivalSource': p['arrivalSource'], 'sourceToArrivalMetres': round(distance, 2), 'roundingDistanceFromPathMetres': round(off_path, 4), 'spawn': p['spawn'], 'terrainY': p['terrainY']})
            print(p['id'], 'checked path', path, round(distance), 'm from source', flush=True)
        else:
            p['aerialOnly'] = True
            if not entry.get('aerialOnly'):
                p['description'] += ' Aerial visit only: no suitable public-path arrival passed the existing terrain and building checks within 1 km.'
            arrivals.append({'id': p['id'], 'sectionId': p['sectionId'], 'result': 'aerial-only', 'source': p['source'], 'reason': 'No public walking arrival requested for this island' if entry.get('aerialOnly') else 'No public-path point within 1 km passed dry-triangle, slope and building-clearance checks'})
            print(p['id'], 'aerial only', flush=True)
        places.append(p)
    sections = []
    for entry in config['sections']:
        section_surfaces = [surface for surface in surfaces if surface['sectionId'] == entry['id']]
        section_places = [place for place in places if place['sectionId'] == entry['id']]
        sections.append({'id': entry['id'], 'status': 'mapped-detail-added', 'note': f'{entry["title"]}: {len(section_places)} source-grounded visit points and {len(section_surfaces)} retained mapped surface polygons. Arrival checks are local clearance checks; detailed architecture, coastline and full-route review remain pending.', 'sources': sorted(set([p['source'] for p in section_places] + [PUBLIC_PIER_REFERENCE, BEACH_REFERENCE]))})
    package = {'schemaVersion': 1, 'regionGroup': 'islands', 'places': places, 'surfaces': surfaces, 'buildingOverrides': [], 'sections': sections}
    encoded = json.dumps(package, ensure_ascii=False, separators=(',', ':'))+'\n'
    (OUT / 'regional').mkdir(parents=True, exist_ok=True)
    (OUT / 'regional/islands.json').write_text(encoded)
    DOCS.mkdir(parents=True, exist_ok=True)
    report = {'schemaVersion': 1, 'producer': 'GPT-6 Astra geography agent', 'issues': ['HKS-122', 'HKS-123'], 'licence': 'ODbL-1.0', 'attribution': '© OpenStreetMap contributors', 'licenceURL': 'https://www.openstreetmap.org/copyright', 'generator': str((HERE / 'build.py').relative_to(ROOT)), 'configuration': str((HERE / 'config.json').relative_to(ROOT)), 'output': '3d-viewer/city/data/regional/islands.json', 'outputSha256': hashlib.sha256(encoded.encode()).hexdigest(), 'outputBytes': len(encoded.encode()), 'crs': 'EPSG:2326', 'origin': ORIGIN, 'axes': 'x = easting - 834500; z = 816500 - northing; metres', 'counts': {'sections': len(sections), 'places': len(places), 'walkableArrivals': sum(not place.get('aerialOnly') for place in places), 'aerialOnly': sum(bool(place.get('aerialOnly')) for place in places), 'surfaces': len(surfaces), 'surfaceKinds': dict(sorted(collections.Counter(surface['kind'] for surface in surfaces).items())), 'vertices': sum(sum(len(ring) for ring in surface['rings']) for surface in surfaces), 'buildingOverrides': 0, 'omissions': dict(sorted(omissions.items()))}, 'sources': sources, 'islandMasks': config['islands'], 'precision': 'Retained OSM footprints projected into HK1980; simplification at 0.5 m with preserved topology, coordinates rounded to 0.1 m. This is encoding precision, not a claim of survey accuracy. Source island polygons with a 25 m buffer only assign complete features to this package; they do not edit coastline. Section labels use nearest configured anchor on the source island, not official boundaries.', 'arrivalPolicy': 'Mapped footway/pedestrian/path/living_street, excluding explicit private/no-foot access, underground, bridge and nonzero layer; maximum 1000 m from source feature centre. Rounded spawn and four points 2 m away must lie on fully dry existing terrain triangles with less than 1.5 m elevation difference. The 1.2 m character disc must clear vertically overlapping buildings. Both raw and rendered terrain are checked. A checked point does not establish a complete accessible route.', 'limits': ['No new buildings or estimated building heights are invented; existing house/Tai O massing rules remain unchanged.', 'Piers are mapped visual surface footprints; no surveyed deck elevation or walking collision is asserted.', 'Tai O promenade source way/115584709 carries a note about imagery distortion. Tai O tidal channels remain unresolved by the existing 70 m terrain.', 'Existing terrain can smooth narrow coastlines, small islands and beaches. No channel/coastline correction is generated.', 'Open pier lines are omitted because their source supplies no closed width footprint. Explicit rooftop, indoor and underground surfaces are omitted because this layer has no sourced structural elevation.', 'Construction/inactive surfaces and duplicate multipolygon members are omitted.', 'Source sparse village geometry remains sparse; these additions do not complete architectural or route review.', 'Historic Lantau map images were not used or modified.'], 'arrivals': arrivals, 'sections': [{'id': section['id'], 'places': sum(p['sectionId'] == section['id'] for p in places), 'surfaces': sum(s['sectionId'] == section['id'] for s in surfaces)} for section in sections]}
    (DOCS / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report['counts'], indent=2), flush=True)


if __name__ == '__main__':
    main()
