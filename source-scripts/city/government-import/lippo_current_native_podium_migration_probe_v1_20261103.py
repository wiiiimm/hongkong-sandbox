"""Measure the exact installed tower on the proposed original Lippo podium.

No dependency, catalogue, terrain, source, review or acceptance mutation.
"""
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon

from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-lippo-current-native-podium-migration-probe-v1-20261103'
LOCAL = HERE / 'local' / BATCH
RUNTIME = 'government-xl-silvercord-lippo-complete-floor-runtime-v2-20261103'
ATTRIBUTES = 'government-xl-silvercord-lippo-original-attributes-v1-20261101'
NATIVE = 'government-xl-silvercord-lippo-changed-native-check-v1-20261103'
TOWER, PODIUM = 'landsd/239465:0', 'landsd/231645:0'
EXPECTED = {
    TOWER: '2ca41f96bdce41f47c95891182450878c1fc694b12c3ae22bbeb29ff07cc276c',
    PODIUM: 'cfe390f024ac815a8c8ae3f422724fd72e4cd5c164e7325f9404cd81fc1b46da',
}
FIELDS = [('literal', 'completeLiteralWorldPosition'),
          ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
          ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]


def owned():
    lease = read(LOCAL / 'reservation.json')
    assert reservations.owns(lease)
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}

    def take(batch, path):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take(RUNTIME, BASE / RUNTIME / 'selection.json.gz')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes())
    assert manifest_sha == selection['manifestSHA256']
    manifest = read(manifest_path)
    refs.append(manifest_path)
    catalogue_refs, matches = [], []
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        catalogue_refs.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
        for entry in read(path)['models']:
            if entry['uid'] == TOWER:
                matches.append((entry, path))
            assert entry['uid'] != PODIUM, 'Podium is already installed; do not repeat acquisition'
    assert len(matches) == 1
    entry, catalogue = matches[0]
    assert entry['sha256'] == EXPECTED[TOWER] and entry['triangles'] == 3597
    prior_dependency = [d for d in entry.get('supportDependencies', []) if isinstance(d, dict) and d['uid'] == PODIUM]
    assert prior_dependency == [dict(uid=PODIUM, state='surveyed-footprint-fallback', csuid='3551417531P20050812')]
    asset = (catalogue.parent / entry['asset']).resolve()
    assert asset.is_relative_to(ROOT) and digest(asset.read_bytes()) == EXPECTED[TOWER]
    refs.append(asset)
    pointer_path = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    pointer_sha = digest(pointer_path.read_bytes())
    pointer = read(pointer_path)
    refs.append(pointer_path)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        installed = db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s', (pointer['snapshotId'], TOWER)).fetchall()
    assert installed == [('installed-verified', EXPECTED[TOWER])]
    inputs = take(NATIVE, BASE / NATIVE / 'neighbour-inputs.json.gz')
    form = next(r['building'] for r in inputs['rows'] if r['building']['uid'] == TOWER)
    assert form['buildingCSUID'] == entry['buildingCSUID']
    tower_input = out / 'tower-renderer-input.json.gz'
    save(tower_input, dict(currentManifest=dict(path=str(manifest_path.relative_to(ROOT)), sha256=manifest_sha),
                          currentCatalogueRefs=catalogue_refs,
                          evidenceRefs=[dict(path=str((BASE / NATIVE / 'neighbour-inputs.json.gz').relative_to(ROOT)), sha256=digest((BASE / NATIVE / 'neighbour-inputs.json.gz').read_bytes()))],
                          expectedSourceByUid={TOWER: [EXPECTED[TOWER], 3597]},
                          rows=[dict(uid=TOWER, entry=entry, building=form, path=str(asset.relative_to(ROOT)))]))
    tool = HERE / 'selected_original_render_attributes_v1.mjs'
    tower_output = out / 'tower-attributes.json.gz'
    with (out / 'tower-renderer.log').open('w') as log:
        subprocess.run(['node', str(tool), str(tower_input.relative_to(ROOT)), str(tower_output.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1800)
    attrs = read(tower_output)
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows']) == 1
    for path, sha in attrs['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    tower_attr = attrs['rows'][0]
    podium = next(r for r in selection['rows'] if r['uid'] == PODIUM)
    podium_asset = ROOT / podium['candidate']['path']
    assert podium['sourceSHA256'] == EXPECTED[PODIUM] and digest(podium_asset.read_bytes()) == EXPECTED[PODIUM]
    attributes = take(ATTRIBUTES, BASE / ATTRIBUTES / 'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    podium_attr = next(r for r in attributes['rows'] if r['uid'] == PODIUM)
    geometry = next(r for r in take(RUNTIME, HERE / 'local' / RUNTIME / 'runtime-geometry.json.gz')['rows'] if r['uid'] == PODIUM)
    assert geometry['sourceSHA256'] == EXPECTED[PODIUM]
    worlds = {}
    for uid, attr, path in [(TOWER, tower_attr, asset), (PODIUM, podium_attr, podium_asset)]:
        assert attr['sourceSHA256'] == EXPECTED[uid] and digest(path.read_bytes()) == EXPECTED[uid]
        refs.append(path)
        indices = np.asarray(attr['completeOriginalIndex']).reshape(-1, 3)
        worlds[uid] = dict(original=decode_original_world_triangles(path.read_bytes()))
        worlds[uid].update({mode: np.asarray(attr[field], dtype='<f8').reshape(-1, 3)[indices] for mode, field in FIELDS})
        assert all(len(tri) == len(indices) for tri in worlds[uid].values())
    actual = np.asarray(geometry['position']).reshape(-1, 3)[np.asarray(geometry['index']).reshape(-1, 3)]
    assert np.array_equal(actual, worlds[PODIUM]['literal'])
    ground = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    kernel = module('lippo_current_migration_foundation', HERE / 'xl-final-script-pass.py')
    support_tool = HERE / 'wave_retained_basic_support_v1_20261017.mjs'
    rows = []
    for mode, target in worlds[TOWER].items():
        assert reservations.owns(lease)
        support = worlds[PODIUM][mode]
        folder = out / mode
        save(folder / 'input.json.gz', dict(rows=[dict(uid=TOWER, position=target.reshape(-1).tolist(), index=list(range(target.size // 3)))], podium=support.tolist()))
        with (folder / 'worker.log').open('w') as log:
            subprocess.run(['node', str(support_tool), str(folder.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=1800)
        raw = read(folder / 'support.json.gz')
        assert len(raw['rows']) == 1 and raw['rows'][0]['uid'] == TOWER
        for path, sha in raw['inputHashes'].items():
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
        proof = raw['rows'][0]['proof']
        foundation = kernel.foundation_context(target, np.concatenate([ground, support]), Polygon(form['rings'][0], form['rings'][1:]))
        row = dict(mode=mode, sourceWorldSHA256ByUid={uid: digest(worlds[uid][mode].astype('<f8').tobytes()) for uid in EXPECTED},
                   support=proof, compoundFoundation=foundation)
        save(folder / 'diagnostic.json.gz', row)
        rows.append(dict(mode=mode, samples=proof['samples'], strictContacts=proof['strictContacts'], unresolved=len(proof['unresolved']), strictSupportPassed=proof['passed'],
                         completeFaces=foundation['triangles'], completeGroundFaces=foundation['completeTerrainTriangles'], fullyBuried=foundation['fullyBuriedTriangles'], upwardBuried=foundation['fullyBuriedUpwardTriangles'], minimumGapM=foundation['minimumGapM']))
        print(rows[-1], flush=True)
    assert reservations.owns(lease) and digest(manifest_path.read_bytes()) == manifest_sha
    for ref in catalogue_refs:
        assert digest((ROOT / ref['path']).read_bytes()) == ref['sha256']
    assert digest(pointer_path.read_bytes()) == pointer_sha
    result = dict(uids=[TOWER, PODIUM], sourceSHA256ByUid=EXPECTED, currentManifestSHA256=manifest_sha, snapshotId=pointer['snapshotId'], installedTowerEntry=entry,
                  retainedOriginalDependency=prior_dependency, groundProviderUid=PODIUM, completeActualDrawnGroundSHA256=digest(ground.tobytes()), rows=rows,
                  sourceGeometryChanges=0, sourcePoseChanges=0, catalogueChanges=0, supportMigrationApproved=False, physicalAcceptance=False, installationApproved=False, publication=False,
                  qualification='Four complete coordinate streams and unchanged strict support/compound-foundation kernels. The current installed tower remains on its old surveyed fallback contract. Raw failures require investigation; no new support or publication approval is inferred.')
    save(out / 'summary.json', result)
    refs.extend([tower_output, tool, support_tool, HERE / 'xl-final-script-pass.py', HERE / 'exact_packed_world_geometry_20261009.py'])
    module('lippo_current_migration_probe_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'exact-current-installed-tower-proposed-original-podium-support-diagnostic', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    if '--owned' in sys.argv:
        owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('lippo-native-migration-' + str(uuid.uuid4()), ['building:' + u for u in [TOWER, PODIUM]] + ['immutable-source-proof:' + BATCH], batch=BATCH, ttl=3600)
        assert claim['ok'], claim
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
