"""Inspect both immutable Island Industrial originals; no acceptance transfer."""
from pathlib import Path
from collections import Counter
import shapely
from shapely.geometry import Polygon, MultiPoint
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives


def main():
    batch = 'government-xl-island-industrial-complete-interface-v1-20261023'
    base = ROOT / 'docs/astra-city/government-import'
    out = base / batch
    assert not out.exists()
    names = ['government-xl-all-200-original-terrain-batch-v2-20261022',
             'government-xl-island-industrial-podium-acquire-v1-20261023',
             'government-xl-island-industrial-podium-alternative-v1-20261023']
    pins, refs = {}, [Path(__file__)]
    for name in names:
        _, bound = authenticate(base / name)
        pins.update(bound)
        refs.append(base / name / 'result.json')
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    owner = next(r for r in take(base / names[0] / 'selection.json.gz')['rows']
                 if r['uid'] == 'landsd/20270:0')
    acquired = take(base / names[1] / 'summary.json')
    lookup = take(base / names[2] / 'lookup.json')
    assert acquired['sourceRecovered'] and len(acquired['rows']) == 1
    podium = acquired['rows'][0]
    assert podium['uid'] == 'landsd/159422:0'
    assert podium['model'] == lookup['rows'][0]['matchedOriginalModels'][0]
    sources = [(owner['candidate']['path'], owner['sourceSHA256']),
               (podium['asset']['path'], podium['sourceSHA256'])]
    triangles = []
    for path, sha in sources:
        asset = ROOT / path
        raw = asset.read_bytes()
        assert digest(raw) == sha
        refs.append(asset)
        triangles.append(decode_original_world_triangles(raw))
    assert [len(t) for t in triangles] == [11166, 537]
    forms = [owner['source']['building'], podium['currentForm']]
    projections = [shapely.union_all([MultiPoint(f[:, [0, 2]]).convex_hull for f in t])
                   for t in triangles]
    polygons = [Polygon(f['rings'][0], f['rings'][1:]) for f in forms]
    contacts = exact_component_contacts_with_primitives(
        triangles[0], range(len(triangles[0])), triangles[1], range(len(triangles[1])),
        maximum_pairs=1000000)
    assert contacts['allPairsExamined']
    save(out / 'complete-contacts.json.gz', contacts)
    rows = []
    for i in [0, 1]:
        own, projected = polygons[i], projections[i]
        rows.append(dict(uid=forms[i]['uid'], sourceFaces=len(triangles[i]),
            worldBounds=dict(min=triangles[i].min((0, 1)).tolist(), max=triangles[i].max((0, 1)).tolist()),
            sourceProjectionAreaM2=projected.area, targetAreaM2=own.area,
            targetCoveredBySource=projected.intersection(own).area / own.area,
            uncoveredCurrentFootprintM2=own.difference(projected).area,
            sourceExcessM2=projected.difference(own).area,
            sourceExcessInOtherCurrentFootprintM2=projected.difference(own).intersection(polygons[1-i]).area))
    summary = dict(uids=[f['uid'] for f in forms],
        sourceSHA256ByUid=dict(zip([f['uid'] for f in forms], [s[1] for s in sources])),
        rows=rows, completePairEnumeration=True, allOriginalPrimitivesRetained=True,
        zeroAreaContactsReceiveSurfaceSupportCredit=False,
        trianglePairsTested=contacts['trianglePairsTested'],
        contactDimensions=dict(Counter(str(c['dimension']) for c in contacts['contacts'])),
        sourceProjectedIntersectionM2=projections[0].intersection(projections[1]).area,
        identityAccepted=False, physicalSupportAccepted=False, installationApproved=False,
        sourceGeometryChanges=0,
        qualification='Complete original pair contact/projection diagnostics. Shared GeoRef, permit and contact do not establish source attribution or physical acceptance. No geometry edits, publication or installed credit.')
    save(out / 'summary.json', summary)
    refs.extend(HERE / n for n in ['exact_original_primitive_contacts_v1.py',
        'exact_packed_world_geometry_20261009.py', 'exact_original_component_contacts_20261009.py',
        'exact_original_shell_intersections_20261009.py'])
    module('island_interface_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'complete-original-adjacent-pair-diagnostic', refs, summary)
    print({k: summary[k] for k in ['trianglePairsTested', 'contactDimensions', 'rows']}, flush=True)


if __name__ == '__main__':
    main()
