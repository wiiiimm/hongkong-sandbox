"""Source identity and adjoining-sheet routing before acquisition; no acceptance."""
import importlib.util
from pathlib import Path

from shapely.geometry import Polygon, box
from shapely.strtree import STRtree

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('terrain_preflight_identity', HERE / 'xl-remaining-direct.py')
_identity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_identity)


class SourceSheetIndex:
    def __init__(self, source_index):
        assert source_index['completePagination'], 'Incomplete government source sheet index'
        self.features = source_index['features']
        self.polygons = [Polygon(f['geometry']['rings'][0], f['geometry']['rings'][1:])
                         for f in self.features]
        assert all(p.is_valid for p in self.polygons)
        self.tree = STRtree(self.polygons)

    def covering_sheets(self, world_bounds):
        lo, hi = world_bounds
        assert lo[0] < hi[0] and lo[2] < hi[2], 'Source has no horizontal extent'
        # World z increases southward; HK1980 northing increases northward.
        area = box(834500 + lo[0], 816500 - hi[2],
                   834500 + hi[0], 816500 - lo[2])
        hits = []
        for idx in self.tree.query(area):
            intersection = area.intersection(self.polygons[idx]).area
            if intersection > 1e-8:
                hits.append({'sheet': self.features[idx]['attributes']['SHEETNO'],
                             'intersectionM2': intersection})
        assert hits, 'No indexed government source sheet covers the model'
        return sorted(hits, key=lambda h: h['sheet'])


def identity_proof(row, context):
    assert row['uid'] == context['uid']
    assert row['sourceSHA256'] == context['sourceSHA256']
    target = row['source']['building']
    matches = row['native']['model']['matching']['viewerMatches']
    unique = len(matches) == 1 and matches[0]['uid'] == row['uid']
    exact_object = unique and matches[0]['objectId'] == target['objectId']
    exact_csuid = unique and matches[0]['buildingCSUID'] == target['buildingCSUID']
    projection = _identity.identity_clear(context['identity'])
    proof = {'exactObjectId': exact_object, 'exactBuildingCSUID': exact_csuid,
             'uniqueViewerMatch': unique, 'detailedProjectionAccepted': projection}
    passed = bool(exact_object and exact_csuid and projection)
    return {'passed': passed, 'proof': proof,
            'reasons': [] if passed else ['source-identity-fit'],
            'qualification': 'Existing bounded source projection and exact identifiers only; no new threshold or installation credit.'}


def preflight(row, context, source_index):
    identity = identity_proof(row, context)
    sheets = source_index.covering_sheets(row['native']['model']['worldBounds'])
    primary = row['native']['sheet']
    primary_intersects = primary in {s['sheet'] for s in sheets}
    return {'uid': row['uid'], 'sourceSHA256': row['sourceSHA256'],
            'primarySheet': primary, 'primarySheetIntersects': primary_intersects,
            'identity': identity, 'indexedSheets': sheets,
            'adjacentSheets': [s['sheet'] for s in sheets if s['sheet'] != primary],
            'canStartTerrainWork': identity['passed'] and primary_intersects,
            'sourceGeometryChanges': 0, 'externalAICalls': 0, 'publication': False,
            'qualification': 'Indexed polygon intersections route original source acquisition. Actual TIN coverage, contact, foundation, neighbours, runtime and publication gates remain required.'}
