"""Classify the final Lantau holds using unchanged source geometry and current forms."""
import gzip
import hashlib
import json
import struct
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOC = ROOT / 'docs/astra-city/government-import/government-lantau-final-held-review-20260921'
SOURCE = ROOT / 'docs/astra-city/government-import'
BOXES = {
    'landsd/112959:0': 'government-tai-o-northwest-600-20260921',
    'landsd/182471:0': 'government-shek-pik-fan-lau-304-20260917',
}


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def source_row(batch, uid):
    rows = read(SOURCE / batch / 'check-selection.json.gz')['rows']
    return next(row for row in rows if row['uid'] == uid)


def source_mesh(row, batch):
    entry = row['candidate']['entry']
    path = HERE / 'local' / batch / 'recovered' / entry['asset']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
    raw = gzip.decompress(path.read_bytes())
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2
    json_length, json_type = struct.unpack_from('<II', raw, 12)
    assert json_type == 0x4e4f534a
    gltf = json.loads(raw[20:20 + json_length])
    bin_offset = 20 + json_length
    bin_length, bin_type = struct.unpack_from('<II', raw, bin_offset)
    assert bin_type == 0x004e4942
    binary = memoryview(raw)[bin_offset + 8:bin_offset + 8 + bin_length]
    assert len(gltf['meshes']) == 1 and len(gltf['meshes'][0]['primitives']) == 1
    primitive = gltf['meshes'][0]['primitives'][0]

    def accessor(index):
        descriptor = gltf['accessors'][index]
        view = gltf['bufferViews'][descriptor['bufferView']]
        offset = view.get('byteOffset', 0) + descriptor.get('byteOffset', 0)
        code = {5123: 'H', 5125: 'I', 5126: 'f'}[descriptor['componentType']]
        width = {'SCALAR': 1, 'VEC3': 3}[descriptor['type']]
        return struct.unpack_from('<' + code * (descriptor['count'] * width), binary, offset)

    values = accessor(primitive['attributes']['POSITION'])
    vertices = [values[i:i + 3] for i in range(0, len(values), 3)]
    indices = accessor(primitive['indices'])
    transform = gltf['nodes'][0]['matrix']
    world = [(x + transform[12] - 834500, z + transform[13], -y + transform[14] + 816500)
             for x, y, z in vertices]
    return gltf, world, indices


def flat_box(uid, batch):
    row = source_row(batch, uid)
    entry = row['candidate']['entry']
    building = row['source']['building']
    gltf, vertices, indices = source_mesh(row, batch)
    target = Polygon(building['rings'][0], building['rings'][1:])
    xy = sorted({(round(x, 4), round(z, 4)) for x, _, z in vertices})
    source = Polygon(xy).convex_hull
    elevations = sorted({round(y, 3) for _, y, _ in vertices})
    roof = sum(all(abs(vertices[indices[i + j]][1] - entry['worldBounds'][1][1]) < .002
                   for j in range(3)) for i in range(0, len(indices), 3))
    identity = next(r['identity'] for r in read(SOURCE / batch / 'exact-pass-results.json.gz')['rows']
                    if r['uid'] == uid)
    offset = building['topHeightHKPD'] - entry['worldBounds'][1][1]
    bottom_delta = entry['worldBounds'][0][1] + offset - building['baseHeightHKPD']
    assert identity['exactObjectAndCSUID'] and len(indices) == 30 and len(xy) == 4
    assert len(elevations) == 2 and roof == 2 and len(building['rings'][0]) == 5
    assert not gltf.get('textures') and not gltf.get('images')
    assert source.intersection(target).area / min(source.area, target.area) >= .85
    assert source.centroid.distance(target.centroid) < .3 and abs(bottom_delta) < .5
    return {
        'uid': uid, 'state': 'good-to-go', 'sourceSHA256': entry['sha256'],
        'sourceTriangles': 10, 'sourceHorizontalRoofTriangles': roof,
        'sourceFootprintCorners': len(xy), 'currentFootprintCorners': 4,
        'sourceTextures': 0, 'sourceRoofLevels': elevations,
        'alignedBottomDeltaFromCurrentBaseM': bottom_delta,
        'footprintOverlapOfSmaller': source.intersection(target).area / min(source.area, target.area),
        'footprintCentroidDistanceM': source.centroid.distance(target.centroid),
        'observation': 'The unchanged government asset is only a flat-roof four-wall prism, with no texture or distinct architectural geometry. Its footprint and recorded height match the current simple form closely; importing the buried prism cannot add useful visible detail. Keep the current form.',
    }


def ngong_conflict():
    uid = 'landsd/168823:0'
    row = source_row('government-ngong-ping-peaks-473-20260918', uid)
    entry = row['candidate']['entry']
    bounds = entry['worldBounds']
    _, vertices, indices = source_mesh(row, 'government-ngong-ping-peaks-473-20260918')
    triangles = [Polygon([(vertices[indices[i + j]][0], vertices[indices[i + j]][2])
                          for j in range(3)]) for i in range(0, len(indices), 3)]
    footprint = unary_union([triangle for triangle in triangles if triangle.area > .0001])
    envelope = box(bounds[0][0], bounds[0][2], bounds[1][0], bounds[1][2])
    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    installed = {model['uid'] for url in manifest['officialModelCatalogues']
                 for model in read(ROOT / '3d-viewer' / url)['models']}
    forms = []
    for tile in manifest['tiles']:
        x0, z0, x1, z1 = tile['bounds']
        if not envelope.intersects(box(x0, z0, x1, z1)):
            continue
        for building in read(ROOT / '3d-viewer' / tile['url'])['buildings']:
            polygon = Polygon(building['rings'][0], building['rings'][1:])
            if polygon.intersection(footprint).area > 0:
                forms.append({'uid': building['uid'], 'csuid': building.get('buildingCSUID'),
                              'installedOfficial': building['uid'] in installed,
                              'coveredFraction': polygon.intersection(footprint).area / polygon.area})
    assert len(forms) == 4 and any(f['installedOfficial'] and f['coveredFraction'] > .5
                                   for f in forms if f['uid'] != uid)
    installed_row = source_row('government-ngong-ping-peaks-473-20260918', 'landsd/181268:0')
    _, other_vertices, other_indices = source_mesh(installed_row, 'government-ngong-ping-peaks-473-20260918')

    def surfaces(points, order):
        result = []
        for i in range(0, len(order), 3):
            triangle = [points[order[i + j]] for j in range(3)]
            projection = Polygon([(x, z) for x, _, z in triangle])
            if projection.area > .0001:
                result.append((projection, triangle))
        return result

    def height(triangle, x, z):
        (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = triangle
        denominator = (z2 - z3) * (x1 - x3) + (x3 - x2) * (z1 - z3)
        a = ((z2 - z3) * (x - x3) + (x3 - x2) * (z - z3)) / denominator
        b = ((z3 - z1) * (x - x3) + (x1 - x3) * (z - z3)) / denominator
        return a * y1 + b * y2 + (1 - a - b) * y3

    crossing = 0
    for a, av in surfaces(vertices, indices):
        for b, bv in surfaces(other_vertices, other_indices):
            if not a.intersects(b):
                continue
            intersection = a.intersection(b)
            if intersection.area <= .0001:
                continue
            difference = [height(av, x, z) - height(bv, x, z)
                          for x, z in intersection.exterior.coords]
            if min(difference) <= 0 <= max(difference):
                crossing += 1
    assert crossing > 0
    return {'uid': uid, 'state': 'held', 'sourceSHA256': entry['sha256'],
            'sourceTriangles': entry['triangles'], 'sourceBounds': bounds,
            'projectedSourceAreaM2': footprint.area,
            'surfaceCrossingPairsWithInstalledUid181268': crossing,
            'intersectingForms': sorted(forms, key=lambda f: f['uid']),
            'observation': 'The source mesh extends across four distinct mapped CSUIDs, including one separately installed government model. Their upward surfaces intersect in 3D; importing the whole complex without an assembly-level replacement would duplicate or obscure it. Component identity and suppression need source-level proof.'}


def pui_o_conflict():
    proof = read(SOURCE / 'government-lantau-pui-o-overlap-probe-20260921/terrain-proof.json')
    assert proof['uid'] == 'landsd/195308:0' and proof['maxRenderedHeightAdjustmentM'] > 100
    return {'uid': proof['uid'], 'state': 'held', 'regionalOverlapProbe': proof,
            'observation': 'The unchanged model passes a trial terrain alignment, but that correction moves 3,803 rendered vertices and shifts some terrain over 113 m. The regional terrain seam needs bounded source reconciliation before installation.'}


def main():
    rows = [flat_box(uid, batch) for uid, batch in BOXES.items()]
    rows.extend([ngong_conflict(), pui_o_conflict()])
    report = {'policy': 'source-preserving-final-lantau-disposition-v1',
              'sourceGeometryChanges': 0, 'aiGeometryCalls': 0, 'rows': rows}
    DOC.mkdir(parents=True, exist_ok=True)
    (DOC / 'decision.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps([{'uid': row['uid'], 'state': row['state']} for row in rows]))


if __name__ == '__main__':
    main()
