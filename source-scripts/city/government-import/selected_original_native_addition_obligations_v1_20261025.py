"""Record complete additive-terrain obligations without granting model approval.

Retained native geometry and metadata stay unchanged. This proof is not a
publisher and cannot replace identity, physical or actual image review.
"""
import argparse
from pathlib import Path
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_native_addition_contract_v1_20261025 import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'preview-config', 'regression']:
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    base = ROOT / 'docs/astra-city/government-import'
    config_path = (ROOT / args.preview_config).resolve()
    assert config_path.is_relative_to(base)
    config = read(config_path)
    assert args.batch.startswith('government-xl-') and '/' not in args.batch
    out = base / args.batch
    assert not out.exists()
    refs = [Path(__file__), config_path, HERE / 'original_native_addition_contract_v1_20261025.py']
    pins, receipts = {}, {}

    def take(name, filename):
        assert name.startswith('government-xl-') and '/' not in name
        if name not in pins:
            receipts[name], pins[name] = authenticate(base / name)
            refs.append(base / name / 'result.json')
        path = base / name / filename
        if filename == 'result.json':
            assert read(path) == receipts[name]
        else:
            assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    before = digest(manifest.read_bytes())
    refs.append(manifest)
    terrain_name, model_name = config['terrainScope'], config['modelScope']
    scope = take(terrain_name, 'scope.json')
    model_scope = take(model_name, 'summary.json')
    terrain_forms = take(terrain_name, 'form-obligations.json.gz')
    model_forms = {}
    for row in model_scope['rows']:
        for item in take(model_name, row['uid'].split('/')[1] + '-forms.json.gz'):
            form = item['building']
            assert form['uid'] not in model_forms or model_forms[form['uid']] == form
            model_forms[form['uid']] = form
    regression = take(args.regression, 'summary.json')
    preview = take(config['batch'], 'result.json')
    retained = preview['retainedNativeEntries']
    assert set(retained) == set(config['retainedNativeUids'])
    installed = {}
    for url in read(manifest)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        refs.append(path)
        for entry in read(path)['models']:
            assert entry['uid'] not in installed
            installed[entry['uid']] = entry
            if entry['uid'] in retained:
                assert entry == retained[entry['uid']]
                asset = (path.parent / entry['asset']).resolve()
                assert asset.is_relative_to(ROOT) and digest(asset.read_bytes()) == entry['sha256']
                refs.append(asset)
    assert len(installed) == config['currentNativeActors']
    assert not set(config['sources']) & set(installed)
    # Each prior phase must bind this exact current manifest, not only its count.
    for name in [terrain_name, model_name, args.regression, config['batch']]:
        assert pins[name][str(manifest.relative_to(ROOT))] == before
    forms = verify(model_forms, terrain_forms, scope, model_scope, regression, retained,
                   sources=config['sources'], terrain_targets=config['terrainTargetUids'],
                   native_count=config['currentNativeActors'], expected_count=len(terrain_forms))
    assert digest(manifest.read_bytes()) == before
    save(out / 'form-obligations.json.gz', list(forms.values()))
    summary = dict(uids=list(config['sources']), forms=len(forms),
                   retainedNativeEntries=retained, currentManifestSHA256=before,
                   additiveObligationsVerified=True, installationApproved=False,
                   physicalAcceptance=False, identityAccepted=False, visualAcceptance=False,
                   newlyInstalled=0, publication=False, sourceGeometryChanges=0,
                   nativeMetadataChanges=0, scriptExternalAICalls=0,
                   qualification='Complete additive obligations and retained-native nonregression only; source and visual approval remain separate.')
    save(out / 'summary.json', summary)
    module('native_addition_obligations_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        args.batch, 'original-additive-terrain-complete-obligations', list(dict.fromkeys(refs)), summary)
    print(dict(forms=len(forms), retainedNativeUids=sorted(retained), installationApproved=False), flush=True)


if __name__ == '__main__':
    main()
