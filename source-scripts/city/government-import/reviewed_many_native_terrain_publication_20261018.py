"""Bounded plural terrain replacement; retain every existing publisher guard."""
import copy

def stage_top_level(module, plan, original, manifest, edits, report, delegate):
    entries = plan.get('topLevelTerrainPatches', [])
    plural = [entry for entry in entries if entry.get('replacesMany')]
    if not plural:
        return delegate(plan, original, manifest, edits, report)
    assert len(entries) == len(plural) == 1
    entry = plural[0]
    rows = entry['replacesMany']
    assert not entry.get('replaces') and 2 <= len(rows) <= 16
    assert len({row['url'] for row in rows}) == len(rows)
    assert len({uid for row in rows for uid in row['retainedUids']}) == sum(len(row['retainedUids']) for row in rows), 'Repeated retained native actor'
    parent = module.load(module.ROOT / '3d-viewer/city/data/terrain.json')
    new = module.load(module.ROOT / entry['source'])
    module.validate_patch(new, parent)
    old_patches = []
    for row in rows:
        matches = [item for item in original.get('terrainPatches', []) if item['url'] == row['url']]
        assert len(matches) == 1
        path = module.ROOT / '3d-viewer' / row['url']
        assert module.sha(path) == row['sha256']
        old = module.load(path)
        assert old.get('nativeMesh') and new.get('nativeMesh') and not old.get('patches') and not new.get('patches')
        synthetic = {key: value for key, value in entry.items() if key != 'replacesMany'}
        synthetic.update(replaces=row, nativeReview=row['nativeReview'])
        decision = module.review_native_top_level_replacement(synthetic, old, new)
        assert set(row['retainedUids']) == set(decision['retainedUids']) == set(old['meta']['targetUids']), 'Plural replacement must retain every original native actor'
        a, b, c, d = old['coarseCells']
        x0, z0, x1, z1 = new['coarseCells']
        assert x0 <= a and z0 <= b and x1 >= c and z1 >= d
        assert old.get('hydro') == new.get('hydro')
        module.check_patch_overlap(old, old_patches)
        old_patches.append(old)
    first, *rest = rows
    delegated_entry = {key: value for key, value in entry.items() if key != 'replacesMany'}
    delegated_entry.update(replaces=first, nativeReview=first['nativeReview'])
    delegated_plan = {**plan, 'topLevelTerrainPatches': [delegated_entry]}
    removed = {row['url'] for row in rest}
    delegated_original = copy.deepcopy(original)
    delegated_original['terrainPatches'] = [item for item in original['terrainPatches'] if item['url'] not in removed]
    manifest['terrainPatches'] = [item for item in manifest['terrainPatches'] if item['url'] not in removed]
    delegate(delegated_plan, delegated_original, manifest, edits, report)
    assert report['replacedTerrainPatches'] == [dict(url=first['url'], sha256=first['sha256'], oldAssetRetained=True)]
    report['replacedTerrainPatches'].extend(dict(url=row['url'], sha256=row['sha256'], oldAssetRetained=True) for row in rest)
    report['explicitPluralNativeReplacementReviews'] = [row['nativeReview'] for row in rows]
