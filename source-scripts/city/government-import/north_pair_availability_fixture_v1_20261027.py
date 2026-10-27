"""Prepare private availability fixtures only; no publication or review credit."""
import copy
import gzip
import hashlib
import json
from pathlib import Path

from original_availability_overlay_v1_20261027 import stage
from original_independent_atomic_contract_v1_20261027 import verify_existing_atomic_group

ROOT = Path(__file__).resolve().parents[3]
PREFIX = 'government-xl-west-kowloon-north-pair-after-ocean-'
BATCH = PREFIX + 'availability-fixture-v1-20261027'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def main():
    docs = ROOT / 'docs/astra-city/government-import'
    out = docs / BATCH
    assert not out.exists(), 'Do not overwrite a prior evidence fixture'
    runtime = docs / (PREFIX + 'three-member-runtime-v2-20261027')
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    selection_raw = (runtime / 'selection.json.gz').read_bytes()
    selection = json.loads(gzip.decompress(selection_raw))
    assert selection['manifestSHA256'] == digest(manifest_raw)
    sources = {row['uid']: row['candidate']['entry']['sha256'] for row in selection['rows']}
    assert sources == {
        'landsd/182397:0': 'f16aa7f57a9b89962a6e1f3183e4dea922c7dbcb173515e608deae1ddc4b48b1',
        'landsd/309340:0': 'a8d145aaefe5aff04cd0f3d36b51ddf03baa951cb24d30504f0e9de272f12f0a'}
    existing_uid = 'landsd/272986:0'
    group = sorted([*sources, existing_uid])
    matches = []
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        catalogue = json.loads(path.read_bytes())
        for entry in catalogue['models']:
            assert entry['uid'] not in sources, 'New source is already installed'
            if entry['uid'] == existing_uid:
                matches.append((url, path, catalogue, entry))
    assert len(matches) == 1
    url, old_path, old_catalogue, existing = matches[0]
    assert existing['sha256'] == '7c06fb22e6f8f8e854a0a4c83d6ca448b840785f275b2bed6546ace4f2d611b8'
    overlay = copy.deepcopy(old_catalogue)
    after_existing = next(e for e in overlay['models'] if e['uid'] == existing_uid)
    after_existing['activationGroup'] = group
    originals = {row['uid']: row['candidate']['entry'] for row in selection['rows']}
    new_models = copy.deepcopy(list(originals.values()))
    for entry in new_models:
        entry.update(priority='landmark', proceduralWindows=False, activationGroup=group)
    verify_existing_atomic_group(new_models, sources, originals, dict.fromkeys(sources),
                                 {existing_uid: existing}, {existing_uid: after_existing})
    catalogue = {k: copy.deepcopy(v) for k, v in old_catalogue.items() if k not in ('models', 'counts')}
    catalogue.update(area=BATCH, models=new_models, counts={'packedModels': len(new_models)})
    out.mkdir()
    local = ROOT / 'source-scripts/city/government-import/local' / BATCH
    (local / 'assets').mkdir(parents=True, exist_ok=False)
    asset_evidence = []
    for row in selection['rows']:
        entry = originals[row['uid']]
        raw = (ROOT / row['candidate']['path']).read_bytes()
        assert digest(raw) == entry['sha256'] and len(raw) == entry['bytes']
        (local / entry['asset']).write_bytes(raw)
        asset_evidence.append({'uid': entry['uid'], 'sha256': digest(raw), 'bytes': len(raw)})
    # Diagnostic fixture includes all three exact originals. Its catalogue is
    # never proposed as a published catalogue, which would duplicate South Tower.
    old_asset = (old_path.parent / existing['asset']).read_bytes()
    assert digest(old_asset) == existing['sha256'] and len(old_asset) == existing['bytes']
    (local / existing['asset']).write_bytes(old_asset)
    (local / 'catalogue.json').write_bytes(encoded(catalogue))
    atomic = copy.deepcopy(catalogue)
    atomic['models'].append(copy.deepcopy(after_existing))
    atomic['counts']['packedModels'] = 3
    (local / 'atomic-catalogue.json').write_bytes(encoded(atomic))
    overlay_path = out / 'existing-catalogue-overlay.json'
    overlay_path.write_bytes(encoded(overlay))
    spec = {'url': url, 'destination': str(Path(url).with_name('catalogue-north-atomic-v1-20261027.json')),
            'source': str(overlay_path.relative_to(ROOT)), 'uid': existing_uid, 'activationGroup': group,
            'beforeSHA256': digest(old_path.read_bytes()), 'afterSHA256': digest(overlay_path.read_bytes())}
    inputs = {}
    def pinned_read(path):
        raw = path.read_bytes()
        assert inputs.setdefault(str(path.relative_to(ROOT)), digest(raw)) == digest(raw)
        return raw
    candidate_manifest = copy.deepcopy(manifest)
    edits = {}
    result = stage(ROOT, spec, candidate_manifest, edits, pinned_read)
    assert len(edits) == 1 and old_path not in edits
    assert manifest_path.read_bytes() == manifest_raw
    (out / 'overlay-spec.json').write_bytes(encoded(spec))
    (out / 'availability-only-manifest.json').write_bytes(encoded(candidate_manifest))
    receipt = {'status': 'private-availability-fixture-only', 'publicationApproved': False,
               'sourceReviewApproved': False, 'visualReviewApproved': False, 'installed': False,
               'activationGroup': group, 'sourceAssets': asset_evidence,
               'existingSourceSHA256': existing['sha256'], 'sourceGeometryChanged': False,
               'manifestSHA256': digest(manifest_raw), 'selectionSHA256': digest(selection_raw),
               'pinnedOverlayInputs': inputs, 'overlay': result,
               'privateCatalogue': str((local / 'catalogue.json').relative_to(ROOT)),
               'atomicFixtureCatalogue': str((local / 'atomic-catalogue.json').relative_to(ROOT))}
    (out / 'summary.json').write_bytes(encoded(receipt))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
