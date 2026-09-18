"""Recover V City tower/support models from the pinned government directory; never AI."""
import json
import sys
import zipfile
from pathlib import Path

from shapely.geometry import MultiPoint, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import ROOT, HERE, read, save, digest
sys.path.insert(0, str(HERE.parent / 'citywide-native'))
from download import acquire
from convert import _convert_one

SHEET = '6-SW-6A'
DOC = ROOT / 'docs/astra-city/government-import/government-xl-50-20260913/second-pass/third-pass/terrain-v-city'
LOCAL = HERE / 'local/government-xl-50-second-20260913/third-pass-v-city-supports'
SOURCE = HERE / 'local/government-xl-50-second-20260913/sheets' / SHEET
TARGETS = {
    'landsd/243886:0': 'B153292865802062G0',
    'landsd/248373:0': 'B153692849701063C0',
    'landsd/248374:0': 'B153822854901063C0',
    'landsd/248375:0': 'B153952860301063C0',
    'landsd/248376:0': 'B153482840901062G0',
    'landsd/248377:0': 'B153952843701062G0',
    'landsd/25490:0': 'B153712834601063C0',
    'landsd/25648:0': 'B153562844301063C0',
    'landsd/25826:0': 'B154122836901063C0',
    'landsd/308947:0': 'B153262834301063C0',
}


def main():
    directory = read(SOURCE / 'directory/result.json')
    assert directory['directorySHA256'] == 'f99a5f97551f696b4f05470e1dd803b7d1e1a6ff10a23217c7b2ec497bb2b3bc'
    by_model = {row['modelId']: row for row in directory['models']}
    assert set(TARGETS.values()) <= set(by_model)
    directory['models'] = [by_model[model_id] for model_id in TARGETS.values()]
    out = LOCAL / 'source'
    acquired = acquire(directory, SOURCE / 'directory/zip-directory.bin', out / 'original')
    (out / 'packed').mkdir(parents=True, exist_ok=True)

    manifest = read(ROOT / '3d-viewer/city/data/manifest.json')
    forms = {}
    tile_hashes = {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        raw = path.read_bytes()
        for building in json.loads(raw)['buildings']:
            if building['uid'] in TARGETS:
                forms[building['uid']] = (building, tile['url'])
                tile_hashes[tile['url']] = digest(raw)
    assert set(forms) == set(TARGETS)

    rows = []
    with zipfile.ZipFile(out / 'original' / (SHEET + '.zip')) as archive:
        for uid, model_id in TARGETS.items():
            converted = _convert_one(
                archive,
                archive.getinfo('BUILDING/' + model_id + '/' + model_id + '.gltf'),
                out / 'decoded',
                out / 'packed',
                {},
                {'modelId': model_id},
            )
            building, tile = forms[uid]
            footprint = Polygon(building['rings'][0], building['rings'][1:])
            hull = MultiPoint([[x, z] for x, _, z in converted['terrainSamples']['position']]).convex_hull
            intersection = hull.intersection(footprint).area
            entry = {
                **converted['asset'],
                'uid': uid,
                'modelId': model_id,
                'objectId': building['objectId'],
                'buildingCSUID': building['buildingCSUID'],
                'label': building['name'],
                'recordedBaseHeight': building['baseHeightHKPD'],
                'recordedTopHeight': building['topHeightHKPD'],
                'worldBounds': converted['worldBounds'],
                'triangles': converted['triangles'],
                'footprintCentroidDistanceMetres': hull.centroid.distance(footprint.centroid),
                'overlapOfSmallerFootprint': intersection / min(hull.area, footprint.area),
                'placementReviewed': False,
                'priority': 'unreviewed',
                'publicationApproved': False,
                'rootTranslation': [-834500, 0, 816500],
                'sourceTile': SHEET,
            }
            asset = out / 'packed' / entry['asset']
            assert digest(asset.read_bytes()) == entry['sha256']
            rows.append({
                'uid': uid,
                'source': {'building': building, 'tile': tile, 'tileSHA256': tile_hashes[tile]},
                'candidate': {'path': str(asset), 'entry': entry},
                'native': {'sheet': SHEET, 'model': converted, 'directPinnedRecovery': True},
            })
    save(LOCAL / 'support-runtime.json.gz', {'rows': rows, 'aiCalls': 0, 'modelGeometryChanges': 0})
    save(DOC / 'support-source-recovery.json', {
        'sheet': SHEET,
        'directorySHA256': directory['directorySHA256'],
        'sourceETag': directory['etag'],
        'models': [{
            'uid': row['uid'],
            'modelId': row['candidate']['entry']['modelId'],
            'sourceSHA256': row['candidate']['entry']['sha256'],
            'triangles': row['candidate']['entry']['triangles'],
            'overlapOfSmallerFootprint': row['candidate']['entry']['overlapOfSmallerFootprint'],
            'centroidDistanceMetres': row['candidate']['entry']['footprintCentroidDistanceMetres'],
        } for row in rows],
        'acquisition': {key: value for key, value in acquired.items() if key != 'source'},
        'aiCalls': 0,
        'modelGeometryChanges': 0,
        'publication': False,
    })
    print(json.dumps({'models': len(rows), 'triangles': sum(row['candidate']['entry']['triangles'] for row in rows), 'aiCalls': 0}))


if __name__ == '__main__':
    main()
