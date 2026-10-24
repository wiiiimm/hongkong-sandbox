"""Classify exact original contact roles for both retained neighbouring actors."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role

B = 'government-xl-nam-cheong-foreign-contact-roles-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D = BASE / B


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    geometry = 'government-xl-nam-cheong-foreign-geometry-v1-20261023'
    contacts = 'government-xl-nam-cheong-foreign-contacts-v1-20261023'
    runtime = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
    for batch in [geometry, contacts, runtime]:
        _, bound = authenticate(BASE / batch)
        pins.update(bound)
        refs.append(BASE / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    def original(path, sha):
        path = ROOT / path
        assert digest(path.read_bytes()) == sha
        refs.append(path)
        return decode_original_world_triangles(path.read_bytes())

    selected = next(r for r in take(BASE / runtime / 'selection.json.gz')['rows'] if r['uid'] == 'landsd/268867:0')
    source = original(selected['candidate']['path'], selected['sourceSHA256'])
    metadata = take(BASE / geometry / 'summary.json')
    native = original(metadata['foreignNativeAssetPath'], metadata['foreignNativeSourceSHA256'])
    basic = take(BASE / geometry / 'basic-attributes.json.gz')['rows'][0]
    basic_faces = np.concatenate([np.asarray(m['position']).reshape(-1, 3)[np.asarray(m['index']).reshape(-1, 3)] for m in basic['meshes']])
    rows = []
    for uid, foreign in [('landsd/262871:0', native), ('landsd/233291:0', basic_faces)]:
        records = take(BASE / contacts / ('268867:0-' + uid.split('/')[1] + '-original.json.gz'))
        assert records['allPairsExamined']
        classified = []
        for c in records['contacts']:
            points = [tuple(Fraction(v) for v in point) for point in c['exactPoints']]
            role = contact_role(rational_face(source[c['sourceFaceA']]), rational_face(foreign[c['sourceFaceB']]), points, c['dimension'], c['primitiveDimensions'])
            classified.append(dict(c, contactRole=role))
        save(D / (uid.split('/')[1] + '.json.gz'), classified)
        rows.append(dict(foreignUid=uid, totalContacts=len(classified),
                         roles=dict(Counter(c['contactRole'] for c in classified)),
                         sourceFaces=sorted({c['sourceFaceA'] for c in classified}),
                         foreignFaces=sorted({c['sourceFaceB'] for c in classified}),
                         foreignRetained=True))
    result = dict(uids=[selected['uid']], sourceSHA256=selected['sourceSHA256'], rows=rows,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Original-world exact contact-role evidence only. Contact roles do not establish ownership, architectural intent, acceptable collision or permission to remove a foreign actor.')
    save(D / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_original_shell_intersections_20261009.py', 'exact_contact_role_context_v1_20261023.py'])
    module('foreign_role_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B, 'exact-original-foreign-contact-role-diagnostic', refs, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
