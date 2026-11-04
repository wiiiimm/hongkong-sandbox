"""Exact surface contacts against retained actual foreign actors in four worlds."""
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives

B = 'government-xl-nam-cheong-foreign-contacts-v1-20261023'
BASE = ROOT / 'docs/astra-city/government-import'
D = BASE / B
KEYS = dict(literal='completeLiteralWorldPosition',
            left='completeExplicitLeftAssociatedFloat32WorldPosition',
            balanced='completeExplicitBalancedFloat32WorldPosition')


def main():
    assert not D.exists()
    refs, pins = [Path(__file__)], {}
    foreign = 'government-xl-nam-cheong-foreign-geometry-v1-20261023'
    attrs = 'government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
    runtime = 'government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-runtime'
    for batch in [foreign, attrs, runtime]:
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

    selections = {r['uid']: r for r in take(BASE / runtime / 'selection.json.gz')['rows']}
    source_attrs = take(BASE / attrs / 'attributes.json.gz')['rows']
    native = take(BASE / foreign / 'native-attributes.json.gz')['rows'][0]
    basic = take(BASE / foreign / 'basic-attributes.json.gz')['rows'][0]
    metadata = take(BASE / foreign / 'summary.json')
    native_index = np.asarray(native['completeOriginalIndex']).reshape(-1, 3)
    native_modes = {mode: np.asarray(native[key]).reshape(-1, 3)[native_index]
                    for mode, key in KEYS.items()}
    native_modes['original'] = original(metadata['foreignNativeAssetPath'], native['sourceSHA256'])
    basic_tri = np.concatenate([np.asarray(m['position']).reshape(-1, 3)[
        np.asarray(m['index']).reshape(-1, 3)] for m in basic['meshes']])
    assert all(m['identityArithmeticAllThreeExactlyEqual'] for m in basic['meshes'])
    summaries = []
    for source in source_attrs:
        selected = selections[source['uid']]
        assert selected['sourceSHA256'] == source['sourceSHA256']
        ix = np.asarray(source['completeOriginalIndex']).reshape(-1, 3)
        modes = {mode: np.asarray(source[key]).reshape(-1, 3)[ix] for mode, key in KEYS.items()}
        modes['original'] = original(selected['candidate']['path'], source['sourceSHA256'])
        for mode, a in modes.items():
            for foreign_uid, b in [(native['uid'], native_modes[mode]), (basic['uid'], basic_tri)]:
                # Inclusive bounds only: every omitted face has a separating
                # axis against the complete opposing actor, without padding.
                ids_a = np.flatnonzero(np.all(a.max(1) >= b.min((0, 1)), axis=1) &
                                       np.all(a.min(1) <= b.max((0, 1)), axis=1))
                ids_b = np.flatnonzero(np.all(b.max(1) >= a.min((0, 1)), axis=1) &
                                       np.all(b.min(1) <= a.max((0, 1)), axis=1))
                contacts = exact_component_contacts_with_primitives(a, ids_a, b, ids_b) if len(ids_a) and len(ids_b) else dict(contacts=[], trianglePairsTested=0, allPairsExamined=True)
                assert contacts['allPairsExamined']
                tag = source['uid'].split('/')[1] + '-' + foreign_uid.split('/')[1] + '-' + mode
                save(D / (tag + '.json.gz'), contacts)
                row = dict(uid=source['uid'], foreignUid=foreign_uid, mode=mode,
                           completeSourceFaces=len(a), completeForeignFaces=len(b),
                           sourceFacesAfterInclusiveBounds=len(ids_a), foreignFacesAfterInclusiveBounds=len(ids_b),
                           trianglePairsTested=contacts['trianglePairsTested'], contacts=len(contacts['contacts']),
                           dimensions=dict(Counter(str(c['dimension']) for c in contacts['contacts'])))
                summaries.append(row)
                print(row, flush=True)
    result = dict(uids=sorted(selections), rows=summaries, sourceGeometryChanges=0,
                  allForeignActorsRetained=True, installationApproved=False,
                  qualification='Complete unmodified actor surface-pair intersection diagnostics in original and three renderer arithmetic worlds. No containment, identity, support or publication approval is inferred from zero surface contacts.')
    save(D / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py',
        'exact_original_primitive_contacts_v1.py', 'exact_original_component_contacts_20261009.py',
        'exact_original_shell_intersections_20261009.py'])
    module('foreign_contact_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        B, 'complete-actual-foreign-surface-contact-diagnostic', refs, result)


if __name__ == '__main__':
    main()
