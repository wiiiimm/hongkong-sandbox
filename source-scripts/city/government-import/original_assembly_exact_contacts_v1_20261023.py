"""Enumerate exact original surface contacts for explicitly selected source pairs."""
import argparse
from pathlib import Path
from collections import Counter
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--capture', required=True)
    p.add_argument('--pair', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    _, pins = authenticate(base / a.capture)
    path = base / a.capture / 'selection.json.gz'
    assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
    sources = {r['uid']: r for r in read(path)['rows']}
    pairs = [s.split(',') for s in a.pair]
    assert all(len(pair) == 2 and pair[0] != pair[1] and set(pair) <= set(sources) for pair in pairs)
    assert len(set(map(tuple, pairs))) == len(pairs)
    refs = [Path(__file__), base / a.capture / 'result.json', path]
    geometry = {}
    for uid in {u for pair in pairs for u in pair}:
        source = sources[uid]
        asset = ROOT / source['candidate']['path']
        assert digest(asset.read_bytes()) == source['sourceSHA256']
        refs.append(asset)
        geometry[uid] = decode_original_world_triangles(asset.read_bytes())
        assert len(geometry[uid]) == source['triangles']
    rows = []
    for left, right in pairs:
        first, second = geometry[left], geometry[right]
        result = exact_component_contacts_with_primitives(first, range(len(first)), second, range(len(second)))
        assert result['allPairsExamined']
        save(doc / (left.split('/')[1] + '-' + right.split('/')[1] + '.json.gz'), result)
        row = dict(uid=left, supportUid=right, completeSourceFaces=len(first), completeSupportFaces=len(second),
                   trianglePairsTested=result['trianglePairsTested'], contacts=len(result['contacts']),
                   contactDimensions=dict(Counter(str(c['dimension']) for c in result['contacts'])))
        rows.append(row)
        print(row, flush=True)
    result = dict(uids=sorted(sources), rows=rows, sourceGeometryChanges=0, installationApproved=False,
                  sourceSHA256ByUid={u: r['sourceSHA256'] for u, r in sources.items()},
                  qualification='Every inclusive-AABB candidate pair checked with exact rational original point/segment/triangle contacts. Degenerate primitives preserved without surface-support credit. Contact presence does not establish architectural intent, support, acceptable collision or installation.')
    save(doc / 'summary.json', result)
    refs.extend(HERE / n for n in ['exact_packed_world_geometry_20261009.py', 'exact_original_primitive_contacts_v1.py', 'exact_original_component_contacts_20261009.py', 'exact_original_shell_intersections_20261009.py'])
    module('assembly_exact_contacts_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'complete-exact-original-assembly-surface-contacts', refs, result)


if __name__ == '__main__':
    main()
