"""Classify every saved exact original pair contact without granting acceptance."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role

B = 'government-xl-nam-cheong-fu-yun-contact-roles-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D = BASE / B


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    batches = ['government-xl-nam-cheong-fu-yun-complete-interface-v2-20261023',
               'government-xl-after-fu-wong-nam-cheong-capture-v1-20261023',
               'government-xl-nam-cheong-fu-yun-acquire-v1-20261023']
    for batch in batches:
        _, bound = authenticate(BASE / batch)
        pins.update(bound)
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    contacts = take(BASE / batches[0] / 'complete-contacts.json.gz')
    summary = take(BASE / batches[0] / 'summary.json')
    selection = take(BASE / batches[1] / 'selection.json.gz')
    nam = next(r for r in selection['rows'] if r['uid'] == 'landsd/268867:0')
    fu = take(BASE / batches[2] / 'summary.json')
    triangles = []
    for path, sha in [(nam['candidate']['path'], nam['sourceSHA256']),
                      (fu['asset']['path'], fu['sourceSHA256'])]:
        asset = ROOT / path
        assert digest(asset.read_bytes()) == sha
        refs.append(asset)
        triangles.append(decode_original_world_triangles(asset.read_bytes()))
    assert contacts['allPairsExamined']
    classified = []
    for record in contacts['contacts']:
        points = [tuple(Fraction(v) for v in point) for point in record['exactPoints']]
        faces = [rational_face(triangles[i][record[key]])
                 for i, key in enumerate(['sourceFaceA', 'sourceFaceB'])]
        classified.append(dict(record, contactRole=contact_role(
            *faces, points, record['dimension'], record['primitiveDimensions'])))
    save(D / 'classified-contacts.json.gz', classified)
    result = dict(uids=['landsd/268867:0', 'landsd/270874:0'],
                  sourceSHA256ByUid=summary['sourceSHA256ByUid'],
                  allSavedContactsClassified=len(classified) == len(contacts['contacts']),
                  trianglePairsTested=contacts['trianglePairsTested'],
                  roles=dict(Counter(r['contactRole'] for r in classified)),
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Exact contact role diagnostics only. Shared edges and planes do not establish ownership or approval; transverse crossings require investigation.')
    save(D / 'summary.json', result)
    refs.extend(HERE / name for name in ['exact_contact_role_context_v1_20261023.py',
        'exact_packed_world_geometry_20261009.py', 'exact_original_shell_intersections_20261009.py'])
    module('pair_role_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        B, 'exact-original-pair-contact-role-diagnostic', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
