"""Complete original/support foundations and finite contacts in four coordinate modes."""
import argparse
import subprocess
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'attributes', 'uid', 'support']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc, local = base / args.batch, HERE / 'local' / args.batch
    assert not doc.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}
    for name in [args.runtime, args.attributes]:
        _, bound = authenticate(base / name)
        refs.append(base / name / 'result.json')
        for key, sha in bound.items():
            assert key not in pins or pins[key] == sha
            pins[key] = sha
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(base / args.runtime / 'selection.json.gz')['rows']
    runtime = {r['uid']: r for r in take(HERE / 'local' / args.runtime / 'runtime-geometry.json.gz')['rows']}
    attributes = take(base / args.attributes / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attributes['rows']}
    worlds = {mode: {} for mode in ['original', 'literal', 'explicitLeftF32', 'explicitBalancedF32']}
    for uid in [args.uid, args.support]:
        row = next(r for r in selected if r['uid'] == uid)
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == attrs[uid]['sourceSHA256'] == runtime[uid]['sourceSHA256']
        refs.append(asset)
        worlds['original'][uid] = decode_original_world_triangles(asset.read_bytes())
        indices = np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1, 3)
        for mode, field in [('literal', 'completeLiteralWorldPosition'), ('explicitLeftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('explicitBalancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            worlds[mode][uid] = np.asarray(attrs[uid][field], dtype='<f8').reshape(-1, 3)[indices]
        captured = np.asarray(runtime[uid]['position']).reshape(-1, 3)[np.asarray(runtime[uid]['index']).reshape(-1, 3)]
        assert np.array_equal(captured, worlds['literal'][uid])
    payload = {mode: dict(source=dict(position=w[args.uid].reshape(-1).tolist()), support=dict(position=w[args.support].reshape(-1).tolist())) for mode, w in worlds.items()}
    inputpath, outputpath = local / 'input.json.gz', doc / 'interfaces.json.gz'
    save(inputpath, payload)
    tool = HERE / 'four_world_support_probe_v1.mjs'
    doc.mkdir(parents=True)
    subprocess.run(['node', str(tool), str(inputpath), str(outputpath)], cwd=ROOT, check=True)
    reports = {r['mode']: r['interface'] for r in read(outputpath)['rows']}
    final = module('four_world_pair_foundation', HERE / 'xl-final-script-pass.py')
    ground = np.asarray(runtime[args.uid]['drawnGroundGeometry']).reshape(-1, 3, 3)
    building = next(r['source']['building'] for r in selected if r['uid'] == args.uid)
    polygon = Polygon(building['rings'][0], building['rings'][1:])
    summary = []
    for mode, w in worlds.items():
        tri, podium = w[args.uid], w[args.support]
        foundation = final.foundation_context(tri, np.concatenate([ground, podium]), polygon)
        targets = []
        low, high = tri.min(1), tri.max(1)
        for witness in reports[mode]['unresolved']:
            point = np.asarray(witness['position'])
            broad = np.flatnonzero(np.all(low <= point+.001, axis=1) & np.all(high >= point-.001, axis=1))
            incident = [int(i) for i in broad if np.linalg.norm(np.cross(tri[i, 1]-tri[i, 0], tri[i, 2]-tri[i, 0])) > 0 and np.linalg.norm(closest(point, tri[i])-point) <= .001]
            assert incident
            targets.append(dict(witness=witness, incidentFaces=incident))
        faces = sorted({i for t in targets for i in t['incidentFaces']})
        proof = exact_finite_contacts(tri, faces, podium, list(range(len(podium)))) if faces else dict(contacts=[])
        for target in targets:
            target['positiveContacts'] = [c for c in proof['contacts'] if c['sourceFaceA'] in target['incidentFaces'] and c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 and c['dimension'] > 0]
        unresolved = sum(not t['positiveContacts'] for t in targets)
        passed = foundation['completeTerrainTriangles'] == foundation['triangles'] and foundation['fullyBuriedTriangles'] == 0 and unresolved == 0
        result = dict(uid=args.uid, supportUid=args.support, mode=mode, sourceWorldSHA256=digest(tri.astype('<f8').tobytes()), supportWorldSHA256=digest(podium.astype('<f8').tobytes()), foundation=foundation, interface=reports[mode], finiteTargets=targets, finiteProof=proof, passed=passed)
        save(doc / (mode + '.json.gz'), result)
        row = dict(mode=mode, faces=foundation['triangles'], covered=foundation['completeTerrainTriangles'], buried=foundation['fullyBuriedTriangles'], rawUnresolved=len(targets), remainingUnexplained=unresolved, passed=passed)
        summary.append(row)
        print(row, flush=True)
    result = dict(uids=[args.uid, args.support], rows=summary, allModesPassed=all(r['passed'] for r in summary), installationApproved=False, publication=False, sourceGeometryChanges=0, scriptExternalAICalls=0)
    save(doc / 'summary.json', result)
    refs.extend([inputpath, tool, HERE / 'support-interface.mjs', HERE / 'xl-final-script-pass.py', HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'exact_original_finite_triangle_contacts_20261010.py', HERE / 'pool_incident_wall_contacts_v1_20261017.py'])
    module('four_world_pair_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(args.batch, 'complete-four-world-original-pair-support', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
