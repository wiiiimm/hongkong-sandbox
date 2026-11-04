"""Full current replacement-parent scope; provisional actors get no install credit."""
import sys
import json
import subprocess
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from hierarchical_group_changed_actor_scope_v2_20261026 import separation

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-silvercord-lippo-full-current-parent-scope-v3-20261103'
PRIOR = 'government-xl-after-observatory-current-native-bounds-v1-20261102'
ATTR = 'government-xl-tower3-june-garden-six-originals-current-v1-20261102-attributes'
CANDIDATE = 'government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
PARENT = 'city/data/government-xl-one-peking-cycle-original-terrain-20261101.json'
NEW_CATALOGUE = 'city/data/official-models/government-xl-june-garden-qualified-stage-v4-20261103/catalogue.json'
LOCAL = HERE / 'local' / BATCH
UIDS = ['landsd/233997:0', 'landsd/231645:0']


def owned():
    lease = read(LOCAL / 'reservation.json'); assert reservations.owns(lease)
    refs = [Path(__file__), HERE / 'exact_packed_world_bounds_v3_20261010.py',
            HERE / 'hierarchical_group_changed_actor_scope_v2_20261026.py']; pins = {}
    def take(batch, name):
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name; assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    inventory = take(PRIOR, 'complete-bounds.json.gz'); attrs = take(ATTR, 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows']) == 6
    for path, sha in attrs['inputHashes'].items():
        if path.endswith(('.js', '.mjs')):
            assert digest((ROOT / path).read_bytes()) == sha; refs.append(ROOT / path)
    for name in ['official-model-assets.js', 'geo.js']:
        path = ROOT / '3d-viewer/city' / name
        assert digest(path.read_bytes()) == pins[PRIOR][str(path.relative_to(ROOT))]; refs.append(path)
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'; mh = digest(manifest_path.read_bytes())
    manifest = read(manifest_path); refs.append(manifest_path)
    models = {}; assets = {}; old_catalogues = set()
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url; sha = digest(path.read_bytes()); key = str(path.relative_to(ROOT)); refs.append(path)
        catalogue = read(path); assert catalogue['rootTranslation'] == [-834500, 0, 816500]
        if key in pins[PRIOR]:
            assert sha == pins[PRIOR][key], 'Prior catalogue metadata changed'; old_catalogues.add(key)
        else: assert url == NEW_CATALOGUE, 'Unknown additional current catalogue'
        for model in catalogue['models']:
            uid = model['uid']; assert uid not in models; models[uid] = model; assets[uid] = path.parent / model['asset']
    prior_raw = subprocess.check_output(['git', 'show', 'HEAD:3d-viewer/city/data/manifest.json'], cwd=ROOT)
    assert digest(prior_raw) == pins[PRIOR]['3d-viewer/city/data/manifest.json'], 'Prior manifest must be exact frozen bytes'
    prior_manifest = json.loads(prior_raw)
    prior_path = BASE / BATCH / 'prior-current-manifest.json'; prior_path.parent.mkdir(parents=True, exist_ok=True); prior_path.write_bytes(prior_raw); refs.append(prior_path)
    expected_old_catalogues = {'3d-viewer/' + url for url in prior_manifest['officialModelCatalogues']}
    assert old_catalogues == expected_old_catalogues
    rows = inventory['rows']; assert len(rows) == 7095 and len({r['uid'] for r in rows}) == len(rows)
    by = {r['uid']: r for r in rows}; additions = set(models) - set(by); captured = {r['uid']: r for r in attrs['rows']}
    assert additions == set(captured) and set(by) <= set(models) and len(models) == 7101
    for uid, asset in assets.items():
        assert digest(asset.read_bytes()) == models[uid]['sha256']; refs.append(asset)
        if uid in by: assert by[uid]['sourceSHA256'] == models[uid]['sha256']
    for uid in sorted(additions):
        captured_row = captured[uid]; original = packed_world_bounds(assets[uid].read_bytes())
        assert original['sourceSHA256'] == captured_row['sourceSHA256'] == models[uid]['sha256']
        rows.append(dict(uid=uid, sourceSHA256=models[uid]['sha256'],
                         completeFourWorldBounds=[original['originalWholeSourceBounds'], captured_row['completeLiteralWorldBounds'],
                                                 captured_row['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],
                                                 captured_row['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],
                         completeOriginalPOSITIONProof=original, provisionalCurrentActorOnly=True))
    proposal = take(CANDIDATE, 'summary.json'); path = ROOT / proposal['candidate']['path']
    assert digest(path.read_bytes()) == proposal['candidate']['sha256']; new = read(path); refs.append(path)
    old_path = ROOT / '3d-viewer' / PARENT; assert digest(old_path.read_bytes()) == proposal['replacedParent']['sha256']
    old = read(old_path); refs.append(old_path); base_path = ROOT / '3d-viewer/city/data/terrain.json'; parent = read(base_path); refs.append(base_path)
    builder = module('pair_full_parent_extent', HERE / 'resolve_pass_indexed_parent_clipping_v2.py')
    boxes = [list(builder.extent(old['coarseCells'], parent)), list(builder.extent(new['coarseCells'], parent))]
    def visit(node):
        if node.get('nativeMesh'):
            values = np.asarray(node['nativeMesh']['position']).reshape(-1, 3)
            for points in [values, values.astype('<f4').astype('<f8')]:
                lo, hi = points.min(0), points.max(0); boxes.append([float(lo[0]), float(lo[2]), float(hi[0]), float(hi[2])])
        for child in node.get('patches', []): visit(child)
    north_ref=proposal['additionalTopLevelPatch'];north_path=ROOT/north_ref['path'];assert digest(north_path.read_bytes())==north_ref['sha256'];north=read(north_path);refs.append(north_path)
    assert digest(base_path.read_bytes())==north_ref['parentSHA256'];boxes.append(list(builder.extent(north['coarseCells'],parent)));visit(north)
    visit(old); visit(new); full_boxes = [list(b) for b in sorted(set(map(tuple, boxes)))]
    def contains(a, b): return a[0] <= b[0] and a[1] <= b[1] and a[2] >= b[2] and a[3] >= b[3]
    boxes = [b for i, b in enumerate(full_boxes) if not any(i != j and contains(a, b) for j, a in enumerate(full_boxes))]
    assert boxes and all(any(contains(a, b) for a in boxes) for b in full_boxes)
    native_rows = []; affected = []
    for row in rows:
        bounds = np.asarray(row['completeFourWorldBounds']).reshape(-1, 3)
        lo, hi = bounds.min(0)[[0, 2]], bounds.max(0)[[0, 2]]
        proofs = [separation(lo, hi, box) for box in boxes]; touches = not all(p['strictlyDisjoint'] for p in proofs)
        native_rows.append(dict(row, touchesFullReplacementParent=touches, completeParentExtentSeparations=proofs))
        if touches: affected.append(row['uid'])
    basic = []; support_owners = {}
    for model in models.values():
        for dependency in model.get('supportDependencies', []):
            uid = dependency['uid'] if isinstance(dependency, dict) else dependency
            if uid not in models: support_owners.setdefault(uid, []).append(model['uid'])
    support_forms = {}
    for tile in manifest['tiles']:
        path = ROOT / '3d-viewer' / tile['url']; sha = digest(path.read_bytes()); key = str(path.relative_to(ROOT))
        assert sha == inventory['currentFormTileHashes'][key]; refs.append(path)
        for form in read(path)['buildings']:
            points = np.asarray([p for ring in form['rings'] for p in ring]); lo, hi = points.min(0), points.max(0)
            proofs = [separation(lo, hi, box) for box in boxes]
            if not all(p['strictlyDisjoint'] for p in proofs): basic.append(form)
            if form['uid'] in support_owners: support_forms[form['uid']] = form
    assert set(support_forms) == set(support_owners)
    out = BASE / BATCH; save(out / 'complete-current-actor-bounds.json.gz', dict(rows=native_rows))
    save(out / 'full-parent-form-obligations.json.gz', basic)
    save(out / 'all-registered-basic-supports.json.gz', dict(forms=support_forms, owners=support_owners))
    result = dict(uids=UIDS, currentManifestSHA256=mh, currentDetailedActorsAccounted=len(rows),
                  verifiedPriorInstalledActors=7095, provisionalCurrentActors=sorted(additions), provisionalInstallationCredit=0,
                  fullReplacementClosedXZBoxes=full_boxes, exactRedundantBoxContainmentEnvelopes=boxes, affectedNativeUids=sorted(affected), basicFormsInFullParentScope=len(basic),
                  allRegisteredNonNativeSupportsAccounted=len(support_forms), allCurrentAssetBytesAndPriorMetadataVerified=True,
                  installationApproved=False, physicalAcceptance=False, publication=False,
                  qualification='Full replaced coarse extent and every old/new packed vertex, including unused and Float32 positions. Complete prior original/literal/Float32 actor census reused only under identical old asset/catalogue/transform bytes. Six provisional current actors have frozen source-bound renderer attributes and fresh complete original POSITION bounds; no installed approval or count is transferred. Any touching native/BASIC form remains a complete regression obligation.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease) and digest(manifest_path.read_bytes()) == mh
    module('pair_full_current_parent_scope_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'full-current-parent-coarse-packed-four-world-native-and-basic-scope', list(dict.fromkeys(refs)), result)
    print(dict(currentActors=len(rows), affectedNative=len(affected), basicForms=len(basic), installationApproved=False), flush=True)


if __name__ == '__main__':
    if '--owned' in sys.argv: owned()
    else:
        assert not LOCAL.exists() and not (BASE / BATCH).exists()
        claim = reservations.claim('pair-full-current-parent-scope-' + str(uuid.uuid4()), ['building:'+u for u in UIDS] + ['immutable-source-proof:'+BATCH], batch=BATCH, ttl=3600)
        assert claim['ok']
        execute_reserved(claim['reservation'], LOCAL / 'reservation.json', [sys.executable, __file__, '--owned'])
