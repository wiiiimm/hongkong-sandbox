"""Stage an immutable catalogue URL replacement for one availability annotation.

This is a preparation helper, not a publisher or an approval adapter. Callers
must still run the original publisher's dependency and acceptance checks.
"""
import hashlib
import json
from pathlib import Path, PurePosixPath

from original_availability_catalogue_v1_20261027 import verify


def stage(root, spec, manifest, edits, read_bytes):
    root = Path(root).resolve()
    viewer = root / '3d-viewer'
    paths = {}
    for key in ('url', 'destination'):
        relative = PurePosixPath(spec[key])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert relative.as_posix() == spec[key]
        path = viewer / relative
        assert path.resolve().is_relative_to(viewer.resolve())
        assert not path.is_symlink()
        paths[key] = path
    old, new = paths['url'], paths['destination']
    assert old != new and old.parent == new.parent, 'Preserve relative asset resolution'
    assert old.suffix == new.suffix == '.json'
    assert old not in edits and new not in edits and not new.exists()
    urls = manifest['officialModelCatalogues']
    assert urls.count(spec['url']) == 1 and spec['destination'] not in urls
    before_raw = read_bytes(old)
    assert hashlib.sha256(before_raw).hexdigest() == spec['beforeSHA256']
    source = root / spec['source']
    assert source.resolve().is_relative_to(root) and not source.is_symlink()
    after_raw = read_bytes(source)
    assert hashlib.sha256(after_raw).hexdigest() == spec['afterSHA256']
    before, after = json.loads(before_raw), json.loads(after_raw)
    result = verify(before, after, spec['uid'], spec['activationGroup'])
    entry = next(m for m in before['models'] if m['uid'] == spec['uid'])
    asset_relative = PurePosixPath(entry['asset'])
    assert not asset_relative.is_absolute() and '..' not in asset_relative.parts
    asset = old.parent / asset_relative
    assert asset.resolve().is_relative_to(viewer.resolve()) and not asset.is_symlink()
    asset_raw = read_bytes(asset)
    assert len(asset_raw) == entry['bytes']
    assert hashlib.sha256(asset_raw).hexdigest() == entry['sha256']
    # Mutate only after every check passes. Old catalogue and asset stay intact.
    edits[new] = after_raw
    manifest['officialModelCatalogues'] = [spec['destination'] if u == spec['url'] else u for u in urls]
    return {**result, 'oldURL': spec['url'], 'newURL': spec['destination'],
            'oldCatalogueRetained': True, 'existingAssetRetained': True,
            'publicationApprovedByThisHelper': False}
