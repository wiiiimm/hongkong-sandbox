"""Classify exact Island Industrial interfaces and combined footprint coverage."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import shapely
from shapely.geometry import Polygon, MultiPoint
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = 'government-xl-island-industrial-contact-roles-v1-20261023'
    out = base / batch
    assert not out.exists()
    names = ['government-xl-island-industrial-complete-interface-v1-20261023',
             'government-xl-all-200-original-terrain-batch-v2-20261022',
             'government-xl-island-industrial-podium-acquire-v1-20261023']
    pins, refs = {}, [Path(__file__)]
    for name in names:
        _, bound = authenticate(base / name)
        pins.update(bound)
        refs.append(base / name / 'result.json')
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    interface = take(base / names[0] / 'summary.json')
    contacts = take(base / names[0] / 'complete-contacts.json.gz')
    owner = next(r for r in take(base / names[1] / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/20270:0')
    podium = take(base / names[2] / 'summary.json')['rows'][0]
    tri = []
    for path, sha in [(owner['candidate']['path'], owner['sourceSHA256']), (podium['asset']['path'], podium['sourceSHA256'])]:
        asset = ROOT / path
        assert digest(asset.read_bytes()) == sha
        refs.append(asset)
        tri.append(decode_original_world_triangles(asset.read_bytes()))
    classified = []
    for record in contacts['contacts']:
        points = [tuple(Fraction(v) for v in point) for point in record['exactPoints']]
        faces = [rational_face(tri[i][record[key]]) for i, key in enumerate(['sourceFaceA', 'sourceFaceB'])]
        classified.append(dict(record, contactRole=contact_role(*faces, points, record['dimension'], record['primitiveDimensions'])))
    save(out / 'classified-contacts.json.gz', classified)
    forms = [owner['source']['building'], podium['currentForm']]
    polys = [Polygon(f['rings'][0], f['rings'][1:]) for f in forms]
    projected = shapely.union_all([MultiPoint(f[:, [0, 2]]).convex_hull for t in tri for f in t])
    combined = shapely.union_all(polys)
    result = dict(uids=interface['uids'], sourceSHA256ByUid=interface['sourceSHA256ByUid'],
        roles=dict(Counter(r['contactRole'] for r in classified)), allSavedContactsClassified=True,
        contacts=len(classified), combinedTargetAreaM2=combined.area,
        combinedTargetCoveredBySource=combined.intersection(projected).area / combined.area,
        combinedUncoveredM2=combined.difference(projected).area,
        combinedSourceExcessM2=projected.difference(combined).area,
        podiumFootprintCoveredByBothOriginals=polys[1].intersection(projected).area / polys[1].area,
        sourceGeometryChanges=0, installationApproved=False,
        qualification='Complete source contact-role and joint footprint diagnostics. Combined coverage does not waive individual identity, finite physical support, unrelated-form checks or source placement. No generated geometry or installation credit.')
    save(out / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_contact_role_context_v1_20261023.py', 'exact_original_shell_intersections_20261009.py', 'exact_packed_world_geometry_20261009.py'])
    module('island_roles_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'complete-original-pair-contact-role-diagnostic', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
