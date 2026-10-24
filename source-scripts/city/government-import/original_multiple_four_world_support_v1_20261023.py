"""Whole original support/foundation diagnostics in all four source representations."""
import argparse, subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'supported']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--support', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base, modes = ROOT / 'docs/astra-city/government-import', ['original', 'literal', 'leftF32', 'balancedF32']
    doc = base / a.batch
    assert not doc.exists()
    refs, cache = [Path(__file__)], {}
    def take(name, path):
        if name not in cache:
            cache[name] = authenticate(base / name)[1]
            refs.append(base / name / 'result.json')
        assert digest(path.read_bytes()) == cache[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = {r['uid']: r for r in take(a.runtime, base / a.runtime / 'selection.json.gz')['rows']}
    geometry = {r['uid']: r for r in take(a.runtime, HERE / 'local' / a.runtime / 'runtime-geometry.json.gz')['rows']}
    attrs = take(a.attributes, base / a.attributes / 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attrs['rows']}
    assert len(a.support)==len(set(a.support)) and 0<len(a.support)<=7 and a.supported not in a.support
    assert {a.supported,*a.support} <= set(selected)&set(attrs)&set(geometry)
    fields = dict(literal='completeLiteralWorldPosition', leftF32='completeExplicitLeftAssociatedFloat32WorldPosition', balancedF32='completeExplicitBalancedFloat32WorldPosition')
    worlds, sources = {}, {}
    for uid in [a.supported, *a.support]:
        row, attr, g = selected[uid], attrs[uid], geometry[uid]
        path = ROOT / row['candidate']['path']
        raw = path.read_bytes()
        assert digest(raw) == row['sourceSHA256'] == attr['sourceSHA256'] == g['sourceSHA256']
        refs.append(path)
        sources[uid] = row['sourceSHA256']
        index = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = dict(original=decode_original_world_triangles(raw))
        for mode, field in fields.items():
            worlds[uid][mode] = np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[index]
        literal = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        assert np.array_equal(literal, worlds[uid]['literal'])
        assert all(len(t) == row['triangles'] for t in worlds[uid].values())
    ground = np.asarray(geometry[a.supported]['drawnGroundGeometry']).reshape(-1, 3, 3)
    f = selected[a.supported]['source']['building']
    polygon = Polygon(f['rings'][0], f['rings'][1:])
    final = module('four_mode_support_foundation', HERE / 'xl-final-script-pass.py')
    tool, rows = HERE / 'wave_retained_basic_support_v1_20261017.mjs', []
    for mode in modes:
        target = worlds[a.supported][mode]
        support = np.concatenate([worlds[u][mode] for u in a.support])
        folder = doc / mode
        position = target.reshape(-1).tolist()
        save(folder / 'input.json.gz', dict(rows=[dict(uid=a.supported, position=position, index=list(range(len(position) // 3)))], podium=support.tolist()))
        with (folder / 'worker.log').open('w') as log:
            subprocess.run(['node', str(tool), str(folder.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        result = read(folder / 'support.json.gz')
        assert len(result['rows']) == 1 and result['rows'][0]['uid'] == a.supported
        proof = result['rows'][0]['proof']
        for path, sha in result['inputHashes'].items():
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
        foundation = final.foundation_context(target, np.concatenate([ground, support]), polygon)
        passed = proof['passed'] and foundation['completeTerrainTriangles'] == foundation['triangles'] and foundation['fullyBuriedTriangles'] == foundation['fullyBuriedUpwardTriangles'] == 0 and foundation['minimumGapM'] >= -.5
        row = dict(mode=mode, sourceWorldSHA256ByUid={u: digest(worlds[u][mode].astype('<f8').tobytes()) for u in sources}, support=proof, compoundFoundation=foundation, passed=passed)
        save(folder / 'diagnostic.json', row)
        rows.append(row)
        print(dict(mode=mode, passed=passed, samples=proof['samples'], strictContacts=proof['strictContacts'], unresolved=len(proof['unresolved']), buried=foundation['fullyBuriedTriangles']), flush=True)
    summary = dict(uids=sorted(sources), sourceSHA256ByUid=sources, supportedUid=a.supported, supportUids=a.support, rows=rows, allFourModesPassed=all(r['passed'] for r in rows), physicalSupportAccepted=False, installationApproved=False, sourceGeometryChanges=0, qualification='Complete indexed original facets in original/literal/leftFloat32/balancedFloat32 coordinate representations. Existing strict support/embedding limits and full compound-foundation checks preserved. Diagnostic triangle-array expansion preserves every face/coordinate/order, with no source asset, pose or runtime geometry changes. Physical/source identity/continuous/browser/publication approval remains separate.')
    save(doc / 'summary.json', summary)
    refs += [tool, HERE / 'xl-final-script-pass.py', HERE / 'exact_packed_world_geometry_20261009.py']
    module('four_world_pair_support_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'four-world-original-multiple-support-support-diagnostic', refs, summary)


if __name__ == '__main__':
    main()
